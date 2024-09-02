from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any
from datetime import datetime, date
import re
import logging
from src.integration.kobotoolbox.kobotoolbox_service import KoboDataService


class DataQualityService:
    def __init__(self):
        self.kobo_service = KoboDataService()

    async def check_all(self) -> Dict[str, List[Dict[str, Any]]]:
        try:
            kobo_data = await self.kobo_service.fetch_kobo_data()
            if not kobo_data:
                logging.warning("No Kobo data fetched.")
                return {}

            with ThreadPoolExecutor() as executor:
                futures = {
                    "surveys": executor.submit(self.check_surveys, kobo_data),
                }
                return {key: future.result() for key, future in futures.items()}
        except Exception as e:
            logging.error(f"Error in check_all: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def check_surveys(surveys: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        issues = []
        for survey in surveys:
            try:
                if not survey.get("_id"):
                    issues.append({"type": "missing_id", "survey_id": "unknown"})
                    continue  # Skip further checks if _id is missing

                survey_id = survey.get("_id")

                try:
                    start_time = datetime.fromisoformat(survey.get("starttime", ""))
                    end_time = datetime.fromisoformat(survey.get("endtime", ""))
                    if start_time and end_time and start_time > end_time:
                        issues.append(
                            {"type": "invalid_time_range", "survey_id": survey_id, "value": start_time}
                        )
                except ValueError:
                    issues.append(
                        {"type": "invalid_time_format", "survey_id": survey_id, "value": survey.get("starttime", "")}
                    )

                try:
                    survey_date = datetime.strptime(
                        survey.get("cd_survey_date", ""), "%Y-%m-%d"
                    ).date()
                    if survey_date > date.today():
                        issues.append({"type": "future_survey_date_date", "survey_id": survey_id, "value": survey_date})
                except ValueError:
                    issues.append(
                        {"type": "invalid_date_format", "survey_id": survey_id, "value": survey.get("cd_survey_date", "")}
                    )

                if not survey.get("sec_a/unique_id"):
                    issues.append({"type": "missing_unique_id", "survey_id": survey_id, "value": survey.get("sec_a/unique_id")})

                # Location checks
                if not survey.get("sec_a/cd_biz_country_name"):
                    issues.append({"type": "missing_country", "survey_id": survey_id, "value": survey.get("sec_a/cd_biz_country_name")})
                if not survey.get("sec_a/cd_biz_region_name"):
                    issues.append({"type": "missing_region", "survey_id": survey_id, "value": survey.get("sec_a/cd_biz_region_name")})
                if not survey.get("sec_c/cd_location"):
                    issues.append(
                        {"type": "missing_specific_location", "survey_id": survey_id, "value": survey.get("sec_c/cd_location")}
                    )

                # Surveyor checks
                if not survey.get("sec_b/bda_name"):
                    issues.append(
                        {"type": "missing_surveyor_name", "survey_id": survey_id, "value": survey.get("sec_b/bda_name")}
                    )
                if not survey.get("sec_b/cd_cohort"):
                    issues.append({"type": "missing_cohort", "survey_id": survey_id, "value": survey.get("sec_b/cd_cohort")})
                if not survey.get("sec_b/cd_program"):
                    issues.append({"type": "missing_program", "survey_id": survey_id, "value": survey.get("sec_b/cd_program")})

                # Client checks
                if not survey.get("sec_c/cd_client_id_manifest"):
                    issues.append(
                        {"type": "missing_client_id_manifest", "survey_id": survey_id, "value": survey.get("sec_c/cd_client_id_manifest")}
                    )
                if not survey.get("sec_c/cd_client_name"):
                    issues.append(
                        {"type": "missing_client_name", "survey_id": survey_id, "value": survey.get("sec_c/cd_client_name")}
                    )

                try:
                    age = int(survey.get("sec_c/cd_age", ""))
                    if age < 0 or age > 120:
                        issues.append({"type": "invalid_age", "survey_id": survey_id, "value": survey.get("sec_c/cd_age", "")})
                except ValueError:
                    issues.append(
                        {"type": "invalid_age_format", "survey_id": survey_id, "value": survey.get("sec_c/cd_age", "")}
                    )

                if survey.get("sec_c/cd_gender") not in ["Male", "Female"]:
                    issues.append({"type": "invalid_gender", "survey_id": survey_id, "value": survey.get("sec_c/cd_gender")})

                if not re.match(
                    r"^\+?1?\d{9,15}$", survey.get("sec_c/cd_clients_phone", "")
                ):
                    issues.append(
                        {"type": "invalid_phone_number", "survey_id": survey_id, "value": survey.get("sec_c/cd_clients_phone", "")}
                    )

                if survey.get("sec_c/cd_clients_phone_smart_feature") not in [
                    "Smart phone",
                    "Feature phone",
                    "Basic phone",
                    "Smart phone Feature phone",
                ]:
                    issues.append(
                        {"type": "invalid_phone_type", "survey_id": survey_id, "value": survey.get("sec_c/cd_clients_phone_smart_feature")}
                    )

                # Business checks
                if survey.get("group_mx5fl16/cd_biz_status") not in [
                    "Existing Business",
                    "New Business",
                    "Idea stage",
                ]:
                    issues.append(
                        {"type": "invalid_business_status", "survey_id": survey_id, "value": survey.get("group_mx5fl16/cd_biz_status")}
                    )

                if survey.get("group_mx5fl16/bd_biz_operating") not in ["yes", "no"]:
                    issues.append(
                        {"type": "invalid_business_operating", "survey_id": survey_id, "value": survey.get("group_mx5fl16/bd_biz_operating")}
                    )

                # Geolocation check
                geolocation = survey.get("_geolocation")
                if (
                    geolocation
                    and isinstance(geolocation, list)
                    and len(geolocation) == 2
                ):
                    lat, lon = geolocation
                    if lat is not None and (lat < -90 or lat > 90):
                        issues.append(
                            {"type": "invalid_latitude", "survey_id": survey_id, "value": geolocation}
                        )
                    if lon is not None and (lon < -180 or lon > 180):
                        issues.append(
                            {"type": "invalid_longitude", "survey_id": survey_id, "value": geolocation}
                        )
                elif geolocation is not None:
                    issues.append(
                        {"type": "invalid_geolocation_format", "survey_id": survey_id, "value": geolocation}
                    )

            except Exception as e:
                logging.error(
                    f"Error processing survey {survey.get('_id', 'unknown')}: {str(e)}"
                )
                issues.append(
                    {
                        "type": "processing_error",
                        "survey_id": survey.get("_id", "unknown"),
                        "error": str(e),
                    }
                )

        return issues

    @staticmethod
    def generate_summary(issues: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        summary = {
            "total_issues": sum(len(issue_list) for issue_list in issues.values()),
            "issues_by_type": {},
            "issues_by_entity": {
                entity: len(issues) for entity, issues in issues.items()
            },
        }
        for entity_issues in issues.values():
            for issue in entity_issues:
                issue_type = issue["type"]
                if issue_type in summary["issues_by_type"]:
                    summary["issues_by_type"][issue_type] += 1
                else:
                    summary["issues_by_type"][issue_type] = 1
        return summary

    async def process_and_report(self) -> Dict[str, Any]:
        issues = await self.check_all()
        summary = self.generate_summary(issues)
        return {"issues": issues, "summary": summary}
