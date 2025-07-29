from typing import Dict, List, Optional, Union
from dataclasses import dataclass



# 경제자유화지수
@dataclass(frozen=True)
class EconomicFreedomIndexConfig:

    # CSV 원본 컬럼명
    EXCEL_PERIOD: str = "Index Year"
    EXCEL_COUNTRY: str = "Country"
    EXCEL_SCORE: str = "Overall Score"

    # 임시 컬럼 (변환 과정에서 생성)
    TEMP_ISO_CODE: str = "ISO코드"

    # DB 컬럼명
    DB_ISO: str = "cont_code"
    DB_COUNTRY: str = "cont_en_nm"
    DB_RANK: str = "eco_lib_rank"

    SKIP_ROWS = 4

    @classmethod
    def get_required_csv_columns(cls) -> List[str]:
        return [cls.EXCEL_COUNTRY, cls.EXCEL_SCORE]
    
    @classmethod
    def get_final_column_mapping(cls) -> Dict[str, str]:
        return {
            cls.TEMP_ISO_CODE: cls.DB_ISO,
            cls.EXCEL_COUNTRY: cls.DB_COUNTRY,
            cls.EXCEL_SCORE: cls.DB_RANK
        }
    
    @classmethod
    def get_sort_columns(cls) -> List[str]:
        return [cls.DB_RANK]

# 부패인식지수
@dataclass(frozen=True)
class CorruptionPerceptionIndexConfig:

    # 엑셀 원본 컬럼명
    EXCEL_COUNTRY:str = "Country / Territory"
    EXCEL_ISO3:str = "ISO3"
    EXCEL_REGION:str = "Region"
    EXCEL_RANK:str = "Rank"

    # TEMP_ISO_CODE
    TEMP_ISO_CODE: str = "ISO코드"

    # DB 컬럼명
    DB_ISO: str = "cont_code"
    DB_ENG_NM: str = "cont_en_nm"
    DB_RANK: str = "corr_perc_rank"


    @classmethod
    def get_header_columns(cls) -> List[str]:
        """헤더 검증용 컬럼"""
        return [cls.EXCEL_COUNTRY, cls.EXCEL_ISO3, cls.EXCEL_REGION]
    
    @classmethod
    def get_required_csv_columns(cls) -> List[str]:
        return [cls.EXCEL_COUNTRY, cls.EXCEL_RANK]
    
    @classmethod
    def get_final_column_mapping(cls) -> Dict[str, str]:
        return {
            cls.TEMP_ISO_CODE: cls.DB_ISO,
            cls.EXCEL_COUNTRY: cls.DB_ENG_NM,
            cls.EXCEL_RANK: cls.DB_RANK
        }
    
    @classmethod
    def get_sort_columns(cls) -> List[str]:
        return [cls.DB_RANK]
    
# 인간개발지수
@dataclass(frozen=True)
class HumanDevelopmentIndexConfig:

    # 엑셀 원본 컬럼명
    EXCEL_RANK:str = "HDI rank"
    EXCEL_COUNTRY:str = "Country"

    # 임시 컬럼 (변환 과정에서 생성)
    TEMP_ISO_CODE: str = "ISO코드"

    # DB 컬럼명
    DB_ISO: str = "cont_code"
    DB_ENG_NM: str = "cont_en_nm"
    DB_RANK: str = "hdi_rank"

    @classmethod
    def get_header_columns(cls) -> List[str]:
        """헤더 검증용 컬럼"""
        return [cls.EXCEL_RANK, cls.EXCEL_COUNTRY]
    
    @classmethod
    def get_required_csv_columns(cls) -> List[str]:
        return [cls.EXCEL_RANK, cls.EXCEL_COUNTRY]
    
    @classmethod
    def get_final_column_mapping(cls) -> Dict[str, str]:
        return {
            cls.TEMP_ISO_CODE: cls.DB_ISO,
            cls.EXCEL_COUNTRY: cls.DB_ENG_NM,
            cls.EXCEL_RANK: cls.DB_RANK
        }
    
    @classmethod
    def get_sort_columns(cls) -> List[str]:
        return [cls.DB_RANK]

# 세계경쟁력지수
@dataclass(frozen=True)
class WorldCompetitivenessIndexConfig:
    
    # 엑셀 원본 컬럼명
    EXCEL_RANK:str = "WCR"
    EXCEL_COUNTRY:str = "Country"
    EXCEL_ISO:str = "국가코드"

    # 임시 컬럼 (변환 과정에서 생성)
    TEMP_ISO_CODE: str = "ISO코드"

    # DB 컬럼명
    DB_ISO: str = "cont_code"
    DB_ENG_NM: str = "cont_en_nm"
    DB_RANK: str = "wcr_rank"
    
    @classmethod
    def get_header_columns(cls) -> List[str]:
        """헤더 검증용 컬럼"""
        return [cls.EXCEL_RANK, cls.EXCEL_COUNTRY, cls.EXCEL_ISO]
    
    @classmethod
    def get_required_csv_columns(cls) -> List[str]:
        return [cls.EXCEL_RANK, cls.EXCEL_ISO]
    
    @classmethod
    def get_final_column_mapping(cls) -> Dict[str, str]:
        return {
            cls.EXCEL_ISO: cls.DB_ISO,
            cls.EXCEL_COUNTRY: cls.DB_ENG_NM,
            cls.EXCEL_RANK: cls.DB_RANK
        }
    
    @classmethod
    def get_sort_columns(cls) -> List[str]:
        return [cls.DB_RANK]


SocioeconomicConfigType = Union[
    EconomicFreedomIndexConfig,
    CorruptionPerceptionIndexConfig,
    HumanDevelopmentIndexConfig,
    WorldCompetitivenessIndexConfig
]
