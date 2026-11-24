import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class SignupRequest(BaseModel):
    """
    회원가입 요청 바디 데이터

    - 보안상 `role`은 입력받지 않습니다. 가입 계정은 서버에서 항상 기본 권한(USER)으로 생성되며,
      권한 변경은 관리자 API(/admin/users/{id}/role)로만 가능합니다.
    - 실제 OAuth 검증 없이 소셜 계정(provider/providerId)을 만들 수 있으면 남의 이메일로 비밀번호 없는
      계정을 선점할 수 있으므로, 공개 회원가입은 이메일(LOCAL) 가입만 허용합니다.
    - 정의되지 않은 필드(role 등)가 들어오면 조용히 무시하지 않고 422로 거부합니다.
    """

    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(..., description="비밀번호는 최소 8자 이상이어야 합니다.")
    name: str = Field(..., description="사용자 이름")
    provider: Literal["LOCAL"] = "LOCAL"

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 2:
            raise ValueError("이름은 공백을 제외하고 최소 2자 이상 입력해야 합니다.")

        # 특수문자가 들어간 비정상적인 이름 차단
        if not re.match(r"^[a-zA-Z가-힣0-9\s]+$", cleaned):
            raise ValueError("이름에는 특수문자를 포함할 수 없습니다.")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("일반 이메일 회원가입 시 비밀번호는 필수입니다.")
        if len(v) < 8:
            raise ValueError("비밀번호는 최소 8자 이상이어야 합니다.")
        return v


class LoginRequest(BaseModel):
    """로컬 로그인 요청 바디 데이터"""

    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("비밀번호를 입력해주세요.")
        return v


class UpdateMeRequest(BaseModel):
    """내 정보 수정 요청 바디 데이터 (이름 및 이메일만 변경 허용)"""

    email: EmailStr
    name: str = Field(..., description="수정할 사용자 이름")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 2:
            raise ValueError("수정할 이름은 공백을 제외하고 최소 2자 이상이어야 합니다.")
        if not re.match(r"^[a-zA-Z가-힣0-9\s]+$", cleaned):
            raise ValueError("이름에는 특수문자를 포함할 수 없습니다.")
        return cleaned


class TokenRefreshRequest(BaseModel):
    """Access Token 만료 시 갱신 요청 바디 데이터"""

    refreshToken: str

    @field_validator("refreshToken")
    @classmethod
    def validate_token_presence(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("리프레시 토큰이 누락되었습니다.")
        return v.strip()


class TokenResponse(BaseModel):
    """로그인 성공 또는 토큰 갱신 성공 시 클라이언트에 발급하는 JWT 구조"""

    accessToken: str
    refreshToken: str


class UserResponse(BaseModel):
    """API 보안을 위해 패스워드를 제외하고 클라이언트에 노출할 유저 정보"""

    id: int
    email: EmailStr
    name: str
    role: Literal["USER", "ADMIN", "SUPER_ADMIN"]
    provider: Literal["LOCAL", "KAKAO", "GOOGLE", "NAVER"]
    providerId: str | None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class RoleUpdateRequest(BaseModel):
    """[관리자] 회원 권한 변경 요청 구조 (SUPER_ADMIN 관련 제약은 서비스 레이어에서 검증)"""

    role: Literal["USER", "ADMIN", "SUPER_ADMIN"]


class AdminUserListQuery(BaseModel):
    """[관리자] 회원 목록 조회용 쿼리 스트링 명세"""

    keyword: str | None = None
    role: Literal["USER", "ADMIN", "SUPER_ADMIN"] | None = None
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
