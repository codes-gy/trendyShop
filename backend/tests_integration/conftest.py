"""
[실제 PostgreSQL 통합 테스트 설정]

tests/ 의 단위 테스트는 Prisma를 가짜 객체로 대체하므로 트랜잭션/행 잠금 같은 DB 동작을 검증할 수 없습니다.
이 디렉터리의 테스트는 마이그레이션이 적용된 실제 PostgreSQL(DATABASE_URL)에 붙어서 동시성 시나리오를 검증합니다.

실행 방법 (tests/ 와 반드시 따로 실행해야 합니다. tests/conftest.py가 prisma를 가짜 모듈로 바꿔치기하기 때문):

    export DATABASE_URL=postgresql://user:pass@localhost:5432/trendy_test
    prisma generate && prisma migrate deploy
    pytest tests_integration

DATABASE_URL이 없으면 전체가 skip 됩니다. 테스트는 각자 고유한 이메일/상품을 만들어 사용하지만,
그래도 운영/개발 DB가 아닌 테스트 전용 DB에서만 실행하세요.
"""

import os

import pytest

os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_ACCESS_TOKEN_SECRET", "integration-access-secret-0123456789abcdef")
os.environ.setdefault("JWT_REFRESH_TOKEN_SECRET", "integration-refresh-secret-0123456789abcdef")
os.environ.setdefault("PAYMENT_GATEWAY", "fake")


def pytest_collection_modifyitems(config, items):
    import sys

    reason = None
    if not os.getenv("DATABASE_URL"):
        reason = "DATABASE_URL이 설정되지 않아 통합 테스트를 건너뜁니다."
    elif getattr(sys.modules.get("prisma"), "__fake__", False):
        reason = "tests/ 와 같은 세션에서는 prisma가 가짜 모듈이라 실행할 수 없습니다. `pytest tests_integration`으로 따로 실행하세요."

    if reason:
        skip = pytest.mark.skip(reason=reason)
        for item in items:
            item.add_marker(skip)
