from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from fastapi import Depends

from app.db.base import get_main_db
from app.schemas.api_schemas import UploadRequest, UploadResponse
from app.services.eiu_service import process_eiu_economic_indicator
from app.services.major_trade_partner_service import process_data
from app.core.constants.error import ErrorMessages

router = APIRouter()

@router.post(
        "/eiu/economic-indicator",
        response_model=UploadResponse,
        summary="EIU 주요경제지표 엑셀 파일 처리",
        description="EIU 주요경제지표 엑셀 파일을 처리하여 데이터를 추출, 비즈니스 로직에 따라 변환하고 데이터베이스에 저장합니다.",
        tags=["EIU"]
    )
async def process_economic_indicator(
    request: UploadRequest,
    db = Depends(get_main_db),
) -> UploadResponse:
    """EIU 주요경제지표 엑셀 파일 처리.
    
    업로드된 EIU 경제지표 엑셀 파일을 처리하여 데이터를 추출,
    비즈니스 로직에 따라 변환하고 데이터베이스에 저장합니다.
    
    Args:  
        request (UploadRequest): file_seq를 포함한 파일 처리 요청  
        dbprsr: 메인 데이터베이스 세션 의존성 주입  
        dbpdtm: 이력 데이터베이스 세션 의존성 주입  
        
    Returns:  
        UploadResponse: 성공 여부와 메시지가 포함된 처리 결과  
        
    Raises:  
        DataProcessingException: 데이터 처리 실패 시  
        DatabaseException: 데이터베이스 작업 실패 시  
        FileException: 파일 검증 또는 읽기 실패 시  
    """

    # 데이터 처리
    result = await process_eiu_economic_indicator(
        seq=request.file_seq,
        db=db,
        replace_all=True
    )
        
    return UploadResponse(
        success="true",
        message=ErrorMessages.SUCCESS,
    )
        
    
@router.post(
        "/eiu/major-trade-partner",
        response_model=UploadResponse,
        summary="EIU 주요 수출/수입국 엑셀 파일 처리",
        description="EIU 주요 수출/수입국 엑셀 파일을 처리하여 데이터를 추출, 비즈니스 로직에 따라 변환하고 데이터베이스에 저장합니다.",
        tags=["EIU"]
    )
async def process_major_trade_partner(
    request: UploadRequest,
    db = Depends(get_main_db),
) -> UploadResponse:
    """EIU 주요 수출/수입국 엑셀 파일 처리.
    
    업로드된 EIU 주요 수출/수입국 엑셀 파일을 처리하여
    수출/수입국 데이터를 추출하고 처리된 결과를 저장합니다.
    
    Args:
        request (UploadRequest): file_seq를 포함한 파일 처리 요청
        dbprsr: 메인 데이터베이스 세션 의존성 주입
        dbpdtm: 이력 데이터베이스 세션 의존성 주입
        
    Returns:
        UploadResponse: 성공 여부와 메시지가 포함된 처리 결과
        
    Raises:
        DataProcessingException: 데이터 처리 실패 시
        DatabaseException: 데이터베이스 작업 실패 시
        FileException: 파일 검증 또는 읽기 실패 시
    """
    # 주요 수출입국 데이터 처리
    result_df = await process_data(
        seq=request.file_seq,
        db=db,
        replace_all=True
    )
    
    return UploadResponse(
        success="true",
        message=ErrorMessages.SUCCESS,
    )