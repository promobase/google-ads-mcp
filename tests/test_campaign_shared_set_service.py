"""Tests for CampaignSharedSetService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.campaign_shared_set_status import (
    CampaignSharedSetStatusEnum,
)
from google.ads.googleads.v20.enums.types.shared_set_type import SharedSetTypeEnum
from google.ads.googleads.v20.services.services.campaign_shared_set_service import (
    CampaignSharedSetServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.campaign_shared_set_service import (
    MutateCampaignSharedSetsResponse,
)

from src.sdk_services.campaign.campaign_shared_set_service import (
    CampaignSharedSetService,
    register_campaign_shared_set_tools,
)


@pytest.fixture
def campaign_shared_set_service(mock_sdk_client: Any) -> CampaignSharedSetService:
    """Create a CampaignSharedSetService instance with mocked dependencies."""
    # Mock CampaignSharedSetService client
    mock_shared_set_client = Mock(spec=CampaignSharedSetServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_shared_set_client

    with patch(
        "src.sdk_services.campaign.campaign_shared_set_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = CampaignSharedSetService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_attach_shared_set_to_campaign(
    campaign_shared_set_service: CampaignSharedSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test attaching a shared set to a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "111222333"
    shared_set_id = "444555666"
    status = "ENABLED"

    # Create mock response
    mock_response = Mock(spec=MutateCampaignSharedSetsResponse)
    mock_result = Mock()
    mock_result.resource_name = (
        "customers/1234567890/campaignSharedSets/111222333~444555666"
    )
    mock_response.results = [mock_result]

    # Get the mocked shared set service client
    mock_shared_set_client = campaign_shared_set_service.client  # type: ignore
    mock_shared_set_client.mutate_campaign_shared_sets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": "customers/1234567890/campaignSharedSets/111222333~444555666"
            }
        ]
    }

    with patch(
        "src.sdk_services.campaign.campaign_shared_set_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_shared_set_service.attach_shared_set_to_campaign(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            shared_set_id=shared_set_id,
            status=status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_shared_set_client.mutate_campaign_shared_sets.assert_called_once()  # type: ignore
    call_args = mock_shared_set_client.mutate_campaign_shared_sets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.create.campaign == f"customers/{customer_id}/campaigns/{campaign_id}"
    )
    assert (
        operation.create.shared_set
        == f"customers/{customer_id}/sharedSets/{shared_set_id}"
    )
    assert (
        operation.create.status
        == CampaignSharedSetStatusEnum.CampaignSharedSetStatus.ENABLED
    )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Attached shared set {shared_set_id} to campaign {campaign_id}",
    )


@pytest.mark.asyncio
async def test_attach_shared_sets_to_campaigns(
    campaign_shared_set_service: CampaignSharedSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test attaching multiple shared sets to campaigns."""
    # Arrange
    customer_id = "1234567890"
    attachments = [
        {"campaign_id": "111222333", "shared_set_id": "444555666", "status": "ENABLED"},
        {"campaign_id": "777888999", "shared_set_id": "444555666", "status": "REMOVED"},
        {"campaign_id": "111222333", "shared_set_id": "123456789"},  # Default ENABLED
    ]

    # Create mock response
    mock_response = Mock(spec=MutateCampaignSharedSetsResponse)
    mock_results = []
    for attachment in attachments:
        mock_result = Mock()
        mock_result.resource_name = (
            f"customers/{customer_id}/campaignSharedSets/"
            f"{attachment['campaign_id']}~{attachment['shared_set_id']}"
        )
        mock_results.append(mock_result)
    mock_response.results = mock_results

    # Get the mocked shared set service client
    mock_shared_set_client = campaign_shared_set_service.client  # type: ignore
    mock_shared_set_client.mutate_campaign_shared_sets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": mock_result.resource_name} for mock_result in mock_results
        ]
    }

    with patch(
        "src.sdk_services.campaign.campaign_shared_set_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_shared_set_service.attach_shared_sets_to_campaigns(
            ctx=mock_ctx,
            customer_id=customer_id,
            attachments=attachments,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_shared_set_client.mutate_campaign_shared_sets.assert_called_once()  # type: ignore
    call_args = mock_shared_set_client.mutate_campaign_shared_sets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 3

    # Verify each operation
    for i, attachment in enumerate(attachments):
        operation = request.operations[i]
        assert (
            operation.create.campaign
            == f"customers/{customer_id}/campaigns/{attachment['campaign_id']}"
        )
        assert (
            operation.create.shared_set
            == f"customers/{customer_id}/sharedSets/{attachment['shared_set_id']}"
        )
        expected_status = attachment.get("status", "ENABLED")
        assert operation.create.status == getattr(
            CampaignSharedSetStatusEnum.CampaignSharedSetStatus, expected_status
        )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Attached 3 shared sets to campaigns",
    )


@pytest.mark.asyncio
async def test_update_campaign_shared_set_status(
    campaign_shared_set_service: CampaignSharedSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating campaign shared set status."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "111222333"
    shared_set_id = "444555666"
    status = "REMOVED"

    # Create mock response
    mock_response = Mock(spec=MutateCampaignSharedSetsResponse)
    mock_result = Mock()
    mock_result.resource_name = (
        "customers/1234567890/campaignSharedSets/111222333~444555666"
    )
    mock_response.results = [mock_result]

    # Get the mocked shared set service client
    mock_shared_set_client = campaign_shared_set_service.client  # type: ignore
    mock_shared_set_client.mutate_campaign_shared_sets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": "customers/1234567890/campaignSharedSets/111222333~444555666"
            }
        ]
    }

    with patch(
        "src.sdk_services.campaign.campaign_shared_set_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_shared_set_service.update_campaign_shared_set_status(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            shared_set_id=shared_set_id,
            status=status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_shared_set_client.mutate_campaign_shared_sets.assert_called_once()  # type: ignore
    call_args = mock_shared_set_client.mutate_campaign_shared_sets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    # When status is REMOVED, the service just removes the attachment
    assert (
        operation.remove
        == f"customers/{customer_id}/campaignSharedSets/{campaign_id}~{shared_set_id}"
    )

    # Verify logging - when status is REMOVED, it logs a detach message
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Detached shared set {shared_set_id} from campaign {campaign_id}",
    )


@pytest.mark.asyncio
async def test_list_campaign_shared_sets(
    campaign_shared_set_service: CampaignSharedSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing campaign shared sets."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "111222333"
    shared_set_type = "NEGATIVE_KEYWORDS"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []
    shared_set_info = [
        {
            "campaign_id": "111222333",
            "shared_set_id": "444555666",
            "shared_set_name": "Negative Keywords Set 1",
            "shared_set_type": SharedSetTypeEnum.SharedSetType.NEGATIVE_KEYWORDS,
            "status": CampaignSharedSetStatusEnum.CampaignSharedSetStatus.ENABLED,
        },
        {
            "campaign_id": "111222333",
            "shared_set_id": "777888999",
            "shared_set_name": "Negative Keywords Set 2",
            "shared_set_type": SharedSetTypeEnum.SharedSetType.NEGATIVE_KEYWORDS,
            "status": CampaignSharedSetStatusEnum.CampaignSharedSetStatus.REMOVED,
        },
    ]

    for info in shared_set_info:
        row = Mock()
        row.campaign_shared_set = Mock()
        row.campaign_shared_set.resource_name = (
            f"customers/{customer_id}/campaignSharedSets/"
            f"{info['campaign_id']}~{info['shared_set_id']}"
        )
        row.campaign_shared_set.campaign = (
            f"customers/{customer_id}/campaigns/{info['campaign_id']}"
        )
        row.campaign_shared_set.shared_set = (
            f"customers/{customer_id}/sharedSets/{info['shared_set_id']}"
        )
        row.campaign_shared_set.status = info["status"]

        row.campaign = Mock()
        row.campaign.id = info["campaign_id"]
        row.campaign.name = "Test Campaign"

        row.shared_set = Mock()
        row.shared_set.id = info["shared_set_id"]
        row.shared_set.name = info["shared_set_name"]
        row.shared_set.type = info["shared_set_type"]
        row.shared_set.status = "ENABLED"

        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results

    # Mock serialize_proto_message
    def mock_serialize(obj):
        return {"campaign_shared_set": "test_data", "campaign": "test_campaign"}

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return campaign_shared_set_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    with (
        patch(
            "src.sdk_services.campaign.campaign_shared_set_service.get_sdk_client",
            return_value=mock_sdk_client,
        ),
        patch(
            "src.sdk_services.campaign.campaign_shared_set_service.serialize_proto_message",
            side_effect=mock_serialize,
        ),
    ):
        # Act
        result = await campaign_shared_set_service.list_campaign_shared_sets(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            shared_set_type=shared_set_type,
        )

    # Assert
    assert len(result) == 2

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert f"campaign.id = {campaign_id}" in query
    assert f"shared_set.type = '{shared_set_type}'" in query
    assert "FROM campaign_shared_set" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 2 campaign shared sets",
    )


@pytest.mark.asyncio
async def test_detach_shared_set_from_campaign(
    campaign_shared_set_service: CampaignSharedSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test detaching a shared set from a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "111222333"
    shared_set_id = "444555666"
    resource_name = (
        f"customers/{customer_id}/campaignSharedSets/{campaign_id}~{shared_set_id}"
    )

    # Create mock response
    mock_response = Mock(spec=MutateCampaignSharedSetsResponse)
    mock_result = Mock()
    mock_result.resource_name = resource_name
    mock_response.results = [mock_result]

    # Get the mocked shared set service client
    mock_shared_set_client = campaign_shared_set_service.client  # type: ignore
    mock_shared_set_client.mutate_campaign_shared_sets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"results": [{"resource_name": resource_name}]}

    with patch(
        "src.sdk_services.campaign.campaign_shared_set_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_shared_set_service.detach_shared_set_from_campaign(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            shared_set_id=shared_set_id,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_shared_set_client.mutate_campaign_shared_sets.assert_called_once()  # type: ignore
    call_args = mock_shared_set_client.mutate_campaign_shared_sets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.remove == resource_name

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Detached shared set {shared_set_id} from campaign {campaign_id}",
    )


@pytest.mark.asyncio
async def test_get_campaigns_using_shared_set(
    campaign_shared_set_service: CampaignSharedSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test getting campaigns using a shared set."""
    # Arrange
    customer_id = "1234567890"
    shared_set_id = "444555666"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []
    campaign_info = [
        {"campaign_id": "111222333", "campaign_name": "Campaign 1"},
        {"campaign_id": "777888999", "campaign_name": "Campaign 2"},
    ]

    for info in campaign_info:
        row = Mock()
        row.campaign_shared_set = Mock()
        row.campaign_shared_set.resource_name = (
            f"customers/{customer_id}/campaignSharedSets/"
            f"{info['campaign_id']}~{shared_set_id}"
        )
        row.campaign_shared_set.status = (
            CampaignSharedSetStatusEnum.CampaignSharedSetStatus.ENABLED
        )

        row.campaign = Mock()
        row.campaign.id = info["campaign_id"]
        row.campaign.name = info["campaign_name"]
        row.campaign.status = "ENABLED"
        row.campaign.advertising_channel_type = "SEARCH"

        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results

    # Mock serialize_proto_message
    def mock_serialize(obj):
        return {
            "campaign_shared_set": {"status": "ENABLED"},
            "campaign": {"name": "Test Campaign"},
        }

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return campaign_shared_set_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    with (
        patch(
            "src.sdk_services.campaign.campaign_shared_set_service.get_sdk_client",
            return_value=mock_sdk_client,
        ),
        patch(
            "src.sdk_services.campaign.campaign_shared_set_service.serialize_proto_message",
            side_effect=mock_serialize,
        ),
    ):
        # Act
        result = await campaign_shared_set_service.get_campaigns_using_shared_set(
            ctx=mock_ctx,
            customer_id=customer_id,
            shared_set_id=shared_set_id,
        )

    # Assert
    assert len(result) == 2

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert f"shared_set.id = {shared_set_id}" in query
    assert "FROM campaign_shared_set" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Found 2 campaigns using shared set {shared_set_id}",
    )


@pytest.mark.asyncio
async def test_error_handling_attach_shared_set(
    campaign_shared_set_service: CampaignSharedSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when attaching shared set fails."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "111222333"
    shared_set_id = "444555666"
    status = "ENABLED"

    # Get the mocked shared set service client and make it raise exception
    mock_shared_set_client = campaign_shared_set_service.client  # type: ignore
    mock_shared_set_client.mutate_campaign_shared_sets.side_effect = (
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await campaign_shared_set_service.attach_shared_set_to_campaign(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            shared_set_id=shared_set_id,
            status=status,
        )

    assert "Failed to attach shared set to campaign" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to attach shared set to campaign: Test Google Ads Exception",
    )


def test_register_campaign_shared_set_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_campaign_shared_set_tools(mock_mcp)

    # Assert
    assert isinstance(service, CampaignSharedSetService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 6  # 6 tools registered

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "attach_shared_set_to_campaign",
        "attach_shared_sets_to_campaigns",
        "update_campaign_shared_set_status",
        "list_campaign_shared_sets",
        "detach_shared_set_from_campaign",
        "get_campaigns_using_shared_set",
    ]

    assert set(tool_names) == set(expected_tools)
