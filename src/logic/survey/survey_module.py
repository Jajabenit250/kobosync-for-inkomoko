from .survey_service import SurveyService
from .survey_controller import SurveyController

class SurveyModule:

    def __init__(self):
        self.providers = [SurveyService]
        self.controllers = [SurveyController]
