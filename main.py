from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import data_processor
from app.core.settings import get_settings
from app.core.logger import setup_logger,get_logger

settings = get_settings()

setup_logger()
logger = get_logger()

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    debug=settings.DEBUG
)

logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(data_processor.router, prefix="/api/v1", tags=["data"])

# container health 체크
@app.get("/health")
async def health_check():
    logger.info("Health check endpoint accessed")
    return {"status":"ok"}

@app.get("/")
async def root():
    return {"message": "Data ETL API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090) 