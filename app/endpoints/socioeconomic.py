from fastapi import APIRouter
from fastapi import Depends

from app.db.base import get_main_db, get_dbpdtm_db
from app.schemas.api_schemas import UploadRequest, UploadResponse
from app.services.socioeconomic_index_service import process_data
from app.core.logger import get_logger
from app.core.constants.error import ErrorMessages

logger = get_logger()

router = APIRouter()


@router.post(
        "/socioeconomic-index/economic-freedom",
        response_model=UploadResponse,
        summary="경제자유화지수 CSV 파일 처리",
        description="Heritage Foundation에서 발표하는 경제자유화지수 데이터를 처리하여 데이터베이스에 저장합니다.",
        tags=["Socioeconomic"]
    )
async def upload_socioeconomic_index_economic_freedom(
    request: UploadRequest,
    dbprsr = Depends(get_main_db),
    dbpdtm = Depends(get_dbpdtm_db)
) -> UploadResponse:
    """경제자유화지수 CSV 파일 처리.
    
    Heritage Foundation에서 발표하는 경제자유화지수 데이터를
    처리하여 데이터베이스에 저장합니다.
    
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
    result = await process_data(
        seq=request.file_seq,
        dbprsr=dbprsr,
        dbpdtm=dbpdtm,
        replace_all=True,
        flag="경제자유화지수"
    )
        
    return UploadResponse(
        success="true",
        message=ErrorMessages.SUCCESS,
    )

    

@router.post(
        "/socioeconomic-index/corruption-perception",
        response_model=UploadResponse,
        summary="부패인식지수 엑셀 파일 처리",
        description="Transparency International에서 발표하는 부패인식지수 데이터를 처리하여 데이터베이스에 저장합니다.",
        tags=["Socioeconomic"]
    )
async def upload_socioeconomic_index_corruption_perception(
    request: UploadRequest,
    dbprsr = Depends(get_main_db),
    dbpdtm = Depends(get_dbpdtm_db)
) -> UploadResponse:
    """부패인식지수 엑셀 파일 처리.
    
    Transparency International에서 발표하는 부패인식지수 데이터를
    처리하여 데이터베이스에 저장합니다.
    
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
    result = await process_data(
        seq=request.file_seq,
        flag="부패인식지수",
        dbprsr=dbprsr,
        dbpdtm=dbpdtm,
        replace_all=True
    )
        
    return UploadResponse(
        success="true",
        message=ErrorMessages.SUCCESS,
    )
    

@router.post(
        "/socioeconomic-index/human-development",
        response_model=UploadResponse,
        summary="인간개발지수 엑셀 파일 처리",
        description="UNDP에서 발표하는 인간개발지수 데이터를 처리하여 데이터베이스에 저장합니다.",
        tags=["Socioeconomic"]
    )
async def upload_socioeconomic_index_human_development(
    request: UploadRequest,
    dbprsr = Depends(get_main_db),
    dbpdtm = Depends(get_dbpdtm_db)
) -> UploadResponse:
    """인간개발지수 엑셀 파일 처리.
    
    UNDP에서 발표하는 인간개발지수 데이터를
    처리하여 데이터베이스에 저장합니다.
    
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
    result = await process_data(
        seq=request.file_seq,
        flag="인간개발지수",
        dbprsr=dbprsr,
        dbpdtm=dbpdtm,
        replace_all=True
    )
        
    return UploadResponse(
        success="true",
        message=ErrorMessages.SUCCESS,
    )


@router.post(
        "/socioeconomic-index/world-competitiveness",
        response_model=UploadResponse,
        summary="세계경쟁력지수 엑셀 파일 처리",
        description="IMD에서 발표하는 세계경쟁력지수 데이터를 처리하여 데이터베이스에 저장합니다.",
        tags=["Socioeconomic"]
    )
async def upload_socioeconomic_index_world_competitiveness(
    request: UploadRequest,
    dbprsr = Depends(get_main_db),
    dbpdtm = Depends(get_dbpdtm_db)
) -> UploadResponse:
    """세계경쟁력지수 엑셀 파일 처리.
    
    IMD에서 발표하는 세계경쟁력지수 데이터를
    처리하여 데이터베이스에 저장합니다.
    
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
    result = await process_data(
        seq=request.file_seq,
        flag="세계경쟁력지수",
        dbprsr=dbprsr,
        dbpdtm=dbpdtm,
        replace_all=True
    )
        
    return UploadResponse(
        success="true",
        message=ErrorMessages.SUCCESS,
    )