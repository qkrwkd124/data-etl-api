"""파일 관련 공통 기능 유틸리티.

파일 검증, 저장 등의 공통 기능을 제공합니다.
보안과 안정성을 고려한 파일 처리를 포함합니다.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List
import traceback

from app.core.logger import get_logger
from app.core.setting import get_settings
from app.core.constants.error import ErrorMessages, ErrorCode
from app.core.exceptions import FileException

settings = get_settings()
logger = get_logger()


async def validate_file(
        file_path: str,
        file_exts_nm: str
)-> None:
    """파일 유효성 검사.
    
    파일 확장자와 존재 여부를 검증합니다.
    보안을 위해 허용된 확장자만 처리합니다.
    
    Args:
        file_path (str): 검증할 파일 경로
        file_exts_nm (str): 파일 확장자
        
    Raises:
        FileException:
            - 지원하지 않는 확장자일 때 (FILE_EXTENSION_ERROR)
            - 파일이 존재하지 않을 때 (FILE_NOT_FOUND)
            
    Note:
        현재 지원하는 확장자: XLSX, CSV
    """
    if file_exts_nm.upper() not in ["XLSX", "CSV"]:
        logger.error(f"파일 확장자가 올바르지 않습니다: {file_path}")
        raise FileException(
            message=ErrorMessages.get_message(ErrorCode.FILE_EXTENSION_ERROR),
            error_code=ErrorCode.FILE_EXTENSION_ERROR,
            detail={
                "file_path": file_path,
                "file_exts_nm": file_exts_nm
            }
        )
    
    if not Path(file_path).exists():
        logger.error(f"파일이 존재하지 않습니다: {file_path}")
        raise FileException(
            message=ErrorMessages.get_message(ErrorCode.FILE_NOT_FOUND),
            error_code=ErrorCode.FILE_NOT_FOUND,
            detail={
                "file_path": file_path
            }
        )
    
def read_csv_file(
        file_path: str,
        required_cols: List[str],
        sep: str = ",",
        line_terminator: str = "\n",
        skiprows: int = None
    ) -> pd.DataFrame:
    try :
        df = pd.read_csv(file_path, sep=sep, lineterminator=line_terminator, skiprows=skiprows)

        for col in required_cols:
            if col not in df.columns:
                raise FileException(
                    message=ErrorMessages.get_message(ErrorCode.FILE_HEADER_NOT_FOUND),
                    error_code=ErrorCode.FILE_HEADER_NOT_FOUND,
                    detail={
                        "file_path": file_path,
                    }
                )

        return df
    
    except Exception as e:
        logger.error(f"Error reading CSV file: \n{traceback.format_exc()}")
        raise FileException(
            message=ErrorMessages.get_message(ErrorCode.FILE_READ_ERROR),
            error_code=ErrorCode.FILE_READ_ERROR,
            detail={
                "file_path": file_path,
            }
        )

def save_dataframe_to_csv(
    df: pd.DataFrame,
    filename_prefix: str,
    output_dir: str = settings.CSV_OUTPUT_DIR,
    add_timestamp: bool = True
) -> str:
    """
    DataFrame을 CSV로 저장하는 공통 함수
    
    Args:
        df: 저장할 DataFrame
        filename_prefix: 파일명 접두사
        output_dir: 출력 디렉토리
        add_timestamp: 타임스탬프 추가 여부
        
    Returns:
        저장된 파일의 전체 경로
    """
    try:
        # 출력 디렉토리 생성
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 파일명 생성
        if add_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{filename_prefix}_{timestamp}.csv"
        else:
            filename = f"{filename_prefix}.csv"
            
        file_path = Path(output_path,filename)
        
        # CSV 저장 (Excel에서 한글 제대로 보이도록)
        df.to_csv(
            file_path,
            index=False,
            encoding=settings.CSV_OUPUT_ENCOFING,
            na_rep=settings.CSV_OUPUT_NA_REP
        )
        
        logger.info(f"CSV 파일 저장 완료: {file_path} ({len(df)}행)")
        return str(file_path)
        
    except Exception as e:
        logger.error(f"CSV 저장 중 오류 발생: \n{traceback.format_exc()}")
        raise