from typing import Any, Dict, Optional
from enum import Enum


"""계층적 예외 처리 시스템.

에러 코드 기반의 체계적인 예외 관리를 제공합니다.
각 계층별로 적절한 예외 클래스를 사용하여 에러를 처리합니다.
"""

class ErrorCode(Enum):
    """에러 코드 정의"""
    # 파일 관련 에러 (1000번대)
    FILE_NOT_FOUND = "E1001"
    FILE_EXTENSION_ERROR = "E1002"
    FILE_READ_ERROR = "E1003"
    FILE_HEADER_NOT_FOUND = "E1004"
    
    # 데이터 처리 에러 (2000번대)
    DATA_PROCESSING_ERROR = "E2001"
    DATA_VALIDATION_ERROR = "E2002"
    DATA_TRANSFORM_ERROR = "E2003"
    
    # 데이터베이스 에러 (3000번대)
    # DATABASE_CONNECTION_ERROR = "E3001"
    # DATABASE_QUERY_ERROR = "E3002"
    # DATABASE_TRANSACTION_ERROR = "E3003"
    DATABASE_ERROR = "E3001"
    
    # 요청 검증 에러 (4000번대)
    INVALID_REQUEST_PARAMETER = "E4001"
    MISSING_REQUIRED_FIELD = "E4002"

    # 데이터 조회 에러 (5000번대)
    DATA_NOT_FOUND = "E5001"
    FILE_INFO_NOT_FOUND = "E5002"
    
    # 시스템 에러 (9000번대)
    SYSTEM_ERROR = "E9001"
    UNKNOWN_ERROR = "E9999"

class BaseAppException(Exception):
    """애플리케이션 기본 예외 클래스.
    
    모든 커스텀 예외의 기본 클래스입니다.
    에러 코드, 메시지, 상태 코드, 상세 정보를 포함합니다.
    
    Args:
        message (str): 에러 메시지
        error_code (ErrorCode): 에러 코드
        status_code (int): HTTP 상태 코드 (기본값: 500)
        detail (dict): 추가 상세 정보 (선택사항)
    """
    
    def __init__(
        self, 
        message: str,
        error_code: ErrorCode,
        status_code: int = 500,
        detail: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_code": self.error_code.value,
            "message": self.message,
            "detail": self.detail
        }
    
class BusinessLogicException(BaseAppException):
    """비즈니스 로직 예외 (200번대).
    
    비즈니스 규칙 위반이나 잘못된 요청으로 인한 예외입니다.
    클라이언트에서 수정 가능한 에러를 나타냅니다.
    """
    
    def __init__(self, message: str, error_code: ErrorCode, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, status_code=200, detail=detail)


class FileException(BusinessLogicException):
    """파일 관련 예외"""
    pass


class DataProcessingException(BusinessLogicException):
    """데이터 처리 관련 예외"""
    pass


class ValidationException(BusinessLogicException):
    """요청 검증 관련 예외"""
    pass

class DataNotFoundException(BusinessLogicException):
    """데이터 조회 실패 예외"""
    
    def __init__(self, message: str, error_code: ErrorCode, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, detail)

class DatabaseException(BaseAppException):
    """데이터베이스 관련 예외"""
    
    def __init__(self, message: str, error_code: ErrorCode, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, status_code=200, detail=detail)
    pass

class SystemException(BaseAppException):
    """시스템 관련 예외"""
    
    def __init__(self, message: str, error_code: ErrorCode, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, status_code=200, detail=detail)