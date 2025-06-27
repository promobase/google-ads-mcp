"""Tests for ExperimentService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.experiment_status import ExperimentStatusEnum
from google.ads.googleads.v20.enums.types.experiment_type import ExperimentTypeEnum
from google.ads.googleads.v20.services.services.experiment_service import (
    ExperimentServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.experiment_service import (
    MutateExperimentsResponse,
)

from src.sdk_services.campaign.experiment_service import (
    ExperimentService,
    register_experiment_tools,
)


@pytest.fixture
def experiment_service(mock_sdk_client: Any) -> ExperimentService:
    """Create an ExperimentService instance with mocked dependencies."""
    # Mock ExperimentService client
    mock_experiment_client = Mock(spec=ExperimentServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_experiment_client

    with patch(
        "src.sdk_services.campaign.experiment_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = ExperimentService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_experiment(
    experiment_service: ExperimentService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating an experiment."""
    # Arrange
    customer_id = "1234567890"
    name = "Test Experiment"
    description = "Test experiment description"
    suffix = "[experiment]"
    experiment_type = "SEARCH_CUSTOM"
    start_date = "2024-01-01"
    end_date = "2024-12-31"

    # Create mock response
    mock_response = Mock(spec=MutateExperimentsResponse)
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/experiments/444555666"
    mock_response.results = [mock_result]

    # Get the mocked experiment service client
    mock_experiment_client = experiment_service.client  # type: ignore
    mock_experiment_client.mutate_experiments.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": "customers/1234567890/experiments/444555666"}]
    }

    with patch(
        "src.sdk_services.campaign.experiment_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await experiment_service.create_experiment(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            description=description,
            suffix=suffix,
            experiment_type=experiment_type,
            start_date=start_date,
            end_date=end_date,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_experiment_client.mutate_experiments.assert_called_once()  # type: ignore
    call_args = mock_experiment_client.mutate_experiments.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert operation.create.type_ == ExperimentTypeEnum.ExperimentType.SEARCH_CUSTOM
    assert operation.create.status == ExperimentStatusEnum.ExperimentStatus.SETUP
    assert operation.create.description == description
    assert operation.create.suffix == suffix
    assert operation.create.start_date == start_date
    assert operation.create.end_date == end_date

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created experiment '{name}'",
    )


@pytest.mark.asyncio
async def test_create_experiment_minimal(
    experiment_service: ExperimentService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating an experiment with minimal parameters."""
    # Arrange
    customer_id = "1234567890"
    name = "Minimal Experiment"

    # Create mock response
    mock_response = Mock(spec=MutateExperimentsResponse)
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/experiments/444555666"
    mock_response.results = [mock_result]

    # Get the mocked experiment service client
    mock_experiment_client = experiment_service.client  # type: ignore
    mock_experiment_client.mutate_experiments.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": "customers/1234567890/experiments/444555666"}]
    }

    with patch(
        "src.sdk_services.campaign.experiment_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await experiment_service.create_experiment(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_experiment_client.mutate_experiments.assert_called_once()  # type: ignore
    call_args = mock_experiment_client.mutate_experiments.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id

    operation = request.operations[0]
    assert operation.create.name == name
    assert (
        operation.create.type_ == ExperimentTypeEnum.ExperimentType.SEARCH_CUSTOM
    )  # Default
    assert (
        not hasattr(operation.create, "description")
        or operation.create.description == ""
    )
    assert not hasattr(operation.create, "suffix") or operation.create.suffix == ""
    assert (
        not hasattr(operation.create, "start_date") or operation.create.start_date == ""
    )
    assert not hasattr(operation.create, "end_date") or operation.create.end_date == ""


@pytest.mark.asyncio
async def test_schedule_experiment(
    experiment_service: ExperimentService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test scheduling an experiment."""
    # Arrange
    customer_id = "1234567890"
    experiment_id = "444555666"
    validate_only = False

    # Create mock response
    mock_response = Mock()
    # Mock the response object to have the necessary attributes
    mock_response.resource_name = f"customers/{customer_id}/experiments/{experiment_id}"

    # Get the mocked experiment service client
    mock_experiment_client = experiment_service.client  # type: ignore
    mock_experiment_client.schedule_experiment.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "resource_name": f"customers/{customer_id}/experiments/{experiment_id}"
    }

    with patch(
        "src.sdk_services.campaign.experiment_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await experiment_service.schedule_experiment(
            ctx=mock_ctx,
            customer_id=customer_id,
            experiment_id=experiment_id,
            validate_only=validate_only,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_experiment_client.schedule_experiment.assert_called_once()  # type: ignore
    call_args = mock_experiment_client.schedule_experiment.call_args  # type: ignore
    request = call_args[1]["request"]
    assert (
        request.resource_name == f"customers/{customer_id}/experiments/{experiment_id}"
    )
    assert request.validate_only == validate_only

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Scheduled experiment {experiment_id}",
    )


@pytest.mark.asyncio
async def test_schedule_experiment_validate_only(
    experiment_service: ExperimentService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test validating experiment scheduling."""
    # Arrange
    customer_id = "1234567890"
    experiment_id = "444555666"
    validate_only = True

    # Create mock response
    mock_response = Mock()
    mock_response.resource_name = f"customers/{customer_id}/experiments/{experiment_id}"

    # Get the mocked experiment service client
    mock_experiment_client = experiment_service.client  # type: ignore
    mock_experiment_client.schedule_experiment.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "resource_name": f"customers/{customer_id}/experiments/{experiment_id}"
    }

    with patch(
        "src.sdk_services.campaign.experiment_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await experiment_service.schedule_experiment(
            ctx=mock_ctx,
            customer_id=customer_id,
            experiment_id=experiment_id,
            validate_only=validate_only,
        )

    # Assert
    assert result == expected_result

    # Verify logging for validation
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Validated experiment {experiment_id}",
    )


@pytest.mark.asyncio
async def test_end_experiment(
    experiment_service: ExperimentService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test ending an experiment."""
    # Arrange
    customer_id = "1234567890"
    experiment_id = "444555666"
    validate_only = False

    # Create mock response
    mock_response = Mock()

    # Get the mocked experiment service client
    mock_experiment_client = experiment_service.client  # type: ignore
    mock_experiment_client.end_experiment.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "resource_name": f"customers/{customer_id}/experiments/{experiment_id}"
    }

    with patch(
        "src.sdk_services.campaign.experiment_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await experiment_service.end_experiment(
            ctx=mock_ctx,
            customer_id=customer_id,
            experiment_id=experiment_id,
            validate_only=validate_only,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_experiment_client.end_experiment.assert_called_once()  # type: ignore
    call_args = mock_experiment_client.end_experiment.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.experiment == f"customers/{customer_id}/experiments/{experiment_id}"
    assert request.validate_only == validate_only

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Ended experiment {experiment_id}",
    )


@pytest.mark.asyncio
async def test_promote_experiment(
    experiment_service: ExperimentService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test promoting an experiment."""
    # Arrange
    customer_id = "1234567890"
    experiment_id = "444555666"
    validate_only = False

    # Create mock response
    mock_response = Mock()

    # Get the mocked experiment service client
    mock_experiment_client = experiment_service.client  # type: ignore
    mock_experiment_client.promote_experiment.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "resource_name": f"customers/{customer_id}/experiments/{experiment_id}"
    }

    with patch(
        "src.sdk_services.campaign.experiment_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await experiment_service.promote_experiment(
            ctx=mock_ctx,
            customer_id=customer_id,
            experiment_id=experiment_id,
            validate_only=validate_only,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_experiment_client.promote_experiment.assert_called_once()  # type: ignore
    call_args = mock_experiment_client.promote_experiment.call_args  # type: ignore
    request = call_args[1]["request"]
    assert (
        request.resource_name == f"customers/{customer_id}/experiments/{experiment_id}"
    )
    assert request.validate_only == validate_only

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Promoted experiment {experiment_id}",
    )


@pytest.mark.asyncio
async def test_list_experiments(
    experiment_service: ExperimentService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing experiments."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "111222333"
    status_filter = "ENABLED"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []
    experiment_info = [
        {
            "id": "444555666",
            "name": "Experiment 1",
            "description": "First experiment",
            "status": ExperimentStatusEnum.ExperimentStatus.ENABLED,
            "type": ExperimentTypeEnum.ExperimentType.SEARCH_CUSTOM,
            "traffic_split_percent": 50,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
        },
        {
            "id": "777888999",
            "name": "Experiment 2",
            "description": "Second experiment",
            "status": ExperimentStatusEnum.ExperimentStatus.ENABLED,
            "type": ExperimentTypeEnum.ExperimentType.DISPLAY_CUSTOM,
            "traffic_split_percent": 60,
            "start_date": "2024-02-01",
            "end_date": "2024-11-30",
        },
    ]

    for info in experiment_info:
        row = Mock()
        row.experiment = Mock()
        row.experiment.id = info["id"]
        row.experiment.name = info["name"]
        row.experiment.description = info["description"]
        row.experiment.status = info["status"]
        row.experiment.type_ = info["type"]
        row.experiment.traffic_split_percent = info["traffic_split_percent"]
        row.experiment.campaigns = [f"customers/{customer_id}/campaigns/{campaign_id}"]
        row.experiment.start_date = info["start_date"]
        row.experiment.end_date = info["end_date"]
        row.experiment.resource_name = (
            f"customers/{customer_id}/experiments/{info['id']}"
        )
        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results

    # Mock serialize_proto_message
    def mock_serialize(obj):
        return {"experiment": {"name": "Test Experiment", "status": "ENABLED"}}

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return experiment_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    with (
        patch(
            "src.sdk_services.campaign.experiment_service.get_sdk_client",
            return_value=mock_sdk_client,
        ),
        patch(
            "src.sdk_services.campaign.experiment_service.serialize_proto_message",
            side_effect=mock_serialize,
        ),
    ):
        # Act
        result = await experiment_service.list_experiments(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            status_filter=status_filter,
        )

    # Assert
    assert len(result) == 2

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert (
        f"experiment.campaigns CONTAINS 'customers/{customer_id}/campaigns/{campaign_id}'"
        in query
    )
    assert f"experiment.status = '{status_filter}'" in query
    assert "FROM experiment" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 2 experiments",
    )


@pytest.mark.asyncio
async def test_list_experiments_no_filters(
    experiment_service: ExperimentService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing all experiments without filters."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_google_ads_service.search.return_value = []

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return experiment_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    with patch(
        "src.sdk_services.campaign.experiment_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        result = await experiment_service.list_experiments(
            ctx=mock_ctx,
            customer_id=customer_id,
        )

    # Assert
    assert result == []

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    query = call_args[1]["query"]
    assert "WHERE" not in query  # No filters should be applied


@pytest.mark.asyncio
async def test_error_handling_create_experiment(
    experiment_service: ExperimentService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when creating experiment fails."""
    # Arrange
    customer_id = "1234567890"
    name = "Test Experiment"

    # Get the mocked experiment service client and make it raise exception
    mock_experiment_client = experiment_service.client  # type: ignore
    mock_experiment_client.mutate_experiments.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await experiment_service.create_experiment(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
        )

    assert "Failed to create experiment" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create experiment: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_schedule_experiment(
    experiment_service: ExperimentService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when scheduling experiment fails."""
    # Arrange
    customer_id = "1234567890"
    experiment_id = "444555666"

    # Get the mocked experiment service client and make it raise exception
    mock_experiment_client = experiment_service.client  # type: ignore
    mock_experiment_client.schedule_experiment.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await experiment_service.schedule_experiment(
            ctx=mock_ctx,
            customer_id=customer_id,
            experiment_id=experiment_id,
        )

    assert "Failed to schedule experiment" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to schedule experiment: Test Google Ads Exception",
    )


def test_register_experiment_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_experiment_tools(mock_mcp)

    # Assert
    assert isinstance(service, ExperimentService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 5  # 5 tools registered

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_experiment",
        "schedule_experiment",
        "end_experiment",
        "promote_experiment",
        "list_experiments",
    ]

    assert set(tool_names) == set(expected_tools)
