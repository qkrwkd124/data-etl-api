import pandas as pd
from typing import Optional, Dict, Any, List
from pathlib import Path
from app.core.logger import get_logger

logger = get_logger()

def _find_header_idx(df: pd.DataFrame, header_cols: List[str]) -> Optional[int]:
    """
    DataFrame에서 헤더 행(컬럼명이 위치한 행)의 인덱스를 찾습니다.

    Args:
        df (pd.DataFrame): 헤더 행을 찾을 데이터프레임 (header=None으로 읽은 원본)
        header_cols (List[str]): 헤더로 기대하는 컬럼명 리스트 (예: ["기간", "국가", ...])

    Returns:
        Optional[int]: 헤더 행의 인덱스(0부터 시작). 찾지 못하면 None 반환.

    Note:
        - 상위 20개 행에서 header_cols와 정확히 일치하는 행을 찾습니다.
        - 각 셀의 좌우 공백을 제거하여 비교합니다.
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
        """
        엑셀 파일을 읽고, 지정된 헤더 컬럼이 포함된 행을 찾아 데이터프레임을 반환합니다.

        Args:
            file_path (str): 읽을 엑셀 파일의 경로
            header_cols (List[str]): 헤더로 사용할 컬럼명 리스트 (예: ["기간", "국가", ...])
            sheet_name (str|int, optional): 읽을 시트명 또는 인덱스. 기본값은 0 (첫 번째 시트)

        Returns:
            pd.DataFrame: 헤더가 적용된 데이터프레임

        Raises:
            ValueError: 헤더 행을 찾을 수 없을 때 발생
            Exception: 파일 읽기 또는 처리 중 기타 예외 발생 시
        """

        # 첫 번째 시트 읽기
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

        # 데이터 시작 위치 찾기 (헤더가 있는 행)
        header_idx = _find_header_idx(df, header_cols)

        if header_idx is None:
            raise ValueError("헤더 행을 찾을 수 없습니다.")

        df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_idx)

        #총계 행 제거 (첫 번째 데이터 행이 보통 총계)
        df = df[df.iloc[:, 0] != "총계"].copy()

        logger.info(f"엑셀 파일 읽기 완료: {len(df)}행")
        return df

    except Exception as e:
        logger.error(f"Error reading excel file: {e}")
        raise e

