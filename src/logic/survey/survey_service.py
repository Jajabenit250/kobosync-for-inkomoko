from sqlalchemy.orm import Session
from src.database.models.survey_model import Survey as SurveyModel
from src.database.entity.survey_entity import Survey as SurveyEntity
from src.common.utils.db_utils import db_request_handler

class SurveyService:

    @db_request_handler
    async def add_survey(self, survey: SurveyModel, db: Session):
        new_survey = SurveyEntity(**survey.dict())
        db.add(new_survey)
        db.flush()
        return new_survey.survey_id

    @db_request_handler
    async def get_surveys(self, db: Session):
        surveys = db.query(SurveyEntity).all()
        return [SurveyModel.from_orm(survey) for survey in surveys]

    @db_request_handler
    async def get_survey(self, survey_id: str, db: Session):
        survey = db.query(SurveyEntity).filter(SurveyEntity.survey_id == survey_id).first()
        if survey:
            return SurveyModel.from_orm(survey)
        return None

    @db_request_handler
    async def update_survey(self, survey_id: str, survey_data: SurveyModel, db: Session):
        existing_survey = db.query(SurveyEntity).filter(SurveyEntity.survey_id == survey_id).first()
        if existing_survey:
            for key, value in survey_data.dict(exclude_unset=True).items():
                setattr(existing_survey, key, value)
            db.flush()
            return SurveyModel.from_orm(existing_survey)
        return None

    @db_request_handler
    async def delete_survey(self, survey_id: str, db: Session):
        existing_survey = db.query(SurveyEntity).filter(SurveyEntity.survey_id == survey_id).first()
        if existing_survey:
            db.delete(existing_survey)
            db.flush()
            return True
        return False