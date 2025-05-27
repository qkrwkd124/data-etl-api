from pydantic import BaseModel, Field

class EIUUploadRequest(BaseModel):
    file_path: str = Field(..., description="파일 경로")
    file_name: str = Field(..., description="파일 이름")

class EIUUploadResponse(BaseModel):
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="메시지")