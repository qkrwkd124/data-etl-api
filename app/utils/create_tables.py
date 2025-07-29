"""
데이터베이스 테이블 생성 스크립트
"""
from sqlalchemy.ext.asyncio import create_async_engine
from app.db.base import Base
from app.models.history import DataUploadAutoHistory  # 모델 import
from app.models.shared_models import COUNTRY_INFO, CountryMapping
from app.models.customs import ExportImportStatByCountry, ExportImportItemByCountry
from app.models.EIU import EconomicData, MajorTradePartner
from app.models.socioeconomic import EconomicFreedomIndex, CorruptionPerceptionIndex, HumanDevelopmentIndex, WorldCompetitivenessIndex
from app.core.setting import get_settings

settings = get_settings()

async def create_tables():
    """테이블 생성"""
    engine = create_async_engine(
        url=settings.DATABASE,
        echo=True  # SQL 쿼리 로그 출력
    )
    
    async with engine.begin() as conn:
        # 모든 테이블 생성
        await conn.run_sync(Base.metadata.create_all)
        print("✅ 테이블이 성공적으로 생성되었습니다!")
    
    await engine.dispose()

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_tables())