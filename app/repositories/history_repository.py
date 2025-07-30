from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy import text, update, select, desc, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from app.models.history import DataUploadAutoHistory
from app.core.logger import logger
from app.core.exceptions import DataNotFoundException, ErrorCode, DatabaseException
from app.core.constants.error import ErrorMessages

class DataUploadAutoHistoryRepository:
    """데이터 업로드 자동화 이력 Repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_next_seq(self, seq_name: str = "file_seq") -> int:
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

     # ====================================
    # 새로 추가: 관리자 페이지용 조회 함수들
    # ====================================

    async def get_all(self, limit: int = 100, offset: int = 0, filters: Dict[str, Any] = None) -> List[DataUploadAutoHistory]:
        """모든 이력 조회 (페이징, 필터링 지원)"""
        try:
            stmt = select(DataUploadAutoHistory)
            
            # 필터 조건 추가
            if filters:
                for field, value in filters.items():
                    if hasattr(DataUploadAutoHistory, field) and value is not None:
                        stmt = stmt.where(getattr(DataUploadAutoHistory, field) == value)
            
            stmt = (
                stmt.order_by(desc(DataUploadAutoHistory.reg_dtm))
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"이력 목록 조회 중 오류: {str(e)}")
            raise DatabaseException(
                message=ErrorMessages.get_message(ErrorCode.DATABASE_ERROR),
                error_code=ErrorCode.DATABASE_ERROR,
                detail={"limit": limit, "offset": offset, "filters": filters}
            )

    async def get_count(self, filters: Dict[str, Any] = None) -> int:
        """전체 이력 개수 (필터링 지원)"""
        try:
            stmt = select(func.count(DataUploadAutoHistory.file_seq))
            
            # 필터 조건 추가
            if filters:
                for field, value in filters.items():
                    if hasattr(DataUploadAutoHistory, field) and value is not None:
                        stmt = stmt.where(getattr(DataUploadAutoHistory, field) == value)
            
            result = await self.session.execute(stmt)
            return result.scalar() or 0
        except Exception as e:
            logger.error(f"이력 개수 조회 중 오류: {str(e)}")
            raise DatabaseException(
                message=ErrorMessages.get_message(ErrorCode.DATABASE_ERROR),
                error_code=ErrorCode.DATABASE_ERROR,
                detail={"filters": filters}
            )

    async def get_by_status(self, fin_yn: str) -> List[DataUploadAutoHistory]:
        """상태별 이력 조회"""
        try:
            stmt = (
                select(DataUploadAutoHistory)
                .where(DataUploadAutoHistory.fin_yn == fin_yn)
                .order_by(desc(DataUploadAutoHistory.reg_dtm))
            )
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"상태별 이력 조회 중 오류: {str(e)}")
            raise DatabaseException(
                message=ErrorMessages.get_message(ErrorCode.DATABASE_ERROR),
                error_code=ErrorCode.DATABASE_ERROR,
                detail={"fin_yn": fin_yn}
            )

    async def create(self, history_data: Dict[str, Any]) -> DataUploadAutoHistory:
        """새 이력 생성"""
        try:
            # file_seq가 없으면 시퀀스에서 생성
            if 'file_seq' not in history_data or history_data['file_seq'] is None:
                history_data['file_seq'] = await self.get_next_seq()
            
            # 새 이력 객체 생성
            history = DataUploadAutoHistory(**history_data)
            self.session.add(history)
            await self.session.flush()  # ID 생성을 위해 flush
            await self.session.commit()
            
            logger.info(f"새 이력 생성 완료: file_seq={history.file_seq}")
            return history
            
        except Exception as e:
            logger.error(f"이력 생성 중 오류: {str(e)}")
            await self.session.rollback()
            raise DatabaseException(
                message=ErrorMessages.get_message(ErrorCode.DATABASE_ERROR),
                error_code=ErrorCode.DATABASE_ERROR,
                detail=history_data
            )

    async def update(self, file_seq: int, data_wrk_nm: str, update_data: Dict[str, Any]) -> Optional[DataUploadAutoHistory]:
        """특정 이력 업데이트 (복합키 사용)"""
        try:
            # 업데이트 실행
            stmt = (
                update(DataUploadAutoHistory)
                .where(
                    DataUploadAutoHistory.file_seq == file_seq,
                    DataUploadAutoHistory.data_wrk_nm == data_wrk_nm
                )
                .values(**update_data)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            if result.rowcount > 0:
                # 업데이트된 객체 조회해서 반환
                return await self.get_by_composite_key(file_seq, data_wrk_nm)
            return None
            
        except Exception as e:
            logger.error(f"이력 업데이트 중 오류: {str(e)}")
            await self.session.rollback()
            raise DatabaseException(
                message=ErrorMessages.get_message(ErrorCode.DATABASE_ERROR),
                error_code=ErrorCode.DATABASE_ERROR,
                detail={"file_seq": file_seq, "data_wrk_nm": data_wrk_nm}
            )

    async def get_by_composite_key(self, file_seq: int, data_wrk_nm: str) -> Optional[DataUploadAutoHistory]:
        """복합키로 특정 이력 조회"""
        try:
            stmt = select(DataUploadAutoHistory).where(
                DataUploadAutoHistory.file_seq == file_seq,
                DataUploadAutoHistory.data_wrk_nm == data_wrk_nm
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"복합키 이력 조회 중 오류: {str(e)}")
            raise DatabaseException(
                message=ErrorMessages.get_message(ErrorCode.DATABASE_ERROR),
                error_code=ErrorCode.DATABASE_ERROR,
                detail={"file_seq": file_seq, "data_wrk_nm": data_wrk_nm}
            )

    async def delete(self, file_seq: int, data_wrk_nm: str) -> bool:
        """이력 삭제"""
        try:
            stmt = delete(DataUploadAutoHistory).where(
                DataUploadAutoHistory.file_seq == file_seq,
                DataUploadAutoHistory.data_wrk_nm == data_wrk_nm
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            logger.info(f"이력 삭제 완료: file_seq={file_seq}, data_wrk_nm={data_wrk_nm}")
            return result.rowcount > 0
            
        except Exception as e:
            logger.error(f"이력 삭제 중 오류: {str(e)}")
            await self.session.rollback()
            raise DatabaseException(
                message=ErrorMessages.get_message(ErrorCode.DATABASE_ERROR),
                error_code=ErrorCode.DATABASE_ERROR,
                detail={"file_seq": file_seq, "data_wrk_nm": data_wrk_nm}
            )