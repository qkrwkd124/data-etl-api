from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, insert, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
import pandas as pd
from datetime import datetime

from app.models.EIU import EconomicData, MajorTradePartner
from app.models.shared_models import COUNTRY_INFO, CountryMapping
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
            
            # # 현재 시간 추가
            # current_time = datetime.now()
            # for record in records:
            #     record['created_at'] = current_time
            #     record['updated_at'] = current_time
            
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

    async def get_country_mapping(self) -> Dict[str, str]:
        """
        tb_mezz100에서 국가 코드와 국가영문명 매핑 조회
        
        Returns:
            {country_code: country_name_en} 딕셔너리
        """

        try:
            stmt = select(
                COUNTRY_INFO.std_infrm_ctry_cd,
                COUNTRY_INFO.trgtpsn_eng_nm
                          ).where(
                              EconomicData.eiu_country_code == COUNTRY_INFO.std_infrm_ctry_cd
                          )
            result = await self.session.execute(stmt)
            mapping = dict(result.fetchall())

            logger.info(f"국가 매핑 {len(mapping)}개 조회 완료")
            return mapping

        except Exception as e:
            logger.error(f"국가 매핑 조회 중 오류: {str(e)}")
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
    
class EIUPartnerRepository:
    """EIU 주요수출입국 Repository - ORM을 사용한 데이터베이스 작업"""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_partner_ISO_mapping(self) -> Dict[str, str]:
        """
        tb_rhr350에서 영문국가명과 표준약식국가코드 매핑 조회
        """
        try:
            stmt = select(
                CountryMapping.eng_ctry_nm,
                CountryMapping.std_infrm_ctry_cd
            )
            result = await self.session.execute(stmt)
            mapping = {}
            for eng_ctry_nm, std_infrm_ctry_cd in result.fetchall():
                mapping[eng_ctry_nm.lower()] = std_infrm_ctry_cd
            # mapping = dict(result.fetchall())
            return mapping
        except Exception as e:
            logger.error(f"주요수출입국 매핑 조회 중 오류: {str(e)}")
            raise

    async def get_partner_name(self) -> str:

        try :
            stmt = select(
                COUNTRY_INFO.std_infrm_ctry_cd,
                COUNTRY_INFO.trgtpsn_nm
            )
            result = await self.session.execute(stmt)
            return dict(result.fetchall())
        except Exception as e:
            logger.error(f"주요수출입국 국가명 조회 중 오류: {str(e)}")
            raise

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
            insert_stmt = insert(MajorTradePartner).values(records)
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
            stmt = delete(MajorTradePartner)
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


if __name__ == "__main__":
    import asyncio
    from app.db.base import get_main_db
    async def main():
        async for session in get_main_db():
            try : 
                repo = EIUEconomicIndicatorRepository(session)
                mapping = await repo.get_country_mapping()
                print(mapping)
            except Exception as e:
                print(f"에러 발생 {str(e)}")
                break
            finally:
                break

    asyncio.run(main())