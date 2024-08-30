from sqlalchemy import Column
from clickhouse_sqlalchemy import types, engines
from src.database.db import Base
from src.common.constants.enum_constant import BusinessStatus, IsOperating

class Business(Base):
    __tablename__ = "businesses"

    business_id = Column(types.UInt32, primary_key=True)
    client_id = Column(types.UInt32)
    status = Column(types.Enum(BusinessStatus))
    is_operating = Column(types.Enum(IsOperating))

    __table_args__ = (
        engines.MergeTree(order_by=['business_id', 'client_id']),
    )