import logging
import sys

# 로거 인스턴스 생성
logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)

# 로그 포맷 정의 (시간 [로그레벨] 메시지)
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# 콘솔 출력 핸들러 추가
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def log_info(message: str):
    logger.info(message)


def log_error(message: str, exception: Exception | None = None):
    if exception:
        logger.error(f"{message} | Exception: {str(exception)}", exc_info=True)
    else:
        logger.error(message)
