from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from app.core.config import settings

# 데이터베이스 디렉토리 존재하는지 확인
db_path = settings.database_url.replace("sqlite:///", "")
os.makedirs(os.path.dirname(db_path), exist_ok=True)

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ErrorLog(Base):
    __tablename__ = "errors"

    id = Column(String, primary_key=True)
    case_name = Column(Text, nullable=False)
    command = Column(Text, nullable=False)
    error_log = Column(Text, nullable=False)
    code_snippet = Column(Text)
    file_path = Column(Text)
    line_number = Column(Integer)
    ai_solution = Column(Text)
    root_cause = Column(Text)
    tags = Column(Text)  # JSON 문자열
    created_at = Column(DateTime, default=datetime.utcnow)
    vector_id = Column(String)


def init_db():
    """데이터베이스 테이블 초기화"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """데이터베이스 세션을 가져오는 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
