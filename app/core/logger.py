from loguru import logger
import sys
from pathlib import Path
from app.core.settings import get_settings

settings = get_settings()

# 로그 디렉토리 생성
log_path = Path(settings.LOG_DIR)


def _is_main_execution() -> bool:
    """__main__ 실행인지 확인"""
    import inspect
    
    for frame_info in inspect.stack():
        if frame_info.filename.endswith('.py'):
            frame_globals = frame_info.frame.f_globals
            if frame_globals.get('__name__') == '__main__':
                return True
    return False


# 로거 설정
def setup_logger():
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