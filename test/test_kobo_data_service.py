# test_kobo_data_service.py
import pytest
from unittest.mock import Mock, patch
from src.logic.kobo.kobo_service import KoboService

@pytest.fixture
def mock_aiohttp_session():
    with patch('aiohttp.ClientSession') as mock_session:
        yield mock_session

@pytest.mark.asyncio
async def test_fetch_kobo_data(mock_aiohttp_session):
    mock_response = Mock()
    mock_response.status = 200
    mock_response.json.return_value = {"results": [{"id": 1, "data": "test"}]}
    mock_aiohttp_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response

    service = KoboService()
    result = await service.fetch_kobo_data()

    assert result == [{"id": 1, "data": "test"}]

@pytest.mark.asyncio
async def test_fetch_kobo_data_error(mock_aiohttp_session):
    mock_response = Mock()
    mock_response.status = 404
    mock_aiohttp_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response

    service = KoboService()
    with pytest.raises(Exception):
        await service.fetch_kobo_data()

