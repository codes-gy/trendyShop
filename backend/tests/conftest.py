"""
[pytest 전역 설정]

CI 환경 및 로컬 환경에서 `prisma generate`로 생성되는 실제 DB 클라이언트 없이도
앱 모듈을 임포트하고 단위 테스트를 돌릴 수 있도록, `prisma` 패키지를 가짜(Fake)
모듈로 대체합니다.

각 테스트는 필요한 모델 접근자(예: `prisma.user`, `prisma.product`)의 개별
메서드를 `monkeypatch`로 원하는 값을 반환하도록 다시 오버라이드해서 사용합니다.
"""

import sys
import types
from unittest.mock import AsyncMock, MagicMock

_MODEL_METHODS = (
    "find_unique",
    "find_first",
    "find_many",
    "create",
    "update",
    "delete",
    "upsert",
    "count",
)


class _FakeModelAccessor(MagicMock):
    """prisma.<model> 형태의 접근자를 흉내내는 가짜 객체입니다."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for method in _MODEL_METHODS:
            setattr(self, method, AsyncMock())


# schema.prisma에 정의된 모델들의 접근자 이름 (prisma-client-py는 카멜케이스로 노출합니다)
_KNOWN_MODEL_ACCESSORS = (
    "user",
    "product",
    "productimage",
    "cartitem",
    "order",
    "orderitem",
    "payment",
    "delivery",
    "review",
)


class FakePrisma:
    """실제 DB 커넥션 없이 connect/disconnect 흐름만 흉내내는 가짜 Prisma 클라이언트입니다."""

    def __init__(self, *args, **kwargs):
        self._connected = False

    async def connect(self, *args, **kwargs):
        self._connected = True

    async def disconnect(self, *args, **kwargs):
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def __getattr__(self, name: str):
        # user, product, cartItem, order 등 모델 접근자를 요청 시점에 생성합니다.
        accessor = _FakeModelAccessor()
        object.__setattr__(self, name, accessor)
        return accessor


# monkeypatch.setattr(Prisma, "user", ...) 처럼 클래스 속성으로 바로 오버라이드할 수
# 있도록, 알려진 모델 접근자들은 클래스 레벨 속성으로 미리 등록해둡니다.
# (monkeypatch.setattr은 기본적으로 대상 속성이 이미 존재해야 동작합니다.)
for _accessor_name in _KNOWN_MODEL_ACCESSORS:
    setattr(FakePrisma, _accessor_name, _FakeModelAccessor())


def _install_fake_prisma() -> None:
    if "prisma" in sys.modules and getattr(sys.modules["prisma"], "__fake__", False):
        return

    fake_prisma = types.ModuleType("prisma")
    fake_prisma.__fake__ = True
    fake_prisma.Prisma = FakePrisma

    fake_client_submodule = types.ModuleType("prisma.client")
    fake_client_submodule.Prisma = FakePrisma

    sys.modules["prisma"] = fake_prisma
    sys.modules["prisma.client"] = fake_client_submodule


# 테스트 파일들이 `app.*`를 임포트하기 전에 반드시 먼저 실행되어야 하므로
# conftest.py 최상단(모듈 로드 시점)에서 바로 적용합니다.
_install_fake_prisma()
