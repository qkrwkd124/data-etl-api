"""EIU 데이터 관련 상수 및 타입"""

from enum import Enum
from typing import Dict, List

class EIUDataType(str, Enum):
    """EIU 데이터 타입 구분"""
    ACTUAL = "ACT"      # 실제 데이터
    ESTIMATE = "EST"    # 예측 데이터  
    FORECAST = "FOR"    # 미래 데이터
    UNKNOWN = "?"       # 알수 없는 데이터
    MISSING = "–"       # 누락 데이터 (EIU 특유의 대시 표기)

# EIU 코드
EIU_CODES: List[str] = [
    "PSBR", "DCPI", "CARA", "BALC", "XRPD", "XPP1", "XPP2", "XPP3", "XPP4", 
    "FRES", "MEXP", "MIMP", "MPP1", "MPP2", "MPP3", "PUDP", "DGDP", "TDPY", "BALM"
]

# EIU 컬럼 매핑
EIU_COLUMN_MAPPING: Dict[str, str] = {
    "Series": "series",
    "Code": "code", 
    "Currency": "currency",
    "Units": "units",
    "Source": "source",
    "Definition": "definition", 
    "Note": "note",
    "Published": "published"
}

# EIU 색상 코드 (예측 데이터 식별용)
EIU_ESTIMATE_COLOR = "0000588D"