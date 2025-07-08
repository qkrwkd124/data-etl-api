from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Index
from app.db.base import Base
from datetime import datetime


class ExportImportStatByCountry(Base):
    __tablename__ = "tb_rhr140"

    impexp_year = Column(String(4), primary_key=True, comment="수출입연도")
    impexp_nation_code = Column(String(2), primary_key=True, comment="수출입국가코드")
    impexp_nation_nm = Column(String(150), comment="수출입국가명")
    impexp_exp_money = Column(String(30), comment="수출금액")
    impexp_imp_money = Column(String(30), comment="수입금액")
    impexp_trade_rate_money = Column(String(30), comment="무역수지")

# class CountryMapping(Base):
#     __tablename__ = "tb_rhr160"

#     iso_code = Column(String(4), primary_key=True, comment="ISO코드")
#     nation_nm = Column(String(200), comment="국가명")
#     trgtpsn_no = Column(String(30), comment="대상자번호")

# class KoreaCountryMapping(Base):
#     __tablename__ = "tb_rhr350"

#     eng_ctry_nm = Column(String(200), primary_key=True, nullable=True, comment="영문국가명")
#     std_infrm_ctry_cd = Column(String(2), primary_key=True, nullable=True, comment="표준약식국가코드")
#     kcs_kor_ctry_nm = Column(String(100), comment="관세청한글국가명")