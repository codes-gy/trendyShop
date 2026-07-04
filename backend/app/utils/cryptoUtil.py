import hashlib
import secrets

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """비밀번호를 Bcrypt 알고리즘으로 안전하게 해싱합니다."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """입력된 평문 비밀번호와 해시된 비밀번호가 일치하는지 확인합니다."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_sha256(text: str) -> str:
    """이메일 인증 토큰 등을 저장할 때 사용할 단방향 SHA-256 해시를 생성합니다."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def generate_secure_token() -> str:
    """비밀번호 재설정 링크 등에 사용할 보안상 안전한 랜덤 HEX 토큰을 생성합니다."""
    return secrets.token_hex(32)
