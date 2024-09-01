from sqlalchemy import Column, ForeignKey, Integer
from clickhouse_sqlalchemy import types, engines
from src.database.db import Base
from src.common.constants.enum_constant import PhoneType, Gender, YesNo, YesNoUnknown
from sqlalchemy.orm import relationship

class Client(Base):
    __tablename__ = 'clients'
    __table_args__ = (
        engines.ReplacingMergeTree(
            order_by='client_id_manifest',
            version='version'
        ),
    )

    client_id_manifest = Column(types.String, primary_key=True)  # Original key: "sec_c/cd_client_id_manifest"
    unique_id = Column(
        types.String, primary_key=True
    )  # Original key: "sec_a/unique_id"
    name = Column(types.String, nullable=True)                                  # Original key: "sec_c/cd_client_name"
    phone = Column(types.String, nullable=True)                                 # Original key: "sec_c/cd_clients_phone"
    alternate_phone = Column(types.String, nullable=True)                       # Original key: "sec_c/cd_phoneno_alt_number"
    phone_type = Column(types.Enum(PhoneType), nullable=True)                   # Original key: "sec_c/cd_clients_phone_smart_feature"
    gender = Column(types.Enum(Gender), nullable=True)                          # Original key: "sec_c/cd_gender"
    age = Column(types.Int, nullable=True)                                  # Original key: "sec_c/cd_age"
    nationality = Column(types.String, nullable=True)                           # Original key: "sec_c/cd_nationality"
    strata = Column(types.String, nullable=True)                                # Original key: "sec_c/cd_strata"
    disability = Column(types.Enum(YesNo), nullable=True)           # Original key: "sec_c/cd_disability"
    education = Column(types.String, nullable=True)                             # Original key: "sec_c/cd_education"
    status = Column(types.String, nullable=True)                                # Original key: "sec_c/cd_client_status"
    sole_income_earner = Column(types.Enum(YesNo), nullable=True)   # Original key: "sec_c/cd_sole_income_earner"
    responsible_for_people = Column(types.Int, nullable=True)               # Original key: "sec_c/cd_howrespble_pple"
    last_updated = Column(types.DateTime, nullable=False)
    version = Column(types.UInt32, nullable=False)                        # New field for update tracking

    surveys = relationship("Survey", back_populates="client")
    