

from enum import Enum


class SurveyStatus(Enum):
    submitted_via_web = 1
    submitted_via_mobile = 2

class PhoneType(Enum):
    smart_phone = 1
    feature_phone = 2

class Gender(Enum):
    male = 1
    female = 2
    other = 3

class HasDisability(Enum):
    yes = 1
    no = 2

class ClientStatus(Enum):
    new_clients = 1
    existing_clients = 2

class IsOperating(Enum):
    yes = 1
    no = 2
    
class BusinessStatus(Enum):
    new_clients = 1
    existing_clients = 2
