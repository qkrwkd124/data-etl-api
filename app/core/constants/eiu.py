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

EIU_CODES:Dict[str, str] = {
    "PSBR": "Budget balance (% of GDP)",
    "DCPI": "Consumer prices (% change pa; av)",
    "CARA": "Current-account balance (% of GDP)",
    "BALC": "Current-account balance (US$)",
    "XRPD": "Exchange rate LCU:US$ (av)",
    "XPP1": "Export 1 (% share)",
    "XPP2": "Export 2 (% share)",
    "XPP3": "Export 3 (% share)",
    "XPP4": "Export 4 (% share)",
    "FRES": "Foreign-exchange reserves (US$)",
    "MEXP": "Goods: exports BOP (US$)",
    "MIMP": "Goods: imports BOP (US$)",
    "MPP1": "Import 1 (% share)",
    "MPP2": "Import 2 (% share)",
    "MPP3": "Import 3 (% share)",
    "PUDP": "Public debt  (% of GDP)",
    "DGDP": "Real GDP (% change pa)",
    "TDPY": "Total debt/GDP (%)",
    "BALM": "Trade balance (US$)",
}

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