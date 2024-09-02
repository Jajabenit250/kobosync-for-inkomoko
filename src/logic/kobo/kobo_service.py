import json
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Any
from datetime import datetime, timezone
import logging
import asyncio
from src.common.utils.db_utils import db_request_handler
from src.integration.kobotoolbox.kobotoolbox_service import KoboDataService
from src.database.entity.survey_entity import Survey
from src.database.entity.location_entity import Location
from src.database.entity.client_entity import Client
from src.database.entity.surveyor_entity import Surveyor
from src.database.entity.survey_response_entity import SurveyResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from src.common.constants.enum_constant import (
    YesNoUnknown,
    BusinessStatus,
    PhoneType,
    Gender,
    YesNo,
    ResponseType,
)
from datetime import datetime, timezone


class KoboService:
    def __init__(self):
        self.data_service = KoboDataService()

    @staticmethod
    def map_enum_value(enum_class, value):
        if value is None:
            return None
        value = str(value).lower().replace(" ", "_").strip()
        try:
            return enum_class[value].name
        except KeyError:
            logging.warning(f"Unknown enum value: {value} for {enum_class.__name__}")
            return None

    @staticmethod
    def safe_get(dictionary, key, default=""):
        """Safely get a value from a dictionary, returning a default if the key is missing or the value is None."""
        value = dictionary.get(key)
        return default if value is None else value

    @db_request_handler
    async def extract_and_save_data(self, db: Session):
        try:
            kobo_data = await self.data_service.fetch_kobo_data()
            if not kobo_data:
                logging.warning("No Kobo data fetched.")
                return

            tasks = [
                self.save_locations(self.extract_locations(kobo_data), db),
                self.save_surveyors(self.extract_surveyors(kobo_data), db),
                self.save_clients(self.extract_clients(kobo_data), db),
                self.save_surveys(self.extract_surveys(kobo_data), db),
                self.save_survey_responses(
                    self.extract_survey_responses(kobo_data), db
                ),
            ]

            await asyncio.gather(*tasks)

            logging.info(f"Data extraction and saving completed at {datetime.now()}")
        except Exception as e:
            logging.error(f"Error in extract_and_save_data: {str(e)}")
            raise

    def extract_surveys(self, kobo_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        current_time = self.format_datetime_for_clickhouse(
            datetime.now(timezone.utc).isoformat()
        )
        return [
            {
                "_id": int(self.safe_get(survey, "_id", 0)),
                "formhub_uuid": self.safe_get(survey, "formhub/uuid"),
                "start_time": self.format_datetime_for_clickhouse(
                    self.safe_get(survey, "starttime")
                ),
                "end_time": self.format_datetime_for_clickhouse(
                    self.safe_get(survey, "endtime")
                ),
                "survey_date": self.format_date(
                    self.safe_get(survey, "cd_survey_date")
                ),
                "instance_id": self.safe_get(survey, "meta/instanceID"),
                "xform_id_string": self.safe_get(survey, "_xform_id_string"),
                "uuid": self.safe_get(survey, "_uuid"),
                "submission_time": self.format_datetime_for_clickhouse(
                    self.safe_get(survey, "_submission_time")
                ),
                "version": self.safe_get(survey, "__version__"),
                "location_id": f"{self.safe_get(survey, 'sec_a/cd_biz_country_name')}|{self.safe_get(survey, 'sec_a/cd_biz_region_name')}|{self.safe_get(survey, 'sec_c/cd_location')}",
                "surveyor_id": self.safe_get(survey, "sec_b/bda_name"),
                "client_id_manifest": self.safe_get(
                    survey, "sec_c/cd_client_id_manifest"
                ),
                "business_status": self.map_enum_value(
                    BusinessStatus, self.safe_get(survey, "group_mx5fl16/cd_biz_status")
                ),
                "business_operating": self.map_enum_value(
                    YesNoUnknown,
                    self.safe_get(survey, "group_mx5fl16/bd_biz_operating", "unknown"),
                ),
                "_geolocation": self.format_geolocation(
                    self.safe_get(survey, "_geolocation", [])
                ),
                "_tags": self.format_array_for_clickhouse(
                    self.safe_get(survey, "_tags", [])
                ),
                "_notes": self.format_array_for_clickhouse(
                    self.safe_get(survey, "_notes", [])
                ),
                "_validation_status": self.format_dict_to_string(
                    self.safe_get(survey, "_validation_status", {})
                ),
                "_submitted_by": self.safe_get(survey, "_submitted_by"),
                "last_updated": current_time,
            }
            for survey in kobo_data
        ]

    def format_datetime_for_clickhouse(self, value):
        if value:
            try:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                return None
        return None

    def format_date(self, value):
        if value:
            try:
                return datetime.strptime(value, "%Y-%m-%d").date().isoformat()
            except ValueError:
                return None
        return None

    def format_geolocation(self, geolocation):
        if isinstance(geolocation, list) and len(geolocation) == 2:
            return f"{geolocation[0]},{geolocation[1]}"
        return None

    def format_array_for_clickhouse(self, value):
        if isinstance(value, list):
            return json.dumps(value)
        return "[]"

    def format_dict_to_string(self, value):
        if isinstance(value, dict):
            return json.dumps(value)
        return "{}"

    async def save_surveys(self, surveys: List[Dict[str, Any]], db: Session):
        try:
            for survey in surveys:
                existing_survey = db.query(Survey).filter_by(_id=survey["_id"]).first()
                if existing_survey:
                    for key, value in survey.items():
                        if (
                            key != "_id"
                            and key != "submission_time"
                            and key != "client_id_manifest"
                        ):  # Don't update the primary keys
                            setattr(existing_survey, key, value)
                else:
                    new_survey = Survey(**survey)
                    db.add(new_survey)
            db.flush()
            logging.info(f"Saved {len(surveys)} surveys")
        except SQLAlchemyError as e:
            logging.error(f"Database error while saving surveys: {str(e)}")
            raise

    def extract_locations(
        self, kobo_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        return [
            {
                "location_id": f"{survey['sec_a/cd_biz_country_name']}|{survey['sec_a/cd_biz_region_name']}|{survey['sec_c/cd_location']}",
                "country": survey["sec_a/cd_biz_country_name"],
                "region": survey["sec_a/cd_biz_region_name"],
                "specific_location": survey["sec_c/cd_location"],
            }
            for survey in kobo_data
        ]

    async def save_locations(self, locations: List[Dict[str, Any]], db: Session):
        try:
            for location in locations:
                existing_location = (
                    db.query(Location)
                    .filter_by(location_id=location["location_id"])
                    .first()
                )
                if not existing_location:
                    new_location = Location(**location)
                    db.add(new_location)
            db.flush()
            logging.info(f"Saved {len(locations)} locations")
        except SQLAlchemyError as e:
            logging.error(f"Database error while saving locations: {str(e)}")
            raise

    def extract_clients(self, kobo_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        current_time = datetime.now()
        return [
            {
                "client_id_manifest": self.safe_get(
                    survey, "sec_c/cd_client_id_manifest", ""
                ),
                "unique_id": self.safe_get(survey, "sec_a/unique_id"),
                "name": self.safe_get(survey, "sec_c/cd_client_name", ""),
                "phone": self.safe_get(survey, "sec_c/cd_clients_phone", ""),
                "alternate_phone": self.safe_get(
                    survey, "sec_c/cd_phoneno_alt_number", ""
                ),
                "phone_type": self.map_enum_value(
                    PhoneType,
                    self.safe_get(survey, "sec_c/cd_clients_phone_smart_feature"),
                )
                or PhoneType.smart_phone.name,
                "gender": self.map_enum_value(
                    Gender, self.safe_get(survey, "sec_c/cd_gender")
                )
                or Gender.other.name,
                "age": int(self.safe_get(survey, "sec_c/cd_age", 0)),
                "nationality": self.safe_get(survey, "sec_c/cd_nationality", ""),
                "strata": self.safe_get(survey, "sec_c/cd_strata", ""),
                "disability": self.map_enum_value(
                    YesNo, self.safe_get(survey, "sec_c/cd_disability")
                )
                or YesNo.no.name,
                "education": self.safe_get(survey, "sec_c/cd_education", ""),
                "status": self.safe_get(survey, "sec_c/cd_client_status", ""),
                "sole_income_earner": self.map_enum_value(
                    YesNo, self.safe_get(survey, "sec_c/cd_sole_income_earner")
                )
                or YesNo.no.name,
                "responsible_for_people": int(
                    self.safe_get(survey, "sec_c/cd_howrespble_pple", 0)
                ),
                "last_updated": current_time,
                "version": int(current_time.timestamp()),
            }
            for survey in kobo_data
        ]

    async def save_clients(self, clients: List[Dict[str, Any]], db: Session):
        try:
            for client in clients:
                existing_client = (
                    db.query(Client)
                    .filter_by(client_id_manifest=client["client_id_manifest"])
                    .first()
                )
                if existing_client:
                    for key, value in client.items():
                        if (
                            key != "client_id_manifest" and key != "version"
                        ):  # Don't update the primary keys
                            setattr(existing_client, key, value)
                else:
                    new_client = Client(**client)
                    db.add(new_client)
            db.flush()
            logging.info(f"Saved {len(clients)} clients")
        except SQLAlchemyError as e:
            logging.error(f"Database error while saving clients: {str(e)}")
            raise

    def extract_surveyors(
        self, kobo_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        return [
            {
                "surveyor_id": survey.get("sec_b/bda_name"),
                "name": survey.get("sec_b/bda_name"),
                "cohort": survey.get("sec_b/cd_cohort"),
                "program": survey.get("sec_b/cd_program"),
            }
            for survey in kobo_data
        ]

    async def save_surveyors(self, surveyors: List[Dict[str, Any]], db: Session):
        try:
            for surveyor in surveyors:
                existing_surveyor = (
                    db.query(Surveyor)
                    .filter_by(surveyor_id=surveyor["surveyor_id"])
                    .first()
                )
                if not existing_surveyor:
                    new_surveyor = Surveyor(**surveyor)
                    db.add(new_surveyor)
            db.flush()
            logging.info(f"Saved {len(surveyors)} surveyors")
        except SQLAlchemyError as e:
            logging.error(f"Database error while saving surveyors: {str(e)}")
            raise

    def extract_survey_responses(
        self, kobo_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        responses = []
        for survey in kobo_data:
            for key, value in survey.items():
                if key.startswith(("sec_a/", "sec_b/", "sec_c/", "group_mx5fl16/")):
                    responses.append(
                        {
                            "_id": int(self.safe_get(survey, "_id", 0)),
                            "unique_id": int(self.safe_get(survey, "sec_a/unique_id", 0)),
                            "question_key": key,
                            "response": str(value),
                            "response_type": self.map_enum_value(
                                ResponseType, self.get_response_type(value)
                            ),
                            "last_updated": datetime.now()
                        }
                    )
        return responses

    def get_response_type(self, value: Any) -> str:
        if isinstance(value, (int, float)):
            return "number"
        elif isinstance(value, bool):
            return "choice"
        elif isinstance(value, list):
            return "multiple_choice"
        elif isinstance(value, str):
            try:
                datetime.strptime(value, "%Y-%m-%d")
                return "date"
            except ValueError:
                return "text"
        else:
            return "text"

    async def save_survey_responses(self, responses: List[Dict[str, Any]], db: Session):
        try:
            for response in responses:
                existing_response = (
                    db.query(SurveyResponse)
                    .filter_by(
                        _id = response["_id"],
                        unique_id=response["unique_id"],
                        question_key=response["question_key"],
                    )
                    .first()
                )
                if existing_response:
                    for key, value in response.items():
                        if (
                            key != "_id" and key != "unique_id" and key != 'question_key' and key != 'last_updated' 
                        ):  # Don't update the primary keys
                            setattr(existing_response, key, value)
                else:
                    new_response = SurveyResponse(**response)
                    db.add(new_response)
            db.flush()
            logging.info(f"Saved {len(responses)} survey responses")
        except SQLAlchemyError as e:
            logging.error(f"Database error while saving survey responses: {str(e)}")
            raise

    @db_request_handler
    async def auto_update_current_data(self, db: Session):
        try:
            # Fetch the survey with the earliest submission_date to determine the last update date
            last_submitted_survey = (
                db.query(Survey.submission_time)
                .order_by(Survey.submission_time.desc())
                .first()
            )

            # Fetch all Kobo data
            kobo_data = await self.data_service.fetch_kobo_data()

            if not kobo_data:
                logging.warning("No Kobo data fetched.")
                return

            # Filter data with submission_date greater than last_update_date
            if last_submitted_survey.submission_time:
                filtered_data = [
                    survey
                    for survey in kobo_data
                    if datetime.fromisoformat(
                        self.format_datetime_for_clickhouse(
                            self.safe_get(survey, "_submission_time")
                        )
                    )
                    > last_submitted_survey.submission_time
                ]
            else:
                filtered_data = kobo_data

            if not filtered_data:
                logging.info("No new data to save after filtering.")
                return

            tasks = [
                self.save_locations(self.extract_locations(filtered_data), db),
                self.save_surveyors(self.extract_surveyors(filtered_data), db),
                self.save_clients(self.extract_clients(filtered_data), db),
                self.save_surveys(self.extract_surveys(filtered_data), db),
                self.save_survey_responses(self.extract_survey_responses(filtered_data), db)
            ]

            await asyncio.gather(*tasks)
            logging.info(f"Data extraction and saving completed at {datetime.now()}")

        except Exception as e:
            logging.error(f"Error in daily extraction: {str(e)}")
            raise

    def setup_cron_job(self):
        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            self.daily_extraction, CronTrigger(hour=0, minute=0)
        )  # Run at midnight every day
        scheduler.start()
        logging.info("Cron job for daily extraction has been set up")
