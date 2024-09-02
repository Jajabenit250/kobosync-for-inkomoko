from typing import Any, List, Optional
from pydantic import BaseModel, Field


class LocationModel(BaseModel):
    location_id: str
    country: str
    region: str
    specific_location: str

    class Config:
        orm_mode = True

class ClientModel(BaseModel):
    client_id_manifest: str
    name: str
    phone: str
    phone_type: str
    gender: str
    age: int
    nationality: str

    class Config:
        orm_mode = True

class SurveyorModel(BaseModel):
    surveyor_id: str
    name: str
    cohort: str
    program: str

class SurveyResponseModel(BaseModel):
    question_key: str
    response: str
    response_type: str

# Updated SurveyModel to include related data
class SurveyModel(BaseModel):
    id: int = Field(..., alias='_id')
    formhub_uuid: str
    start_time: str
    end_time: str
    survey_date: str
    unique_id: str
    instance_id: str
    xform_id_string: str
    uuid: str
    submission_time: str
    version: str
    business_status: str
    business_operating: Optional[str]
    geolocation: Optional[str]
    tags: Optional[str]
    notes: Optional[str]
    validation_status: Optional[str]
    submitted_by: Optional[str]
    
    # Related data
    location: Optional[LocationModel]
    client: Optional[ClientModel]
    surveyor: Optional[SurveyorModel]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

# Input model for filtering surveys
class SurveyFilterModel(BaseModel):
    unique_id: Optional[str] = None
    location_id: Optional[str] = None
    surveyor_id: Optional[str] = None
    client_id_manifest: Optional[str] = None
    business_status: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class SurveyResponse(BaseModel):
    total: int
    surveys: List[SurveyModel]

class SurveyStatisticsResponse(BaseModel):
    total_surveys: int
    avg_duration_seconds: Optional[float]
    earliest_survey: Optional[str]
    latest_survey: Optional[str]
    business_status_distribution: dict
