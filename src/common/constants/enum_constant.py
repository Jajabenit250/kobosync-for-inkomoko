

from enum import Enum


class SurveyStatus(Enum):
    submitted_via_web = 1
    submitted_via_mobile = 2

class PhoneType(Enum):
    smart_phone = 1
    feature_phone = 2
    smart_phone_feature_phone = 3

class Gender(Enum):
    male = 1
    female = 2
    other = 3

class ClientStatus(Enum):
    new_clients = 1
    existing_clients = 2

class YesNo(Enum):
    yes = 1
    no = 2

class YesNoUnknown(Enum):
    yes = 1
    no = 2
    unknown = 3
    
class BusinessStatus(Enum):
    idea_stage = 1
    existing_business = 2

class ResponseType(Enum):
    TEXT = 1
    NUMBER = 2
    CHOICE = 3
    MULTIPLE_CHOICE = 4
    DATE = 5
