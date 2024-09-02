from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class Issue(BaseModel):
    type: str
    survey_id: int
    value: Optional[Any] = None

class IssuesByEntity(BaseModel):
    surveys: List[Issue]

class IssuesByType(BaseModel):
    invalid_business_operating: Optional[int] = 0
    future_survey_date_date: Optional[int] = 0

class Summary(BaseModel):
    total_issues: int
    issues_by_type: IssuesByType
    issues_by_entity: Dict[str, int]

class DataQualityCheckResponse(BaseModel):
    message: str
    summary: Summary
    issues: IssuesByEntity
