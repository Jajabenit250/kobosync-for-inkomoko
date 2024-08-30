from sqlalchemy import Column
from clickhouse_sqlalchemy import types, engines
from src.database.db import Base

class EducationLevel(Base):
    __tablename__ = "education_levels"

    education_level_id = Column(types.UInt8, primary_key=True)
    description = Column(types.String)

    __table_args__ = (
        engines.MergeTree(order_by=['education_level_id']),
    )
    