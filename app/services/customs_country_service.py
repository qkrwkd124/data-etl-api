import pandas as pd
import asyncio
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import traceback

from app.repositories.customs_repository import ExportImportStatByCountryRepository
from app.repositories.history_repository import DataUploadAutoHistoryRepository
from app.core.constants.customs import CustomsCountryConfig as Config
from app.core.logger import get_logger
from app.utils.file_utils import save_dataframe_to_csv, validate_file
from app.models.customs import ExportImportStatByCountry
from app.core.constants.error import ErrorMessages, ErrorCode
from app.utils.excel_utils import read_excel_file
from app.core.exceptions import (
    DataProcessingException,
    DatabaseException,
    FileException,
    DataNotFoundException,
    ValidationException
)

logger = get_logger()


async def _preprocess_data(
        df: pd.DataFrame
)-> pd.DataFrame:
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

    # 필수 컬럼 확인 (모델 정의 참고)
    final_df = final_df[Config.get_output_columns()].copy()
    
    # 정렬
    final_df = final_df.sort_values(by=Config.get_sort_columns())

    return final_df


async def process_data(
        seq: int,
        dbprsr: AsyncSession,
        dbpdtm: AsyncSession,
        replace_all: bool = True,
)-> pd.DataFrame:
    try :
        # repository 초기화
        expimp_repository = ExportImportStatByCountryRepository(dbprsr)
        history_repository = DataUploadAutoHistoryRepository(dbpdtm)

        history_info = await history_repository.get_history_info(seq)

        file_path = str(Path(history_info.file_path_nm,history_info.file_nm))
        logger.info(f"관세청 수출입규모 파일 처리 시작:{file_path}")

        # 0. 이력 데이터 삽입
        await history_repository.start_processing(seq)

        # 1. 파일 유효성 검사
        await validate_file(file_path, history_info.file_exts_nm)

        raw_df = await read_excel_file(file_path, header_cols=Config.get_header_columns())

        try :
            # 3. 데이터 전처리
            processed_df = await _preprocess_data(raw_df)

            # 4. 국가명 -> ISO 코드 변환
            transformed_df = await _transform_country_name(processed_df,expimp_repository)

            # 5. 최종 형태로 변환 및 파일 생성
            final_df = await _create_final_output(transformed_df)

        except Exception as e:
            logger.error(f"데이터 전처리 중 오류가 발생했습니다: \n{traceback.format_exc()}")
            raise DataProcessingException(
                message=ErrorMessages.get_message(ErrorCode.DATA_PROCESSING_ERROR),
                error_code=ErrorCode.DATA_PROCESSING_ERROR,
                detail={
                    "file_path": file_path,
                }
            )

        try :
            # 6. 데이터베이스 저장
            if replace_all:
                await expimp_repository.replace_all_data(final_df)
            else:
                await expimp_repository.insert_dataframe(final_df)
        except Exception as e:
            logger.error(f"database error: \n{traceback.format_exc()}")
            raise DatabaseException(
                message=ErrorMessages.get_message(ErrorCode.DATABASE_ERROR),
                error_code=ErrorCode.DATABASE_ERROR,
                detail={
                    "file_path": file_path,
                }
            )

        # 7. 파일 저장
        final_file_path = save_dataframe_to_csv(final_df, filename_prefix="customs_country_data", add_timestamp=True)

        # 8. 이력 업데이트
        await history_repository.success_processing(seq,
                                                    result_table_name=ExportImportStatByCountry.__tablename__,
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



if __name__ == "__main__":
    file_path = '/appdata/storage/research/original'
    file_name = '6-1. 수출입 실적(국가별)_20240613.xlsx'
    # file_full_path = Path(file_path,file_name)

    async def main():

        from app.db.base import session_factories

        async with session_factories["main"]() as main_db, session_factories["dbpdtm"]() as dbpdtm_db:
            try :
                df = await process_data(
                    seq=1,
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