"""Shared test fixtures and utilities for Google Ads MCP tests."""

from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any, AsyncIterator, Dict, List
from unittest.mock import AsyncMock, Mock
import sys

import pytest
import pytest_asyncio
from fastmcp import Context
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.v24.errors.types.errors import (
    GoogleAdsError,
    GoogleAdsFailure,
)
from google.ads.googleads.v24.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)


def _install_sdk_services_aliases() -> None:
    """Map legacy test patch paths to the current service module objects."""
    import src

    sdk_package_name = "src.sdk_services"
    sdk_package = ModuleType(sdk_package_name)
    setattr(sdk_package, "__path__", [])
    sys.modules.setdefault(sdk_package_name, sdk_package)
    setattr(src, "sdk_services", sdk_package)

    services_root = Path(src.__file__).with_name("services")
    for service_file in services_root.glob("*/*_service.py"):
        category = service_file.parent.name
        module_name = service_file.stem
        actual_name = f"src.services.{category}.{module_name}"
        category_alias_name = f"{sdk_package_name}.{category}"
        module_alias_name = f"{category_alias_name}.{module_name}"

        category_package = sys.modules.get(category_alias_name)
        if category_package is None:
            category_package = ModuleType(category_alias_name)
            setattr(category_package, "__path__", [])
            sys.modules[category_alias_name] = category_package
            setattr(sdk_package, category, category_package)

        module = import_module(actual_name)
        sys.modules[module_alias_name] = module
        setattr(category_package, module_name, module)


_install_sdk_services_aliases()


@pytest.fixture
def mock_google_ads_client() -> Mock:
    """Create a mock GoogleAdsClient."""
    client = Mock(spec=GoogleAdsClient)
    client.get_service = Mock()
    return client


@pytest.fixture
def mock_sdk_client(mock_google_ads_client: Mock) -> Mock:
    """Create a mock SdkClient with a mocked GoogleAdsClient."""
    sdk_client = Mock()
    sdk_client.client = mock_google_ads_client
    return sdk_client


@pytest_asyncio.fixture
async def mock_ctx() -> AsyncIterator[AsyncMock]:
    """Create a mock FastMCP context."""
    ctx = AsyncMock(spec=Context)
    ctx.log = AsyncMock()
    yield ctx


@pytest.fixture
def mock_google_ads_service() -> Mock:
    """Create a mock GoogleAdsServiceClient."""
    service = Mock(spec=GoogleAdsServiceClient)
    service.search = Mock()
    service.search_stream = Mock()
    service.mutate = Mock()
    return service


@pytest.fixture
def google_ads_failure() -> Mock:
    """Create a sample GoogleAdsFailure for error testing."""
    failure = Mock(spec=GoogleAdsFailure)
    error = Mock(spec=GoogleAdsError)
    error.message = "Test error message"

    # Mock error code
    error.error_code = Mock()
    error.error_code.request_error = Mock()

    failure.errors = [error]
    return failure


@pytest.fixture
def google_ads_exception(google_ads_failure: Mock) -> Exception:
    """Create a GoogleAdsException for error testing."""

    # Create a real GoogleAdsException instance for proper inheritance
    # Use a custom exception class that properly inherits from Exception
    class MockGoogleAdsException(Exception):
        def __init__(self, failure: Any) -> None:
            super().__init__("Test Google Ads Exception")
            self.failure = failure
            self.error = None
            self.call = None
            self.request_id = None

    return MockGoogleAdsException(google_ads_failure)


def create_mock_proto_message(data: Dict[str, Any]) -> Mock:
    """Create a mock proto message with the given data.

    Args:
        data: Dictionary of field values

    Returns:
        Mock object that behaves like a proto message
    """
    mock_message = Mock()

    # Set attributes from data
    for key, value in data.items():
        setattr(mock_message, key, value)

    # Add common proto message methods
    mock_message.SerializeToString = Mock(return_value=b"serialized")
    mock_message.CopyFrom = Mock()
    mock_message.Clear = Mock()

    return mock_message


def create_mock_search_response(rows: List[Dict[str, Any]]) -> List[Mock]:
    """Create a mock search response with GoogleAdsRow objects.

    Args:
        rows: List of dictionaries representing row data

    Returns:
        List of mock GoogleAdsRow objects
    """
    mock_rows = []
    for row_data in rows:
        mock_row = Mock()
        for field, value in row_data.items():
            # Handle nested fields (e.g., "campaign.id" -> row.campaign.id)
            parts = field.split(".")
            current = mock_row
            for part in parts[:-1]:
                if not hasattr(current, part):
                    setattr(current, part, Mock())
                current = getattr(current, part)
            setattr(current, parts[-1], value)
        mock_rows.append(mock_row)
    return mock_rows


def create_mock_mutate_response(
    resource_names: List[str], partial_failure_error: Any = None
) -> Mock:
    """Create a mock mutate response.

    Args:
        resource_names: List of resource names for the results
        partial_failure_error: Optional partial failure error

    Returns:
        Mock mutate response
    """
    response = Mock()

    # Create results
    results = []
    for resource_name in resource_names:
        result = Mock()
        result.resource_name = resource_name
        results.append(result)

    response.results = results
    response.partial_failure_error = partial_failure_error

    return response


# Common test data
TEST_CUSTOMER_ID = "1234567890"
TEST_CAMPAIGN_ID = "111222333"
TEST_AD_GROUP_ID = "444555666"
TEST_BUDGET_ID = "777888999"
TEST_RESOURCE_NAME = f"customers/{TEST_CUSTOMER_ID}/campaigns/{TEST_CAMPAIGN_ID}"


# Helper functions for creating common mock objects
def create_mock_campaign(
    campaign_id: str = TEST_CAMPAIGN_ID,
    name: str = "Test Campaign",
    status: str = "ENABLED",
) -> Mock:
    """Create a mock Campaign object."""
    campaign = Mock()
    campaign.id = campaign_id
    campaign.name = name
    campaign.status = status
    campaign.resource_name = f"customers/{TEST_CUSTOMER_ID}/campaigns/{campaign_id}"
    return campaign


def create_mock_ad_group(
    ad_group_id: str = TEST_AD_GROUP_ID,
    campaign_id: str = TEST_CAMPAIGN_ID,
    name: str = "Test Ad Group",
    status: str = "ENABLED",
) -> Mock:
    """Create a mock AdGroup object."""
    ad_group = Mock()
    ad_group.id = ad_group_id
    ad_group.name = name
    ad_group.status = status
    ad_group.campaign = f"customers/{TEST_CUSTOMER_ID}/campaigns/{campaign_id}"
    ad_group.resource_name = f"customers/{TEST_CUSTOMER_ID}/adGroups/{ad_group_id}"
    return ad_group


def create_mock_campaign_budget(
    budget_id: str = TEST_BUDGET_ID,
    name: str = "Test Budget",
    amount_micros: int = 10000000,
) -> Mock:
    """Create a mock CampaignBudget object."""
    budget = Mock()
    budget.id = budget_id
    budget.name = name
    budget.amount_micros = amount_micros
    budget.resource_name = f"customers/{TEST_CUSTOMER_ID}/campaignBudgets/{budget_id}"
    return budget
