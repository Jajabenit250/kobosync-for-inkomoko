# test_data_quality_service.py
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

def test_check_locations(data_quality_service):
    locations = [
        {
            "location_id": "LOC1",
            "country": "Country1",
            "region": "Region1",
            "specific_location": "Location1"
        },
        {
            "location_id": "",
            "country": "",
            "region": "Region2",
            "specific_location": ""
        }
    ]
    
    issues = data_quality_service.check_locations(locations)
    
    assert len(issues) == 3  # Missing location_id, missing country, missing specific_location

def test_check_clients(data_quality_service):
    clients = [
        {
            "client_id_manifest": "CLI1",
            "name": "John Doe",
            "phone": "1234567890",
            "phone_type": "Smart phone",
            "gender": "Male",
            "age": 30,
            "nationality": "Country1",
            "responsible_for_people": 2
        },
        {
            "client_id_manifest": "",
            "name": "",
            "phone": "invalid",
            "phone_type": "Invalid",
            "gender": "Invalid",
            "age": -1,
            "nationality": "",
            "responsible_for_people": "invalid"
        }
    ]
    
    issues = data_quality_service.check_clients(clients)
    
    assert len(issues) == 8  # Missing client_id_manifest, missing name, invalid phone, invalid phone_type, invalid gender, invalid age, missing nationality, invalid responsible_for_people
