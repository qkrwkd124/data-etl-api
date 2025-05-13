from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime

class DataSource(str, Enum):
    EIU = "eiu"
    CUSTOMS = "customs"
    ECONOMIC_INDICES = "economic_indices"

class DataRequest(BaseModel):
    file_path: str = Field(..., description="처리할 파일의 경로")
    file_name: str = Field(..., description="처리할 파일의 이름")
    data_source: DataSource = Field(..., description="데이터 소스 유형")
    process_date: Optional[datetime] = Field(default=None, description="데이터 처리 날짜")

class DataResponse(BaseModel):
    success: bool = Field(..., description="처리 성공 여부")
    message: str = Field(..., description="처리 결과 메시지")
    processed_rows: Optional[int] = Field(default=None, description="처리된 행 수")
    error: Optional[str] = Field(default=None, description="에러 메시지") 