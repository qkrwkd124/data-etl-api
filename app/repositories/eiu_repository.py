from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, insert, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
import pandas as pd
from datetime import datetime

from app.models.EIU import EconomicData
from app.core.logger import get_logger

logger = get_logger()

class EIUEconomicIndicatorRepository:
    """EIU 경제지표 Repository - ORM을 사용한 데이터베이스 작업"""
    
    def __init__(self, session: AsyncSession):
        self.session = session

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
            
            # 현재 시간 추가
            current_time = datetime.now()
            for record in records:
                record['created_at'] = current_time
                record['updated_at'] = current_time
            
            # 대량 삽입
            insert_stmt = insert(EconomicData).values(records)
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
            stmt = delete(EconomicData)
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
    
    async def delete_by_country(self, country_code: str) -> int:
        """
        특정 국가의 모든 데이터 삭제
        
        Args:
            country_code: 삭제할 국가 코드
            
        Returns:
            삭제된 레코드 수
        """
        try:
            stmt = delete(EconomicData).where(
                EconomicData.eiu_country_code == country_code
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            deleted_count = result.rowcount
            logger.info(f"국가 {country_code}의 {deleted_count}개 레코드를 삭제했습니다.")
            return deleted_count
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"국가별 데이터 삭제 중 오류: {str(e)}")
            raise
    
    async def insert_country_data(self, df: pd.DataFrame, country_code: str) -> int:
        """
        특정 국가의 데이터만 삽입
        
        Args:
            df: 삽입할 DataFrame
            country_code: 국가 코드
            
        Returns:
            삽입된 레코드 수
        """
        try:
            # 해당 국가 데이터만 필터링
            country_df = df[df['eiu_country_code'] == country_code]
            
            if country_df.empty:
                logger.info(f"국가 {country_code}의 데이터가 없습니다.")
                return 0
            
            # 삽입
            inserted_count = await self.insert_dataframe(country_df)
            await self.session.commit()
            
            logger.info(f"국가 {country_code}의 {inserted_count}개 레코드 삽입 완료")
            return inserted_count
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"국가별 데이터 삽입 중 오류: {str(e)}")
            raise
    
    async def replace_country_data(self, df: pd.DataFrame, country_code: str) -> dict:
        """
        특정 국가의 데이터를 삭제하고 새 데이터 삽입 (국가별 교체)
        
        Args:
            df: 새로 삽입할 DataFrame
            country_code: 국가 코드
            
        Returns:
            처리 결과 딕셔너리
        """
        try:
            # 1. 해당 국가 데이터 삭제
            deleted_count = await self.delete_by_country(country_code)
            
            # 2. 새 데이터 삽입
            inserted_count = await self.insert_country_data(df, country_code)
            
            result = {
                "country_code": country_code,
                "deleted_count": deleted_count,
                "inserted_count": inserted_count,
                "success": True
            }
            
            logger.info(f"국가 {country_code} 데이터 교체 완료 - 삭제: {deleted_count}개, 삽입: {inserted_count}개")
            return result
            
        except Exception as e:
            logger.error(f"국가별 데이터 교체 중 오류: {str(e)}")
            raise
    
    async def find_by_country_and_code(
        self, 
        country_code: str, 
        eiu_code: str
    ) -> Optional[EconomicData]:
        """
        국가 코드와 EIU 코드로 데이터 조회
        """
        try:
            stmt = select(EconomicData).where(
                EconomicData.eiu_country_code == country_code,
                EconomicData.eiu_code == eiu_code
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"데이터 조회 중 오류: {str(e)}")
            raise
    
    async def find_all_by_country(self, country_code: str) -> List[EconomicData]:
        """
        국가별 모든 데이터 조회
        """
        try:
            stmt = select(EconomicData).where(
                EconomicData.eiu_country_code == country_code
            )
            result = await self.session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"국가별 데이터 조회 중 오류: {str(e)}")
            raise
    
    async def find_all(self) -> List[EconomicData]:
        """
        모든 데이터 조회
        """
        try:
            stmt = select(EconomicData)
            result = await self.session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"전체 데이터 조회 중 오류: {str(e)}")
            raise
    
    async def count_total_records(self) -> int:
        """
        전체 레코드 수 조회
        """
        try:
            stmt = select(EconomicData)
            result = await self.session.execute(stmt)
            return len(result.scalars().all())
        except Exception as e:
            logger.error(f"전체 레코드 수 조회 중 오류: {str(e)}")
            raise
    
    async def count_by_country(self, country_code: str) -> int:
        """
        특정 국가의 레코드 수 조회
        """
        try:
            stmt = select(EconomicData).where(
                EconomicData.eiu_country_code == country_code
            )
            result = await self.session.execute(stmt)
            return len(result.scalars().all())
        except Exception as e:
            logger.error(f"국가별 레코드 수 조회 중 오류: {str(e)}")
            raise