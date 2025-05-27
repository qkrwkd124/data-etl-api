from fastapi import APIRouter, HTTPException
from app.schemas.api_schemas import EIUUploadRequest, EIUUploadResponse
from app.services.eiu_service import process_eiu_economic_indicator
from typing import Dict, Any
from fastapi import Depends
from app.db.base import get_main_db

router = APIRouter()

@router.post("/eiu/economic-indicator/upload", response_model=EIUUploadResponse)
async def process_data(
    request: EIUUploadRequest,
    dbprsr = Depends(get_main_db)
) -> Dict[str, Any]:
    """
    엑셀 파일을 처리하는 엔드포인트
    
    Args:
        request (DataRequest): 처리할 파일 정보
        
    Returns:
        Dict[str, Any]: 처리 결과
    """
    try:

        # 데이터 처리
        result = await process_eiu_economic_indicator(
            file_path=request.file_path,
            file_name=request.file_name,
            dbprsr=dbprsr,
            replace_all=True
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
            
        return EIUUploadResponse(
            success=True,
            message="데이터 처리 완료",
        )
        
    except Exception as e:
        return EIUUploadResponse(
            success=False,
            message="데이터 처리 실패",
        ) 