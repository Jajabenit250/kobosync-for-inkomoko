from sqlalchemy import Column
from clickhouse_sqlalchemy import types, engines
from src.database.db import Base

class Nationality(Base):
    __tablename__ = "nationalities"

    nationality_id = Column(types.UInt16, primary_key=True)
    name = Column(types.String)

    __table_args__ = (
        engines.MergeTree(order_by=['nationality_id']),
    )
    