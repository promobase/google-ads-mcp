"""Tests for Asset Group Asset service."""

from unittest.mock import AsyncMock, MagicMock, Mock, patch
from typing import Any

import pytest
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.asset_field_type import AssetFieldTypeEnum
from google.ads.googleads.v20.enums.types.asset_link_status import AssetLinkStatusEnum
from google.ads.googleads.v20.resources.types.asset_group_asset import AssetGroupAsset
from google.ads.googleads.v20.services.types.asset_group_asset_service import (
    AssetGroupAssetOperation,
    MutateAssetGroupAssetsResponse,
    MutateAssetGroupAssetResult,
)
from google.rpc import status_pb2

from src.sdk_services.assets.asset_group_asset_service import (
    AssetGroupAssetService,
    create_asset_group_asset_tools,
)


@pytest.fixture
def asset_group_asset_service():
    """Create an Asset Group Asset service instance."""
    return AssetGroupAssetService()


@pytest.fixture
def mock_context():
    """Create a mock FastMCP context."""
    ctx = AsyncMock()
    ctx.log = AsyncMock()
    return ctx


@pytest.fixture
def mock_client():
    """Create a mock Asset Group Asset service client."""
    return MagicMock()


@pytest.mark.asyncio
class TestAssetGroupAssetService:
    """Test cases for AssetGroupAssetService."""

    async def test_create_asset_group_asset_success(
        self, asset_group_asset_service: Any, mock_context: Any, mock_client: Any
    ):
        """Test successful creation of an asset group asset link."""
        # Mock the client
        asset_group_asset_service._client = mock_client

        # Create mock response
        mock_result = MutateAssetGroupAssetResult()
        mock_result.resource_name = (
            "customers/1234567890/assetGroupAssets/9876543210~1111111111~HEADLINE"
        )

        mock_response = MutateAssetGroupAssetsResponse()
        mock_response.results.append(mock_result)  # type: ignore

        mock_client.mutate_asset_group_assets.return_value = mock_response  # type: ignore

        # Execute
        result = await asset_group_asset_service.create_asset_group_asset(
            ctx=mock_context,
            customer_id="123-456-7890",
            asset_group_id="9876543210",
            asset_id="1111111111",
            field_type=AssetFieldTypeEnum.AssetFieldType.HEADLINE,
        )

        # Verify request
        request = mock_client.mutate_asset_group_assets.call_args[1]["request"]  # type: ignore
        assert request.customer_id == "1234567890"
        assert len(request.operations) == 1
        assert request.partial_failure is False
        assert request.validate_only is False

        operation = request.operations[0]
        assert (
            operation.create.asset_group
            == "customers/1234567890/assetGroups/9876543210"
        )
        assert operation.create.asset == "customers/1234567890/assets/1111111111"
        assert operation.create.field_type == AssetFieldTypeEnum.AssetFieldType.HEADLINE

        # Verify logging
        mock_context.log.assert_called_with(  # type: ignore
            level="info",
            message="Created asset group asset link: asset 1111111111 to asset group 9876543210 as HEADLINE",
        )

    async def test_create_with_different_field_types(
        self, asset_group_asset_service: Any, mock_context: Any, mock_client: Any
    ):
        """Test creating assets with different field types."""
        asset_group_asset_service._client = mock_client

        mock_response = MutateAssetGroupAssetsResponse()
        mock_response.results.append(MutateAssetGroupAssetResult())  # type: ignore
        mock_client.mutate_asset_group_assets.return_value = mock_response  # type: ignore

        # Test with MARKETING_IMAGE
        await asset_group_asset_service.create_asset_group_asset(
            ctx=mock_context,
            customer_id="1234567890",
            asset_group_id="9999999999",
            asset_id="2222222222",
            field_type=AssetFieldTypeEnum.AssetFieldType.MARKETING_IMAGE,
        )

        request = mock_client.mutate_asset_group_assets.call_args[1]["request"]  # type: ignore
        operation = request.operations[0]
        assert (
            operation.create.field_type
            == AssetFieldTypeEnum.AssetFieldType.MARKETING_IMAGE
        )

    async def test_update_asset_group_asset_status_success(
        self, asset_group_asset_service: Any, mock_context: Any, mock_client: Any
    ):
        """Test successful update of asset group asset status."""
        asset_group_asset_service._client = mock_client

        mock_response = MutateAssetGroupAssetsResponse()
        mock_response.results.append(MutateAssetGroupAssetResult())  # type: ignore
        mock_client.mutate_asset_group_assets.return_value = mock_response  # type: ignore

        # Execute
        result = await asset_group_asset_service.update_asset_group_asset_status(
            ctx=mock_context,
            customer_id="1234567890",
            asset_group_id="9876543210",
            asset_id="1111111111",
            field_type=AssetFieldTypeEnum.AssetFieldType.HEADLINE,
            status=AssetLinkStatusEnum.AssetLinkStatus.PAUSED,
        )

        # Verify request
        request = mock_client.mutate_asset_group_assets.call_args[1]["request"]  # type: ignore
        operation = request.operations[0]

        # Check resource name format with ~ delimiter
        assert operation.update.resource_name == (
            "customers/1234567890/assetGroupAssets/9876543210~1111111111~HEADLINE"
        )
        assert operation.update.status == AssetLinkStatusEnum.AssetLinkStatus.PAUSED
        assert list(operation.update_mask.paths) == ["status"]

    async def test_remove_asset_group_asset_success(
        self, asset_group_asset_service: Any, mock_context: Any, mock_client: Any
    ):
        """Test successful removal of an asset group asset."""
        asset_group_asset_service._client = mock_client

        mock_response = MutateAssetGroupAssetsResponse()
        mock_response.results.append(MutateAssetGroupAssetResult())  # type: ignore
        mock_client.mutate_asset_group_assets.return_value = mock_response  # type: ignore

        # Execute
        result = await asset_group_asset_service.remove_asset_group_asset(
            ctx=mock_context,
            customer_id="1234567890",
            asset_group_id="9876543210",
            asset_id="3333333333",
            field_type=AssetFieldTypeEnum.AssetFieldType.YOUTUBE_VIDEO,
        )

        # Verify request
        request = mock_client.mutate_asset_group_assets.call_args[1]["request"]  # type: ignore
        operation = request.operations[0]

        # Check resource name format with ~ delimiter
        assert operation.remove == (
            "customers/1234567890/assetGroupAssets/9876543210~3333333333~YOUTUBE_VIDEO"
        )

        # Verify logging
        mock_context.log.assert_called_with(  # type: ignore
            level="info",
            message="Removed asset group asset: asset 3333333333 from asset group 9876543210",
        )

    async def test_create_with_partial_failure(
        self, asset_group_asset_service: Any, mock_context: Any, mock_client: Any
    ):
        """Test create with partial failure mode."""
        asset_group_asset_service._client = mock_client

        # Create response with partial failure error
        mock_response = MutateAssetGroupAssetsResponse()
        mock_response.results.append(MutateAssetGroupAssetResult())  # type: ignore

        partial_error = status_pb2.Status()
        partial_error.code = 3  # INVALID_ARGUMENT
        partial_error.message = "Partial failure occurred"
        mock_response.partial_failure_error.CopyFrom(partial_error)  # type: ignore

        mock_client.mutate_asset_group_assets.return_value = mock_response  # type: ignore

        result = await asset_group_asset_service.create_asset_group_asset(
            ctx=mock_context,
            customer_id="1234567890",
            asset_group_id="9876543210",
            asset_id="4444444444",
            field_type=AssetFieldTypeEnum.AssetFieldType.DESCRIPTION,
            partial_failure=True,
        )

        request = mock_client.mutate_asset_group_assets.call_args[1]["request"]  # type: ignore
        assert request.partial_failure is True

    async def test_create_api_error(
        self, asset_group_asset_service: Any, mock_context: Any, mock_client: Any
    ):
        """Test create with API error."""
        asset_group_asset_service._client = mock_client

        # Mock API error
        error = GoogleAdsException(None, None, None, None)
        error.failure = Mock()
        error.failure.__str__ = Mock(return_value="Asset not found")
        mock_client.mutate_asset_group_assets.side_effect = error  # type: ignore

        with pytest.raises(Exception) as exc_info:
            await asset_group_asset_service.create_asset_group_asset(
                ctx=mock_context,
                customer_id="1234567890",
                asset_group_id="9876543210",
                asset_id="nonexistent",
                field_type=AssetFieldTypeEnum.AssetFieldType.HEADLINE,
            )

        assert "Google Ads API error: Asset not found" in str(exc_info.value)

    async def test_update_general_error(
        self, asset_group_asset_service: Any, mock_context: Any, mock_client: Any
    ):
        """Test update with general error."""
        asset_group_asset_service._client = mock_client
        mock_client.mutate_asset_group_assets.side_effect = Exception("Network error")  # type: ignore

        with pytest.raises(Exception) as exc_info:
            await asset_group_asset_service.update_asset_group_asset_status(
                ctx=mock_context,
                customer_id="1234567890",
                asset_group_id="9876543210",
                asset_id="5555555555",
                field_type=AssetFieldTypeEnum.AssetFieldType.LOGO,
                status=AssetLinkStatusEnum.AssetLinkStatus.ENABLED,
            )

        assert "Failed to update asset group asset status: Network error" in str(
            exc_info.value
        )


@pytest.mark.asyncio
class TestAssetGroupAssetTools:
    """Test cases for Asset Group Asset tool functions."""

    async def test_create_asset_group_asset_tool(self, mock_context: Any):
        """Test create_asset_group_asset tool function."""
        service = AssetGroupAssetService()
        tools = create_asset_group_asset_tools(service)
        create_tool = tools[0]  # First tool is create_asset_group_asset

        # Mock the service method
        with patch.object(service, "create_asset_group_asset") as mock_create:
            mock_create.return_value = {  # type: ignore
                "results": [
                    {"resource_name": "customers/123/assetGroupAssets/456~789~HEADLINE"}
                ]
            }

            await create_tool(
                ctx=mock_context,
                customer_id="1234567890",
                asset_group_id="9876543210",
                asset_id="1111111111",
                field_type="HEADLINE",
            )

            mock_create.assert_called_once_with(  # type: ignore
                ctx=mock_context,
                customer_id="1234567890",
                asset_group_id="9876543210",
                asset_id="1111111111",
                field_type=AssetFieldTypeEnum.AssetFieldType.HEADLINE,
                partial_failure=False,
                validate_only=False,
            )

    async def test_update_asset_group_asset_status_tool(self, mock_context: Any):
        """Test update_asset_group_asset_status tool function."""
        service = AssetGroupAssetService()
        tools = create_asset_group_asset_tools(service)
        update_tool = tools[1]  # Second tool is update_asset_group_asset_status

        with patch.object(service, "update_asset_group_asset_status") as mock_update:
            mock_update.return_value = {"results": [{"resource_name": "test"}]}  # type: ignore

            await update_tool(
                ctx=mock_context,
                customer_id="1234567890",
                asset_group_id="9876543210",
                asset_id="2222222222",
                field_type="MARKETING_IMAGE",
                status="PAUSED",
                validate_only=True,
            )

            mock_update.assert_called_once_with(  # type: ignore
                ctx=mock_context,
                customer_id="1234567890",
                asset_group_id="9876543210",
                asset_id="2222222222",
                field_type=AssetFieldTypeEnum.AssetFieldType.MARKETING_IMAGE,
                status=AssetLinkStatusEnum.AssetLinkStatus.PAUSED,
                partial_failure=False,
                validate_only=True,
            )

    async def test_remove_asset_group_asset_tool(self, mock_context: Any):
        """Test remove_asset_group_asset tool function."""
        service = AssetGroupAssetService()
        tools = create_asset_group_asset_tools(service)
        remove_tool = tools[2]  # Third tool is remove_asset_group_asset

        with patch.object(service, "remove_asset_group_asset") as mock_remove:
            mock_remove.return_value = {"results": [{"resource_name": "test"}]}  # type: ignore

            await remove_tool(
                ctx=mock_context,
                customer_id="1234567890",
                asset_group_id="9876543210",
                asset_id="3333333333",
                field_type="YOUTUBE_VIDEO",
            )

            mock_remove.assert_called_once_with(  # type: ignore
                ctx=mock_context,
                customer_id="1234567890",
                asset_group_id="9876543210",
                asset_id="3333333333",
                field_type=AssetFieldTypeEnum.AssetFieldType.YOUTUBE_VIDEO,
                partial_failure=False,
                validate_only=False,
            )
