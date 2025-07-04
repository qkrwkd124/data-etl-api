# app/core/constants/customs.py
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass(frozen=True)
class CustomsCountryConfig:

    # 엑셀 원본 컬럼명
    EXCEL_PERIOD: str = "기간"
    EXCEL_COUNTRY: str = "국가"
    EXCEL_EXPORT_AMOUNT: str = "수출 금액"
    EXCEL_IMPORT_AMOUNT: str = "수입 금액"
    EXCEL_TRADE_BALANCE: str = "무역수지"
    
    # 임시 컬럼 (변환 과정에서 생성)
    TEMP_ISO_CODE: str = "ISO코드"
    
    # DB 컬럼명
    DB_YEAR: str = "impexp_year"
    DB_NATION_CODE: str = "impexp_nation_code"
    DB_NATION_NAME: str = "impexp_nation_nm"
    DB_EXPORT_MONEY: str = "impexp_exp_money"
    DB_IMPORT_MONEY: str = "impexp_imp_money"
    DB_TRADE_BALANCE: str = "impexp_trade_rate_money"


    @classmethod
    def get_required_excel_columns(cls) -> List[str]:
        """필수 엑셀 컬럼 목록"""
        return [
            cls.EXCEL_PERIOD,
            cls.EXCEL_COUNTRY,
            cls.EXCEL_EXPORT_AMOUNT,
            cls.EXCEL_IMPORT_AMOUNT,
            cls.EXCEL_TRADE_BALANCE
        ]
    
    @classmethod
    def get_header_columns(cls) -> List[str]:
        """헤더 검증용 컬럼"""
        return [cls.EXCEL_PERIOD, cls.EXCEL_COUNTRY]
    
    @classmethod
    def get_output_columns(cls) -> List[str]:
        """출력용 컬럼 순서"""
        return [
            cls.DB_YEAR,
            cls.DB_NATION_CODE,
            cls.DB_NATION_NAME,
            cls.DB_EXPORT_MONEY,
            cls.DB_IMPORT_MONEY,
            cls.DB_TRADE_BALANCE
        ]
    
    @classmethod
    def validate_excel_columns(cls, df_columns: List[str]) -> List[str]:
        """엑셀 컬럼 검증 - 누락된 필수 컬럼 반환"""
        required = cls.get_required_excel_columns()
        return [col for col in required if col not in df_columns]
    
    @classmethod
    def get_sort_columns(cls) -> List[str]:
        """정렬용 컬럼"""
        return [cls.DB_YEAR, cls.DB_NATION_NAME]
    
    @classmethod
    def get_final_column_mapping(cls) -> Dict[str, str]:
        """최종 컬럼 매핑 (엑셀 -> DB)"""
        return {
            cls.EXCEL_PERIOD: cls.DB_YEAR,
            cls.TEMP_ISO_CODE: cls.DB_NATION_CODE,
            cls.EXCEL_COUNTRY: cls.DB_NATION_NAME,
            cls.EXCEL_EXPORT_AMOUNT: cls.DB_EXPORT_MONEY,
            cls.EXCEL_IMPORT_AMOUNT: cls.DB_IMPORT_MONEY,
            cls.EXCEL_TRADE_BALANCE: cls.DB_TRADE_BALANCE
        }
    
# 싱글톤 인스턴스 (편의를 위해)
CONFIG = CustomsCountryConfig()