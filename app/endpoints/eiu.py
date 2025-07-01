from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from fastapi import Depends

from app.db.base import get_main_db
from app.schemas.api_schemas import EIUUploadRequest, EIUUploadResponse
from app.services.eiu_service import process_eiu_economic_indicator
from app.services.major_trade_partner_service import process_eiu_major_trade_partner

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
            
        return EIUUploadResponse(
            success=True,
            message="데이터 처리 완료",
        )
        
    except Exception as e:
        return EIUUploadResponse(
            success=False,
            message="데이터 처리 실패",
        )
    
@router.post("/eiu/major-trade-partner/upload", response_model=EIUUploadResponse)
async def process_major_trade_partner(
    request: EIUUploadRequest,
    dbprsr = Depends(get_main_db)
) -> Dict[str, Any]:
    """
    EIU 주요 수출입국 엑셀 파일을 처리하는 엔드포인트
    
    Args:
        request (EIUUploadRequest): 처리할 파일 정보
        
    Returns:
        Dict[str, Any]: 처리 결과
    """
    try:
        # 주요 수출입국 데이터 처리
        result_df = await process_eiu_major_trade_partner(
            file_path=request.file_path,
            file_name=request.file_name,
            dbprsr=dbprsr,
            replace_all=True
        )
        
        return EIUUploadResponse(
            success=True,
            message=f"주요 수출입국 데이터 처리 완료 ({result_df.shape[0]}행 처리됨)",
        )
        
    except Exception as e:
        return EIUUploadResponse(
            success=False,
            message=f"주요 수출입국 데이터 처리 실패: {str(e)}",
        )