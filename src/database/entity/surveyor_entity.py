from clickhouse_sqlalchemy import types, engines
from sqlalchemy import Column
from src.database.db import Base
from sqlalchemy.orm import relationship


class Surveyor(Base):
    __tablename__ = "surveyors"
    __table_args__ = (
        engines.ReplacingMergeTree(
            order_by=('surveyor_id'),
            partition_by=None,
            primary_key=('surveyor_id')
        ),
    )

    surveyor_id = Column(
        types.String, primary_key=True
    )  # Composite key: bda_name + cohort + program
    name = Column(types.String)  # Original key: "sec_b/bda_name"
    cohort = Column(types.String)  # Original key: "sec_b/cd_cohort"
    program = Column(types.String)  # Original key: "sec_b/cd_program"

    surveys = relationship("Survey", back_populates="surveyor")
