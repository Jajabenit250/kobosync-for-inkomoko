from pydantic import Field
from src.database.common_model import CommonModel
from src.common.constants.enum_constant import PhoneType, Gender, HasDisability, ClientStatus

class Client(CommonModel):
    client_id: int = Field(primary_key=True)
    name: str
    id_manifest: str
    location: str
    phone_primary: str
    phone_secondary: str
    phone_type: PhoneType
    gender: Gender
    age: int
    nationality_id: int = Field(index=True)
    strata: str
    has_disability: HasDisability
    education_level_id: int = Field(index=True)
    client_status: ClientStatus
    is_sole_income_earner: HasDisability
    dependents: int