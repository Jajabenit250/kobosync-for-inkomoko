from typing import List
from src.database.common_model import CommonModel
from src.common.constants.enum_constant import Gender


class ClientDemographics(CommonModel):
    nationality_id: int
    gender: Gender
    age_group: int
    client_count: int
    avg_age: float
    education_levels: List[int]