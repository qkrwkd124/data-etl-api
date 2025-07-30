from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.endpoints import eiu, customs, admin
from app.core.setting import get_settings
from app.core.logger import setup_logger, get_logger
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
app.include_router(eiu.router, tags=["eiu"])
app.include_router(customs.router, tags=["customs"])
app.include_router(admin.router)

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