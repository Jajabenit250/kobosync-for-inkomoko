from sqlalchemy import Column
from clickhouse_sqlalchemy import types, engines
from src.database.db import Base
from src.common.constants.enum_constant import SurveyStatus

class Survey(Base):
    __tablename__ = "surveys"

    survey_id = Column(types.UUID, primary_key=True)
    form_uuid = Column(types.UUID)
    start_time = Column(types.DateTime)
    end_time = Column(types.DateTime)
    survey_date = Column(types.Date)
    unique_id = Column(types.String)
    bda_id = Column(types.UInt32)
    client_id = Column(types.UInt32)
    business_id = Column(types.UInt32)
    cohort_id = Column(types.UInt16)
    program_id = Column(types.UInt16)
    submission_time = Column(types.DateTime)
    _version = Column(types.String)
    xform_id_string = Column(types.String)
    status = Column(types.Enum(SurveyStatus))
    latitude = Column(types.Float64, nullable=True)
    longitude = Column(types.Float64, nullable=True)

    __table_args__ = (
        engines.MergeTree(
            order_by=['survey_date', 'start_time', 'survey_id'],
            partition_by=['survey_date']
        ),
    )
    