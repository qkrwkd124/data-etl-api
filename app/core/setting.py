from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # 기본 설정
    APP_NAME: str = "Data ETL API"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "EIU, 관세청, 사회경제지수 데이터 ETL API"
    
    # API 설정
    # API_V1_STR: str = "/api/v1"
    
    # 데이터베이스 설정
    DATABASE: Optional[str] = None
    
    # 로깅 설정
    LOG_DIR: str = "app/logs"
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <yellow>PID:{process}</yellow> | <cyan>\"{name}\"</cyan>, <cyan>{function}</cyan>, <cyan>{line}</cyan> : <level>{message}</level>"
    DATE_FORMAT: str = '%Y/%m/%d %H:%M:%S'  
    
    # 파일 처리 설정
    CSV_OUTPUT_DIR: str = "/storage/research/final"
    CSV_OUPUT_ENCOFING: str = "utf-8"
    CSV_OUPUT_NA_REP: str = "NULL"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """설정 인스턴스 반환 (싱글톤).
    
    LRU 캐시를 사용하여 설정 인스턴스를 한 번만 생성하고
    재사용합니다.
    
    Returns:
        Settings: 애플리케이션 설정 인스턴스
    """
    return Settings()