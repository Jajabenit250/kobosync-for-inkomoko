from pydantic import Field
from src.database.common_model import CommonModel

class Cohort(CommonModel):
    cohort_id: int = Field(primary_key=True)
    name: str