import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class SignupRequest(BaseModel):
    """회원가입 요청 바디 데이터"""

    email: EmailStr
    password: str | None = Field(None, description="비밀번호는 최소 8자 이상이어야 합니다.")
    name: str = Field(..., description="사용자 이름")
    role: Literal["USER", "ADMIN", "SUPER_ADMIN"] = "USER"
    provider: Literal["LOCAL", "KAKAO", "GOOGLE", "NAVER"] = "LOCAL"
    providerId: str | None = Field(None, description="소셜 로그인 연동 시 고유 ID")

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

    @model_validator(mode="after")
    def validate_provider_dependencies(self) -> "SignupRequest":
        # 일반 로컬 회원가입일 때
        if self.provider == "LOCAL":
            if not self.password or not self.password.strip():
                raise ValueError("일반 이메일 회원가입 시 비밀번호는 필수입니다.")
            if len(self.password) < 8:
                raise ValueError("비밀번호는 최소 8자 이상이어야 합니다.")

        # 소셜 가입(간편 로그인)일 때
        else:
            if not self.providerId or not self.providerId.strip():
                raise ValueError(f"{self.provider} 회원가입 시 소셜 연동은 필수입니다.")
            # 보안상 소셜 가입 유저의 패스워드는 무조건 비워둠(None)
            self.password = None

        return self


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
