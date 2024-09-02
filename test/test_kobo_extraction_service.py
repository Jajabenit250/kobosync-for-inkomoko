import pytest
from unittest.mock import Mock, patch
from src.logic.kobo.kobo_service import KoboService
from src.database.entity.survey_entity import Survey
from src.database.entity.location_entity import Location
from src.database.entity.client_entity import Client
from src.database.entity.surveyor_entity import Surveyor
from src.database.entity.survey_response_entity import SurveyResponse

@pytest.fixture
def mock_clickhouse_session():
    with patch('clickhouse_sqlalchemy.create_engine') as mock_engine:
        mock_session = Mock()
        mock_engine.return_value.connect.return_value.__enter__.return_value = mock_session
        yield mock_session

@pytest.fixture
def extraction_service(mock_clickhouse_session):
    return KoboService(mock_clickhouse_session)

@pytest.mark.asyncio
async def test_extract_and_save_data(extraction_service, mock_clickhouse_session):
    mock_kobo_data = [
        {
            "_id": "1",
            "formhub/uuid": "test-uuid",
            "starttime": "2023-01-01T10:00:00",
            "endtime": "2023-01-01T11:00:00",
            "cd_survey_date": "2023-01-01",
            "sec_a/unique_id": "UID1",
            "_submission_time": "2023-01-01T12:00:00",
            "__version__": "v1",
            "meta/instanceID": "instance1",
            "_xform_id_string": "form1",
            "_status": "submitted",
            "_geolocation": [0, 0],
            "sec_a/cd_biz_country_name": "Country1",
            "sec_a/cd_biz_region_name": "Region1",
            "sec_c/cd_location": "Location1",
            "sec_b/bda_name": "Surveyor1",
            "sec_c/cd_client_id_manifest": "Client1",
            "group_mx5fl16/cd_biz_status": "Existing Business",
            "group_mx5fl16/bd_biz_operating": "yes"
        }
    ]
    
    await extraction_service.extract_and_save_data(mock_kobo_data)
    
    mock_clickhouse_session.execute.assert_called()
    mock_clickhouse_session.commit.assert_called()

@pytest.mark.asyncio
async def test_save_surveys(extraction_service, mock_clickhouse_session):
    surveys = [
        {
            "_id": "1",
            "formhub_uuid": "test-uuid",
            "start_time": "2023-01-01T10:00:00",
            "end_time": "2023-01-01T11:00:00",
            "survey_date": "2023-01-01",
            "unique_id": "UID1",
            "location_id": "LOC1",
            "surveyor_id": "SUR1",
            "client_id_manifest": "CLI1",
            "business_status": "Existing Business",
            "business_operating": "yes"
        }
    ]
    
    await extraction_service.save_surveys(surveys, mock_clickhouse_session)
    
    mock_clickhouse_session.execute.assert_called()

