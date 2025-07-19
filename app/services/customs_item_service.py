import pandas as pd
import asyncio
from typing import List, Dict, Any, Optional, Tuple,Literal
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
from datetime import datetime
import os
import sys

from app.schemas.history_schemas import DataUploadAutoHistoryCreate, JobType
from app.core.logger import get_logger
from app.utils.excel_utils import read_excel_file
from app.utils.file_utils import validate_file, save_dataframe_to_csv
from app.core.constants.customs import CustomsTypeConfig as Config
from app.repositories.customs_repository import ExportImportItemByCountryRepository
from app.repositories.history_repository import DataUploadAutoHistoryRepository,DataUploadAutoHistoryUpdate


logger = get_logger()


async def _export_preprocess_data(
    df: pd.DataFrame,
    flag: str,
)-> pd.DataFrame:
    
    major_regex = Config.MAJOR_CATEGORY_REGEX
    sub_regex = Config.SUB_CATEGORY_REGEX
    
    if flag == "수출":
        # 1. 성질명 컬럼에서 major/sub 정규표현식에 해당하는 행만 남김
        is_major = df[Config.EXCEL_CATEGORY].astype(str).str.match(major_regex)
        is_sub = df[Config.EXCEL_CATEGORY].astype(str).str.match(sub_regex)
        df = df[is_major | is_sub].copy()

        # 2. "카. 기 타"를 "카. 경공업품(기타)"로 변경, "바. 기 타"를 "바. 중화학 공업품(기타)"로 변경
        def replace_k_other(category: str) -> str:
            if isinstance(category, str) and category.strip().startswith("카. 기 타"):
                return "카. 경공업품(기타)"
            elif isinstance(category, str) and category.strip().startswith("바. 기 타"):
                return "바. 중화학 공업품(기타)"
            
            return category

        df[Config.EXCEL_CATEGORY] = df[Config.EXCEL_CATEGORY].apply(replace_k_other)

    elif flag == "수입":
        # 1. 성질명 컬럼에서 major/sub 정규표현식에 해당하는 행만 남김
        is_sub = df[Config.EXCEL_CATEGORY].astype(str).str.match(sub_regex)
        df = df[is_sub].copy()
        
        # 2. "카. 기 타"를 "카. 경공업품(기타)"로 변경, "바. 기 타"를 "바. 중화학 공업품(기타)"로 변경
        def replace_k_other(category: str) -> str:
            if isinstance(category, str) and category.strip().startswith("라. 기 타"):
                return "라. 자본재(기타)"
            elif isinstance(category, str) and category.strip().startswith("자. 기 타"):
                return "자. 원자재(기타)"
            
            return category

        df[Config.EXCEL_CATEGORY] = df[Config.EXCEL_CATEGORY].apply(replace_k_other)

    # 3. major/sub prefix(예: "1. ", "가. ") 제거
    def remove_prefix(category: str) -> str:
        if not isinstance(category, str):
            return category
        # major prefix 제거
        
        category = pd.Series(category).str.replace(major_regex, "", regex=True).iloc[0]
        # sub prefix 제거
        category = pd.Series(category).str.replace(sub_regex, "", regex=True).iloc[0]
        return category.strip()

    df[Config.EXCEL_CATEGORY] = df[Config.EXCEL_CATEGORY].apply(remove_prefix)

    return df

async def _transform_country_name(
        df: pd.DataFrame,
        repository: ExportImportItemByCountryRepository
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

        # 정렬 (예: 첫 번째 컬럼은 오름차순, 두 번째 컬럼은 내림차순)
        sort_columns = Config.get_sort_columns()
        ascending = [True, False]  # 필요에 따라 동적으로 지정
        final_df = final_df.sort_values(by=sort_columns, ascending=ascending)

        return final_df
    except Exception as e:
        logger.error(f"Error creating final output: {e}")
        raise e
    

async def process_data(
    file_path: str,
    file_name: str,
    flag: str = Literal["수출", "수입"],
    dbprsr: AsyncSession = None,
    dbpdtm: AsyncSession = None,
    replace_all: bool = True,
)-> pd.DataFrame:
    
    try :
        file_path = Path(file_path,file_name)
        logger.info(f"관세청 수출/수입품 파일 처리 시작:{file_path}")

        # repository 초기화
        expimptype_repository = ExportImportItemByCountryRepository(dbprsr)
        history_repository = DataUploadAutoHistoryRepository(dbpdtm)

        # 0. 이력 데이터 삽입
        seq = await history_repository.get_next_seq()
        history_data = DataUploadAutoHistoryCreate(
            data_wrk_no=seq,
            data_wrk_nm=JobType.CUSTOMS_ITEM.format(flag=flag),
            strt_dtm=datetime.now(),
            refl_file_nm=file_path.name,
            reg_usr_id="system",
            reg_dtm=datetime.now(),
            mod_usr_id="system",
            mod_dtm=datetime.now()
        )
        await history_repository.insert_history(seq, history_data)

        # 1. 파일 유효성 검사
        if not await validate_file(file_path):
            logger.error(f"파일이 존재하지 않습니다: {file_path}")
            return ValueError(f"파일이 존재하지 않습니다: {file_path}")
        
        # 2. 엑셀 파일 읽기
        raw_df = await read_excel_file(file_path, header_cols=Config.get_header_columns())

        # 3. 데이터 전처리
        preprocess_df = await _export_preprocess_data(raw_df,flag)

        # 4. 국가명 -> ISO 코드 변환 -> 무보 국가명 매핑
        transformed_df = await _transform_country_name(preprocess_df, expimptype_repository)

        # 5. 최종 형태로 변환 및 파일 생성
        final_df = await _create_final_output(transformed_df)

        # 6. 데이터베이스 저장
        if replace_all:
            await expimptype_repository.replace_all_data(final_df)
        else:
            await expimptype_repository.delete_by_flag(flag)
            await expimptype_repository.insert_dataframe(final_df)

        # 7. 파일 저장
        final_file_path = save_dataframe_to_csv(final_df, filename_prefix="customs_type_data", add_timestamp=True)

        # 8. 이력 업데이트
        await history_repository.update_history(seq, DataUploadAutoHistoryUpdate(
            end_dtm=datetime.now(),
            fin_yn="Y",
            scr_file_nm=final_file_path,
            rslt_tab_nm="tb_rhr130",
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