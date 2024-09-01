# conftest.py
import pytest
from clickhouse_sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base

@pytest.fixture(scope="session")
def engine():
    return create_engine("clickhouse://localhost")

@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def dbsession(engine, tables):
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()
    