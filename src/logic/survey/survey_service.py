from typing import Any, Dict, List, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from src.database.entity.survey_entity import Survey as SurveyEntity
from src.common.utils.db_utils import db_request_handler
from src.database.models.survey_model import SurveyFilterModel, SurveyModel, LocationModel, ClientModel, SurveyorModel, SurveyResponseModel
from datetime import datetime, date

class SurveyService:
    
    @db_request_handler
    async def get_surveys(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 10,
        filters: SurveyFilterModel = SurveyFilterModel(),
    ) -> List[SurveyModel]:
        print("inside")
        query = db.query(SurveyEntity)

        # Apply filters
        for key, value in filters.dict(exclude_unset=True).items():
            if value is not None:
                if key == "start_date":
                    query = query.filter(SurveyEntity.survey_date >= value)
                elif key == "end_date":
                    query = query.filter(SurveyEntity.survey_date <= value)
                else:
                    query = query.filter(getattr(SurveyEntity, key) == value)

        surveys = query.order_by(SurveyEntity._id).offset(skip).limit(limit).all()
        
        return [self._convert_to_survey_model(survey) for survey in surveys]
    
    #TODO: add get one survey and include survey responses

    def _convert_to_survey_model(self, survey: SurveyEntity) -> SurveyModel:
        survey_dict = {
            "_id": survey._id,
            "formhub_uuid": survey.formhub_uuid,
            "start_time": self._convert_to_str(survey.start_time),
            "end_time": self._convert_to_str(survey.end_time),
            "survey_date": self._convert_to_str(survey.survey_date),
            "unique_id": survey.instance_id or survey.uuid or str(survey._id),
            "instance_id": survey.instance_id,
            "xform_id_string": survey.xform_id_string,
            "uuid": survey.uuid,
            "submission_time": self._convert_to_str(survey.submission_time),
            "version": survey.version,
            "business_status": str(survey.business_status) if survey.business_status else None,
            "business_operating": str(survey.business_operating) if survey.business_operating else None,
            "geolocation": survey._geolocation,
            "tags": survey._tags,
            "notes": survey._notes,
            "validation_status": survey._validation_status,
            "submitted_by": survey._submitted_by,
            "location": LocationModel(
                location_id=survey.location.location_id,
                country=survey.location.country,
                region=survey.location.region,
                specific_location=survey.location.specific_location
            ) if survey.location else None,
            "client": ClientModel(
                client_id_manifest=survey.client.client_id_manifest,
                name=survey.client.name,
                phone=survey.client.phone,
                phone_type=str(survey.client.phone_type),
                gender=str(survey.client.gender),
                age=survey.client.age,
                nationality=survey.client.nationality
            ) if survey.client else None,
            "surveyor": SurveyorModel(
                surveyor_id=survey.surveyor.surveyor_id,
                name=survey.surveyor.name,
                cohort=survey.surveyor.cohort,
                program=survey.surveyor.program
            ) if survey.surveyor else None
            # todo: include survey response when retrieving one survey
        }
        return SurveyModel(**survey_dict)

    def _convert_to_str(self, value: Any) -> Optional[str]:
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        return str(value) if value is not None else None
