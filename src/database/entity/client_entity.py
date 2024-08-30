from sqlalchemy import Column
from clickhouse_sqlalchemy import types, engines
from src.database.db import Base
from src.common.constants.enum_constant import PhoneType, Gender, ClientStatus

class Client(Base):
    __tablename__ = "clients"

    client_id = Column(types.UInt32, primary_key=True)
    name = Column(types.String)
    id_manifest = Column(types.String)
    location = Column(types.String)
    phone_primary = Column(types.String)
    phone_secondary = Column(types.String)
    phone_type = Column(types.Enum(PhoneType))
    gender = Column(types.Enum(Gender))
    age = Column(types.UInt8)
    nationality_id = Column(types.UInt16)
    strata = Column(types.String)
    has_disability = Column(types.UInt8)
    education_level_id = Column(types.UInt8)
    client_status = Column(types.Enum(ClientStatus))
    is_sole_income_earner = Column(types.UInt8)
    dependents = Column(types.UInt8)

    __table_args__ = (
        engines.MergeTree(order_by=['client_id', 'name']),
    )
    