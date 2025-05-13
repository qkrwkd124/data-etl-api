from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import data_processor

app = FastAPI(
    title="Data ETL API",
    description="EIU, 관세청, 경제지수 데이터 ETL API",
    version="1.0.0"
)

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

@app.get("/")
async def root():
    return {"message": "Data ETL API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090) 