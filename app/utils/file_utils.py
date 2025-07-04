import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional
from app.core.logger import get_logger
from app.core.settings import get_settings

settings = get_settings()
logger = get_logger()

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
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
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
        logger.error(f"CSV 저장 중 오류 발생: {str(e)}")
        raise