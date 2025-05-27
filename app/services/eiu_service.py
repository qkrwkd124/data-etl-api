import pandas as pd
import os
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import openpyxl
from openpyxl.styles import PatternFill
from openpyxl.utils.cell import get_column_letter
import sys
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.eiu_repository import EIUEconomicIndicatorRepository
from app.schemas.eiu_schemas import ProcessedExcelRow, ExcelRowData
from app.core.constants.eiu import EIU_CODES, EIU_COLUMN_MAPPING, EIU_ESTIMATE_COLOR, EIUDataType
from app.core.logger import get_logger

logger = get_logger()


def _get_cell_color(cell) -> Optional[str]:
        """
        셀의 배경색 RGB 값을 반환
        
        Args:
            cell: openpyxl 셀 객체
            
        Returns:
            RGB 문자열 또는 None (배경색이 없는 경우)
        """
        if cell.fill.patternType == 'solid':
            return cell.font.color.rgb
        return None

def _find_header_row(sheet) -> Optional[int]:
    """헤더 행 찾기 - 누락된 함수 구현"""
    for row_idx in range(1, 20): # 상위 20행 내에서 헤더 찾기기
        series_cell = sheet.cell(row=row_idx, column=1).value
        code_cell = sheet.cell(row=row_idx, column=2).value
        
        if series_cell == "Series" and code_cell == "Code":
            return row_idx
        
    return None


def _extract_column_names(sheet, header_row: int) -> List[str]:
    """컬럼 이름 추출 - 기존 로직 함수화"""
    column_names = []
    col_idx = 1
    while True:
        cell_value = sheet.cell(row=header_row, column=col_idx).value
        if cell_value is None:
            break
        column_names.append(cell_value)
        col_idx += 1
    return column_names

def _create_excel_row_from_sheet_data(
    sheet, 
    row_idx: int, 
    column_names: List[str], 
    country_code: str
) -> Optional[ExcelRowData]:
     
    row_data = {
        "country_code": country_code,
        "year_data": {}
    }

    for col_idx, col_name in enumerate(column_names, start=1):
        cell = sheet.cell(row=row_idx, column=col_idx)
        cell_value = str(cell.value)

        #일반 필드 처리
        if col_name in EIU_COLUMN_MAPPING:
            row_data[EIU_COLUMN_MAPPING[col_name]] = cell_value
            
        #연도 데이터 처리
        elif isinstance(col_name, str) and col_name.strip().isdigit():
            color = _get_cell_color(cell)
            if cell_value != "–" :
                if color == EIU_ESTIMATE_COLOR : # 블루
                    year_value = f"{EIUDataType.ESTIMATE.value}|{cell_value}"
                else :
                    year_value = f"{EIUDataType.ACTUAL.value}|{cell_value}"
            else :
                year_value = EIUDataType.MISSING.value
            
            row_data["year_data"][col_name] = year_value
    
    excel_row = ExcelRowData(**row_data)
    
    return excel_row


def _create_default_excel_row(code: str, country_code: str, year_columns: List[str]) -> ExcelRowData:
    """
    누락된 코드에 대한 기본 스키마 객체 생성
    """
    default_year_data = {year: EIUDataType.MISSING.value for year in year_columns}
    
    return ExcelRowData(
        country_code=country_code,
        code=code,
        series="",
        currency="", 
        units="",
        source="",
        definition="",
        note="", 
        published="",
        year_data=default_year_data
    )


def _convert_to_dataframe(excel_rows: List[ExcelRowData],year_columns: List[str]) -> pd.DataFrame:
    """
    ExcelRowData 리스트를 DataFrame으로 변환
    """
    
    if not excel_rows :
        return pd.DataFrame()
    
    df_data = [excel_row.to_dataframe_dict(year_columns) for excel_row in excel_rows]
    
    df = pd.DataFrame(df_data)

    if year_columns :
        max_year = max(map(int,year_columns))
        max_YY = max_year % 100

        for i in range(max_YY + 1, 52) :
            df[f"eiu_year{i}"] = EIUDataType.FORECAST.value

    return df

async def process_data(file_path:str) :

    logger.info(f"원본 파일 처리 시작 : {file_path}")

    workbook = openpyxl.load_workbook(file_path)
    sheet_names = workbook.sheetnames

    # 모든 Excel 행 데이터
    all_excel_rows = []

    for sheet_name in sheet_names:
        logger.info(f"시트 처리중 : {sheet_name}")
        sheet = workbook[sheet_name]

        header_row = None

        # 헤더 행 찾기 (보통 'Series'와 'Code' 컬럼이 있는 행)
        header_row = _find_header_row(sheet)
        if header_row is None:
            logger.error(f"헤더 행을 찾을 수 없음: {sheet_name}")
            return Exception(f"헤더 행을 찾을 수 없음: {sheet_name}")

        # 컬럼 이름 추출
        column_names = _extract_column_names(sheet, header_row)

        logger.info(f"열 이름 : {column_names}")

        #연도 컬럼 식별
        year_columns = [col for col in column_names if isinstance(col,str) and col.strip().isdigit()]

        # 시트의 데이터를 코드별로 저장할 딕셔너리
        sheet_data_by_code = {}

        #데이터 행 처리
        for row_idx in range(header_row + 1, sheet.max_row + 1):
            
            # 스키마 객체 생성
            excel_row = _create_excel_row_from_sheet_data(
                sheet, row_idx, column_names, sheet_name
            )

            if excel_row and excel_row.code and excel_row.code in EIU_CODES :
                sheet_data_by_code[excel_row.code] = excel_row


        # 누락된 코드에 대한 기본 데이터 생성
        for code in EIU_CODES :
            if code not in sheet_data_by_code :
                default_row = _create_default_excel_row(code, sheet_name, year_columns)
                sheet_data_by_code[code] = default_row

        all_excel_rows.extend(sheet_data_by_code.values())

    df = _convert_to_dataframe(all_excel_rows, year_columns)

    if df.empty :
        raise ValueError("처리할 수 있는 데이터가 없습니다.")
    
    return df

async def process_eiu_economic_indicator(
        file_path: str,
        file_name: str,
        dbprsr: AsyncSession,
        replace_all: bool = True
) :
    """
    EIU 파일 전체 처리 (가공 + Repository를 통한 DB 저장 + CSV 저장)
    
    Args:
        file_path: 처리할 파일 경로
        file_name: 파일명 (선택사항)
        session: 데이터베이스 세션
        replace_all: True면 전체 교체, False면 추가
        
    Returns:
        처리 결과 딕셔너리
    """

    try :
        file_full_path = Path(file_path, file_name)
        logger.info(f"EIU Economic Indicator 파일 처리 시작: {file_full_path}")

        # 1. 데이터 가공
        df = await process_data(file_full_path)

        if df.empty :
            raise ValueError("처리할 수 있는 데이터가 없습니다.")
        
        #. 2. 데이터베이스 저장
        logger.info("2. 데이터베이스 저장 중...")
        repository = EIUEconomicIndicatorRepository(dbprsr)

        if replace_all :
            db_result = await repository.replace_all_data(df)
        else :
            insert_count = await repository.insert_dataframe(df)
            await dbprsr.commit()

        logger.info(f"데이터베이스 저장 완료: {db_result}")

        #. 3. CSV 저장

        logger.info(f"EIU Economic Indicator 파일 처리 완료: {file_full_path}")
    except Exception as e:

        logger.error(f"EIU Economic Indicator 파일 처리 중 오류: {str(e)}")


if __name__ == "__main__" :

    # current_file_path = Path(os.getcwd()) 
    # if str(current_file_path) not in sys.path:
    #     sys.path.insert(0, str(current_file_path))

    file_path = "/appdata/storage/research/original/2.EIU_AllDataByGeography_로데이터.xlsx"

    data = asyncio.run(process_data(file_path))
    print( data[data["eiu_country_code"] == "CA"][['eiu_year20','eiu_year21','eiu_year22','eiu_year23','eiu_year24']] )
    
