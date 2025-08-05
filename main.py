from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.endpoints import eiu, customs, admin, socioeconomic
from app.core.setting import get_settings
from app.core.logger import setup_logger, get_logger
from app.core.exceptions import BaseAppException, ErrorCode
from app.core.constants.error import ErrorMessages
import time
import uuid

settings = get_settings()

setup_logger()
logger = get_logger()

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    debug=settings.DEBUG
)

# 로깅 미들웨어
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    # 고유 요청 ID 생성
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    
    # 요청 시작 시간
    start_time = time.time()
    
    # 요청 정보
    path = request.url.path
    method = request.method
    client_ip = request.client.host if request.client else "N/A"
    user_agent = request.headers.get("User-Agent", "N/A")
    
    # 요청 시작 로그
    logger.info(f"[{request_id}] Request started | {method} {path} | IP: {client_ip} | User-Agent: {user_agent}")
    
    try:
        # 요청 처리
        response = await call_next(request)
        
        # 처리 시간 계산
        process_time = time.time() - start_time
        
        # 응답 로그
        logger.info(
            f"[{request_id}] Request completed | {method} {path} | "
            f"Status: {response.status_code} | Time: {process_time:.3f}s"
        )
        
        return response
    except Exception as e:
        # 에러 발생 시 로그
        process_time = time.time() - start_time
        logger.error(
            f"[{request_id}] Request failed | {method} {path} | "
            f"Error: {str(e)} | Time: {process_time:.3f}s"
        )
        raise

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서비스 설정
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 라우터 등록
app.include_router(eiu.router)
app.include_router(customs.router)
app.include_router(socioeconomic.router)
app.include_router(admin.router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """요청 검증 예외 처리기.
    
    Pydantic 요청 검증 실패 시 표준화된 에러 응답을 반환합니다.
    
    Args:
        request (Request): 실패한 요청 객체
        exc (RequestValidationError): 검증 예외 객체
        
    Returns:
        JSONResponse: 표준화된 에러 응답
    """
    logger.warning(f"요청 검증 실패 - Path: {request.url.path}, 에러: {exc.errors()}")
    return JSONResponse(
        status_code=200,
        content={
            "success": "false",
            "error_code": ErrorCode.INVALID_REQUEST_PARAMETER.value,
            "message": ErrorMessages.get_message(ErrorCode.INVALID_REQUEST_PARAMETER),
            "detail": None
        }
    )


@app.exception_handler(BaseAppException)
async def custom_exception_handler(request: Request, exc: BaseAppException):
    """커스텀 예외 처리기.
    
    애플리케이션에서 정의한 커스텀 예외를 처리하여
    표준화된 에러 응답을 반환합니다.
    
    Args:
        request (Request): 실패한 요청 객체
        exc (BaseAppException): 커스텀 예외 객체
        
    Returns:
        JSONResponse: 표준화된 에러 응답
    """
    logger.error(
        f"커스텀 예외 발생 - Path: {request.url.path}, "
        f"Code: {exc.error_code.value}, Status: {exc.status_code}, "
        f"Message: {exc.message}, Detail: {exc.detail}"
    )
    return JSONResponse(
        status_code=200,
        content={
            "success": "false",
            "error_code": exc.error_code.value,
            "message": exc.message,
            "detail": exc.detail
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """일반 예외 처리기.
    
    예상하지 못한 시스템 에러를 처리하여
    표준화된 에러 응답을 반환합니다.
    
    Args:
        request (Request): 실패한 요청 객체
        exc (Exception): 시스템 예외 객체
        
    Returns:
        JSONResponse: 표준화된 에러 응답
    """
    logger.error(f"시스템 에러 - Path: {request.url.path}, 에러: {exc}")
    return JSONResponse(
        status_code=200,
        content={
            "success": "false",
            "error_code": ErrorCode.SYSTEM_ERROR.value,
            "message": ErrorMessages.get_message(ErrorCode.SYSTEM_ERROR),
            "detail": None
        }
    )

# container health 체크
@app.get("/health")
async def health_check():
    return {"status":"ok"}

@app.get("/")
async def root():
    return {"message": "Data ETL API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090) 