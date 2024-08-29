

from pydantic import Field
from src.database.common_model import CommonModel
from src.common.constants.enum_constant import ClientStatus, IsOperating


class Business(CommonModel):
    business_id: int = Field(primary_key=True)
    client_id: int = Field(index=True)
    status: ClientStatus
    is_operating: IsOperating