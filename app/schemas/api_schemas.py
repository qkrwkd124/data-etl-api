from pydantic import BaseModel, Field, validator
from app.core.constants.error import ErrorMessages, ErrorCode
from app.core.exceptions import ValidationException

# class UploadRequest(BaseModel):
#     file_path: str = Field(..., description="파일 경로")
#     file_name: str = Field(..., description="파일 이름")

class UploadRequest(BaseModel):
    file_seq: int = Field(..., description="파일순번")

class UploadResponse(BaseModel):
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="메시지")