"""Tests for Customer Asset Service."""

import pytest
from unittest.mock import Mock, patch

from google.ads.googleads.v20.services.services.customer_asset_service import (
    CustomerAssetServiceClient,
)
from google.ads.googleads.v20.services.types.customer_asset_service import (
    CustomerAssetOperation,
    MutateCustomerAssetsRequest,
    MutateCustomerAssetsResponse,
    MutateCustomerAssetResult,
)
from google.ads.googleads.v20.resources.types.customer_asset import CustomerAsset
from google.ads.googleads.v20.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v20.enums.types.asset_field_type import (
    AssetFieldTypeEnum,
)
from google.ads.googleads.v20.enums.types.asset_link_status import (
    AssetLinkStatusEnum,
)
from google.protobuf import field_mask_pb2

from src.sdk_services.assets.customer_asset_service import CustomerAssetService
from src.core.exceptions import GoogleAdsException


class TestCustomerAssetService:
    """Test cases for CustomerAssetService."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock CustomerAssetServiceClient."""
        return Mock(spec=CustomerAssetServiceClient)

    @pytest.fixture
    def service(self, mock_client):
        """Create a CustomerAssetService instance with mock client."""
        return CustomerAssetService(mock_client)

    def test_mutate_customer_assets_success(self, service, mock_client):
        """Test successful customer assets mutation."""
        # Arrange
        customer_id = "1234567890"
        operations = [Mock(spec=CustomerAssetOperation)]
        expected_response = MutateCustomerAssetsResponse(
            results=[
                MutateCustomerAssetResult(
                    resource_name="customers/1234567890/customerAssets/123~LOGO"
                )
            ]
        )
        mock_client.mutate_customer_assets.return_value = expected_response

        # Act
        response = service.mutate_customer_assets(
            customer_id=customer_id,
            operations=operations,
        )

        # Assert
        assert response == expected_response
        mock_client.mutate_customer_assets.assert_called_once()

        call_args = mock_client.mutate_customer_assets.call_args[1]
        request = call_args["request"]
        assert isinstance(request, MutateCustomerAssetsRequest)
        assert request.customer_id == customer_id
        assert request.operations == operations
        assert request.partial_failure is False
        assert request.validate_only is False

    def test_mutate_customer_assets_with_options(self, service, mock_client):
        """Test customer assets mutation with all options."""
        # Arrange
        customer_id = "1234567890"
        operations = [Mock(spec=CustomerAssetOperation)]
        expected_response = MutateCustomerAssetsResponse()
        mock_client.mutate_customer_assets.return_value = expected_response

        # Act
        response = service.mutate_customer_assets(
            customer_id=customer_id,
            operations=operations,
            partial_failure=True,
            validate_only=True,
            response_content_type=ResponseContentTypeEnum.ResponseContentType.MUTABLE_RESOURCE,
        )

        # Assert
        assert response == expected_response
        call_args = mock_client.mutate_customer_assets.call_args[1]
        request = call_args["request"]
        assert request.partial_failure is True
        assert request.validate_only is True
        assert (
            request.response_content_type
            == ResponseContentTypeEnum.ResponseContentType.MUTABLE_RESOURCE
        )

    def test_mutate_customer_assets_failure(self, service, mock_client):
        """Test customer assets mutation failure."""
        # Arrange
        customer_id = "1234567890"
        operations = [Mock(spec=CustomerAssetOperation)]
        mock_client.mutate_customer_assets.side_effect = Exception("API Error")

        # Act & Assert
        with pytest.raises(
            GoogleAdsException, match="Failed to mutate customer assets"
        ):
            service.mutate_customer_assets(
                customer_id=customer_id,
                operations=operations,
            )

    def test_create_customer_asset_operation(self, service):
        """Test creating customer asset operation."""
        # Arrange
        asset = "customers/1234567890/assets/123"
        field_type = AssetFieldTypeEnum.AssetFieldType.LOGO
        status = AssetLinkStatusEnum.AssetLinkStatus.ENABLED

        # Act
        operation = service.create_customer_asset_operation(
            asset=asset,
            field_type=field_type,
            status=status,
        )

        # Assert
        assert isinstance(operation, CustomerAssetOperation)
        assert operation.create.asset == asset
        assert operation.create.field_type == field_type
        assert operation.create.status == status

    def test_create_update_operation(self, service):
        """Test creating update operation."""
        # Arrange
        resource_name = "customers/1234567890/customerAssets/123~LOGO"
        status = AssetLinkStatusEnum.AssetLinkStatus.PAUSED

        # Act
        operation = service.create_update_operation(
            resource_name=resource_name,
            status=status,
        )

        # Assert
        assert isinstance(operation, CustomerAssetOperation)
        assert operation.update.resource_name == resource_name
        assert operation.update.status == status
        assert operation.update_mask.paths == ["status"]

    def test_create_update_operation_with_custom_mask(self, service):
        """Test creating update operation with custom field mask."""
        # Arrange
        resource_name = "customers/1234567890/customerAssets/123~LOGO"
        status = AssetLinkStatusEnum.AssetLinkStatus.PAUSED
        update_mask = field_mask_pb2.FieldMask(paths=["status", "custom_field"])

        # Act
        operation = service.create_update_operation(
            resource_name=resource_name,
            status=status,
            update_mask=update_mask,
        )

        # Assert
        assert isinstance(operation, CustomerAssetOperation)
        assert operation.update_mask == update_mask

    def test_create_remove_operation(self, service):
        """Test creating remove operation."""
        # Arrange
        resource_name = "customers/1234567890/customerAssets/123~LOGO"

        # Act
        operation = service.create_remove_operation(resource_name=resource_name)

        # Assert
        assert isinstance(operation, CustomerAssetOperation)
        assert operation.remove == resource_name
        assert not operation.create
        assert not operation.update

    def test_create_customer_asset(self, service, mock_client):
        """Test creating a single customer asset."""
        # Arrange
        customer_id = "1234567890"
        asset = "customers/1234567890/assets/123"
        field_type = AssetFieldTypeEnum.AssetFieldType.LOGO
        status = AssetLinkStatusEnum.AssetLinkStatus.ENABLED

        expected_response = MutateCustomerAssetsResponse(
            results=[
                MutateCustomerAssetResult(
                    resource_name="customers/1234567890/customerAssets/123~LOGO"
                )
            ]
        )
        mock_client.mutate_customer_assets.return_value = expected_response

        # Act
        response = service.create_customer_asset(
            customer_id=customer_id,
            asset=asset,
            field_type=field_type,
            status=status,
        )

        # Assert
        assert response == expected_response
        mock_client.mutate_customer_assets.assert_called_once()

    def test_update_customer_asset_status(self, service, mock_client):
        """Test updating customer asset status."""
        # Arrange
        customer_id = "1234567890"
        resource_name = "customers/1234567890/customerAssets/123~LOGO"
        status = AssetLinkStatusEnum.AssetLinkStatus.PAUSED

        expected_response = MutateCustomerAssetsResponse(
            results=[MutateCustomerAssetResult(resource_name=resource_name)]
        )
        mock_client.mutate_customer_assets.return_value = expected_response

        # Act
        response = service.update_customer_asset_status(
            customer_id=customer_id,
            resource_name=resource_name,
            status=status,
        )

        # Assert
        assert response == expected_response
        mock_client.mutate_customer_assets.assert_called_once()

    def test_remove_customer_asset(self, service, mock_client):
        """Test removing customer asset."""
        # Arrange
        customer_id = "1234567890"
        resource_name = "customers/1234567890/customerAssets/123~LOGO"

        expected_response = MutateCustomerAssetsResponse(
            results=[MutateCustomerAssetResult(resource_name=resource_name)]
        )
        mock_client.mutate_customer_assets.return_value = expected_response

        # Act
        response = service.remove_customer_asset(
            customer_id=customer_id,
            resource_name=resource_name,
        )

        # Assert
        assert response == expected_response
        mock_client.mutate_customer_assets.assert_called_once()


@pytest.mark.asyncio
class TestCustomerAssetMCPServer:
    """Test cases for Customer Asset MCP server."""

    @patch("src.sdk_servers.customer_asset_server.get_client")
    async def test_create_customer_asset_tool(self, mock_get_client):
        """Test create customer asset MCP tool."""
        # Arrange
        from src.sdk_servers.customer_asset_server import create_customer_asset_server

        mock_client = Mock(spec=CustomerAssetServiceClient)
        mock_get_client.return_value = mock_client

        mock_response = MutateCustomerAssetsResponse(
            results=[
                MutateCustomerAssetResult(
                    resource_name="customers/1234567890/customerAssets/123~LOGO"
                )
            ]
        )
        mock_client.mutate_customer_assets.return_value = mock_response

        server = create_customer_asset_server()

        # Act
        response = await server.call_tool()(
            name="create_customer_asset",
            arguments={
                "customer_id": "1234567890",
                "asset": "customers/1234567890/assets/123",
                "field_type": "LOGO",
                "status": "ENABLED",
            },
        )

        # Assert
        assert len(response) == 1
        assert "customers/1234567890/customerAssets/123~LOGO" in response[0].text
        assert "create" in response[0].text

    @patch("src.sdk_servers.customer_asset_server.get_client")
    async def test_update_customer_asset_status_tool(self, mock_get_client):
        """Test update customer asset status MCP tool."""
        # Arrange
        from src.sdk_servers.customer_asset_server import create_customer_asset_server

        mock_client = Mock(spec=CustomerAssetServiceClient)
        mock_get_client.return_value = mock_client

        mock_response = MutateCustomerAssetsResponse(
            results=[
                MutateCustomerAssetResult(
                    resource_name="customers/1234567890/customerAssets/123~LOGO"
                )
            ]
        )
        mock_client.mutate_customer_assets.return_value = mock_response

        server = create_customer_asset_server()

        # Act
        response = await server.call_tool()(
            name="update_customer_asset_status",
            arguments={
                "customer_id": "1234567890",
                "resource_name": "customers/1234567890/customerAssets/123~LOGO",
                "status": "PAUSED",
            },
        )

        # Assert
        assert len(response) == 1
        assert "customers/1234567890/customerAssets/123~LOGO" in response[0].text
        assert "update_status" in response[0].text
        assert "PAUSED" in response[0].text
