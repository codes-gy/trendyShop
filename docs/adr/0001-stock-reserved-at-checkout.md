# 재고는 결제가 아니라 체크아웃 시점에 조건부 UPDATE로 잡는다

재고는 결제 승인 때가 아니라 주문 생성(체크아웃) 트랜잭션 안에서 `UPDATE ... WHERE stock >= :qty AND isAvailable AND deletedAt IS NULL` 한 문장으로 차감합니다(`OrderRepository.createOrderWithItems`). 영향받은 행이 0이면 주문 전체를 롤백하고 409를 돌려줍니다. 서비스 레이어의 재고 확인은 빠른 실패용일 뿐 보장이 아닙니다. 결제 직전에 재고가 사라지는 일을 막는 대신, 결제 대기 주문이 재고를 붙잡게 되는 비용을 받아들였습니다. 별도 락 서버(Redis 등)나 `SELECT ... FOR UPDATE` 대신 PostgreSQL의 행 잠금과 WHERE 재평가에 기대는 쪽을 골랐습니다.

## Consequences

- 재고를 되돌리는 경로(주문 취소, 결제 대기 만료)는 모두 주문 상태를 compare-and-set으로 `CANCELLED`로 바꾸는 데 성공했을 때만 재고를 복구합니다(`cancelOrderWithRestock`). 이 순서가 깨지면 동시 취소 시 재고가 여러 번 복구됩니다.
- 결제 대기 만료는 스케줄러 없이 그 주문을 조회하거나 결제를 시도할 때만 평가합니다(`OrderService._expireIfStale`). 아무도 건드리지 않는 방치 주문은 재고를 계속 붙잡습니다.

근거: `da91e16`(PR #29, 재고 3개에 8건 주문 성공을 실제 PostgreSQL에서 재현 후 수정), `19289fa`(PR #10), `ed8362f`(PR #12), `backend/tests_integration/test_concurrency.py`.
