from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Index
from app.db.base import Base
from datetime import datetime


class EconomicFreedomIndex(Base):
    __tablename__ = "tb_rhr090"

    __table_args__ = {
        "comment": "경제자유화지수",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci"
    }

    cont_code = Column(String(2), primary_key=True, comment="국가코드")
    cont_en_nm = Column(String(200), comment="국가영문명")
    eco_lib_rank = Column(BigInteger, comment="경제자유도순위")
    

class CorruptionPerceptionIndex(Base):
    __tablename__ = "tb_rhr080"

    __table_args__ = {
        "comment": "부패인식지수",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci"
    }

    cont_code = Column(String(2), primary_key=True, comment="국가코드")
    cont_en_nm = Column(String(200), comment="국가영문명")
    corr_perc_rank = Column(BigInteger, comment="부패인식순위")

class HumanDevelopmentIndex(Base):
    __tablename__ = "tb_rhr110"

    __table_args__ = {
        "comment": "인간개발지수",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci"
    }

    cont_code = Column(String(2), primary_key=True, comment="국가코드")
    cont_en_nm = Column(String(200), comment="국가영문명")
    hdi_rank = Column(BigInteger, comment="인간개발순위")

class WorldCompetitivenessIndex(Base):
    __tablename__ = "tb_rhr360"

    __table_args__ = {
        "comment": "세계경쟁력지수",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci"
    }

    cont_code = Column(String(2), primary_key=True, comment="국가코드")
    cont_en_nm = Column(String(200), comment="국가영문명")
    wcr_rank = Column(BigInteger, comment="세계경쟁력순위")
    
    
    