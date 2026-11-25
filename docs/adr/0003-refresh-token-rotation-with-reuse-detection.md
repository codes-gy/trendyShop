# 리프레시 토큰은 해시로 저장해 회전시키고, 액세스 토큰은 상태 없이 둔다

로그아웃 후에도 리프레시 토큰이 계속 유효하고 같은 토큰을 무한히 재사용할 수 있던 문제를 막으려고, 리프레시 토큰만 서버 상태로 관리하기로 했습니다. 원문 대신 SHA-256 해시를 `RefreshToken` 테이블에 저장하고, 재발급 때마다 compare-and-set으로 회전시키며, 이미 폐기된 토큰이 다시 들어오면 탈취로 보고 그 회원의 리프레시 토큰을 전부 폐기합니다(`AuthService.refreshToken`). 액세스 토큰은 매 요청 DB 조회를 피하려고 상태 없는 JWT로 남겨 두었기 때문에, 로그아웃해도 만료 시각까지는 유효합니다. 이 창은 `JWT_ACCESS_TOKEN_EXPIRES`를 짧게 잡아 줄입니다.

근거: `1d8ce51`(PR #29), `backend/prisma/migrations/20261125000000_add_refresh_token_and_unique_payment_key`, `test_concurrent_refresh_with_same_token_rotates_once`.
