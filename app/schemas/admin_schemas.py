"""
관리자 페이지용 스키마
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# 간단한 작업번호 매핑 (딕셔너리로 충분)
WORK_TYPE_MAPPING = {
    "주요 경제지표(EIU)": {"data_wrk_no": 1, "endpoint": "/eiu/economic-indicator"},
    "주요 수출/수입국(EIU)": {"data_wrk_no": 2, "endpoint": "/eiu/major-trade-partner"},
    "국가별 수출입규모(관세청)": {"data_wrk_no": 3, "endpoint": "/customs/trade/country"},
    "주요 수출/수입품(관세청) - 수출실적": {"data_wrk_no": 4, "endpoint": "/customs/trade/item-country/export"},
    "주요 수출/수입품(관세청) - 수입실적": {"data_wrk_no": 5, "endpoint": "/customs/trade/item-country/import"},
    "부패인식지수": {"data_wrk_no": 6, "endpoint": "/socioeconomic-index/corruption-perception"},
    "경제자유화지수": {"data_wrk_no": 7, "endpoint": "/socioeconomic-index/economic-freedom"},
    "인간개발지수": {"data_wrk_no": 8, "endpoint": "/socioeconomic-index/human-development"},
    "세계경쟁력지수": {"data_wrk_no": 9, "endpoint": "/socioeconomic-index/world-competitiveness"},
}
class HistoryResponse(BaseModel):
    """히스토리 응답 스키마"""
    file_seq: Decimal = Field(..., description="파일순번")
    data_wrk_no: Optional[Decimal] = Field(None, description="데이터작업번호")
    data_wrk_nm: str = Field(..., description="데이터작업명")
    strt_dtm: Optional[datetime] = Field(None, description="시작일시")
    end_dtm: Optional[datetime] = Field(None, description="종료일시")
    fin_yn: Optional[str] = Field(None, description="완료여부")
    rmk_ctnt: Optional[str] = Field(None, description="비고내용")
    file_nm: Optional[str] = Field(None, description="파일명")
    file_path_nm: Optional[str] = Field(None, description="파일경로명")
    file_exts_nm: Optional[str] = Field(None, description="파일연장명")
    file_size: Optional[str] = Field(None, description="파일크기")
    proc_cnt: Optional[Decimal] = Field(None, description="처리건수")
    reg_usr_id: str = Field(..., description="등록사용자ID")
    reg_dtm: datetime = Field(..., description="등록일시")
    
    class Config:
        from_attributes = True

class HistoryListResponse(BaseModel):
    """히스토리 목록 응답 스키마"""
    items: List[HistoryResponse]
    total: int
    page: int
    size: int
    total_pages: int

class FileUploadResponse(BaseModel):
    """파일 업로드 응답 스키마"""
    filename: str = Field(..., description="파일명")
    size: int = Field(..., description="파일크기")
    content_type: str = Field(..., description="파일타입")
    upload_path: str = Field(..., description="업로드경로")
    file_seq: Optional[int] = Field(None, description="생성된 파일순번")

class JobExecuteRequest(BaseModel):
    """작업 실행 요청 스키마"""
    job_type: str = Field(..., description="작업타입")
    file_path: str = Field(..., description="파일경로")
    user_id: str = Field(default="admin", description="사용자ID")

class JobExecuteResponse(BaseModel):
    """작업 실행 응답 스키마"""
    success: bool = Field(..., description="성공여부")
    message: str = Field(..., description="결과메시지") 
    file_seq: Optional[int] = Field(None, description="생성된 파일순번")
    processing_time: Optional[float] = Field(None, description="처리시간(초)")