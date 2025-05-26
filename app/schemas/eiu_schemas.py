from pydantic import BaseModel, Field, field_validator
from enum import Enum
from typing import Optional, Dict, Any, List

CODES = ["PSBR", "DCPI", "CARA", "BALC", "XRPD", "XPP1", "XPP2", "XPP3", "XPP4", "FRES", "MEXP", "MIMP", "MPP1","MPP2", "MPP3","PUDP","DGDP","TDPY","BALM"]

class DataType(str, Enum):
    """데이터 타입 구분"""
    ACTUAL = "ACT"      # 실제 데이터
    ESTIMATE = "EST"    # 예측 데이터
    FORECAST = "FOR"    # 미래 데이터
    UNKNOWN = "?"       # 알수 없는 데이터터
    MISSING = "–"       # 누락 데이터
    

    
class ProcessedYearData(BaseModel):
    """처리된 연도별 데이터"""
    year: str = Field(..., description="연도")
    value: Optional[str] = Field(None, description="원본 값")
    data_type: DataType = Field(..., description="데이터 타입")
    processed_value: Optional[str] = Field(default=None, description="처리된 값 (타입|값)")
    
    
    @field_validator('processed_value',mode='after')
    def create_processed_value(cls, v, info):
        # processed_value가 명시적으로 주어진 경우 우선 사용
        # if v is not None:
        #     return v

        data = info.data
        data_type = data.get('data_type')
        value = data.get('value')

        if value and value != DataType.MISSING.value:
            return f"{data_type.value}|{value}"
        return DataType.MISSING.value
    
class ExcelRowData(BaseModel):
    """Excel에서 읽어온 원본 행 데이터"""
    country_code: str = Field(..., description="국가 코드")
    series: Optional[str] = Field(None, description="시리즈명")
    code: Optional[str] = Field(None, description="데이터 코드")
    currency: Optional[str] = Field(None, description="통화")
    units: Optional[str] = Field(None, description="단위")
    source: Optional[str] = Field(None, description="출처")
    definition: Optional[str] = Field(None, description="정의")
    note: Optional[str] = Field(None, description="노트")
    published: Optional[str] = Field(None, description="발행일")
    year_data: Dict[str, Any] = Field(default_factory=dict, description="연도별 데이터")
    
    # @field_validator('code')
    # def validate_code(cls, v):
    #     if v and v not in CODES:
    #         raise ValueError(f"지원하지 않는 코드: {v}")
    #     return v
    
class ProcessedExcelRow(BaseModel):
    """가공된 Excel 행 데이터"""
    country_code: str
    series_title: Optional[str] = None
    code: str
    currency: Optional[str] = None
    units: Optional[str] = None
    year_data: List[Any] = Field(default_factory=list)
    
    def to_dict_format(self) -> Dict[str, Any]:
        """DataFrame 형식으로 변환"""
        result = {
            "eiu_country_code": self.country_code,
            "eiu_series_title": self.series_title,
            "eiu_code": self.code,
            "eiu_currency": self.currency,
            "eiu_units": self.units
        }
        
        # 연도 데이터 추가
        for year_data in self.year_data:
            year_num = int(year_data.year) % 100
            result[f"eiu_year{year_num}"] = year_data.processed_value
            
        return result

class ProcessingResult(BaseModel):
    """처리 결과"""
    total_sheets: int
    total_rows: int
    success_count: int
    error_messages: list = []
    error_count: int = 0

    def add_error(self, message: str):
        """에러 추가"""
        self.error_messages.append(message)
        self.error_count += 1
        
    def add_success(self):
        """성공 카운트 증가"""
        self.success_count += 1