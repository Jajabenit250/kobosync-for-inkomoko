from typing import Optional, List, Union
from pydantic import BaseModel
from datetime import datetime

class KoboDataModel(BaseModel):
    _id: int
    formhub_uuid: str
    starttime: datetime
    endtime: datetime
    cd_survey_date: datetime
    sec_a_unique_id: str
    sec_a_cd_biz_country_name: str
    sec_a_cd_biz_region_name: str
    sec_b_bda_name: str
    sec_b_cd_cohort: str
    sec_b_cd_program: str
    sec_c_cd_client_name: str
    sec_c_cd_client_id_manifest: str
    sec_c_cd_location: str
    sec_c_cd_clients_phone: str
    sec_c_cd_phoneno_alt_number: Optional[str] = None
    sec_c_cd_clients_phone_smart_feature: str
    sec_c_cd_gender: str
    sec_c_cd_age: str
    sec_c_cd_nationality: str
    sec_c_cd_strata: str
    sec_c_cd_disability: str
    sec_c_cd_education: str
    sec_c_cd_client_status: str
    sec_c_cd_sole_income_earner: str
    sec_c_cd_howrespble_pple: str
    group_mx5fl16_cd_biz_status: str
    group_mx5fl16_bd_biz_operating: str
    __version__: str
    meta_instanceID: str
    _xform_id_string: str
    _uuid: str
    _attachments: List[dict]
    _status: str
    _geolocation: List[Union[float, None]]
    _submission_time: datetime
    _tags: List[str]
    _notes: List[str]
    _validation_status: dict
    _submitted_by: Optional[str] = None

