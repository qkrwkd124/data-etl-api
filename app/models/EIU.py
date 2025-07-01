from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
from typing import Optional
from app.schemas.eiu_schemas import EIUDataType
class EconomicData(Base):
    """경제 데이터 모델 - EIU 데이터 저장"""
    __tablename__ = "tb_rhr100"

    eiu_cont_en_nm = Column(String(200), index=True, comment="EIU국가영문명")
    eiu_country_code = Column(String(2), primary_key=True, index=True, comment="EIU국가코드")
    eiu_currency = Column(String(10), comment="EIU통화명")
    eiu_series_title = Column(String(350), comment="EIU시리즈제목")
    eiu_code = Column(String(50), primary_key=True, index=True, comment="EIU코드")
    eiu_units = Column(String(30), nullable=True, comment="EIU단위")
    # 연도별 데이터 (19년부터 51년까지)
    eiu_year1 = Column(String(300), nullable=True, default=EIUDataType.UNKNOWN.value,comment="2001년")
    eiu_year2 = Column(String(300), nullable=True, default=EIUDataType.UNKNOWN.value,comment="2002년")
    eiu_year3 = Column(String(300), nullable=True, default=EIUDataType.UNKNOWN.value,comment="2003년")
    eiu_year4 = Column(String(300), nullable=True, default=EIUDataType.UNKNOWN.value,comment="2004년")
    eiu_year5 = Column(String(300), nullable=True, default=EIUDataType.UNKNOWN.value,comment="2005년")
    eiu_year6 = Column(String(300), nullable=True, default=EIUDataType.UNKNOWN.value,comment="2006년")
    eiu_year7 = Column(String(300), nullable=True, default=EIUDataType.UNKNOWN.value,comment="2007년")
    eiu_year8 = Column(String(300), nullable=True, default=EIUDataType.UNKNOWN.value,comment="2008년")
    eiu_year9 = Column(String(300), nullable=True, default=EIUDataType.UNKNOWN.value,comment="2009년")
    eiu_year10 = Column(String(300), nullable=True, default=EIUDataType.UNKNOWN.value,comment="2010년")
    eiu_year11 = Column(String(300), nullable=True, default=EIUDataType.UNKNOWN.value,comment="2011년")
    eiu_year12 = Column(String(300), nullable=True, default=EIUDataType.UNKNOWN.value,comment="2012년")
    eiu_year13 = Column(String(300), nullable=True, default=EIUDataType.UNKNOWN.value,comment="2013년")
    eiu_year14 = Column(String(300), nullable=True, default=EIUDataType.UNKNOWN.value,comment="2014년")
    eiu_year15 = Column(String(300), nullable=True, default=EIUDataType.UNKNOWN.value,comment="2015년")
    eiu_year16 = Column(String(300), nullable=True, default=EIUDataType.UNKNOWN.value,comment="2016년")
    eiu_year17 = Column(String(300), nullable=True, default=EIUDataType.UNKNOWN.value,comment="2017년")
    eiu_year18 = Column(String(300), nullable=True, default=EIUDataType.UNKNOWN.value,comment="2018년")
    eiu_year19 = Column(String(300), nullable=True, default=EIUDataType.UNKNOWN.value,comment ="2019년")
    eiu_year20 = Column(String(300), nullable=True, default=EIUDataType.UNKNOWN.value,comment="2020년")
    eiu_year21 = Column(String(300), nullable=True, default=EIUDataType.UNKNOWN.value,comment="2021년")
    eiu_year22 = Column(String(300), nullable=True, comment="2022년")
    eiu_year23 = Column(String(300), nullable=True, comment="2023년")
    eiu_year24 = Column(String(300), nullable=True, comment="2024년")
    eiu_year25 = Column(String(300), nullable=True, comment="2025년")
    eiu_year26 = Column(String(300), nullable=True, comment="2026년")
    eiu_year27 = Column(String(300), nullable=True, comment="2027년")
    eiu_year28 = Column(String(300), nullable=True, comment="2028년")
    eiu_year29 = Column(String(300), nullable=True, comment="2029년")
    eiu_year30 = Column(String(300), nullable=True, comment="2030년")
    eiu_year31 = Column(String(300), nullable=True, comment="2031년")
    eiu_year32 = Column(String(300), nullable=True, comment="2032년")
    eiu_year33 = Column(String(300), nullable=True, comment="2033년")
    eiu_year34 = Column(String(300), nullable=True, comment="2034년")
    eiu_year35 = Column(String(300), nullable=True, comment="2035년")
    eiu_year36 = Column(String(300), nullable=True, comment="2036년")
    eiu_year37 = Column(String(300), nullable=True, comment="2037년")
    eiu_year38 = Column(String(300), nullable=True, comment="2038년")
    eiu_year39 = Column(String(300), nullable=True, comment="2039년")
    eiu_year40 = Column(String(300), nullable=True, comment="2040년")
    eiu_year41 = Column(String(300), nullable=True, comment="2041년")
    eiu_year42 = Column(String(300), nullable=True, comment="2042년")
    eiu_year43 = Column(String(300), nullable=True, comment="2043년")
    eiu_year44 = Column(String(300), nullable=True, comment="2044년")
    eiu_year45 = Column(String(300), nullable=True, comment="2045년")
    eiu_year46 = Column(String(300), nullable=True, comment="2046년")
    eiu_year47 = Column(String(300), nullable=True, comment="2047년")
    eiu_year48 = Column(String(300), nullable=True, comment="2048년")
    eiu_year49 = Column(String(300), nullable=True, comment="2049년")
    eiu_year50 = Column(String(300), nullable=True, comment="2050년")
    eiu_year51 = Column(String(300), nullable=True, comment="2051년")
    created_at = Column(DateTime, default=datetime.now, comment="생성일")
    updated_at = Column(DateTime, default=datetime.now, comment="수정일")

class MajorTradePartner(Base):
    __tablename__ = "tb_rhr150"

    cont_code = Column(String(3), primary_key=True, comment="국가코드")
    cont_nm = Column(String(150), comment="국가명")
    maj_imp_cont_nm = Column(String(150), comment="주요수입국가명")
    imp_rate = Column(String(10), comment="수입비율")
    maj_exp_cont_nm = Column(String(150), comment="주요수출국가명")
    exp_rate = Column(String(10), comment="수출비율")


class EIU_PARTNER_ISO(Base):
    __tablename__ = "tb_rhr350"

    eng_ctry_nm = Column(String(200), primary_key=True, nullable=True, comment="영문국가명")
    std_infrm_ctry_cd = Column(String(2), primary_key=True, nullable=True, comment="표준약식국가코드")
