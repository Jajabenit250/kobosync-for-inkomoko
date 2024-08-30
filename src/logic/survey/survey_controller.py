from typing import Annotated
from nest.core import Controller, Get, Post, Depends

from .survey_service import SurveyService
from src.database.models.survey_model import Survey
# from src.database.model.user_model import User
# from src.common.utils.auth.auth_util import get_current_active_user

@Controller("surveys")
class SurveyController:

    service: SurveyService = Depends(SurveyService)

    @Get("/")
    async def get_surveys(self):
        return await self.service.get_surveys()

    @Post("/")
    async def add_survey(self, survey: Survey):
        return await self.service.add_survey(survey)