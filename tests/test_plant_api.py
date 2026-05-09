"""Tests for the HYXI Plant API methods."""

import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

if "aiohttp" not in sys.modules or not hasattr(sys.modules["aiohttp"], "ClientError"):
    m = MagicMock()
    m.ClientError = Exception
    m.ClientResponseError = type("ClientResponseError", (Exception,), {})
    m.ContentTypeError = type("ContentTypeError", (Exception,), {})
    sys.modules["aiohttp"] = m

from src.hyxi_cloud_api.api import HyxiApiClient


def _client() -> HyxiApiClient:
    api = HyxiApiClient("ak", "sk", "https://api.com", MagicMock())
    api._refresh_token = AsyncMock(return_value=True)
    api._request = AsyncMock(
        return_value=(200, {"code": "0", "msg": "Success", "data": {}, "success": True})
    )
    return api


def _request_body(api: HyxiApiClient) -> dict:
    return api._request.call_args.kwargs["json"]


@pytest.mark.asyncio
async def test_create_plant():
    """Test create_plant payload."""
    api = _client()
    location = {"lat": "39.456", "lng": "120.123"}

    await api.create_plant("Europe/Amsterdam", "Plant A", 1, 5000, location)

    call_args = api._request.call_args
    assert call_args.args[:2] == ("POST", "/api/plant/v1/create")
    assert _request_body(api) == {
        "timeZone": "Europe/Amsterdam",
        "plantName": "Plant A",
        "plantType": 1,
        "capacity": 5000,
        "apiLocation": location,
    }


@pytest.mark.asyncio
async def test_configure_plant_price():
    """Test configure_plant_price payload."""
    api = _client()
    tou = {"grid": [], "use": []}

    await api.configure_plant_price("PLANT1", 2, "EUR", tou=tou)

    call_args = api._request.call_args
    assert call_args.args[:2] == ("POST", "/api/plant/v1/plantPrice")
    assert _request_body(api) == {
        "plantId": "PLANT1",
        "priceType": 2,
        "fixedPrice": None,
        "currencyUnit": "EUR",
        "tou": tou,
    }


@pytest.mark.asyncio
async def test_query_plant_list():
    """Test query_plant_list payload."""
    api = _client()

    await api.query_plant_list(page_size=25, current_page=2)

    call_args = api._request.call_args
    assert call_args.args[:2] == ("POST", "/api/plant/v1/page")
    assert _request_body(api) == {"pageSize": 25, "currentPage": 2}


@pytest.mark.asyncio
async def test_query_plant_info():
    """Test query_plant_info params."""
    api = _client()

    await api.query_plant_info("PLANT1")

    call_args = api._request.call_args
    assert call_args.args[:2] == ("GET", "/api/plant/v1/info")
    assert call_args.kwargs["params"] == {"plantId": "PLANT1"}


@pytest.mark.asyncio
async def test_query_plant_device_page():
    """Test query_plant_device_page payload."""
    api = _client()

    await api.query_plant_device_page(
        "PLANT1", device_type="COLLECTOR", page_size=50, current_page=3
    )

    call_args = api._request.call_args
    assert call_args.args[:2] == ("POST", "/api/plant/v1/devicePage")
    assert _request_body(api) == {
        "plantId": "PLANT1",
        "deviceType": "COLLECTOR",
        "pageSize": 50,
        "currentPage": 3,
    }


@pytest.mark.asyncio
async def test_query_plant_power_generation():
    """Test query_plant_power_generation payload."""
    api = _client()

    await api.query_plant_power_generation("PLANT1")

    call_args = api._request.call_args
    assert call_args.args[:2] == ("POST", "/api/plant/v1/queryPowerGeneration")
    assert _request_body(api) == {"plantId": "PLANT1"}


@pytest.mark.asyncio
async def test_query_plant_yield_statistics():
    """Test query_plant_yield_statistics payload."""
    api = _client()

    await api.query_plant_yield_statistics("PLANT1", time_type=3, start_time=2024)

    call_args = api._request.call_args
    assert call_args.args[:2] == ("POST", "/api/plant/v1/queryPlantYeildStatistics")
    assert _request_body(api) == {
        "plantId": "PLANT1",
        "timeType": 3,
        "startTime": 2024,
    }


@pytest.mark.asyncio
async def test_query_plant_power_statistics():
    """Test query_plant_power_statistics payload."""
    api = _client()

    await api.query_plant_power_statistics("PLANT1", "2026-05-09")

    call_args = api._request.call_args
    assert call_args.args[:2] == ("POST", "/api/plant/v1/queryPlantPowerStatistics")
    assert _request_body(api) == {"plantId": "PLANT1", "startTime": "2026-05-09"}


@pytest.mark.asyncio
async def test_query_plant_weather():
    """Test query_plant_weather params."""
    api = _client()

    await api.query_plant_weather("PLANT1", days=7)

    call_args = api._request.call_args
    assert call_args.args[:2] == ("GET", "/api/plant/v1/weather")
    assert call_args.kwargs["params"] == {"plantId": "PLANT1", "days": 7}


@pytest.mark.asyncio
async def test_update_plant():
    """Test update_plant payload."""
    api = _client()
    location = {"lat": "39.456", "lng": "120.123"}

    await api.update_plant("PLANT1", "Europe/Amsterdam", "Plant A", 1, 5000, location)

    call_args = api._request.call_args
    assert call_args.args[:2] == ("POST", "/api/plant/v1/update")
    assert _request_body(api) == {
        "plantId": "PLANT1",
        "timeZone": "Europe/Amsterdam",
        "plantName": "Plant A",
        "plantType": 1,
        "capacity": 5000,
        "apiLocation": location,
    }


@pytest.mark.asyncio
async def test_delete_plant():
    """Test delete_plant payload."""
    api = _client()

    await api.delete_plant("PLANT1")

    call_args = api._request.call_args
    assert call_args.args[:2] == ("POST", "/api/plant/v1/delete")
    assert _request_body(api) == {"plantId": "PLANT1"}


@pytest.mark.asyncio
async def test_fetch_plants_reuses_plant_page_request():
    """Test existing plant fetch path reuses the shared plant page request."""
    api = _client()
    api._request.return_value = (
        200,
        {"success": True, "data": {"list": [{"plantId": "PLANT1"}]}},
    )

    plants = await api._fetch_plants()

    assert plants == [{"plantId": "PLANT1"}]
    call_args = api._request.call_args
    assert call_args.args[:2] == ("POST", "/api/plant/v1/page")
    assert _request_body(api) == {"pageSize": 10, "currentPage": 1}


@pytest.mark.asyncio
async def test_fetch_device_list_reuses_plant_device_page_request():
    """Test existing device fetch path reuses the shared plant device page request."""
    api = _client()
    api._request.return_value = (
        200,
        {"success": True, "data": {"deviceList": [{"deviceSn": "SN1"}]}},
    )

    devices = await api._fetch_device_list_for_plant("PLANT1")

    assert devices == [{"deviceSn": "SN1"}]
    call_args = api._request.call_args
    assert call_args.args[:2] == ("POST", "/api/plant/v1/devicePage")
    assert _request_body(api) == {
        "plantId": "PLANT1",
        "deviceType": "",
        "pageSize": 50,
        "currentPage": 1,
    }


@pytest.mark.asyncio
async def test_plant_error_on_auth_failed():
    """Test PlantError is raised when authentication fails."""
    api = HyxiApiClient("ak", "sk", "https://api.com", MagicMock())
    api._refresh_token = AsyncMock(return_value="auth_failed")

    with pytest.raises(api.PlantError, match="Authentication failed"):
        await api.query_plant_info("PLANT1")


@pytest.mark.asyncio
async def test_plant_error_on_api_failure():
    """Test PlantError is raised when the API returns success=False."""
    api = _client()
    api._request.return_value = (
        200,
        {"success": False, "code": "C000001", "msg": "Parameter error"},
    )

    with pytest.raises(api.PlantError, match="query plant info failed"):
        await api.query_plant_info("PLANT1")


@pytest.mark.asyncio
async def test_plant_validation():
    """Test Plant API input validation."""
    api = _client()

    with pytest.raises(ValueError, match="plant_id must be a non-empty string"):
        await api.query_plant_info("")

    with pytest.raises(ValueError, match="page_size must be a positive integer"):
        await api.query_plant_list(page_size=0)

    with pytest.raises(ValueError, match="current_page must be a positive integer"):
        await api.query_plant_list(current_page=0)

    with pytest.raises(ValueError, match="plant_type must be one of"):
        await api.create_plant("Europe/Amsterdam", "Plant A", 9, 5000, {})

    with pytest.raises(ValueError, match="api_location must be a dictionary"):
        await api.create_plant("Europe/Amsterdam", "Plant A", 1, 5000, None)

    with pytest.raises(ValueError, match="capacity must be a positive number"):
        await api.update_plant("PLANT1", "Europe/Amsterdam", "Plant A", 1, 0, {})

    with pytest.raises(ValueError, match="price_type must be one of"):
        await api.configure_plant_price("PLANT1", 3, "EUR")

    with pytest.raises(ValueError, match="fixed_price is required"):
        await api.configure_plant_price("PLANT1", 1, "EUR")

    with pytest.raises(ValueError, match="tou is required"):
        await api.configure_plant_price("PLANT1", 2, "EUR")

    with pytest.raises(ValueError, match="time_type must be one of"):
        await api.query_plant_yield_statistics("PLANT1", 9, 2024)

    with pytest.raises(ValueError, match="days must be between 1 and 7"):
        await api.query_plant_weather("PLANT1", 8)
