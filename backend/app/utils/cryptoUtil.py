import hashlib
import secrets

import bcrypt


def hash_password(password: str) -> str:
    """비밀번호를 Bcrypt 알고리즘으로 안전하게 해싱합니다."""
    password_bytes = password.encode("utf-8")

    # bcrypt.gensalt()가 안전한 솔트(Salt)를 자동으로 생성하여 결합해 줍니다.
    hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    # DB 저장 및 편리한 사용을 위해 문자열(str)로 변환하여 리턴합니다.
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """입력된 평문 비밀번호와 해시된 비밀번호가 일치하는지 확인합니다."""
    plain_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")

    # bcrypt.checkpw가 내부적으로 salt를 분리하여 연산 후 일치 여부(True/False)를 반환합니다.
    return bcrypt.checkpw(plain_bytes, hashed_bytes)


def hash_sha256(text: str) -> str:
    """이메일 인증 토큰 등을 저장할 때 사용할 단방향 SHA-256 해시를 생성합니다."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def generate_secure_token() -> str:
    """비밀번호 재설정 링크 등에 사용할 보안상 안전한 랜덤 HEX 토큰을 생성합니다."""
    return secrets.token_hex(32)
