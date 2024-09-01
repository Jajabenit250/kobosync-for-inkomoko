from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any
from datetime import datetime, date
import re
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.database.entity.issue_entity import Issue
from src.common.utils.db_utils import db_request_handler
import logging

class DataQualityService:
    @staticmethod
    def check_surveys(surveys: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        issues = []
        for survey in surveys:
            try:
                if not survey.get('_id'):
                    issues.append({"type": "missing_id", "survey_id": survey.get('_id')})
                if not survey.get('formhub_uuid') or not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', survey['formhub_uuid']):
                    issues.append({"type": "invalid_formhub_uuid", "survey_id": survey.get('_id')})
                start_time = datetime.fromisoformat(survey['start_time'])
                end_time = datetime.fromisoformat(survey['end_time'])
                if start_time > end_time:
                    issues.append({"type": "invalid_time_range", "survey_id": survey.get('_id')})
                survey_date = datetime.strptime(survey['survey_date'], "%Y-%m-%d").date()
                if survey_date > date.today():
                    issues.append({"type": "future_date", "survey_id": survey.get('_id')})
                if not survey.get('unique_id'):
                    issues.append({"type": "missing_unique_id", "survey_id": survey.get('_id')})
                if not survey.get('location_id'):
                    issues.append({"type": "missing_location_id", "survey_id": survey.get('_id')})
                if not survey.get('surveyor_id'):
                    issues.append({"type": "missing_surveyor_id", "survey_id": survey.get('_id')})
                if not survey.get('client_id_manifest'):
                    issues.append({"type": "missing_client_id_manifest", "survey_id": survey.get('_id')})
                if survey.get('business_status') not in ['Existing Business', 'New Business', 'Not Operating']:
                    issues.append({"type": "invalid_business_status", "survey_id": survey.get('_id')})
                if survey.get('business_operating') not in ['yes', 'no']:
                    issues.append({"type": "invalid_business_operating", "survey_id": survey.get('_id')})
                if survey.get('_geolocation'):
                    lat, lon = survey['_geolocation']
                    if lat < -90 or lat > 90:
                        issues.append({"type": "invalid_latitude", "survey_id": survey.get('_id')})
                    if lon < -180 or lon > 180:
                        issues.append({"type": "invalid_longitude", "survey_id": survey.get('_id')})
            except KeyError as e:
                issues.append({"type": "missing_required_field", "field": str(e), "survey_id": survey.get('_id')})
            except ValueError as e:
                issues.append({"type": "invalid_data_format", "error": str(e), "survey_id": survey.get('_id')})
        return issues

    @staticmethod
    def check_locations(locations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        issues = []
        for location in locations:
            try:
                if not location.get('location_id'):
                    issues.append({"type": "missing_location_id", "location_id": location.get('location_id')})
                if not location.get('country'):
                    issues.append({"type": "missing_country", "location_id": location.get('location_id')})
                if not location.get('region'):
                    issues.append({"type": "missing_region", "location_id": location.get('location_id')})
                if not location.get('specific_location'):
                    issues.append({"type": "missing_specific_location", "location_id": location.get('location_id')})
            except KeyError as e:
                issues.append({"type": "missing_required_field", "field": str(e), "location_id": location.get('location_id')})
        return issues

    @staticmethod
    def check_clients(clients: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        issues = []
        for client in clients:
            try:
                if not client.get('client_id_manifest'):
                    issues.append({"type": "missing_client_id_manifest", "client_id": client.get('client_id_manifest')})
                if not client.get('name'):
                    issues.append({"type": "missing_name", "client_id": client.get('client_id_manifest')})
                age = int(client['age'])
                if age < 0 or age > 120:
                    issues.append({"type": "invalid_age", "client_id": client.get('client_id_manifest')})
                if client['gender'] not in ['Male', 'Female']:
                    issues.append({"type": "invalid_gender", "client_id": client.get('client_id_manifest')})
                if not re.match(r'^\+?1?\d{9,15}$', client['phone']):
                    issues.append({"type": "invalid_phone_number", "client_id": client.get('client_id_manifest')})
                if client.get('alternate_phone') and not re.match(r'^\+?1?\d{9,15}$', client['alternate_phone']):
                    issues.append({"type": "invalid_alternate_phone_number", "client_id": client.get('client_id_manifest')})
                if client['phone_type'] not in ['Smart phone', 'Feature phone', 'Basic phone']:
                    issues.append({"type": "invalid_phone_type", "client_id": client.get('client_id_manifest')})
                if not client.get('nationality'):
                    issues.append({"type": "missing_nationality", "client_id": client.get('client_id_manifest')})
                if not isinstance(client.get('responsible_for_people'), int) or client['responsible_for_people'] < 0:
                    issues.append({"type": "invalid_responsible_for_people", "client_id": client.get('client_id_manifest')})
            except KeyError as e:
                issues.append({"type": "missing_required_field", "field": str(e), "client_id": client.get('client_id_manifest')})
            except ValueError as e:
                issues.append({"type": "invalid_data_type", "error": str(e), "client_id": client.get('client_id_manifest')})
        return issues

    @staticmethod
    def check_surveyors(surveyors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        issues = []
        for surveyor in surveyors:
            try:
                if not surveyor.get('surveyor_id'):
                    issues.append({"type": "missing_surveyor_id", "surveyor_id": surveyor.get('surveyor_id')})
                if not surveyor.get('name'):
                    issues.append({"type": "missing_name", "surveyor_id": surveyor.get('surveyor_id')})
                if not surveyor.get('cohort'):
                    issues.append({"type": "missing_cohort", "surveyor_id": surveyor.get('surveyor_id')})
                if not surveyor.get('program'):
                    issues.append({"type": "missing_program", "surveyor_id": surveyor.get('surveyor_id')})
            except KeyError as e:
                issues.append({"type": "missing_required_field", "field": str(e), "surveyor_id": surveyor.get('surveyor_id')})
        return issues

    @staticmethod
    def check_survey_responses(responses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        issues = []
        for response in responses:
            try:
                if not response.get('_id'):
                    issues.append({"type": "missing_id", "response_id": f"{response.get('_id')}_{response.get('question_key')}"})
                if not response.get('unique_id'):
                    issues.append({"type": "missing_unique_id", "response_id": f"{response.get('_id')}_{response.get('question_key')}"})
                if not response.get('question_key'):
                    issues.append({"type": "missing_question_key", "response_id": f"{response.get('_id')}_{response.get('question_key')}"})
                if not response.get('response'):
                    issues.append({"type": "missing_response", "response_id": f"{response.get('_id')}_{response.get('question_key')}"})
                if response.get('response_type') not in ['text', 'number', 'choice', 'multiple_choice', 'date']:
                    issues.append({"type": "invalid_response_type", "response_id": f"{response.get('_id')}_{response.get('question_key')}"})
            except KeyError as e:
                issues.append({"type": "missing_required_field", "field": str(e), "response_id": f"{response.get('_id')}_{response.get('question_key')}"})
        return issues

    @classmethod
    def check_all(cls, data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        with ThreadPoolExecutor() as executor:
            futures = {
                "surveys": executor.submit(cls.check_surveys, data.get('surveys', [])),
                "locations": executor.submit(cls.check_locations, data.get('locations', [])),
                "clients": executor.submit(cls.check_clients, data.get('clients', [])),
                "surveyors": executor.submit(cls.check_surveyors, data.get('surveyors', [])),
                "survey_responses": executor.submit(cls.check_survey_responses, data.get('survey_responses', []))
            }
            return {key: future.result() for key, future in futures.items()}

    @staticmethod
    def generate_summary(issues: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        summary = {
            "total_issues": sum(len(issue_list) for issue_list in issues.values()),
            "issues_by_type": {},
            "issues_by_entity": {entity: len(issues) for entity, issues in issues.items()}
        }
        for entity_issues in issues.values():
            for issue in entity_issues:
                issue_type = issue['type']
                if issue_type in summary['issues_by_type']:
                    summary['issues_by_type'][issue_type] += 1
                else:
                    summary['issues_by_type'][issue_type] = 1
        return summary
    
    @db_request_handler
    async def save_issues_to_db(self, issues: Dict[str, List[Dict[str, Any]]], db: Session):
        try:
            for entity_type, entity_issues in issues.items():
                for issue in entity_issues:
                    db_issue = Issue(
                        entity_type=entity_type,
                        issue_type=issue['type'],
                        entity_id=issue.get('survey_id') or issue.get('location_id') or issue.get('client_id') or issue.get('surveyor_id') or issue.get('response_id'),
                        details=issue
                    )
                    db.add(db_issue)
            db.flush()
            logging.info(f"Saved {sum(len(entity_issues) for entity_issues in issues.values())} issues to the database")
        except Exception as e:
            logging.error(f"Error saving issues to database: {str(e)}")
            raise

    @db_request_handler
    async def get_issues(self, entity_type: str = None, issue_type: str = None, limit: int = 100, offset: int = 0, db: Session = None):
        query = db.query(Issue)
        if entity_type:
            query = query.filter(Issue.entity_type == entity_type)
        if issue_type:
            query = query.filter(Issue.issue_type == issue_type)
        
        total = query.count()
        issues = query.order_by(Issue.created_at.desc()).offset(offset).limit(limit).all()
        
        return total, issues

    @db_request_handler
    async def get_summary(self, db: Session):
        issues_by_entity = db.query(Issue.entity_type, func.count(Issue.id)).group_by(Issue.entity_type).all()
        issues_by_type = db.query(Issue.issue_type, func.count(Issue.id)).group_by(Issue.issue_type).all()
        
        return {
            "total_issues": db.query(func.count(Issue.id)).scalar(),
            "issues_by_entity": dict(issues_by_entity),
            "issues_by_type": dict(issues_by_type)
        }
        