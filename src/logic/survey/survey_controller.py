from nest.core import Controller, Get, Depends
from .survey_service import SurveyService
from src.database.models.survey_model import (
    SurveyFilterModel, SurveyModel
)
from typing import Any, List
from fastapi import Query


@Controller("surveys")
class SurveyController:
    service: SurveyService = Depends(SurveyService)

    @Get("/")
    async def get_surveys(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=1000),
        filters: SurveyFilterModel = Depends(),
    ) -> List[SurveyModel]:
        print("-----")
        return await self.service.get_surveys(skip=skip, limit=limit, filters=filters)
