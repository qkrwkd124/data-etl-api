"""
History 비즈니스 로직 서비스
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import math

from app.repositories.history_repository import DataUploadAutoHistoryRepository
from app.schemas.admin_schemas import HistoryResponse, HistoryListResponse
from app.models.history import DataUploadAutoHistory

class HistoryService:
    """History 비즈니스 로직 처리"""
    
    def __init__(self, db: AsyncSession):
        self.repository = DataUploadAutoHistoryRepository(db)
    
    async def get_history_list(self, page: int = 1, size: int = 20, status: str = None, job_type: str = None) -> HistoryListResponse:
        """히스토리 목록 조회 (페이징, 필터링 지원)"""
        offset = (page - 1) * size
        
        # 필터 조건 설정
        filters = {}
        if status:
            filters['fin_yn'] = status
        if job_type:
            filters['data_wrk_nm'] = job_type
        
        # 데이터 조회
        items = await self.repository.get_all(limit=size, offset=offset, filters=filters)
        total = await self.repository.get_count(filters=filters)
        
        # Pydantic v2에서는 from_orm 대신 model_validate를 사용해야 하며, ORM 객체를 dict로 변환하지 않고 바로 검증할 수 있음
        history_items = [HistoryResponse.model_validate(item) for item in items]
        
        total_pages = math.ceil(total / size) if total > 0 else 1
        
        return HistoryListResponse(
            items=history_items,
            total=total,
            page=page,
            size=size,
            total_pages=total_pages
        )
    
    async def create_with_job_type(self, file_info: Dict[str, Any], job_type: str, data_wrk_no: int) -> int:
        """파일 업로드시 작업 유형과 함께 히스토리 생성"""
        now = datetime.now()
        
        # file_seq 생성
        file_seq = await self.repository.get_next_seq()
        
        # 파일 경로에서 디렉토리 경로만 추출 (파일명 제외)
        import os
        file_directory = os.path.dirname(file_info["upload_path"]) + "/"
        
        # 작업 유형 정보와 함께 저장
        history_data = {
            "file_seq": file_seq,
            "data_wrk_no": data_wrk_no,  # 작업번호 설정
            "data_wrk_nm": job_type,     # 작업명 설정
            "strt_dtm": None,            # 아직 시작 안함
            "fin_yn": "N",               # N: 대기 (Y/N만 사용)
            "file_nm": file_info["filename"],
            "file_path_nm": file_directory,  # 파일 디렉토리 경로만
            "file_exts_nm": file_info["filename"].split('.')[-1].upper() if '.' in file_info["filename"] else "",
            "file_size": str(file_info["size"]),
            "file_sort_ord": 1,
            "reg_usr_id": "admin",
            "reg_dtm": now,
            "mod_usr_id": "admin",
            "mod_dtm": now
        }
        
        await self.repository.create(history_data)
        return file_seq
    
    async def get_history_by_seq(self, file_seq: int) -> Optional[HistoryResponse]:
        """file_seq로 히스토리 조회"""
        history = await self.repository.get_history_info(file_seq)
        if history:
            return HistoryResponse.model_validate(history)
        return None

    async def get_history_by_status(self, status: str) -> List[HistoryResponse]:
        """상태별 히스토리 조회"""
        items = await self.repository.get_by_status(status)
        return [HistoryResponse.model_validate(item) for item in items]
    
    async def delete_history(self, file_seq: int, data_wrk_nm: str) -> bool:
        """히스토리 삭제"""
        return await self.repository.delete(file_seq, data_wrk_nm)