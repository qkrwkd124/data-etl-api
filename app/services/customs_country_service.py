import pandas as pd
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
from datetime import datetime

from app.models.customs import CountryMapping, ExportImportStatByCountry
from app.models.shared_models import COUNTRY_INFO
from app.repositories.customs_repository import ExportImportStatByCountryRepository
from app.repositories.history_repository import DataUploadAutoHistoryRepository
from app.core.constants.customs import CustomsCountryConfig as Config
from app.schemas.history_schemas import DataUploadAutoHistoryCreate, DataUploadAutoHistoryUpdate, JobType
from app.db.base import get_main_db, get_dbpdtm_db
from app.core.logger import get_logger
from app.utils.file_utils import save_dataframe_to_csv

logger = get_logger()

async def _validate_file(
        file_path: str
)-> bool:
    return Path(file_path).exists()

def _find_header_idx(df: pd.DataFrame) -> Optional[int]:
    """
    DataFrame에서 헤더 행을 찾기
    기간 및 국가 컬럼이 있는 행을 찾음
    """
    header_cols = Config.get_header_columns()
    for idx in range(min(20, len(df))):
        row = df.iloc[idx]
        if len(row) >= len(header_cols):
            if all(str(row.iloc[i]).strip() == col for i, col in enumerate(header_cols)):
                return idx
    return None

async def _read_excel_file(
        file_path: str
)-> pd.DataFrame:
    try:

        # 첫 번째 시트 읽기
        df = pd.read_excel(file_path, sheet_name=0, header=None)

        # 데이터 시작 위치 찾기 (헤더가 있는 행)
        header_idx = _find_header_idx(df)

        if header_idx is None:
            raise ValueError("헤더 행을 찾을 수 없습니다.")

        df = pd.read_excel(file_path, sheet_name=0, header=header_idx)

        #총계 행 제거 (첫 번째 데이터 행이 보통 총계)
        df = df[df.iloc[:, 0] != "총계"].copy()

        logger.info(f"엑셀 파일 읽기 완료: {len(df)}행")
        return df

    except Exception as e:
        logger.error(f"Error reading excel file: {e}")
        raise e
    

async def _preprocess_data(
        df: pd.DataFrame
)-> pd.DataFrame:
    try:
        #컬럼명 정리
        df.columns = df.columns.str.strip()

        # 필수 컬럼 확인
        missing_cols = Config.validate_excel_columns(df.columns.to_list())
        if missing_cols:
            raise ValueError(f"필수 컬럼이 누락되었습니다: {missing_cols}")
        

        # 기간 데이터 정리(년도만 추출)
        df[Config.EXCEL_PERIOD] = df[Config.EXCEL_PERIOD].astype(str).str.extract(r'(\d{4})')
        
        logger.info(f"데이터 전처리 완료: {len(df)}행")

        return df

    except Exception as e:
        logger.error(f"Error preprocessing data: {e}")
        raise e


async def _transform_country_name(
        df: pd.DataFrame,
        repository: ExportImportStatByCountryRepository
)-> pd.DataFrame:
    try:
        # 관세청 국가명 -> ISO 코드 매핑
        country_names = await repository.get_country_name_mapping()
        # ISO 코드 -> 무보 국가명 매핑
        country_iso_names = await repository.get_country_iso_mapping()


        # 관세청 국가명 -> ISO 코드 변환 함수 정의
        
        def map_korean_country_to_iso(korean_country_name: str)-> str:
            # korean_country_name = korean_country_name.strip()
            return country_names.get(korean_country_name, None)
        
        # ISO 코드 -> 무보 국가명으로 변환
        def map_iso_to_mubo_country(iso_code: str)-> str:
            # iso_code = iso_code.strip()
            return country_iso_names.get(iso_code, None)
        
        df[Config.TEMP_ISO_CODE] = df[Config.EXCEL_COUNTRY].apply(map_korean_country_to_iso)
        df[Config.EXCEL_COUNTRY] = df[Config.TEMP_ISO_CODE].apply(map_iso_to_mubo_country)

        # 매핑되지 않은 국가(ISO 코드가 None이거나 국가명이 None인 경우) 제거
        df = df[df[Config.TEMP_ISO_CODE].notnull() & df[Config.EXCEL_COUNTRY].notnull()].reset_index(drop=True)
        
        logger.info(f"국가명 변환 완료: {len(df)}행")
        return df

    except Exception as e:
        logger.error(f"Error transforming country name: {e}")
        raise e


async def _create_final_output(
        df: pd.DataFrame
)-> pd.DataFrame:
    try:
        # 최종 형태로 데이터 변환
        final_df = df.rename(columns=Config.get_final_column_mapping())

        # 필수 컬럼 확인 (모델 정의 참고)
        final_df = final_df[Config.get_output_columns()].copy()
        
        # 정렬
        final_df = final_df.sort_values(by=Config.get_sort_columns())

        return final_df
    except Exception as e:
        logger.error(f"Error creating final output: {e}")
        raise e


async def process_data(
        file_path: str,
        file_name: str,
        dbprsr: AsyncSession,
        dbpdtm: AsyncSession,
        replace_all: bool = True,
)-> pd.DataFrame:
    try :
        file_path = Path(file_path,file_name)
        logger.info(f"관세청 수출입규모 파일 처리 시작:{file_path}")

        # repository 초기화
        expimp_repository = ExportImportStatByCountryRepository(dbprsr)
        history_repository = DataUploadAutoHistoryRepository(dbpdtm)

        # 0. 이력 데이터 삽입
        seq = await history_repository.get_next_seq()
        history_data = DataUploadAutoHistoryCreate(
            data_wrk_no=seq,
            data_wrk_nm=JobType.CUSTOMS_COUNTRY,
            strt_dtm=datetime.now(),
            refl_file_nm=file_path.name,
            reg_usr_id="system",
            reg_dtm=datetime.now(),
            mod_usr_id="system",
            mod_dtm=datetime.now()
        )
        await history_repository.insert_history(seq, history_data)

        # 1. 파일 유효성 검사
        if not await _validate_file(file_path):
            logger.error(f"파일이 존재하지 않습니다: {file_path}")
            return ValueError(f"파일이 존재하지 않습니다: {file_path}")

        # 2. 엑셀 파일 읽기
        raw_df = await _read_excel_file(file_path)

        # 3. 데이터 전처리
        processed_df = await _preprocess_data(raw_df)

        # 4. 국가명 -> ISO 코드 변환
        transformed_df = await _transform_country_name(processed_df,expimp_repository)

        # 5. 최종 형태로 변환 및 파일 생성
        final_df = await _create_final_output(transformed_df)

        # 6. 데이터베이스 저장
        if replace_all:
            await expimp_repository.replace_all_data(final_df)
        else:
            await expimp_repository.insert_dataframe(final_df)

        # 7. 파일 저장
        final_file_path = save_dataframe_to_csv(final_df, filename_prefix="customs_country_data", add_timestamp=True)

        # 8. 이력 업데이트
        await history_repository.update_history(seq, DataUploadAutoHistoryUpdate(
            end_dtm=datetime.now(),
            fin_yn="Y",
            scr_file_nm=final_file_path,
            rslt_tab_nm="tb_bpc220",
            proc_cnt=len(final_df),
            mod_usr_id="system",
            mod_dtm=datetime.now()
        ))

        return final_df
    except Exception as e:
        logger.error(f"Error processing {file_name}: {e}")

        await history_repository.update_history(seq, DataUploadAutoHistoryUpdate(
            end_dtm=datetime.now(),
            fin_yn="N",
            rmk_ctnt=str(e),
            mod_usr_id="system",
            mod_dtm=datetime.now()
        ))

        raise e


if __name__ == "__main__":
    file_path = '/appdata/storage/research/original'
    file_name = '6-1. 수출입 실적(국가별)_20240613.xlsx'
    # file_full_path = Path(file_path,file_name)

    async def main():

        from app.db.base import session_factories

        async with session_factories["main"]() as main_db, session_factories["dbpdtm"]() as dbpdtm_db:
            try :
                df = await process_data(
                    file_path=file_path,
                    file_name=file_name,
                    dbprsr=main_db,
                    dbpdtm=dbpdtm_db,
                    replace_all=True
                )
                print(df)
                await main_db.commit()
                await dbpdtm_db.commit()
            except Exception as e:
                await main_db.rollback()
                await dbpdtm_db.rollback()
                logger.error(f"Error: {e}")
                raise e

    asyncio.run(main())