"""엑셀 파일 처리 전용 유틸리티.

pandas를 사용한 엑셀 파일 읽기와 헤더 탐지 기능을 제공합니다.
복잡한 엑셀 구조에서 정확한 데이터 영역을 찾는 기능을 포함합니다.
"""

import pandas as pd
from typing import Optional, List
import traceback

from app.core.logger import get_logger
from app.core.constants.error import ErrorMessages, ErrorCode
from app.core.exceptions import FileException

logger = get_logger()

def _find_header_idx(df: pd.DataFrame, header_cols: List[str]) -> Optional[int]:
    """DataFrame에서 헤더 행 인덱스 찾기.
    
    원본 DataFrame에서 지정된 헤더 컬럼명들이 일치하는
    행의 인덱스를 찾습니다.
    
    Args:
        df (pd.DataFrame): 헤더 행을 찾을 데이터프레임 (header=None으로 읽은 원본)
        header_cols (List[str]): 헤더로 기대하는 컬럼명 리스트
        
    Returns:
        Optional[int]: 헤더 행의 인덱스(0부터 시작) 또는 None
        
    Note:
        상위 20개 행에서 header_cols와 정확히 일치하는 행을 찾으며,
        각 셀의 좌우 공백을 제거하여 비교합니다.
    """
    for idx in range(min(20, len(df))):
        row = df.iloc[idx]
        if len(row) >= len(header_cols):
            if all(str(row.iloc[i]).strip() == col for i, col in enumerate(header_cols)):
                return idx
    return None

async def read_excel_file(
        file_path: str,
        header_cols: List[str],
        sheet_name: str = 0
)-> pd.DataFrame:
    try:
        """엑셀 파일 읽기 및 헤더 적용.
    
        지정된 헤더 컬럼이 포함된 행을 찾아서
        올바른 데이터프레임을 반환합니다.
        
        Args:
            file_path (str): 읽을 엑셀 파일의 경로
            header_cols (List[str]): 헤더로 사용할 컬럼명 리스트
            sheet_name (str|int): 읽을 시트명 또는 인덱스 (기본값: 0)
            
        Returns:
            pd.DataFrame: 헤더가 적용되고 총계 행이 제거된 데이터프레임
            
        Raises:
            FileException: 
                - 헤더 행을 찾을 수 없을 때 (FILE_HEADER_NOT_FOUND)
                - 파일 읽기 실패 시 (FILE_READ_ERROR)
                
        Note:
            - keep_default_na=False로 설정하여 빈 셀이 NaN으로 변환되지 않음
            - "총계" 행은 자동으로 제거됨
        """
        # 첫 번째 시트 읽기
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, keep_default_na=False, na_values=[])

        # 데이터 시작 위치 찾기 (헤더가 있는 행)
        header_idx = _find_header_idx(df, header_cols)

        if header_idx is None:
            raise FileException(
                message=ErrorMessages.get_message(ErrorCode.FILE_HEADER_NOT_FOUND),
                error_code=ErrorCode.FILE_HEADER_NOT_FOUND,
                detail={
                    "file_path": file_path,
                    "sheet_name": sheet_name
                }
            )

        df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_idx, keep_default_na=False, na_values=[])

        #총계 행 제거 (첫 번째 데이터 행이 보통 총계)
        df = df[df.iloc[:, 0] != "총계"].copy()

        logger.info(f"엑셀 파일 읽기 완료: {len(df)}행")
        return df
    
    except FileException as e:
        raise

    except Exception as e:
        logger.error(f"Error reading excel file: \n{traceback.format_exc()}")
        raise FileException(
            message=ErrorMessages.get_message(ErrorCode.FILE_READ_ERROR),
            error_code=ErrorCode.FILE_READ_ERROR,
            detail={
                "file_path": file_path,
                "sheet_name": sheet_name
            }
        )

