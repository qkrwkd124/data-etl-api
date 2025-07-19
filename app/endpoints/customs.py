from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from fastapi import Depends

from app.db.base import get_main_db, get_dbpdtm_db
from app.schemas.api_schemas import UploadRequest, UploadResponse
from app.services.customs_country_service import process_data as process_data_country
from app.services.customs_item_service import process_data as process_data_item
from app.core.logger import get_logger

logger = get_logger()

router = APIRouter()


@router.post("/customs/trade/country", response_model=UploadResponse)
async def upload_customs_country(
    request: UploadRequest,
    dbprsr = Depends(get_main_db),
    dbpdtm = Depends(get_dbpdtm_db)
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
        result = await process_data_country(
            file_path=request.file_path,
            file_name=request.file_name,
            dbprsr=dbprsr,
            dbpdtm=dbpdtm,
            replace_all=True
        )
            
        return UploadResponse(
            success=True,
            message="데이터 처리 완료",
        )
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return UploadResponse(
            success=False,
            message="데이터 처리 실패",
        )
    

@router.post("/customs/trade/item-country/export", response_model=UploadResponse)
async def upload_customs_type(
    request: UploadRequest,
    dbprsr = Depends(get_main_db),
    dbpdtm = Depends(get_dbpdtm_db)
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
        result = await process_data_item(
            file_path=request.file_path,
            file_name=request.file_name,
            flag="수출",
            dbprsr=dbprsr,
            dbpdtm=dbpdtm,
            replace_all=True
        )
            
        return UploadResponse(
            success=True,
            message="데이터 처리 완료",
        )
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return UploadResponse(
            success=False,
            message="데이터 처리 실패",
        )
    

@router.post("/customs/trade/item-country/import", response_model=UploadResponse)
async def upload_customs_type(
    request: UploadRequest,
    dbprsr = Depends(get_main_db),
    dbpdtm = Depends(get_dbpdtm_db)
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
        result = await process_data_item(
            file_path=request.file_path,
            file_name=request.file_name,
            flag="수입",
            dbprsr=dbprsr,
            dbpdtm=dbpdtm,
            replace_all=True
        )
            
        return UploadResponse(
            success=True,
            message="데이터 처리 완료",
        )
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return UploadResponse(
            success=False,
            message="데이터 처리 실패",
        )