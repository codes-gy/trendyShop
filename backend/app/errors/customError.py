from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from ..types.responseType import ErrorDetails, ErrorResponseModel
from ..utils.loggerUtil import log_error


def init_exception_handlers(app: FastAPI) -> None:

    # FastAPI 표준 HTTPException 처리
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        log_error(f"HTTP 에러 발생: [{exc.status_code}] {exc.detail}")

        # Pydantic 모델 규격에 맞게 에러 객체 생성
        response_data = ErrorResponseModel(
            success=False,
            message=exc.detail,
            error=ErrorDetails(code=f"HTTP_{exc.status_code}", message=exc.detail),
        )

        return JSONResponse(
            status_code=exc.status_code, content=response_data.model_dump()
        )

    # Pydantic 요청 데이터 검증 실패 에러 (422 Unprocessable Entity) 처리
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        # 파싱 에러 메시지를 보기 좋게 가공
        errors = exc.errors()
        error_details = []
        for err in errors:
            loc = " -> ".join(str(p) for p in err.get("loc", []))
            msg = err.get("msg", "잘못된 입력값입니다.")
            error_details.append(f"[{loc}] {msg}")

        friendly_message = " / ".join(error_details)
        log_error(f"요청 데이터 검증 실패: {friendly_message}")

        # 유효성 검증 실패 규격 모델 생성
        response_data = ErrorResponseModel(
            success=False,
            message="요청 데이터가 유효하지 않습니다.",
            error=ErrorDetails(code="VALIDATION_ERROR", message=friendly_message),
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response_data.model_dump(),
        )

    # ③ 최상위 시스템 에러 (500 Internal Server Error) 처리
    @app.exception_handler(Exception)
    async def universal_exception_handler(request: Request, exc: Exception):
        # 1. 서버 콘솔/파일에 에러 트레이스백 상세 기록
        error_msg = f"지정되지 않은 시스템 에러 발생: {str(exc)}"
        log_error(error_msg, exception=exc)

        # 2. 크리티컬 에러이므로 슬랙으로 즉시 긴급 알림 전송 (주석 해제 시 사용 가능)
        # asyncio.create_task(
        #      send_slack_alert(
        #          f"서버 500 에러 발생!\n경로: {request.url.path}\n에러 내용: {str(exc)}",
        #          level="ERROR",
        #      )
        # )

        # 3. 사용자/프론트엔드에게는 보안을 위해 디테일한 에러를 숨기고 규격화된 메시지만 응답
        response_data = ErrorResponseModel(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error=ErrorDetails(
                code="INTERNAL_SERVER_ERROR", message="잠시 후 다시 시도해 주세요."
            ),
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response_data.model_dump(),
        )
