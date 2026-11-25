# 단위 테스트는 prisma 모듈 자체를 가짜로 바꾸고, DB 동작은 별도 통합 테스트로 검증한다

CI와 로컬에서 Prisma 엔진 바이너리나 DB 없이 테스트를 돌리려고, `backend/tests/conftest.py`가 임포트 시점에 `sys.modules["prisma"]`를 가짜 모듈로 바꿔치기합니다(`prisma.errors`만 진짜를 씁니다). 각 테스트는 리포지토리 함수나 모델 접근자를 `monkeypatch`로 덮어씁니다. 그 대가로 단위 테스트는 트랜잭션·행 잠금·유니크 제약을 전혀 검증하지 못하므로, 동시성과 원자성은 실제 PostgreSQL 위의 `backend/tests_integration/`에서 따로 검증합니다. 두 디렉터리는 같은 pytest 세션에서 돌 수 없습니다(가짜 prisma가 감지되면 통합 테스트는 skip).

근거: `f69b5ae`(PR #3), `be6f675`(PR #29, CI에 통합 테스트 잡 추가), `backend/pyproject.toml`의 `testpaths = ["tests"]`.
