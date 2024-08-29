from datetime import date, datetime
from typing import Optional
from pydantic import UUID4, Field
from src.database.common_model import CommonModel
from src.common.constants.enum_constant import SurveyStatus


class Survey(CommonModel):
    id: UUID4 = Field(index=True, unique=True)
    survey_id: int = Field(primary_key=True)
    form_uuid: UUID4
    start_time: datetime
    end_time: datetime
    survey_date: date = Field(index=True)
    unique_id: str
    bda_id: int = Field(index=True)
    client_id: int = Field(index=True)
    business_id: int = Field(index=True)
    cohort_id: int = Field(index=True)
    program_id: int = Field(index=True)
    submission_time: datetime
    version: str = Field(alias='_version')
    instance_id: UUID4
    xform_id_string: str
    status: SurveyStatus
    latitude: Optional[float] = None
    longitude: Optional[float] = None