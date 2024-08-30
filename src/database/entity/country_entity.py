from sqlalchemy import Column
from clickhouse_sqlalchemy import types, engines
from src.database.db import Base

class Country(Base):
    __tablename__ = "countries"

    country_id = Column(types.UInt16, primary_key=True)
    name = Column(types.String)

    __table_args__ = (
        engines.MergeTree(order_by=['country_id']),
    )
    