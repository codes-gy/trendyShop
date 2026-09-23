# TrendyShop

Python 기반 고성능 비동기 프레임워크인 FastAPI와 Next.js App Router를 활용한 모던 쇼핑몰 프로젝트입니다.

## 기술 스택

**Backend**
- FastAPI (Python 3.12)
- Prisma ORM (`prisma-client-py`) + PostgreSQL
- JWT 기반 인증 (Access/Refresh Token), `passlib`/`bcrypt`
- `ruff` (lint & format)
- `pytest` (단위 테스트)

**Frontend**
- Next.js 16 (App Router)
- React 19
- Tailwind CSS 4

**Infra**
- Docker Compose (PostgreSQL, pgAdmin, Redis)

## 주요 기능

계층은 `router → controller → service → repository` 구조를 따르며, 모든 API 응답은
`{ success, message, data }`(성공) 또는 `{ success, message, error }`(실패) 형태로 통일되어 있습니다.

| 도메인 | 설명 |
| --- | --- |
| **인증 (Auth)** | 이메일 회원가입/로그인, JWT 발급·재발급, 내 정보 조회·수정, 로그아웃. `provider` 필드로 소셜 로그인(카카오/구글/네이버) 스키마를 지원 (실제 OAuth 연동은 미구현) |
| **상품 (Product)** | 키워드/가격/판매여부 검색·필터, 정렬, 페이지네이션, 상세 조회. 등록/수정/삭제(소프트 딜리트)는 관리자 전용 |
| **장바구니 (Cart)** | 담기(이미 담긴 상품이면 수량 병합), 목록, 수량 변경, 삭제. 재고·판매 상태 검증 |
| **주문 (Order)** | 장바구니 선택 체크아웃(주문 스냅샷 생성 + 재고 차감을 트랜잭션으로 처리), 결제 승인, 주문 취소(+재고 복구), 결제 대기(PENDING) 주문 자동 만료 |
| **배송 (Delivery)** | 관리자 전용 배송 등록·상태 변경. 배송 상태에 따라 주문 상태 자동 동기화 (배송시작→SHIPPED, 전량배송완료→DELIVERED) |
| **리뷰 (Review)** | 실구매자만 작성 가능, 동일 상품 중복 작성 방지(DB 유니크 제약), 본인 수정/본인 또는 관리자 삭제 |
| **관리자 (Admin)** | 전체 회원 목록/상세 조회, 권한 변경 (SUPER_ADMIN 승격 및 SUPER_ADMIN 권한 변경은 SUPER_ADMIN만 가능) |

## API 엔드포인트

기본 prefix는 각 라우터 기준이며, 실행 중인 서버의 `/docs`(Swagger UI)에서 전체 스펙을 확인할 수 있습니다.

### Auth (`/auth`)
| Method | Path | 인증 | 설명 |
| --- | --- | --- | --- |
| POST | `/auth/signup` | - | 회원가입 |
| POST | `/auth/login` | - | 로그인 |
| GET | `/auth/me` | 로그인 | 내 정보 조회 |
| PATCH | `/auth/updateMe` | 로그인 | 내 정보 수정 |
| POST | `/auth/logout` | 로그인 | 로그아웃 |
| POST | `/auth/refresh` | - | 토큰 재발급 |

### Product (`/products`)
| Method | Path | 인증 | 설명 |
| --- | --- | --- | --- |
| GET | `/products` | - | 목록 조회 (검색/필터/정렬/페이지네이션) |
| GET | `/products/{id}` | - | 상세 조회 |
| POST | `/products` | 관리자 | 등록 |
| PATCH | `/products/{id}` | 관리자 | 수정 |
| DELETE | `/products/{id}` | 관리자 | 삭제 (소프트 딜리트) |

### Cart (`/cart`)
| Method | Path | 인증 | 설명 |
| --- | --- | --- | --- |
| GET | `/cart` | 로그인 | 내 장바구니 조회 |
| POST | `/cart` | 로그인 | 담기 |
| PATCH | `/cart/{id}` | 로그인(본인) | 수량 변경 |
| DELETE | `/cart/{id}` | 로그인(본인) | 삭제 |

### Order (`/orders`)
| Method | Path | 인증 | 설명 |
| --- | --- | --- | --- |
| GET | `/orders` | 로그인 | 내 주문 목록 |
| GET | `/orders/{id}` | 로그인(본인) | 주문 상세 |
| POST | `/orders` | 로그인 | 주문 생성(체크아웃) |
| POST | `/orders/payment` | 로그인(본인) | 결제 승인 |
| PATCH | `/orders/{id}/cancel` | 로그인(본인) 또는 관리자 | 주문 취소 |

### Delivery (`/deliveries`)
| Method | Path | 인증 | 설명 |
| --- | --- | --- | --- |
| POST | `/deliveries` | 관리자 | 배송 등록 (결제 완료 주문만) |
| PATCH | `/deliveries/{id}` | 관리자 | 배송 상태/운송장 변경 |

### Review (`/reviews`)
| Method | Path | 인증 | 설명 |
| --- | --- | --- | --- |
| GET | `/reviews?productId=` | - | 상품별 리뷰 목록 |
| POST | `/reviews` | 로그인(실구매자) | 작성 |
| PATCH | `/reviews/{id}` | 로그인(본인) | 수정 |
| DELETE | `/reviews/{id}` | 로그인(본인) 또는 관리자 | 삭제 |

### Admin (`/admin/users`)
| Method | Path | 인증 | 설명 |
| --- | --- | --- | --- |
| GET | `/admin/users` | 관리자 | 회원 목록 (검색/역할 필터/페이지네이션) |
| GET | `/admin/users/{id}` | 관리자 | 회원 상세 |
| PATCH | `/admin/users/{id}/role` | 관리자 | 권한 변경 |

## 시작하기

### 1. 데이터베이스 실행 (Docker Compose)

```bash
docker compose up -d postgres
```

PostgreSQL이 `localhost:5432`에 뜹니다 (계정/DB는 `docker-compose.yaml` 참고). 필요하면 pgAdmin(`localhost:8080`)과 Redis(`localhost:6379`)도 함께 뜹니다.

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env  # 없다면 아래 "환경 변수" 항목을 참고해 직접 작성
prisma generate
prisma migrate deploy   # 또는 로컬 개발 중이라면 prisma migrate dev

uvicorn app.main:app --reload
```

기본적으로 `http://localhost:8000`에서 뜨고, `http://localhost:8000/docs`에서 Swagger UI를 확인할 수 있습니다.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

`http://localhost:4000`에서 뜹니다 (백엔드 CORS 설정이 이 포트를 기준으로 되어 있습니다).

## 환경 변수 (`backend/.env`)

| 변수 | 설명 | 예시 |
| --- | --- | --- |
| `DATABASE_URL` | PostgreSQL 연결 문자열 | `postgresql://trendy_user:postgres@localhost:5432/trendy_commerce` |
| `JWT_ALGORITHM` | JWT 서명 알고리즘 | `HS256` |
| `JWT_ACCESS_TOKEN_SECRET` | Access Token 서명 비밀키 | (직접 생성) |
| `JWT_REFRESH_TOKEN_SECRET` | Refresh Token 서명 비밀키 | (직접 생성) |
| `ACCESS_TOKEN_COOKIE_NAME` | Access Token 쿠키 이름 | `accessToken` |
| `REFRESH_TOKEN_COOKIE_NAME` | Refresh Token 쿠키 이름 | `refreshToken` |
| `JWT_ACCESS_TOKEN_EXPIRES` | Access Token 만료 시간 | - |
| `JWT_REFRESH_TOKEN_EXPIRES` | Refresh Token 만료 시간 | - |
| `ORDER_PENDING_EXPIRATION_MINUTES` | 결제 대기 주문 자동 만료 기준(분). 미설정 시 기본 30 | `30` |

## 테스트

```bash
cd backend
prisma generate  # 최초 1회 (실제 DB 연결 없이도 타입 생성만 되면 됩니다)
pytest
```

현재 총 93개의 테스트가 모두 통과합니다. 실제 DB나 Prisma 엔진 바이너리 없이도 돌아가도록,
`tests/conftest.py`에서 Prisma 클라이언트를 가짜(mock) 객체로 대체하고 각 테스트가
리포지토리 함수(예: `ProductRepository.findById`)를 `monkeypatch`로 오버라이드하는 방식을
사용합니다. 그래서 검증 대상은 서비스/컨트롤러/라우터의 로직(권한, 재고 검증, 응답 형태 등)이며,
Prisma 쿼리 자체의 정확성이나 트랜잭션 동작은 실제 DB가 붙은 환경에서 별도로 확인이 필요합니다.

코드 스타일 검사:

```bash
ruff format .
ruff check .
```

## 프로젝트 구조

```
backend/
  app/
    controllers/   # 요청을 받아 서비스 호출 후 표준 응답 포맷으로 감싸는 레이어
    services/       # 비즈니스 로직 (검증, 트랜잭션 조합 등)
    repositories/   # Prisma 쿼리만 담당하는 데이터 접근 레이어
    routers/        # FastAPI 라우트 정의 및 인증/권한 가드 연결
    types/          # Pydantic 요청/응답 스키마
    lib/            # Prisma 클라이언트, JWT, 환경변수, passport(인증 전략) 등 공용 모듈
    errors/         # 전역 예외 핸들러
    utils/          # 범용 유틸 함수
  prisma/
    schema.prisma   # 데이터 모델 정의
    migrations/     # 마이그레이션 이력
  tests/            # 도메인별 pytest 테스트 (+conftest.py의 Prisma mock 설정)
frontend/
  app/              # Next.js App Router 페이지 및 컴포넌트
```

## 알려진 제한 사항

- **결제 대기 주문 자동 만료가 지연 평가(lazy evaluation) 방식입니다.** 별도 스케줄러 없이, 해당
  주문이 조회되거나 결제가 시도되는 시점에만 만료 여부를 확인합니다. 아무도 접근하지 않는 방치
  주문은 재고가 즉시 복구되지 않습니다. 주기적인 배치 정리가 필요하면 스케줄러(APScheduler 등)
  도입이 필요합니다.
- **결제 완료(PAID) 주문을 취소할 때 결제 환불 처리는 자동화되어 있지 않습니다.** `Payment` 모델에
  환불 상태 필드가 없어서, 재고 복구와 주문 상태 전환까지만 처리됩니다.
- **CI(`BACKEND_CHECK.yaml`)에는 `pytest` 실행 단계가 없고 `ruff` 검사만 있습니다.** 테스트를
  CI에서도 자동으로 돌리려면 워크플로에 `prisma generate` 이후 `pytest` 스텝 추가를 권장합니다.
- 상품 이미지 업로드(`ProductImage`)는 API로 구현되어 있지 않습니다 (스키마와 응답 모델에는 이미
  포함되어 있으나, 별도 업로드 엔드포인트가 없습니다).
