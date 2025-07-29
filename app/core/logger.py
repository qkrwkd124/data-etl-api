from loguru import logger
import sys
from pathlib import Path
from app.core.setting import get_settings

settings = get_settings()

# 로그 디렉토리 생성
log_path = Path(settings.LOG_DIR)


def _is_main_execution() -> bool:
    """__main__ 실행인지 확인.
    
    현재 실행 중인 파일이 __main__ 모듈인지 확인합니다.
    
    Returns:
        bool: __main__ 모듈인 경우 True, 그렇지 않은 경우 False
    """
    import inspect
    
    for frame_info in inspect.stack():
        if frame_info.filename.endswith('.py'):
            frame_globals = frame_info.frame.f_globals
            if frame_globals.get('__name__') == '__main__':
                return True
    return False


# 로거 설정
def setup_logger():
    """로거 초기화 및 설정.
    
    실행 환경에 따라 적절한 로깅 핸들러를 설정합니다.
    - 메인 실행: 콘솔 출력 (컬러 로깅)
    - 모듈 import: 파일 출력 (로테이션, 압축)
    """
    # 기본 핸들러 제거
    logger.remove()
    is_main = _is_main_execution()

    if is_main :
        # 콘솔 출력 설정
        logger.add(
            sys.stdout,
            format=settings.LOG_FORMAT,
            level=settings.LOG_LEVEL,
            colorize=True
        )
    else : 
        log_path.mkdir(exist_ok=True)

        # 파일 출력 설정
        logger.add(
            Path.joinpath(log_path, "app.log"),
            rotation="100 MB",
            retention="10 days",
            compression="zip",
            format=settings.LOG_FORMAT,
            level=settings.LOG_LEVEL,
            encoding="utf-8"
        )

# 로거 인스턴스 반환
def get_logger():
    return logger 