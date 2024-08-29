from pydantic import Field
from src.database.common_model import CommonModel

class BusinessDevelopmentAdvisor(CommonModel):
    bda_id: int = Field(primary_key=True)
    name: str
    country_id: int = Field(index=True)
    region_id: int = Field(index=True)