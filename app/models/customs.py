from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Index
from app.db.base import Base
from datetime import datetime


class ExportImportStatByCountry(Base):
    __tablename__ = "export_import_stat_by_country"

    __table_args__ = {
        "comment": "관세청 주요 수출/수입량",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci"
    }

    impexp_year = Column(String(4), primary_key=True, comment="수출입연도")
    impexp_nation_code = Column(String(2), primary_key=True, comment="수출입국가코드")
    impexp_nation_nm = Column(String(150), comment="수출입국가명")
    impexp_exp_money = Column(String(30), comment="수출금액")
    impexp_imp_money = Column(String(30), comment="수입금액")
    impexp_trade_rate_money = Column(String(30), comment="무역수지")

class ExportImportItemByCountry(Base):
    __tablename__ = "export_import_item_by_country"

    __table_args__ = {
        "comment": "관세청 주요 수출/수입국",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci"
    }

    impexp_year = Column(String(4), primary_key=True, comment="수출입연도")
    impexp_flag = Column(String(10), primary_key=True, comment="수출입구분")
    impexp_nation_code = Column(String(2), primary_key=True, comment="수출입국가코드")
    impexp_nation_nm = Column(String(150), primary_key=True, comment="수출입국가명")
    impexp_item_nm = Column(String(150), primary_key=True, comment="수출입품명")
    impexp_item_weight = Column(String(150), comment="수출입품무게")
    impexp_item_money = Column(String(150), comment="수출입품금액")
