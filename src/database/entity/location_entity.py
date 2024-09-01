from sqlalchemy import Column, String
from src.database.db import Base
from clickhouse_sqlalchemy import types, engines
from sqlalchemy.orm import relationship

class Location(Base):
    __tablename__ = 'locations'
    __table_args__ = (
        engines.ReplacingMergeTree(order_by=('location_id',)),
    )

    location_id = Column(types.String, primary_key=True)  # Composite key derived from sec_a fields
    country = Column(types.String)                        # Original key: "sec_a/cd_biz_country_name"
    region = Column(types.String)                         # Original key: "sec_a/cd_biz_region_name"
    specific_location = Column(types.String)              # Original key: "sec_c/cd_location"

    surveys = relationship("Survey", back_populates="location")
