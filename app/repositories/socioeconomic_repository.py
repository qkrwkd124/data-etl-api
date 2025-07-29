from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete
from typing import Dict, Literal
import pandas as pd

from app.core.exceptions import DataNotFoundException, ErrorCode, DatabaseException
from app.core.constants.error import ErrorMessages
from app.core.logger import get_logger
from app.models.shared_models import COUNTRY_INFO, CountryMapping
from app.models.socioeconomic import (
    EconomicFreedomIndex,
    CorruptionPerceptionIndex,
    HumanDevelopmentIndex,
    WorldCompetitivenessIndex
)

logger = get_logger()

class SocioeconomicIndexRepository:
    def __init__(
        self,
        session: AsyncSession,
        flag: Literal["경제자유화지수", "부패인식지수", "인간개발지수", "세계경쟁력지수"]
    ):
        self.session = session
        self.model = {
            "경제자유화지수": EconomicFreedomIndex,
            "부패인식지수": CorruptionPerceptionIndex,
            "인간개발지수": HumanDevelopmentIndex,
            "세계경쟁력지수": WorldCompetitivenessIndex
        }[flag]

    async def get_eng_country_name_mapping(self) -> Dict[str,str]:
        try:
            stmt = select(
                CountryMapping.eng_ctry_nm,
                CountryMapping.std_infrm_ctry_cd
            )
            result = await self.session.execute(stmt)
            return dict(result.fetchall())
        except Exception as e:
            logger.error(f"Error getting eng country name mapping: {e}")
            raise e
        
    async def get_iso2_eng_mapping(self) -> Dict[str,str]:
        try:
            
            stmt = select(
                COUNTRY_INFO.std_infrm_ctry_cd,
                COUNTRY_INFO.trgtpsn_eng_nm,
            )
            result = await self.session.execute(stmt)
            return dict(result.fetchall())
        
        except Exception as e:
            logger.error(f"Error getting iso eng mapping: {e}")
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
            insert_stmt = insert(self.model).values(records)
            await self.session.execute(insert_stmt)
            
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
            stmt = delete(self.model)
            result = await self.session.execute(stmt)
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
            await self.session.commit()
            
            result = {
                "deleted_count": deleted_count,
                "inserted_count": inserted_count,
                "success": True
            }
            
            logger.info(f"데이터 전체 교체 완료 - 삭제: {deleted_count}개, 삽입: {inserted_count}개")
            return result
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"데이터 전체 교체 중 오류: {str(e)}")
            raise