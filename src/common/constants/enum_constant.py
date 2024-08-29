

from enum import Enum


class SurveyStatus(str, Enum):
    submitted_via_web = 'submitted_via_web'
    submitted_via_mobile = 'submitted_via_mobile'

class PhoneType(str, Enum):
    smart_phone = 'Smart phone'
    feature_phone = 'Feature phone'

class Gender(str, Enum):
    male = 'Male'
    female = 'Female'
    other = 'Other'

class HasDisability(str, Enum):
    yes = 'Yes'
    no = 'No'

class ClientStatus(str, Enum):
    new = 'New'
    existing = 'Existing'

class IsOperating(str, Enum):
    yes = 'Yes'
    no = 'No'