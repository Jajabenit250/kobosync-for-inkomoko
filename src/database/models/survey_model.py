from pydantic import BaseModel
from datetime import datetime

class Survey(BaseModel):
    survey_id: str
    form_uuid: str
    start_time: datetime
    end_time: datetime
    survey_date: datetime
    unique_id: str
    bda_id: str
    client_id: str
    business_id: str
    cohort_id: str
    program_id: str
    submission_time: datetime
    _version: str
    xform_id_string: str
    status: str

    class Config:
        orm_mode = True