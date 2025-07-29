"""SQLAlchemy 기반 비동기 데이터베이스 연결 관리.

이중 데이터베이스 연결을 지원하며 비동기 세션 관리를 제공합니다.
FastAPI의 의존성 주입 시스템과 연동됩니다.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.setting import get_settings

settings = get_settings()

engines = {
    "main": create_async_engine(
        url=settings.DATABASE,  # 데이터베이스 연결 URL, 설정 파일에서 가져옴
        echo=False,  # SQL 쿼리 로깅 비활성화 (True로 설정 시 모든 SQL 쿼리가 콘솔에 출력됨)
        future=True  # SQLAlchemy 2.0 스타일의 실행을 활성화 (SQLAlchemy 1.4 이상에서 권장)
    ),
}

# 각 데이터베이스별 세션 팩토리
session_factories = {
    db_name: sessionmaker(
        engine, #세션이 사용할 데이터베이스 엔진입니다.
        class_=AsyncSession, #생성될 세션의 클래스입니다. 여기서는 비동기 작업을 위해 AsyncSession을 사용합니다.
        expire_on_commit=False, #커밋 시 세션에 연결된 모든 인스턴스를 만료시킬지 여부입니다. False로 설정하면 커밋 후에도 객체에 접근할 수 있습니다.
        autocommit=False, #트랜잭션을 자동으로 커밋할지 여부입니다. False는 수동 커밋이 필요함을 의미합니다.
        autoflush=False #쿼리 실행 전에 보류 중인 변경 사항을 데이터베이스에 자동으로 플러시할지 여부입니다. False는 수동 플러시가 필요함을 의미합니다.
    )
    for db_name, engine in engines.items()
}

# Base 클래스 선언 - 모든 모델 클래스의 기본 클래스
Base = declarative_base()

# 데이터베이스 세션 가져오기
async def get_main_db() -> AsyncSession:
    """
    비동기 데이터베이스 세션을 반환하는 의존성 함수
    """
    async with session_factories["main"]() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()