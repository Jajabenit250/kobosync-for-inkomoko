from sqlalchemy import Column
from clickhouse_sqlalchemy import types, engines
from src.database.db import Base

class Region(Base):
    __tablename__ = "regions"

    region_id = Column(types.UInt16, primary_key=True)
    country_id = Column(types.UInt16)
    name = Column(types.String)

    __table_args__ = (
        engines.MergeTree(order_by=['country_id', 'region_id']),
    )