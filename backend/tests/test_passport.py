import pytest
from app.errors.customError import init_exception_handlers
from app.lib.passport.jwtStrategy import jwt_strategy
from app.lib.passport.localStrategy import local_strategy
from app.utils.stringUtil import create_access_token
from fastapi import Depends, FastAPI, status
from fastapi.testclient import TestClient
from pydantic import BaseModel

# 1. 테스트용 가상 FastAPI 앱 생성 및 전역 에러 핸들러 등록
app = FastAPI()
init_exception_handlers(app)


# 데이터 검증 테스트용 간단한 바디 스키마
class LoginPayload(BaseModel):
    email: str
    password: str


# 3. 실전 웹 요청 시나리오 테스트
client = TestClient(app, raise_server_exceptions=False)


# [테스트 라우터 ①] 로그인 엔드포인트
@app.post("/api/login")
async def login(payload: LoginPayload):
    # 우리가 만든 local_strategy 검증
    user = await local_strategy(payload.email, payload.password)
    token = create_access_token(data={"sub": user.email})
    return {"success": True, "message": "로그인 성공", "data": {"access_token": token}}


# [테스트 라우터 ②] JWT 인증이 필요한 보호된 엔드포인트
@app.get("/api/me")
async def get_me(current_user: dict = Depends(jwt_strategy)):
    return {
        "success": True,
        "message": "인증 성공",
        "data": {"email": current_user.email},
    }


# [테스트 라우터 ③] 강제로 500 시스템 에러를 내는 엔드포인트 (전역 핸들러 검증용)
@app.get("/api/error")
async def force_error():
    return 1 / 0


# 2. Prisma DB 조회를 테스트용 가짜 데이터로 대체 (Mocking)
@pytest.fixture(autouse=True)
def mock_prisma_user(monkeypatch):
    import app.lib.passport.localStrategy as local_strat
    from prisma.client import Prisma

    class FakeUser:
        def __init__(self):
            self.email = "test@example.com"
            # passlib를 타지 않으므로 평문 형태나 임의의 문자열을 두어도 무방합니다.
            self.password = "mocked_hashed_password_123"

    # 1. 가짜 데이터베이스 find_unique 조회 함수
    async def fake_find_unique(*args, **kwargs):
        where = kwargs.get("where", {})
        if where.get("email") == "test@example.com":
            return FakeUser()
        return None

    class FakeUserActions:
        find_unique = fake_find_unique

    @property
    def fake_user_property(self):
        return FakeUserActions()

    # Prisma 클래스의 user 프로퍼티를 가짜 객체로 대체
    monkeypatch.setattr(Prisma, "user", fake_user_property)

    # 2. 🔥 passlib 버그를 완전히 우회하기 위해 verify_password 함수를 직접 모킹
    # 입력된 비밀번호가 'password123'이면 True, 틀리면 False를 반환하는 직관적인 가짜 검증 함수입니다.
    def fake_verify_password(plain_password: str, hashed_password: str) -> bool:
        return plain_password == "password123"

    # localStrategy 파일이 내포한 verify_password 함수를 가짜 함수로 덮어씌웁니다.
    monkeypatch.setattr(local_strat, "verify_password", fake_verify_password)


def test_passport_and_exception_flow():
    # -------------------------------------------------------------
    # 시나리오 1: 잘못된 패스워드로 로그인 시도 (401 에러 및 exceptionUtil 검증)
    # -------------------------------------------------------------
    wrong_login_resp = client.post(
        "/api/login", json={"email": "test@example.com", "password": "wrong"}
    )
    assert wrong_login_resp.status_code == status.HTTP_401_UNAUTHORIZED

    json_data = wrong_login_resp.json()
    assert json_data["success"] is False
    assert "error" in json_data
    assert json_data["error"]["code"] == "HTTP_401"

    # -------------------------------------------------------------
    # 시나리오 2: 바디 데이터 규격 유실 (422 Pydantic 검증 에러 흐름 테스트)
    # -------------------------------------------------------------
    bad_request_resp = client.post("/api/login", json={"email": "not_match_payload"})
    assert bad_request_resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert bad_request_resp.json()["error"]["code"] == "VALIDATION_ERROR"

    # -------------------------------------------------------------
    # 시나리오 3: 올바른 로그인 및 토큰 발급
    # -------------------------------------------------------------
    login_resp = client.post(
        "/api/login", json={"email": "test@example.com", "password": "password123"}
    )
    assert login_resp.status_code == status.HTTP_200_OK
    token = login_resp.json()["data"]["access_token"]

    # -------------------------------------------------------------
    # 시나리오 4: 인증 헤더 없이 보호된 라우터 접근 (401 차단 검증)
    # -------------------------------------------------------------
    no_auth_resp = client.get("/api/me")
    assert no_auth_resp.status_code == status.HTTP_401_UNAUTHORIZED

    # -------------------------------------------------------------
    # 시나리오 5: 발급받은 토큰 장착 후 보호된 라우터 접근 (성공 검증)
    # -------------------------------------------------------------
    headers = {"Authorization": f"Bearer {token}"}
    auth_resp = client.get("/api/me", headers=headers)
    assert auth_resp.status_code == status.HTTP_200_OK
    assert auth_resp.json()["data"]["email"] == "test@example.com"

    # -------------------------------------------------------------
    # 시나리오 6: 시스템 내부 에러 발생 시 500 핸들러 가동 검증
    # -------------------------------------------------------------
    system_error_resp = client.get("/api/error")
    assert system_error_resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert system_error_resp.json()["error"]["code"] == "INTERNAL_SERVER_ERROR"
