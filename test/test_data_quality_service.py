import pytest
from src.logic.data_quality.data_quality_service import DataQualityService

@pytest.fixture
def data_quality_service():
    return DataQualityService()

def test_check_surveys(data_quality_service):
    surveys = [
        {
            "_id": "1",
            "formhub_uuid": "valid-uuid",
            "start_time": "2023-01-01T10:00:00",
            "end_time": "2023-01-01T11:00:00",
            "survey_date": "2023-01-01",
            "unique_id": "UID1",
            "location_id": "LOC1",
            "surveyor_id": "SUR1",
            "client_id_manifest": "CLI1",
            "business_status": "Existing Business",
            "business_operating": "yes"
        },
        {
            "_id": "",
            "formhub_uuid": "invalid-uuid",
            "start_time": "2023-01-01T12:00:00",
            "end_time": "2023-01-01T11:00:00",
            "survey_date": "2025-01-01",
            "unique_id": "",
            "location_id": "",
            "surveyor_id": "",
            "client_id_manifest": "",
            "business_status": "Invalid",
            "business_operating": "maybe"
        }
    ]
    
    issues = data_quality_service.check_surveys(surveys)
    
    assert len(issues) == 9  # Missing _id, invalid formhub_uuid, invalid time range, future date, missing unique_id, missing location_id, missing surveyor_id, missing client_id_manifest, invalid business_status, invalid business_operating

