# 결제 완료는 서버가 PG 승인 API로 직접 확인한 결과로만 확정한다

클라이언트가 보낸 `paymentKey`/`amount`만으로 주문을 `PAID`로 바꾸면 실제 결제 없이 결제 완료를 만들 수 있었습니다. 그래서 서버가 서버에 저장된 주문 금액으로 토스페이먼츠 승인 API(`POST /v1/payments/confirm`)를 직접 호출하고, 응답의 금액·PG 주문번호·결제 키·상태(`DONE`)를 다시 검증한 뒤에만 `PENDING → PAID` 전환과 `Payment` 생성을 한 트랜잭션으로 처리합니다(`app/lib/payment.py`, `OrderService.approvePayment`, `OrderRepository.markPaidWithPayment`). 게이트웨이 기본값은 `toss`이고 시크릿 키가 없으면 승인은 항상 실패합니다(fail-closed). `fake`는 명시했을 때만 선택됩니다.

## Consequences

- PG 주문번호 형식 `trendy-order-{주문ID}`(`toPgOrderId`)는 프론트엔드 결제 위젯 호출과 묶여 있어 바꾸기 어렵습니다.
- PG 환불(결제 취소) API는 연동하지 않았습니다. 그래서 결제 완료 주문은 회원이 직접 취소할 수 없고(409) 관리자만 취소하며, 관리자 취소 후에는 수동 환불이 필요합니다. PG 승인 후 DB 반영 직전에 주문이 만료·취소된 경우도 로그(`수동 확인/환불 필요`)를 보고 수동 처리합니다.
- 결제 키는 DB 유니크 제약으로 한 번만 쓰입니다(`20261125000000_add_refresh_token_and_unique_payment_key`).

근거: `da91e16`(PR #29), `e5122fe`(PR #5).
