from datetime import date
from src.database.common_model import CommonModel
from src.common.constants.enum_constant import PhoneType

class SurveysDailyCount(CommonModel):
    survey_date: date
    program_id: int
    cohort_id: int
    survey_count: int