from sqlalchemy import text, insert, update, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.history import DataUploadAutoHistory
from app.core.logger import logger
from datetime import datetime
from sqlalchemy.exc import NoResultFound
from app.core.exceptions import DataNotFoundException, ErrorCode, DatabaseException
from app.core.constants.error import ErrorMessages

class DataUploadAutoHistoryRepository:
    """데이터 업로드 자동화 이력 Repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_next_seq(self, seq_name: str = "tb_bpc220_file_seq") -> int:
        """
        다음 시퀀스 값 조회 (MariaDB용)
        
        Args:
            seq_name: 시퀀스명
            
        Returns:
            다음 시퀀스 값
        """
        try:
            # 증가된 값 조회
            select_stmt = text(f"SELECT NEXT VALUE FOR {seq_name}")
            result = await self.session.execute(select_stmt)
            seq_value = result.scalar_one()
            
            logger.info(f"시퀀스 {seq_name} 다음 값: {seq_value}")
            return seq_value
        except Exception as e:
            logger.error(f"시퀀스 조회 중 오류: {str(e)}")
            raise

    async def get_history_info(self, seq: int) -> DataUploadAutoHistory:
        """
        파일 정보 조회
        """
        try:
            select_stmt = select(DataUploadAutoHistory).where(DataUploadAutoHistory.file_seq == seq)
            result = await self.session.execute(select_stmt)
            file_info = result.scalar_one()
            return file_info
        except NoResultFound:
            logger.error(f"파일 정보 조회 중 오류: 시퀀스 값이 없습니다.")
            raise DataNotFoundException(
                message=ErrorMessages.get_message(ErrorCode.DATA_NOT_FOUND),
                error_code=ErrorCode.DATA_NOT_FOUND,
                detail={
                    "seq": seq
                }
            )
        except Exception as e:
            logger.error(f"파일 정보 조회 중 오류: {str(e)}")
            raise DatabaseException(
                message=ErrorMessages.get_message(ErrorCode.DATABASE_ERROR),
                error_code=ErrorCode.DATABASE_ERROR,
                detail={
                    "seq": seq
                }
            )

    async def update_history(self, seq: int, **update_data) -> None:
        """
        이력 데이터 업데이트
        
        Args:
            seq: 업데이트할 이력 순번
            update_data: 업데이트할 데이터
        """
        try:
            if not update_data:
                logger.warning(f"업데이트할 데이터가 없습니다: seq={seq}")
                return None
            
            # 업데이트 실행
            update_stmt = update(DataUploadAutoHistory).where(
                DataUploadAutoHistory.file_seq == seq
            ).values(update_data)
            
            await self.session.execute(update_stmt)
            await self.session.commit()
            
            logger.info(f"이력 데이터 업데이트 완료: 파일순번={seq}")
            
        except Exception as e:
            logger.error(f"이력 데이터 업데이트 중 오류: {str(e)}")
            await self.session.rollback()
            raise DatabaseException(
                message=ErrorMessages.get_message(ErrorCode.DATABASE_ERROR),
                error_code=ErrorCode.DATABASE_ERROR,
                detail={
                    "seq": seq
                }
            )

    async def start_processing(self, seq: int) -> None:
        await self.update_history(
            seq,
            strt_dtm=datetime.now(),
            mod_dtm=datetime.now()
        )

    async def success_processing(self, seq: int, result_table_name: str, process_count: int, message: str = None) -> None:
        await self.update_history(
            seq,
            end_dtm=datetime.now(),
            fin_yn="Y",
            rmk_ctnt=message,
            rslt_tab_nm=result_table_name,
            proc_cnt=process_count,
            mod_dtm=datetime.now()
        )

    async def fail_processing(self, seq: int, message: str = None) -> None:
        await self.update_history(
            seq,
            end_dtm=datetime.now(),
            fin_yn="N",
            rmk_ctnt=message,
            mod_dtm=datetime.now()
        )

    # async def insert_history(self, seq: int, history_data) -> None:
    #     """
    #     이력 데이터 삽입
        
    #     Args:
    #         history_data: 삽입할 이력 데이터
            
    #     Returns:
    #         삽입된 이력 객체
    #     """
    #     try:
    #         # 이력 데이터 생성
    #         history_dict = history_data.model_dump()
    #         history_dict['data_wrk_no'] = seq
            
    #         # 삽입 실행
    #         insert_stmt = insert(DataUploadAutoHistory).values(history_dict)
    #         await self.session.execute(insert_stmt)

    #         # commit
    #         await self.session.commit()
            
    #         logger.info(f"이력 데이터 삽입 완료: 데이터작업번호={seq}, 데이터작업명={history_data.data_wrk_nm}")
            
    #     except Exception as e:
    #         logger.error(f"이력 데이터 삽입 중 오류: {str(e)}")
    #         await self.session.rollback()
    #         raise
            