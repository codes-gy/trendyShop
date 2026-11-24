"""
[결제 게이트웨이(PG) 연동 모듈]

클라이언트가 보낸 paymentKey/amount만 믿고 주문을 PAID로 바꾸면, 실제로 결제하지 않은 사용자도
임의의 paymentKey로 결제 완료 처리를 할 수 있습니다. 그래서 서버가 PG사의 "결제 승인(confirm)" API를
직접 호출해 실제 승인된 금액/주문번호를 확인한 뒤에만 결제 완료로 처리합니다.

- PaymentGateway: 서비스 레이어가 의존하는 인터페이스
- TossPaymentGateway: 토스페이먼츠 결제 승인 API(POST /v1/payments/confirm) 구현체
- FakePaymentGateway: 로컬 개발/테스트용 가짜 구현체 (PAYMENT_GATEWAY=fake 일 때만 사용)

환불(결제 취소), 웹훅, 가상계좌 입금 대기(WAITING_FOR_DEPOSIT) 처리는 아직 구현되어 있지 않습니다.
"""

import base64
from dataclasses import dataclass
from typing import Protocol

import httpx
from app.lib import env


class PaymentGatewayError(Exception):
    """PG사 승인 실패(거절, 통신 오류, 설정 누락 등)"""

    def __init__(self, message: str, code: str | None = None, retryable: bool = False):
        super().__init__(message)
        self.message = message
        self.code = code
        self.retryable = retryable


@dataclass(frozen=True)
class PaymentConfirmation:
    """PG사가 실제로 승인했다고 응답한 결제 정보"""

    payment_key: str
    pg_order_id: str
    total_amount: int
    status: str  # 토스 기준: DONE(승인 완료), WAITING_FOR_DEPOSIT(가상계좌 입금 대기) 등
    method: str | None = None


def toPgOrderId(order_id: int) -> str:
    """
    [우리 주문 ID → PG 주문번호 변환]
    - 토스페이먼츠 orderId는 6~64자의 영문/숫자/-/_ 문자열이어야 해서, 정수 주문 ID를 그대로 쓸 수 없습니다.
    - 프론트엔드 결제창(위젯) 호출 시에도 반드시 이 형식의 orderId를 넘겨야 승인 검증이 통과합니다.
    """
    return f"trendy-order-{order_id}"


class PaymentGateway(Protocol):
    async def confirm(self, payment_key: str, pg_order_id: str, amount: int) -> PaymentConfirmation: ...


class TossPaymentGateway:
    """토스페이먼츠 결제 승인 API 구현체 (https://docs.tosspayments.com/reference#결제-승인)"""

    def __init__(self, secret_key: str | None, base_url: str, timeout: float = 10.0, transport=None):
        self._secret_key = secret_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._transport = transport  # 테스트에서 httpx.MockTransport 주입용

    async def confirm(self, payment_key: str, pg_order_id: str, amount: int) -> PaymentConfirmation:
        if not self._secret_key:
            raise PaymentGatewayError("결제 게이트웨이 시크릿 키(TOSS_PAYMENTS_SECRET_KEY)가 설정되지 않았습니다.")

        # 시크릿 키 뒤에 ':'를 붙여 base64 인코딩한 값을 Basic 인증 헤더로 보냅니다.
        encoded = base64.b64encode(f"{self._secret_key}:".encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json",
            # 같은 paymentKey 승인 요청이 재시도되어도 PG에서 한 번만 처리되도록 멱등키를 함께 보냅니다.
            "Idempotency-Key": payment_key,
        }
        body = {"paymentKey": payment_key, "orderId": pg_order_id, "amount": amount}

        try:
            async with httpx.AsyncClient(timeout=self._timeout, transport=self._transport) as client:
                resp = await client.post(f"{self._base_url}/v1/payments/confirm", json=body, headers=headers)
        except httpx.HTTPError as e:
            raise PaymentGatewayError("결제 승인 서버와 통신하지 못했습니다.", retryable=True) from e

        try:
            data = resp.json()
        except ValueError:
            data = {}

        if resp.status_code != 200:
            raise PaymentGatewayError(
                data.get("message") or "결제 승인에 실패했습니다.",
                code=data.get("code"),
                retryable=resp.status_code >= 500,
            )

        try:
            return PaymentConfirmation(
                payment_key=str(data["paymentKey"]),
                pg_order_id=str(data["orderId"]),
                total_amount=int(data["totalAmount"]),
                status=str(data["status"]),
                method=data.get("method"),
            )
        except (KeyError, TypeError, ValueError) as e:
            raise PaymentGatewayError("결제 승인 응답 형식이 올바르지 않습니다.") from e


class FakePaymentGateway:
    """
    로컬 개발/테스트용 가짜 게이트웨이. 요청받은 금액 그대로 승인된 것으로 응답합니다.
    운영 환경에서 쓰이면 결제 검증이 무력화되므로, PAYMENT_GATEWAY=fake 를 명시했을 때만 선택됩니다.
    """

    def __init__(self):
        self.confirmed: list[tuple[str, str, int]] = []

    async def confirm(self, payment_key: str, pg_order_id: str, amount: int) -> PaymentConfirmation:
        self.confirmed.append((payment_key, pg_order_id, amount))
        return PaymentConfirmation(
            payment_key=payment_key,
            pg_order_id=pg_order_id,
            total_amount=amount,
            status="DONE",
        )


_gateway: PaymentGateway | None = None


def getPaymentGateway() -> PaymentGateway:
    """환경변수(PAYMENT_GATEWAY)에 따라 사용할 게이트웨이를 반환합니다. (테스트에서는 monkeypatch로 교체)"""
    global _gateway
    if _gateway is None:
        if env.PAYMENT_GATEWAY == "fake":
            _gateway = FakePaymentGateway()
        elif env.PAYMENT_GATEWAY == "toss":
            _gateway = TossPaymentGateway(env.TOSS_PAYMENTS_SECRET_KEY, env.TOSS_PAYMENTS_API_BASE_URL)
        else:
            raise PaymentGatewayError(f"지원하지 않는 PAYMENT_GATEWAY 값입니다: {env.PAYMENT_GATEWAY}")
    return _gateway
