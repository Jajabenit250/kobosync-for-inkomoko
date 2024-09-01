from sqlalchemy import create_engine, MetaData
from clickhouse_sqlalchemy import make_session, get_declarative_base
from src.common.utils.config import config

engine = create_engine(config.CLICKHOUSE_URL)
metadata = MetaData()
metadata.bind = engine  # This is the new way to bind metadata to an engine

Base = get_declarative_base(metadata=metadata)
SessionLocal = make_session(engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal
    try:
        yield db
    finally:
        db.close()
