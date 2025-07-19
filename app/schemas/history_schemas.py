from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class JobType(str, Enum):
    """작업 유형 열거형"""
    CUSTOMS_COUNTRY = "국가별 수출입규모(관세청)"
    CUSTOMS_ITEM = "주요 수출/수입품(관세청) - {{flag}}실적"
    EIU_ECONOMIC = "주요 경제지표(EIU)"
    EIU_PARTNER = "주요 수출/수입국(EIU)"


class DataUploadAutoHistoryCreate(BaseModel):
    """이력 생성 스키마"""
    data_wrk_no: int = Field(..., description="데이터작업번호")
    data_wrk_nm: str = Field(..., description="데이터작업명")
    strt_dtm: datetime = Field(..., description="시작일시")
    refl_file_nm: Optional[str] = Field(None, description="반영파일명")  # Optional: 값이 없어도 됨
    reg_usr_id: str = Field(..., description="등록사용자ID")
    reg_dtm: datetime = Field(..., description="등록일시")
    mod_usr_id: str = Field(..., description="수정사용자ID")
    mod_dtm: datetime = Field(..., description="수정일시")


class DataUploadAutoHistoryUpdate(BaseModel):
    """이력 수정 스키마"""
    end_dtm: datetime = Field(..., description="종료일시")
    fin_yn: Optional[str] = Field(None, description="완료여부")
    rmk_ctnt: Optional[str] = Field(None, description="비고내용")
    scr_file_nm: Optional[str] = Field(None, description="화면파일명")
    rslt_tab_nm: Optional[str] = Field(None, description="결과테이블명")
    proc_cnt: Optional[int] = Field(None, description="처리건수")
    mod_usr_id: str = Field(..., description="수정사용자ID")
    mod_dtm: datetime = Field(..., description="수정일시")