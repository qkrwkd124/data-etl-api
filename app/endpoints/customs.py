from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from fastapi import Depends

from app.db.base import get_main_db, get_dbpdtm_db
from app.schemas.api_schemas import UploadRequest, UploadResponse
from app.services.customs_country_service import process_data as process_data_country
from app.services.customs_item_service import process_data as process_data_item
from app.core.logger import get_logger
from app.core.constants.error import ErrorMessages

logger = get_logger()

router = APIRouter()


@router.post(
        "/customs/trade/country",
        response_model=UploadResponse,
        summary="관세청 국가별 수출입 규모 엑셀 파일 처리",
        description="관세청의 국가별 수출입 규모 통계 데이터를 처리하여 데이터베이스에 저장합니다.",
        tags=["Customs"]
    )
async def upload_customs_country(
    request: UploadRequest,
    dbprsr = Depends(get_main_db),
    dbpdtm = Depends(get_dbpdtm_db)
) -> UploadResponse:
    """관세청 국가별 수출입 규모 엑셀 파일 처리.
    
    관세청의 국가별 수출입 규모 통계 데이터를 처리하여
    데이터베이스에 저장합니다.
    
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
    result = await process_data_country(
        seq=request.file_seq,
        dbprsr=dbprsr,
        dbpdtm=dbpdtm,
        replace_all=True
    )
        
    return UploadResponse(
        success="true",
        message=ErrorMessages.SUCCESS,
    )

    

@router.post(
        "/customs/trade/item-country/export",
        response_model=UploadResponse,
        summary="관세청 품목별 수출 데이터 엑셀 파일 처리",
        description="관세청의 품목별 국가별 수출 통계 데이터를 처리하여 데이터베이스에 저장합니다.",
        tags=["Customs"]
    )
async def upload_customs_export(
    request: UploadRequest,
    dbprsr = Depends(get_main_db),
    dbpdtm = Depends(get_dbpdtm_db)
) -> UploadResponse:
    """관세청 품목별 수출 데이터 엑셀 파일 처리.
    
    관세청의 품목별 국가별 수출 통계 데이터를 처리하여
    데이터베이스에 저장합니다.
    
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
    result = await process_data_item(
        seq=request.file_seq,
        flag="수출",
        dbprsr=dbprsr,
        dbpdtm=dbpdtm,
        replace_all=False
    )
        
    return UploadResponse(
        success="true",
        message=ErrorMessages.SUCCESS,
    )
    

@router.post(
        "/customs/trade/item-country/import",
        response_model=UploadResponse,
        summary="관세청 품목별 수입 데이터 엑셀 파일 처리",
        description="관세청의 품목별 국가별 수입 통계 데이터를 처리하여 데이터베이스에 저장합니다.",
        tags=["Customs"]
    )
async def upload_customs_import(
    request: UploadRequest,
    dbprsr = Depends(get_main_db),
    dbpdtm = Depends(get_dbpdtm_db)
) -> UploadResponse:
    """관세청 품목별 수입 데이터 엑셀 파일 처리.
    
    관세청의 품목별 국가별 수입 통계 데이터를 처리하여
    데이터베이스에 저장합니다.
    
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
    result = await process_data_item(
        seq=request.file_seq,
        flag="수입",
        dbprsr=dbprsr,
        dbpdtm=dbpdtm,
        replace_all=False
    )
        
    return UploadResponse(
        success="true",
        message=ErrorMessages.SUCCESS,
    )