from sqlalchemy import Column, Integer, String, DateTime, Text, BigInteger, Numeric
from app.db.base import Base

class DataUploadAutoHistory(Base):
    """데이터 업로드 자동화 처리 이력 테이블"""
    __tablename__ = "tb_bpc220"

    data_wrk_no = Column(Numeric(10), primary_key=True, comment="데이터작업번호")
    data_wrk_nm = Column(String(400), primary_key=True, nullable=False, comment="데이터작업명")
    strt_dtm = Column(DateTime, comment="시작일시")
    end_dtm = Column(DateTime, comment="종료일시")
    fin_yn = Column(String(1), comment="완료여부")
    rmk_ctnt = Column(String(4000), comment="비고내용")
    refl_file_nm = Column(String(300), comment="반영파일명")
    scr_file_nm = Column(String(1500), comment="화면파일명")
    rslt_tab_nm = Column(String(200), comment="결과테이블명")
    proc_cnt = Column(Numeric(15), comment="처리건수")
    reg_usr_id = Column(String(10), nullable=False, comment="등록사용자ID")
    reg_dtm = Column(DateTime, nullable=False, comment="등록일시")
    mod_usr_id = Column(String(10), nullable=False, comment="수정사용자ID")
    mod_dtm = Column(DateTime, nullable=False, comment="수정일시")


    