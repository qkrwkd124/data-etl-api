from typing import Optional, Dict, Any

import pandas as pd
from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customs import ExportImportStatByCountry
from app.models.shared_models import COUNTRY_INFO, CountryMapping
from app.db.base import get_main_db
from app.core.logger import get_logger

logger = get_logger()

class ExportImportStatByCountryRepository:
    def __init__(self, dbprsr: AsyncSession):
        self.dbprsr = dbprsr

    async def get_country_name_mapping(self) -> Dict[str,str]:
        try:
            stmt = select(
                CountryMapping.kcs_kor_ctry_nm,
                CountryMapping.std_infrm_ctry_cd
            )
            result = await self.dbprsr.execute(stmt)
            return dict(result.fetchall())
        except Exception as e:
            logger.error(f"Error getting country name mapping: {e}")
            raise e
        
    async def get_country_iso_mapping(self) -> Dict[str,str]:
        try:
            stmt = select(
                COUNTRY_INFO.std_infrm_ctry_cd,
                COUNTRY_INFO.trgtpsn_nm
            )
            result = await self.dbprsr.execute(stmt)
            return dict(result.fetchall())
        except Exception as e:
            logger.error(f"Error getting country iso mapping: {e}")
            raise e
        
    async def insert_dataframe(self, df: pd.DataFrame) -> int:
        """
        DataFrame을 데이터베이스에 삽입 (MariaDB용)
        
        Args:
            df: 삽입할 DataFrame
            
        Returns:
            삽입된 레코드 수
        """
        try:
            # DataFrame을 딕셔너리 리스트로 변환
            records = df.to_dict('records')
            
            # 대량 삽입
            insert_stmt = insert(ExportImportStatByCountry).values(records)
            await self.dbprsr.execute(insert_stmt)
            
            logger.info(f"데이터베이스에 {len(records)}개 레코드 삽입 완료")
            return len(records)
            
        except Exception as e:
            logger.error(f"데이터 삽입 중 오류: {str(e)}")
            raise

    async def delete_all(self) -> int:
        """
        모든 EIU 데이터 삭제
        
        Returns:
            삭제된 레코드 수
        """
        try:
            stmt = delete(ExportImportStatByCountry)
            result = await self.dbprsr.execute(stmt)
            deleted_count = result.rowcount
            logger.info(f"모든 EIU 데이터 삭제 완료: {deleted_count}개 레코드")
            return deleted_count
            
        except Exception as e:
            logger.error(f"전체 데이터 삭제 중 오류: {str(e)}")
            raise

    async def replace_all_data(self, df: pd.DataFrame) -> dict:
        """
        모든 데이터를 삭제하고 새 데이터 삽입 (전체 교체)
        
        Args:
            df: 새로 삽입할 DataFrame
            
        Returns:
            처리 결과 딕셔너리
        """
        try:
            # 1. 기존 데이터 모두 삭제
            deleted_count = await self.delete_all()
            
            # 2. 새 데이터 삽입
            inserted_count = await self.insert_dataframe(df)
            
            # 3. 커밋
            await self.dbprsr.commit()
            
            result = {
                "deleted_count": deleted_count,
                "inserted_count": inserted_count,
                "success": True
            }
            
            logger.info(f"데이터 전체 교체 완료 - 삭제: {deleted_count}개, 삽입: {inserted_count}개")
            return result
            
        except Exception as e:
            await self.dbprsr.rollback()
            logger.error(f"데이터 전체 교체 중 오류: {str(e)}")
            raise
    