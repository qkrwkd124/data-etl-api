import pandas as pd
from typing import Literal, Dict, Callable
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import traceback

from app.core.logger import get_logger
from app.core.constants.error import ErrorMessages, ErrorCode
from app.core.exceptions import (
    DataProcessingException,
    DatabaseException,
    FileException,
    DataNotFoundException,
    ValidationException
)
from app.core.constants.socioeconomic import (
    EconomicFreedomIndexConfig as EFI_Config,
    CorruptionPerceptionIndexConfig as CPI_Config,
    HumanDevelopmentIndexConfig as HDI_Config,
    WorldCompetitivenessIndexConfig as WCI_Config,
    SocioeconomicConfigType
)
from app.utils.excel_utils import read_excel_file
from app.utils.file_utils import validate_file, save_dataframe_to_csv, read_csv_file
from app.repositories.history_repository import DataUploadAutoHistoryRepository
from app.repositories.socioeconomic_repository import SocioeconomicIndexRepository

from app.models.socioeconomic import (
    EconomicFreedomIndex,
    CorruptionPerceptionIndex,
    HumanDevelopmentIndex,
    WorldCompetitivenessIndex
)

logger = get_logger()

IndexType = Literal["경제자유화지수", "부패인식지수", "인간개발지수", "세계경쟁력지수"]

CONFIG_MAPPING: Dict[IndexType, SocioeconomicConfigType] = {
    "경제자유화지수": EFI_Config,
    "부패인식지수": CPI_Config,
    "인간개발지수": HDI_Config,
    "세계경쟁력지수": WCI_Config
}



def _handle_processing_error(e: Exception, file_path: str, flag: IndexType) -> None:
    """데이터 처리 에러 핸들링"""
    logger.error(f"data processing error: {e}\n{traceback.format_exc()}")
    raise DataProcessingException(
        message=ErrorMessages.get_message(ErrorCode.DATA_PROCESSING_ERROR),
        error_code=ErrorCode.DATA_PROCESSING_ERROR,
        detail={"file_path": file_path, "flag": flag}
    )


async def _transform_country_name(
        df: pd.DataFrame,
        repository: SocioeconomicIndexRepository,
        flag: IndexType
)-> pd.DataFrame:

    config: SocioeconomicConfigType = CONFIG_MAPPING[flag]

    # 영문 국가명 -> ISO 코드 매핑
    country_names = await repository.get_eng_country_name_mapping()
    # ISO 코드 -> 무보 국가명 매핑 (ISO 코드를 대문자로 변환, 문자열일 때만 upper)
    country_iso_names_raw = await repository.get_iso2_eng_mapping()
    country_iso_names = {k.upper() if isinstance(k, str) else k: v for k, v in country_iso_names_raw.items()}


    # 영문 국가명 -> 무보 ISO 코드 변환 함수 정의
    def map_eng_country_to_iso(eng_country_name: str)-> str:
        # eng_country_name = eng_country_name.strip()
        return country_names.get(eng_country_name, None)
    
    # ISO 코드 -> 무보 영문 국가명으로 변환
    def map_iso_to_mubo_eng_country(iso_code: str)-> str:
        # iso_code = iso_code.strip()
        return country_iso_names.get(iso_code, None)
    
    if flag == "세계경쟁력지수":
        # df[config.TEMP_ISO_CODE] = df[config.EXCEL_ISO]
        df[config.EXCEL_COUNTRY] = df[config.EXCEL_ISO].apply(map_iso_to_mubo_eng_country)
        # logger.info(df[df[config.EXCEL_COUNTRY].isnull()])
    else :
        
        df[config.TEMP_ISO_CODE] = df[config.EXCEL_COUNTRY].apply(map_eng_country_to_iso)
        # logger.info(df[df[config.TEMP_ISO_CODE].isnull()])
        df[config.EXCEL_COUNTRY] = df[config.TEMP_ISO_CODE].apply(map_iso_to_mubo_eng_country)


    # 매핑되지 않은 국가(ISO 코드가 None이거나 국가명이 None인 경우) 제거
    # df = df[df[config.TEMP_ISO_CODE].notnull() & df[config.EXCEL_COUNTRY].notnull()].reset_index(drop=True)
    
    logger.info(f"국가명 변환 완료: {len(df)}행")
    return df

async def _create_final_output(
        df: pd.DataFrame,
        flag: IndexType
)-> pd.DataFrame:
    
    config: SocioeconomicConfigType = CONFIG_MAPPING[flag]
    
    final_df = df.rename(columns=config.get_final_column_mapping())

    sort_columns = config.get_sort_columns()
    ascending = [True]

    final_df = final_df.sort_values(by=sort_columns, ascending=ascending, ignore_index=True)

    logger.info(f"최종 데이터 정렬 완료: {len(final_df)}행")
    
    return final_df


async def _process_economic_freedom(
        file_path: str,
        repository: SocioeconomicIndexRepository,
        flag:str = "경제자유화지수"
    ) -> pd.DataFrame:
    
    
    df = read_csv_file(
        file_path,
        required_cols=EFI_Config.get_required_csv_columns(),
        skiprows=EFI_Config.SKIP_ROWS
    )

    try : 
        raw_df = df[EFI_Config.get_required_csv_columns()].copy()
        raw_df = raw_df[raw_df[EFI_Config.EXCEL_SCORE].notnull()]

        raw_df[EFI_Config.EXCEL_SCORE] = raw_df[EFI_Config.EXCEL_SCORE].rank(method="min", ascending=False).astype(int)

        transformed_df = await _transform_country_name(raw_df, repository, flag)

        final_df = await _create_final_output(transformed_df, flag)

        return final_df
    
    except Exception as e:
        _handle_processing_error(e, file_path, flag)

async def _process_corruption_perception(
        file_path: str,
        repository: SocioeconomicIndexRepository,
        flag:str = "부패인식지수"
    ) -> pd.DataFrame:
    
    df = await read_excel_file(
        file_path,
        header_cols=CPI_Config.get_header_columns()
    )

    try : 

        raw_df = df[CPI_Config.get_required_csv_columns()].copy()

        transformed_df = await _transform_country_name(raw_df, repository, flag)

        final_df = await _create_final_output(transformed_df, flag)

        return final_df
    except Exception as e:
        _handle_processing_error(e, file_path, flag)

async def _process_human_development(
        file_path: str,
        repository: SocioeconomicIndexRepository,
        flag:str = "인간개발지수"
    ) -> pd.DataFrame:
    
    df = await read_excel_file(
        file_path,
        header_cols=HDI_Config.get_header_columns()
    )
    try :
        # '' 값이 있어서 astype(int)에서 에러가 발생하므로, 우선적으로 결측치와 빈 문자열을 제거합니다.
        raw_df = df[df[HDI_Config.EXCEL_RANK].notnull() & (df[HDI_Config.EXCEL_RANK] != '')].copy()
        # astype(int) 적용 전에, 값이 실제로 정수로 변환 가능한지 확인합니다.
        raw_df[HDI_Config.EXCEL_RANK] = raw_df[HDI_Config.EXCEL_RANK].astype(int)
        # raw_df = df[df[HDI_Config.EXCEL_RANK].notnull() | (df[HDI_Config.EXCEL_RANK] != '')]
        # raw_df[HDI_Config.EXCEL_RANK] = raw_df[HDI_Config.EXCEL_RANK].astype(int)

        raw_df = raw_df[HDI_Config.get_required_csv_columns()].copy()

        transformed_df = await _transform_country_name(raw_df, repository, flag)
        
        final_df = await _create_final_output(transformed_df, flag)

        return final_df
    except Exception as e:
        _handle_processing_error(e, file_path, flag)
    
async def _process_world_competitiveness(
        file_path: str,
        repository: SocioeconomicIndexRepository,
        flag:str = "세계경쟁력지수"
    ) -> pd.DataFrame:
    
    df = await read_excel_file(
        file_path,
        header_cols=WCI_Config.get_header_columns()
    )

    try : 
        raw_df = df[WCI_Config.get_required_csv_columns()].copy()
        raw_df = raw_df[raw_df[WCI_Config.EXCEL_RANK].notnull()]

        transformed_df = await _transform_country_name(raw_df, repository, flag)
        
        final_df = await _create_final_output(transformed_df, flag)

        return final_df
    except Exception as e:
        _handle_processing_error(e, file_path, flag)


PROCESSOR_MAPPING: Dict[IndexType, Callable[[str, SocioeconomicIndexRepository, IndexType], pd.DataFrame]] = {
    "경제자유화지수": _process_economic_freedom,
    "부패인식지수": _process_corruption_perception,
    "인간개발지수": _process_human_development,
    "세계경쟁력지수": _process_world_competitiveness
}

async def process_data(
        seq: str,
        flag: str = Literal["경제자유화지수", "부패인식지수", "인간개발지수", "세계경쟁력지수"],
        dbprsr: AsyncSession = None,
        dbpdtm: AsyncSession = None,
        replace_all: bool = True,
    ) -> pd.DataFrame:
    
    try :
        # repository 초기화
        history_repository = DataUploadAutoHistoryRepository(dbpdtm)
        socioeconomic_repository = SocioeconomicIndexRepository(dbprsr, flag)

        history_info = await history_repository.get_history_info(seq)

        file_path = str(Path(history_info.file_path_nm,history_info.file_nm))
        logger.info(f"경제자유화지수 파일 처리 시작:{file_path}")
        
        # 0. 이력 데이터 삽입
        await history_repository.start_processing(seq)
        
        # 1. 파일 유효성 검사
        await validate_file(file_path, history_info.file_exts_nm)
        
        # 2. 데이터 처리
        final_df = await PROCESSOR_MAPPING[flag](file_path, socioeconomic_repository, flag)

        # 3. 데이터 삽입
        try :
            await socioeconomic_repository.replace_all_data(final_df)
        except Exception as e:
            logger.error(f"database error: {e}")
            raise DatabaseException(
                message=ErrorMessages.get_message(ErrorCode.DATABASE_ERROR),
                error_code=ErrorCode.DATABASE_ERROR,
                detail={
                    "file_path": file_path,
                    "flag": flag
                }
            )
        
        # 4. 파일 저장
        final_file_path = save_dataframe_to_csv(final_df, filename_prefix=f"{flag}_data", add_timestamp=True)

        # 5. 이력 업데이트
        await history_repository.success_processing(seq,
                                                    result_table_name={
                                                        "경제자유화지수": EconomicFreedomIndex.__tablename__,
                                                        "부패인식지수": CorruptionPerceptionIndex.__tablename__,
                                                        "인간개발지수": HumanDevelopmentIndex.__tablename__,
                                                        "세계경쟁력지수": WorldCompetitivenessIndex.__tablename__
                                                    }[flag],
                                                    process_count=len(final_df),
                                                    message=ErrorMessages.SUCCESS)
        
        return final_df
    
    except (DataProcessingException, DatabaseException, FileException, DataNotFoundException, ValidationException) as e:
        logger.error(f"처리 실패: {e.error_code.value} - {e.message}")
        await history_repository.fail_processing(seq, message=e.message)
        raise 
    except Exception as e:
        logger.error(f"예상하지 못한 시스템 오류: {e}")
        await history_repository.fail_processing(seq, message=ErrorMessages.get_message(ErrorCode.SYSTEM_ERROR))
        raise e