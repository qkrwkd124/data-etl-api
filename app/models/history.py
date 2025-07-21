from sqlalchemy import Column, Integer, String, DateTime, Text, BigInteger, Numeric
from app.db.base import Base

class DataUploadAutoHistory(Base):
    """데이터 업로드 자동화 처리 이력 테이블"""
    __tablename__ = "tb_bpc220"

    file_seq = Column(Numeric(10), primary_key=True, comment="파일순번")
    data_wrk_nm = Column(String(400), primary_key=True, comment="데이터작업명")
    strt_dtm = Column(DateTime, comment="시작일시")
    end_dtm = Column(DateTime, comment="종료일시")
    fin_yn = Column(String(1), comment="완료여부")
    rmk_ctnt = Column(String(4000), comment="비고내용")
    file_nm = Column(String(1500), comment="파일명")
    file_path_nm = Column(String(200), comment="파일경로명")
    file_exts_nm = Column(String(50), comment="파일연장명")
    file_size = Column(String(10), comment="파일크기")
    file_sort_ord = Column(Numeric(5), comment="파일정렬순서")
    scr_file_nm = Column(String(1500), comment="화면파일명")
    rslt_tab_nm = Column(String(200), comment="결과테이블명")
    proc_cnt = Column(Numeric(15), comment="처리건수")
    reg_usr_id = Column(String(10), nullable=False, comment="등록사용자ID")
    reg_dtm = Column(DateTime, nullable=False, comment="등록일시")
    mod_usr_id = Column(String(10), nullable=False, comment="수정사용자ID")
    mod_dtm = Column(DateTime, nullable=False, comment="수정일시")


    