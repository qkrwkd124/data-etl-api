import pandas as pd
from typing import Literal
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import traceback

from app.core.logger import get_logger
from app.utils.excel_utils import read_excel_file
from app.utils.file_utils import validate_file, save_dataframe_to_csv
from app.core.constants.customs import CustomsTypeConfig as Config
from app.repositories.customs_repository import ExportImportItemByCountryRepository, ExportImportStatByCountryRepository
from app.repositories.history_repository import DataUploadAutoHistoryRepository
from app.models.customs import ExportImportItemByCountry
from app.core.constants.error import ErrorMessages, ErrorCode
from app.core.exceptions import (
    DataProcessingException,
    DatabaseException,
    FileException,
    DataNotFoundException,
    ValidationException
)

logger = get_logger()


async def _validate_export_import_flag(df: pd.DataFrame, flag: str) -> None:
    """파일의 수출입구분 검증.
    
    엑셀 파일에 포함된 수출입구분이 요청된 flag와
    일치하는지 검증합니다.
    
    Args:
        df (pd.DataFrame): 읽어들인 데이터프레임
        flag (str): 기대하는 수출입 구분 ("수출" 또는 "수입")
        
    Raises:
        ValidationException: 파일 내용과 기대값이 불일치할 때
    """
    
    # 수출입구분 컬럼 존재 여부 확인
    if Config.EXCEL_FLAG not in df.columns:
        logger.warning("수출입구분 컬럼이 없어 파일 내용 검증을 건너뜁니다.")
        return
    
    # 수출입구분 컬럼의 고유값 확인
    flag_values = df[Config.EXCEL_FLAG].dropna().unique()
    logger.info(f"파일 내 수출입구분 값들: {flag_values}")
    
    # 기대하는 값이 파일에 있는지 확인
    has_expected_flag = any(flag in str(val) for val in flag_values)
    
    if not has_expected_flag:
        raise ValidationException(
            message=ErrorMessages.get_message(ErrorCode.DATA_VALIDATION_ERROR),
            error_code=ErrorCode.DATA_VALIDATION_ERROR,
            detail={
                "flag": flag
            }
        )
    
    logger.info(f"파일 내용 검증 완료: {flag} 데이터가 올바르게 포함되어 있습니다.")


async def _export_preprocess_data(
    df: pd.DataFrame,
    flag: str,
)-> pd.DataFrame:
    """수출입 데이터 전처리.
    
    성질명 컬럼을 기준으로 필요한 데이터만 필터링하고
    카테고리명을 표준화합니다.
    
    Args:
        df (pd.DataFrame): 원본 데이터프레임
        flag (str): 수출입 구분 ("수출" 또는 "수입")
        
    Returns:
        pd.DataFrame: 전처리된 데이터프레임
        
    Note:
        - 수출: major/sub 카테고리 모두 처리
        - 수입: sub 카테고리만 처리
        - "기 타" 항목의 표준화된 이름으로 변경
    """
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
        repository: ExportImportStatByCountryRepository
)-> pd.DataFrame:
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

    
async def _create_final_output(
        df: pd.DataFrame
)-> pd.DataFrame:
    # 최종 형태로 데이터 변환
    final_df = df.rename(columns=Config.get_final_column_mapping())

    # 정렬 (예: 첫 번째 컬럼은 오름차순, 두 번째 컬럼은 내림차순)
    sort_columns = Config.get_sort_columns()
    ascending = [True, False]  # 필요에 따라 동적으로 지정
    final_df = final_df.sort_values(by=sort_columns, ascending=ascending)

    return final_df
    

async def process_data(
    seq: int,
    flag: str = Literal["수출", "수입"],
    dbprsr: AsyncSession = None,
    dbpdtm: AsyncSession = None,
    replace_all: bool = True,
)-> pd.DataFrame:
    """관세청 품목별 데이터 전체 처리.
    
    파일 검증부터 데이터 가공, 데이터베이스 저장까지
    전체 ETL 프로세스를 수행합니다.
    
    Args:
        seq (int): 파일 처리 순번 (이력 조회용)
        flag (str): 수출입 구분 ("수출" 또는 "수입")
        dbprsr (AsyncSession): 메인 데이터베이스 세션
        dbpdtm (AsyncSession): 이력 데이터베이스 세션
        replace_all (bool): 전체 교체 여부 (기본값: True)
        
    Returns:
        pd.DataFrame: 처리된 데이터프레임
        
    Raises:
        DataProcessingException: 데이터 처리 실패 시
        DatabaseException: 데이터베이스 작업 실패 시
        FileException: 파일 검증 또는 읽기 실패 시
        ValidationException: 데이터 검증 실패 시
    """
    try :
        # repository 초기화
        expimptype_repository = ExportImportItemByCountryRepository(dbprsr)
        expimpcountry_repository = ExportImportStatByCountryRepository(dbprsr)
        history_repository = DataUploadAutoHistoryRepository(dbpdtm)

        history_info = await history_repository.get_history_info(seq)

        file_path = str(Path(history_info.file_path_nm,history_info.file_nm))
        logger.info(f"관세청 수출/수입품 파일 처리 시작:{file_path}")

        # 0. 이력 데이터 삽입
        await history_repository.start_processing(seq)

        # 1. 파일 유효성 검사
        await validate_file(file_path, history_info.file_exts_nm)
        
        # 2. 엑셀 파일 읽기
        raw_df = await read_excel_file(file_path, header_cols=Config.get_header_columns())
        
        # 3. 수출입구분 검증
        await _validate_export_import_flag(raw_df, flag)

        try :
            # 4. 데이터 전처리
            preprocess_df = await _export_preprocess_data(raw_df,flag)

            # 5. 국가명 -> ISO 코드 변환 -> 무보 국가명 매핑
            transformed_df = await _transform_country_name(preprocess_df, expimpcountry_repository)

            # 6. 최종 형태로 변환 및 파일 생성
            final_df = await _create_final_output(transformed_df)

        except Exception as e:
            logger.error(f"data processing error: \n{traceback.format_exc()}")
            raise DataProcessingException(
                message=ErrorMessages.get_message(ErrorCode.DATA_PROCESSING_ERROR),
                error_code=ErrorCode.DATA_PROCESSING_ERROR,
                detail={
                    "file_path": file_path,
                    "flag": flag
                }
            )

        try :
            # 7. 데이터베이스 저장
            if replace_all:
                await expimptype_repository.replace_all_data(final_df)
            else:
                await expimptype_repository.delete_by_flag(flag)
                await expimptype_repository.insert_dataframe(final_df)
        except Exception as e:
            logger.error(f"database error: \n{traceback.format_exc()}")
            raise DatabaseException(
                message=ErrorMessages.get_message(ErrorCode.DATABASE_ERROR),
                error_code=ErrorCode.DATABASE_ERROR,
                detail={
                    "file_path": file_path,
                    "flag": flag
                }
            )
        
        # 8. 파일 저장
        final_file_path = save_dataframe_to_csv(final_df, filename_prefix="customs_type_data", add_timestamp=True)

        # 9. 이력 업데이트
        await history_repository.success_processing(seq,
                                                    result_table_name=ExportImportItemByCountry.__tablename__,
                                                    process_count=len(final_df),
                                                    message=ErrorMessages.SUCCESS)

        return final_df
    except (DataProcessingException, DatabaseException, FileException, DataNotFoundException, ValidationException) as e:
        logger.error(f"처리 실패: {e.error_code.value} - {e.message}")
        await history_repository.fail_processing(seq, message=e.message)
        raise 
    except Exception as e:
        logger.error(f"예상하지 못한 시스템 오류: \n{traceback.format_exc()}")
        await history_repository.fail_processing(seq, message=ErrorMessages.get_message(ErrorCode.SYSTEM_ERROR))
        raise e