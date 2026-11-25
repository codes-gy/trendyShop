# TrendyShop

FastAPI + Prisma(PostgreSQL) 백엔드와 Next.js 프론트엔드로 된 쇼핑몰. 실행·환경 변수·API 목록은 `README.md`에 있습니다.

## 먼저 읽을 것

- **용어**: 도메인 개념에 이름을 붙이거나(모델·함수·응답 메시지·UI 문구) 회원/주문/결제/배송 관련 요구를 해석할 때 `GLOSSARY.md`의 용어를 쓰세요. `_Avoid_`에 있는 동의어는 새 코드에 들이지 않습니다.
- **결정 기록**: 재고 차감·결제 승인·리프레시 토큰·테스트 구조를 바꾸기 전에 `docs/adr/`의 해당 ADR을 읽으세요. 이미 고른 트레이드오프를 되돌리는 변경이면 새 ADR로 남깁니다.

## 깨면 안 되는 불변식

- **권한은 가입 입력에서 받지 않습니다.** `SignupRequest`는 `extra="forbid"`이고 `AuthRepository.createUser`가 `role`을 `USER`로 고정합니다. 권한 변경 경로는 `PATCH /admin/users/{id}/role` 하나이며, `SUPER_ADMIN` 부여와 `SUPER_ADMIN`의 권한 변경은 `SUPER_ADMIN`만 합니다. 공개 가입·이메일 로그인은 `provider=LOCAL`만 허용합니다.
- **재고는 조건부 UPDATE로만 차감합니다.** `update_many(where={stock: {gte: qty}, isAvailable: True, deletedAt: None})` 후 영향 행이 1인지 확인하는 패턴을 유지하세요. 읽고-계산하고-쓰는 방식은 동시 주문에서 초과 판매를 냅니다.
- **주문 상태 전환은 compare-and-set입니다.** `where={"id": ..., "status": <기대 상태>}`로 바꾸고, 재고 복구는 `CANCELLED` 전환이 성공한 트랜잭션 안에서만 합니다.
- **결제 완료(`PAID`)는 PG 승인 응답으로만 만듭니다.** PG에 보내는 금액은 서버에 저장된 `Order.totalPrice`이고, 응답의 금액·PG 주문번호·결제 키·`DONE` 상태를 모두 검증합니다. 결제 완료 주문의 회원 직접 취소는 환불 연동 전까지 막혀 있습니다.
- **리프레시 토큰은 SHA-256 해시로만 저장합니다**(`app/lib/token.hashToken`). 원문을 DB나 로그에 남기지 않습니다.

## 함정

- **두 종류의 테스트는 따로 돌립니다.** `pytest`(= `tests/`)는 `tests/conftest.py`가 `prisma` 모듈을 가짜로 바꿔치기하므로 트랜잭션·유니크 제약을 검증하지 못합니다. DB 동작이 걸린 변경은 `tests_integration/`에 테스트를 두고 실제 PostgreSQL 테스트 전용 DB에서 `DATABASE_URL=... prisma migrate deploy && pytest tests_integration`으로 돌리세요. `DATABASE_URL`이 없으면 조용히 전부 skip 되니 통과로 착각하지 마세요.
- **환경 변수는 임포트 시점에 읽힙니다**(`app/lib/env.py`). JWT 시크릿 등은 `app.*` 임포트보다 먼저 설정되어야 하고(conftest가 테스트용 기본값을 채웁니다), 테스트에서 값을 바꾸려면 `os.environ`이 아니라 `app.lib.env`/사용처 모듈의 속성을 `monkeypatch`하세요. 결제 게이트웨이는 `getPaymentGateway()`를 `monkeypatch`합니다.
- **`prisma generate`가 먼저 필요합니다.** 생성된 클라이언트(`backend/prisma/generated/`, gitignore됨)를 `app/lib/prisma.py`가 `sys.path`에 넣어 임포트합니다. 스키마를 바꾸면 마이그레이션 파일을 함께 커밋하세요.
- **로컬 서버에서 결제를 시험하려면 `PAYMENT_GATEWAY=fake`** 를 명시하세요. 기본값 `toss`는 시크릿 키가 없으면 항상 실패합니다(fail-closed).
- **프론트엔드는 인증만 백엔드에 연결돼 있습니다.** 상품 카탈로그(`frontend/app/lib/products.ts`)와 장바구니(`cart-context.tsx`, localStorage)는 목업이고, 화면의 쿠폰·마일리지·상품 옵션·`isSale`(할인)은 백엔드에 없는 개념입니다. 프론트엔드 작업 전에는 `frontend/AGENTS.md`(Next.js 16 변경 사항)를 따르세요.
- **응답 포맷 예외**: 대부분의 API는 `{success, message, data}`로 감싸지만 `GET /auth/me`는 `response_model=UserResponse`라 감싸지 않습니다.

## 컨벤션

- 백엔드 계층은 `router → controller → service → repository`. Prisma 쿼리는 repository에만, 비즈니스 검증과 `HTTPException`은 service에 둡니다. 여러 쓰기를 묶는 트랜잭션은 repository 함수 하나(`prisma.tx()`) 안에서 끝냅니다.
- 파이썬이지만 함수 이름은 camelCase(`createOrderWithItems`), 모듈은 `from app.repositories import OrderRepository as orderRepository`처럼 별칭으로 임포트합니다. 주석·에러 메시지·커밋 메시지는 한국어입니다.
- 커밋은 `feat:`/`fix:`/`docs:`/`ci:`/`chore:`/`style:` + 한국어 요약, 브랜치는 `feature/gy/<주제>`, `fix/gy/<주제>`. PR은 `.github/PULL_REQUEST_TEMPLATE.md`를 채웁니다.
