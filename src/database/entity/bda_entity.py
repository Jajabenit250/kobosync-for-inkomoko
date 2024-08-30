from sqlalchemy import Column
from clickhouse_sqlalchemy import types, engines
from src.database.db import Base

class BusinessDevelopmentAdvisor(Base):
    __tablename__ = "business_development_advisors"

    bda_id = Column(types.UInt32, primary_key=True)
    name = Column(types.String)
    country_id = Column(types.UInt16)
    region_id = Column(types.UInt16)

    __table_args__ = (
        engines.MergeTree(order_by=['bda_id']),
    )
    