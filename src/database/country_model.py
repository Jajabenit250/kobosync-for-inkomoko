from pydantic import Field
from src.database.common_model import CommonModel
from src.common.constants.enum_constant import PhoneType

class Country(CommonModel):
    country_id: int = Field(primary_key=True)
    name: str