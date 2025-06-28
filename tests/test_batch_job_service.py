"""Tests for BatchJobService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.batch_job_status import BatchJobStatusEnum
from google.ads.googleads.v20.services.services.batch_job_service import (
    BatchJobServiceClient,
)
from google.ads.googleads.v20.services.types.batch_job_service import (
    AddBatchJobOperationsResponse,
    ListBatchJobResultsResponse,
    MutateBatchJobResponse,
)

from src.services.data_import.batch_job_service import (
    BatchJobService,
    register_batch_job_tools,
)


@pytest.fixture
def batch_job_service(mock_sdk_client: Any) -> BatchJobService:
    """Create a BatchJobService instance with mocked dependencies."""
    # Mock BatchJobService client
    mock_batch_job_client = Mock(spec=BatchJobServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_batch_job_client  # type: ignore

    with patch(
        "src.sdk_services.data_import.batch_job_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = BatchJobService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_batch_job(
    batch_job_service: BatchJobService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a batch job."""
    # Arrange
    customer_id = "1234567890"

    # Create mock response
    mock_response = Mock(spec=MutateBatchJobResponse)
    mock_response.result = Mock()
    mock_response.result.resource_name = f"customers/{customer_id}/batchJobs/123"  # type: ignore

    # Get the mocked batch job service client
    mock_batch_job_client = batch_job_service.client  # type: ignore
    mock_batch_job_client.mutate_batch_job.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "result": {"resource_name": f"customers/{customer_id}/batchJobs/123"}
    }

    with patch(
        "src.sdk_services.data_import.batch_job_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await batch_job_service.create_batch_job(
            ctx=mock_ctx,
            customer_id=customer_id,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_batch_job_client.mutate_batch_job.assert_called_once()  # type: ignore
    call_args = mock_batch_job_client.mutate_batch_job.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert request.operation.create is not None

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created batch job for customer {customer_id}",
    )


@pytest.mark.asyncio
async def test_get_batch_job(
    batch_job_service: BatchJobService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test getting batch job details."""
    # Arrange
    customer_id = "1234567890"
    batch_job_resource_name = f"customers/{customer_id}/batchJobs/123"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock()

    # Create mock search result
    mock_row = Mock()
    mock_row.batch_job = Mock()
    mock_row.batch_job.resource_name = batch_job_resource_name  # type: ignore
    mock_row.batch_job.id = 123  # type: ignore
    mock_row.batch_job.status = BatchJobStatusEnum.BatchJobStatus.PENDING  # type: ignore
    mock_row.batch_job.long_running_operation = ""  # type: ignore
    mock_row.batch_job.metadata = Mock()  # type: ignore
    mock_row.batch_job.metadata.creation_date_time = "2024-01-01 12:00:00"  # type: ignore
    mock_row.batch_job.metadata.start_date_time = ""  # type: ignore
    mock_row.batch_job.metadata.completion_date_time = ""  # type: ignore
    mock_row.batch_job.metadata.estimated_completion_ratio = 0.0  # type: ignore
    mock_row.batch_job.metadata.operation_count = 0  # type: ignore
    mock_row.batch_job.metadata.executed_operation_count = 0  # type: ignore

    mock_google_ads_service.search.return_value = [mock_row]  # type: ignore

    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return batch_job_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "batch_job": {
            "resource_name": batch_job_resource_name,
            "id": 123,
            "status": "PENDING",
        }
    }

    with (
        patch(
            "src.sdk_services.data_import.batch_job_service.get_sdk_client",
            return_value=mock_sdk_client,
        ),
        patch(
            "src.sdk_services.data_import.batch_job_service.serialize_proto_message",
            return_value=expected_result,
        ),
    ):
        # Act
        result = await batch_job_service.get_batch_job(
            ctx=mock_ctx,
            customer_id=customer_id,
            batch_job_resource_name=batch_job_resource_name,
        )

    # Assert
    assert result == expected_result

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert "WHERE batch_job.id = 123" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Retrieved batch job details",
    )


@pytest.mark.asyncio
async def test_add_operations_to_batch_job(
    batch_job_service: BatchJobService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding operations to a batch job."""
    # Arrange
    customer_id = "1234567890"
    batch_job_resource_name = f"customers/{customer_id}/batchJobs/123"
    operations_data = [
        {"type": "campaign", "name": "Test Campaign 1"},
        {"type": "ad_group", "name": "Test Ad Group 1"},
    ]

    # Create mock response
    mock_response = Mock(spec=AddBatchJobOperationsResponse)
    mock_response.sequence_token = "abc123"
    mock_response.next_sequence_token = "def456"

    # Get the mocked batch job service client
    mock_batch_job_client = batch_job_service.client  # type: ignore
    mock_batch_job_client.add_batch_job_operations.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "sequence_token": "abc123",
        "next_sequence_token": "def456",
    }

    with patch(
        "src.sdk_services.data_import.batch_job_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await batch_job_service.add_operations_to_batch_job(
            ctx=mock_ctx,
            customer_id=customer_id,
            batch_job_resource_name=batch_job_resource_name,
            operations_data=operations_data,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_batch_job_client.add_batch_job_operations.assert_called_once()  # type: ignore
    call_args = mock_batch_job_client.add_batch_job_operations.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.resource_name == batch_job_resource_name
    assert request.sequence_token == ""
    assert len(request.mutate_operations) == 2

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Added 2 operations to batch job",
    )


@pytest.mark.asyncio
async def test_run_batch_job(
    batch_job_service: BatchJobService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test running a batch job."""
    # Arrange
    customer_id = "1234567890"
    batch_job_resource_name = f"customers/{customer_id}/batchJobs/123"

    # Create mock long running operation
    mock_operation = Mock()
    mock_operation.name = "operations/12345"

    # Get the mocked batch job service client
    mock_batch_job_client = batch_job_service.client  # type: ignore
    mock_batch_job_client.run_batch_job.return_value = mock_operation  # type: ignore

    # Act
    result = await batch_job_service.run_batch_job(
        ctx=mock_ctx,
        customer_id=customer_id,
        batch_job_resource_name=batch_job_resource_name,
    )

    # Assert
    assert result["batch_job_resource_name"] == batch_job_resource_name
    assert result["status"] == "RUNNING"
    assert "long_running_operation" in result

    # Verify the API call
    mock_batch_job_client.run_batch_job.assert_called_once()  # type: ignore
    call_args = mock_batch_job_client.run_batch_job.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.resource_name == batch_job_resource_name

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Started batch job execution",
    )


@pytest.mark.asyncio
async def test_list_batch_job_results(
    batch_job_service: BatchJobService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing batch job results."""
    # Arrange
    customer_id = "1234567890"
    batch_job_resource_name = f"customers/{customer_id}/batchJobs/123"
    page_size = 100

    # Create mock response
    mock_response = Mock(spec=ListBatchJobResultsResponse)
    mock_response.results = []

    # Create mock results
    result1 = Mock()
    result1.operation_index = 0
    result1.mutate_operation_response = Mock()
    result1.mutate_operation_response.campaign_result = Mock()
    result1.mutate_operation_response.campaign_result.resource_name = (
        f"customers/{customer_id}/campaigns/456"
    )

    result2 = Mock()
    result2.operation_index = 1
    result2.mutate_operation_response = Mock()
    result2.mutate_operation_response.ad_group_result = Mock()
    result2.mutate_operation_response.ad_group_result.resource_name = (
        f"customers/{customer_id}/adGroups/789"
    )

    mock_response.results.extend([result1, result2])  # type: ignore
    mock_response.next_page_token = "next123"

    # Get the mocked batch job service client
    mock_batch_job_client = batch_job_service.client  # type: ignore
    mock_batch_job_client.list_batch_job_results.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "operation_index": 0,
                "mutate_operation_response": {
                    "campaign_result": {
                        "resource_name": f"customers/{customer_id}/campaigns/456"
                    }
                },
            },
            {
                "operation_index": 1,
                "mutate_operation_response": {
                    "ad_group_result": {
                        "resource_name": f"customers/{customer_id}/adGroups/789"
                    }
                },
            },
        ],
        "next_page_token": "next123",
    }

    with patch(
        "src.sdk_services.data_import.batch_job_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await batch_job_service.list_batch_job_results(
            ctx=mock_ctx,
            customer_id=customer_id,
            batch_job_resource_name=batch_job_resource_name,
            page_size=page_size,
        )

    # Assert
    assert result == expected_result
    assert len(result["results"]) == 2

    # Verify the API call
    mock_batch_job_client.list_batch_job_results.assert_called_once()  # type: ignore
    call_args = mock_batch_job_client.list_batch_job_results.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.resource_name == batch_job_resource_name
    assert request.page_size == page_size

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Retrieved batch job results",
    )


@pytest.mark.asyncio
async def test_list_batch_jobs(
    batch_job_service: BatchJobService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing batch jobs."""
    # Arrange
    customer_id = "1234567890"
    status_filter = "PENDING"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock()

    # Create mock search results
    mock_results = []
    for i in range(3):
        row = Mock()
        row.batch_job = Mock()
        row.batch_job.resource_name = f"customers/{customer_id}/batchJobs/{i + 100}"
        row.batch_job.id = i + 100
        row.batch_job.status = BatchJobStatusEnum.BatchJobStatus.PENDING
        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return batch_job_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    # Act
    with (
        patch(
            "src.sdk_services.data_import.batch_job_service.get_sdk_client",
            return_value=mock_sdk_client,
        ),
        patch(
            "src.sdk_services.data_import.batch_job_service.serialize_proto_message",
            side_effect=[
                {"batch_job": {"id": i + 100, "status": "PENDING"}} for i in range(3)
            ],
        ),
    ):
        result = await batch_job_service.list_batch_jobs(
            ctx=mock_ctx,
            customer_id=customer_id,
            status_filter=status_filter,
        )

    # Assert
    assert len(result) == 3
    assert all(job["batch_job"]["status"] == "PENDING" for job in result)

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert f"WHERE batch_job.status = '{status_filter}'" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 3 batch jobs",
    )


@pytest.mark.asyncio
async def test_error_handling(
    batch_job_service: BatchJobService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    customer_id = "1234567890"

    # Get the mocked batch job service client and make it raise exception
    mock_batch_job_client = batch_job_service.client  # type: ignore
    mock_batch_job_client.mutate_batch_job.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await batch_job_service.create_batch_job(
            ctx=mock_ctx,
            customer_id=customer_id,
        )

    assert "Failed to create batch job" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create batch job: Test Google Ads Exception",
    )


def test_register_batch_job_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_batch_job_tools(mock_mcp)

    # Assert
    assert isinstance(service, BatchJobService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 6  # 6 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_batch_job",
        "get_batch_job",
        "add_operations_to_batch_job",
        "run_batch_job",
        "list_batch_job_results",
        "list_batch_jobs",
    ]

    assert set(tool_names) == set(expected_tools)
