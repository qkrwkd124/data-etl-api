import pandas as pd
import os
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import openpyxl
from openpyxl.styles import PatternFill
from openpyxl.utils.cell import get_column_letter
import sys

# app 폴더를 sys.path에 추가하여 모듈을 찾을 수 있도록 합니다.
# 현재 파일의 경로를 기준으로 app 폴더의 부모 디렉토리를 추가합니다.
# 이 코드는 노트북이 app/services/ 내에 있다고 가정합니다.
# 만약 다른 위치에 있다면 경로를 적절히 수정해야 합니다.
current_file_path = Path(os.getcwd()) # Jupyter Notebook에서는 os.getcwd()가 현재 노트북 파일이 위치한 디렉토리를 반환합니다.
if str(current_file_path) not in sys.path:
    sys.path.insert(0, str(current_file_path))

from app.schemas.eiu_schemas import ProcessedExcelRow, ProcessedYearData, DataType, ExcelRowData


file_path = "/appdata/storage/research/original/2. EIU_AllDataByGeography_로데이터.xlsx"
CODES = ["PSBR", "DCPI", "CARA", "BALC", "XRPD", "XPP1", "XPP2", "XPP3", "XPP4", "FRES", "MEXP", "MIMP", "MPP1","MPP2", "MPP3","PUDP","DGDP","TDPY","BALM"]
HEADER = ["Country_Code","Series", "Code", "Currency", "Units"]

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
     
      # Excel 컬럼명 → 스키마 필드명 매핑
    COLUMN_MAPPING = {
        "Series": "series",
        "Code": "code", 
        "Currency": "currency",
        "Units": "units",
        "Source": "source",
        "Definition": "definition", 
        "Note": "note",
        "Published": "published"
    }

    row_data = {
        "country_code": country_code,
        "year_data": {}
    }

    for col_idx, col_name in enumerate(column_names, start=1):
        cell = sheet.cell(row=row_idx, column=col_idx)
        cell_value = str(cell.value)

        #일반 필드 처리
        if col_name in COLUMN_MAPPING:
            row_data[COLUMN_MAPPING[col_name]] = cell_value
            
        #연도 데이터 처리
        elif isinstance(col_name, str) and col_name.strip().isdigit():
            color = _get_cell_color(cell)
            if cell_value != "–" :
                if color == "0000588D" : # 블루
                    year_value = f"{DataType.ESTIMATE.value}|{cell_value}"
                else :
                    year_value = f"{DataType.ACTUAL.value}|{cell_value}"
            else :
                year_value = DataType.MISSING.value
            
            row_data["year_data"][col_name] = year_value
            
    excel_row = ExcelRowData(**row_data)
    
    return excel_row


def _create_default_excel_row(code: str, country_code: str, year_columns: List[str]) -> ExcelRowData:
    """
    누락된 코드에 대한 기본 스키마 객체 생성
    """
    default_year_data = {year: DataType.MISSING.value for year in year_columns}
    
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
    
    df_data = []

    for excel_row in excel_rows :
        row_dict = {
            "eiu_country_code": excel_row.country_code,
            "eiu_series_title": excel_row.series,
            "eiu_code": excel_row.code,
            "eiu_currency": excel_row.currency,
            "eiu_units": excel_row.units,
        }

        for year in year_columns :
            year_col = f"eiu_year_{int(year) % 100}"
            row_dict[year_col] = excel_row.year_data.get(year, DataType.MISSING.value)

        df_data.append(row_dict)
    
    df = pd.DataFrame(df_data)

    if year_columns :
        max_year = max(map(int,year_columns))
        max_YY = max_year % 100

        for i in range(max_YY + 1, 52) :
            df[f"eiu_year{i}"] = DataType.FORECAST.value

    return df

async def process_data(file_path:str) :

    print(f"원본 파일 처리 시작 : {file_path}")

    workbook = openpyxl.load_workbook(file_path)
    sheet_names = workbook.sheetnames

    # 모든 Excel 행 데이터
    all_excel_rows = []

    for sheet_name in sheet_names:
        print(f"시트 처리중 : {sheet_name}")
        sheet = workbook[sheet_name]

        header_row = None

        # 헤더 행 찾기 (보통 'Series'와 'Code' 컬럼이 있는 행)
        header_row = _find_header_row(sheet)
        if header_row is None:
            print(f"헤더 행을 찾을 수 없음: {sheet_name}")
            return Exception(f"헤더 행을 찾을 수 없음: {sheet_name}")

        # 컬럼 이름 추출
        column_names = _extract_column_names(sheet, header_row)

        print(f"열 이름 : {column_names}")

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

            if excel_row and excel_row.code and excel_row.code in CODES :
                sheet_data_by_code[excel_row.code] = excel_row


        # 누락된 코드에 대한 기본 데이터 생성
        for code in CODES :
            if code not in sheet_data_by_code :
                default_row = _create_default_excel_row(code, sheet_name, year_columns)
                sheet_data_by_code[code] = default_row

        all_excel_rows.extend(sheet_data_by_code.values())

    df = _convert_to_dataframe(all_excel_rows, year_columns)

    if df.empty :
        raise ValueError("처리할 수 있는 데이터가 없습니다.")
    
    return df
    

if __name__ == "__main__" :
    data = asyncio.run(process_data(file_path))
    print(data)
    
