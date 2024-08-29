from pydantic import Field
from src.database.common_model import CommonModel
from src.common.constants.enum_constant import PhoneType

class Region(CommonModel):
    region_id: int = Field(primary_key=True)
    country_id: int = Field(index=True)
    name: str