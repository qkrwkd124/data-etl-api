from app.core.exceptions import ErrorCode

class ErrorMessages:
    """에러 메시지 매핑"""
    
    MESSAGES = {
        ErrorCode.FILE_NOT_FOUND: "파일을 찾을 수 없습니다.",
        ErrorCode.FILE_EXTENSION_ERROR: "지원하지 않는 파일 확장자입니다.",
        ErrorCode.FILE_READ_ERROR: "파일을 읽는 중 오류가 발생했습니다.",
        ErrorCode.FILE_HEADER_NOT_FOUND: "파일의 헤더를 찾을 수 없습니다.",
        ErrorCode.DATA_PROCESSING_ERROR: "데이터 처리 중 오류가 발생했습니다.",
        ErrorCode.DATA_VALIDATION_ERROR: "데이터 유효성 검사에 실패했습니다.",
        ErrorCode.DATABASE_ERROR:"데이터베이스 처리 중 오류가 발생했습니다.",
        ErrorCode.INVALID_REQUEST_PARAMETER: "요청 파라미터가 유효하지 않습니다.",
        ErrorCode.DATA_NOT_FOUND: "데이터를 찾을 수 없습니다.",
        ErrorCode.SYSTEM_ERROR: "시스템 오류가 발생했습니다.",
    }
    
    SUCCESS = "데이터 처리가 완료되었습니다."
    
    @classmethod
    def get_message(cls, error_code: ErrorCode) -> str:
        return cls.MESSAGES.get(error_code, "알 수 없는 오류가 발생했습니다.")