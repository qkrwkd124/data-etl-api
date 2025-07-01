import sys
import os
import asyncio
import re
import pandas as pd
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, List
from itertools import zip_longest

from app.core.constants.eiu import EIUDataType
from app.schemas.eiu_schemas import TradePartnerData, CountryTradeData
from app.models.EIU import EIU_PARTNER_ISO
from app.repositories.eiu_repository import EIUPartnerRepository
from app.core.logger import get_logger

logger = get_logger()



def _extract_partner_from_definition(sheet_name: str, definition: str) -> Optional[str]:
    """
    Definition 필드에서 파트너 국가를 추출
    예: "Exports to India, as a percentage..." -> "India"
    """
    
    if not definition or pd.isna(definition):
        return None
    

    export_pattern = re.compile(r'Exports (?:from|to) (?:the\s+)?([^,]+?)(?:,)?\s*(?:as a percentage|as percentage)', re.IGNORECASE)
    import_pattern = re.compile(r'Imports (?:from|to) (?:the\s+)?([^,]+?)(?:,)?\s*(?:as a percentage|as percentage)', re.IGNORECASE)

    definition = str(definition).strip()

    if sheet_name.startswith("XPM"):
        match = export_pattern.search(definition)
    elif sheet_name.startswith("MPM"):
        match = import_pattern.search(definition)
    else:
        return None
        
    if match:
        return match.group(1).strip()
    else:
        return None


def _find_header_idx(df: pd.DataFrame) -> Optional[int]:
    """
    DataFrame에서 헤더 행을 찾기
    Geography와 Code 컬럼이 있는 행을 찾음
    """
    for idx in range(min(20, len(df))):
        row = df.iloc[idx]
        if len(row) >= 2:
            if (str(row.iloc[0]).strip() == "Geography" and 
                str(row.iloc[1]).strip() == "Code"):
                return idx
    return None


def _get_column_indices(header_row: pd.Series) -> Dict[str, int]:
        """
        간단한 컬럼 인덱스 매핑 생성
        
        Args:
            header_row: 헤더 행
            
        Returns:
            컬럼명-인덱스 딕셔너리
        """
        column_indices = {}
        
        for idx, col_name in enumerate(header_row):
            if pd.notna(col_name):
                col_str = str(col_name).strip()
                column_indices[col_str] = idx
        
        logger.debug(f"컬럼 인덱스: {column_indices}")
        return column_indices


def _aggregate_country_data(trade_data_list: List[TradePartnerData]) -> Dict[str, CountryTradeData]:
    """국가별로 수출입 데이터를 집계"""
    country_data = {}
    
    for trade_data in trade_data_list:
        
        # 유효한 데이터만 처리 (파트너명이 있고 비율이 0보다 큰 경우)
        if trade_data.partner_name is None or trade_data.partner_rate <= 0:
            continue

        if trade_data.partner_name is not None:
            trade_data.partner_name = trade_data.partner_name.strip().lower()

        country_code = trade_data.country_code.strip()
        
        country_data.setdefault(country_code, CountryTradeData(
            country_code=country_code,
            import_partners=[],
            export_partners=[]
        ))
        
        partner_info = (trade_data.partner_name, trade_data.partner_rate)
        
        if trade_data.trade_type == "export":
            country_data[country_code].export_partners.append(partner_info)
        else:  # import
            country_data[country_code].import_partners.append(partner_info)

    # for country_code, data in country_data.items():
    #     # print(country_code, data)
    #     data.export_partners.sort(key=lambda x: x[1], reverse=True)
    #     data.import_partners.sort(key=lambda x: x[1], reverse=True)

    return country_data


async def _create_integrated_dataframe(country_data: Dict[str, CountryTradeData],partner_repository: EIUPartnerRepository) -> pd.DataFrame:
    """통합 데이터프레임 생성"""
    all_rows = []
    
    # 주요수출입국가명 ISO 매핑정보
    partner_iso_mapping = await partner_repository.get_partner_ISO_mapping()

    # ISO값을 무역보험공사 한글국가명으로 매핑정보
    partner_name_mapping = await partner_repository.get_partner_name()

    for country_code, data in country_data.items():
        # 수출입 총합 계산
        export_total = sum(rate for _, rate in data.export_partners)
        import_total = sum(rate for _, rate in data.import_partners)
        
        # 수출/수입 데이터 존재 여부 확인
        has_export_data = len(data.export_partners) > 0
        has_import_data = len(data.import_partners) > 0

        # zip_longest로 수출/수입 데이터를 동시에 처리
        country_rows = []
        country_name = partner_name_mapping.get(country_code, '')

        for exp_data, imp_data in zip_longest(data.export_partners, data.import_partners, fillvalue=(None, 0)):
            row = {"cont_code": country_code, "cont_nm": country_name}

            exp_partner, exp_rate = exp_data if exp_data is not None else (None, None)
            imp_partner, imp_rate = imp_data if imp_data is not None else (None, None)

            # 수출,수입국 ISO 매핑
            exp_partner_iso = partner_iso_mapping.get(exp_partner, '')
            imp_partner_iso = partner_iso_mapping.get(imp_partner, '')

            # 수출 파트너명이 있는 경우
            # if exp_partner is not None:
                # row["MAJ_EXP_CONT_CODE"] = exp_partner_iso
            row["maj_exp_cont_nm"] = partner_name_mapping.get(exp_partner_iso, '')
            row["exp_rate"] = f"{exp_rate:.3f}%" if exp_rate != 0 else "0%"

            # 수입 파트너명이 있는 경우
            # if imp_partner is not None:
                # row["MAJ_IMP_CONT_CODE"] = imp_partner_iso
            row["maj_imp_cont_nm"] = partner_name_mapping.get(imp_partner_iso, '')
            row["imp_rate"] = f"{imp_rate:.3f}%" if imp_rate != 0 else "0%"

            country_rows.append(row)

        etc_row = {"cont_code": country_code, "cont_nm": country_name}

        # 수출 데이터가 있고 100% 미만인 경우
        if has_export_data and export_total < 100:
            etc_row["maj_exp_cont_nm"] = "기타"
            etc_row["exp_rate"] = f"{100 - export_total:.3f}%"

        # 수입 데이터가 있고 100% 미만인 경우
        if has_import_data and import_total < 100:
            etc_row["maj_imp_cont_nm"] = "기타"
            etc_row["imp_rate"] = f"{100 - import_total:.3f}%"

        # ETC 행에 데이터가 있는 경우에만 추가
        if "maj_exp_cont_nm" in etc_row or "maj_imp_cont_nm" in etc_row:
            country_rows.append(etc_row)
        
        all_rows.extend(country_rows)

    df = pd.DataFrame(all_rows)
    df.where(pd.notna(df), None, inplace=True)

    return df


async def process_data(
        file_path:str,
):
    excel_file = pd.ExcelFile(file_path)
    sheet_names = excel_file.sheet_names
    trade_data_list = []

    for sheet_name in sheet_names:
        if sheet_name.startswith(("XPM", "MPM")):
            logger.info(f"시트 처리 중: {sheet_name}")

            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, keep_default_na=False, na_values=[])

            header_idx = _find_header_idx(df)

            if header_idx is None:
                logger.error(f"헤더 행을 찾을 수 없음: {sheet_name}")
                return []
            
            header_row = df.iloc[header_idx]
            column_indices = _get_column_indices(header_row)
            # print(column_indices)
            
            if sheet_name.startswith("XPM"):
                trade_type = "export"
            elif sheet_name.startswith("MPM"):
                trade_type = "import"
            else :
                logger.error(f"잘못된 시트 이름: {sheet_name}")
                return []
            
            for idx in range(header_idx + 1, len(df)):
                row = df.iloc[idx]
                country_name = row.iloc[column_indices['Geography']]
                country_code = row.iloc[column_indices['Code']]
                definition = row.iloc[column_indices['Definition']] # nan, '–' 로로 표현
                for col in column_indices:
                    if col.isdigit() and len(col) == 4: # 연도값 찾기기
                        rate_value = row.iloc[column_indices[col]]
                        break

                if rate_value is None or pd.isna(rate_value) or rate_value == EIUDataType.MISSING.value: 
                    rate_value = 0.0
                
                partner_name = _extract_partner_from_definition(sheet_name, definition)
                
                trade_partner_data = TradePartnerData(
                    country_code=str(country_code).strip(),
                    partner_name=partner_name,
                    partner_rate=float(rate_value),
                    trade_type=trade_type,
                )

                trade_data_list.append(trade_partner_data)

    return trade_data_list


async def process_eiu_major_trade_partner(
        file_path: str,
        file_name: str,
        dbprsr: AsyncSession,
        replace_all: bool = True
        ) -> pd.DataFrame:
    """
    EIU 주요 수출입국 데이터를 처리하여 통합 데이터프레임을 생성
    
    주요 처리 단계:
    1. EIU 엑셀 파일에서 원본 데이터 추출 (XPM1-4, MPM1-4 시트)
    2. 유효한 데이터만 필터링 (파트너명 존재, 비율 > 0)
    3. 국가별로 수출입 데이터 집계 및 정렬
    4. 수출/수입 데이터가 모두 없는 국가는 제외
    5. 통합 데이터프레임 생성 (수출입 데이터를 한 행에 병합)
    6. 100% 미만인 경우 ETC 행 추가
    
    Args:
        file_path: 파일이 위치한 디렉토리 경로
        file_name: EIU 엑셀 파일명
        dbprsr: 데이터베이스 세션
        
    Returns:
        pd.DataFrame: 통합된 주요 수출입국 데이터프레임
        
    Raises:
        Exception: 파일 처리 중 오류 발생 시
    """
    try:
        file_full_path = Path(file_path) / file_name
        logger.info(f"EIU Major Export and Import Partner 파일 처리 시작: {file_full_path}")

        # Repository 객체 한 번만 생성
        partner_repository = EIUPartnerRepository(dbprsr)

        # 1. 원본 데이터 추출
        logger.info("1단계: 원본 데이터 추출 중...")
        trade_data_list = await process_data(str(file_full_path))
        logger.info(f"총 {len(trade_data_list)}개의 원본 데이터를 추출했습니다.")

        # 2. 국가별 데이터 집계 및 필터링
        logger.info("2단계: 국가별 데이터 집계 및 유효성 검사 중...")
        country_data = _aggregate_country_data(trade_data_list)
        logger.info(f"유효한 데이터가 있는 국가 수: {len(country_data)}")

        # 3. 통합 데이터프레임 생성
        logger.info("3단계: 통합 데이터프레임 생성 중...")
        final_df = await _create_integrated_dataframe(country_data, partner_repository)
        logger.info(f"최종 데이터프레임 생성 완료: {final_df.shape[0]}행 x {final_df.shape[1]}열")

        # 4. 데이터베이스 저장
        logger.info("4단계: 데이터베이스 저장 중...")
        if replace_all :
            db_result = await partner_repository.replace_all_data(final_df)
        else :
            insert_count = await partner_repository.insert_dataframe(final_df)
            await dbprsr.commit()
        logger.info("데이터베이스 저장 완료")

        # 5. 결과 요약 로그
        total_countries = len(country_data)
        countries_with_both = sum(1 for data in country_data.values() 
                                 if len(data.export_partners) > 0 and len(data.import_partners) > 0)
        countries_export_only = sum(1 for data in country_data.values() 
                                   if len(data.export_partners) > 0 and len(data.import_partners) == 0)
        countries_import_only = sum(1 for data in country_data.values() 
                                   if len(data.export_partners) == 0 and len(data.import_partners) > 0)
        
        logger.info(f"처리 결과 요약:")
        logger.info(f"  - 전체 국가 수: {total_countries}")
        logger.info(f"  - 수출/수입 모두 있는 국가: {countries_with_both}")
        logger.info(f"  - 수출만 있는 국가: {countries_export_only}")
        logger.info(f"  - 수입만 있는 국가: {countries_import_only}")

        return final_df
        
    except Exception as e:
        logger.error(f"EIU 주요 수출입국 데이터 처리 중 오류 발생: {str(e)}")
        raise


if __name__ == "__main__":
    file_path = "/appdata/storage/research/original"
    file_name = "EIU_AllDataBySeries_주요수출입국 원본파일_수정본.xlsx"
    file_full_path = Path(file_path,file_name)
    from app.db.base import get_main_db

    async def main():
        async for dbprsr in get_main_db():

            # partner_repository = EIUPartnerRepository(dbprsr)
            # trade_data_list = await process_data(str(file_full_path))
            # country_data = _aggregate_country_data(trade_data_list)
            # df = await _create_integrated_dataframe(country_data, partner_repository)
            df = await process_eiu_major_trade_partner(file_path, file_name, dbprsr, replace_all=True)
            print(df[df['cont_nm'] == '앙골라'])
            break 

    asyncio.run(main())
