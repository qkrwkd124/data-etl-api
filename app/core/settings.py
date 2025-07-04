from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # 기본 설정
    APP_NAME: str = "Data ETL API"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "EIU, 관세청, 경제지수 데이터 ETL API"
    
    # API 설정
    # API_V1_STR: str = "/api/v1"
    
    # 데이터베이스 설정
    CPIDB_DBPRSR: Optional[str] = None
    
    # 로깅 설정
    LOG_DIR: str = "app/logs"
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <yellow>PID:{process}</yellow> | <cyan>\"{name}\"</cyan>, <cyan>{function}</cyan>, <cyan>{line}</cyan> : <level>{message}</level>"
    DATE_FORMAT: str = '%Y/%m/%d %H:%M:%S'  
    
    # 파일 처리 설정
    CSV_OUTPUT_DIR: str = "/storage/research"
    CSV_OUPUT_ENCOFING: str = "utf-8"
    CSV_OUPUT_NA_REP: str = "NULL"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()