"""Tests for Conversion Custom Variable service."""

from unittest.mock import AsyncMock, MagicMock, Mock, patch
from typing import Any

import pytest
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.conversion_custom_variable_status import (
    ConversionCustomVariableStatusEnum,
)
from google.ads.googleads.v20.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v20.resources.types.conversion_custom_variable import (
    ConversionCustomVariable,
)
from google.ads.googleads.v20.services.types.conversion_custom_variable_service import (
    MutateConversionCustomVariablesResponse,
    MutateConversionCustomVariableResult,
)
from google.rpc import status_pb2

from src.services.conversions.conversion_custom_variable_service import (
    ConversionCustomVariableService,
    create_conversion_custom_variable_tools,
)


@pytest.fixture
def conversion_custom_variable_service():
    """Create a Conversion Custom Variable service instance."""
    return ConversionCustomVariableService()


@pytest.fixture
def mock_context():
    """Create a mock FastMCP context."""
    ctx = AsyncMock()
    ctx.log = AsyncMock()
    return ctx


@pytest.fixture
def mock_client():
    """Create a mock Conversion Custom Variable service client."""
    return MagicMock()


@pytest.mark.asyncio
class TestConversionCustomVariableService:
    """Test cases for ConversionCustomVariableService."""

    async def test_create_conversion_custom_variable_success(
        self,
        conversion_custom_variable_service: Any,
        mock_context: Any,
        mock_client: Any,
    ):
        """Test successful creation of a conversion custom variable."""
        # Mock the client
        conversion_custom_variable_service._client = mock_client

        # Create mock response
        mock_result = MutateConversionCustomVariableResult()
        mock_result.resource_name = (
            "customers/1234567890/conversionCustomVariables/123456"
        )

        mock_custom_var = ConversionCustomVariable()
        mock_custom_var.resource_name = mock_result.resource_name
        mock_custom_var.id = 123456
        mock_custom_var.name = "Product Category"
        mock_custom_var.tag = "product_category"
        mock_result.conversion_custom_variable.CopyFrom(mock_custom_var)  # type: ignore

        mock_response = MutateConversionCustomVariablesResponse()
        mock_response.results.append(mock_result)  # type: ignore

        mock_client.mutate_conversion_custom_variables.return_value = mock_response  # type: ignore

        # Execute
        _ = await conversion_custom_variable_service.create_conversion_custom_variable(
            ctx=mock_context,
            customer_id="123-456-7890",
            name="Product Category",
            tag="product_category",
            status=ConversionCustomVariableStatusEnum.ConversionCustomVariableStatus.ENABLED,
        )

        # Verify request
        request = mock_client.mutate_conversion_custom_variables.call_args[1]["request"]  # type: ignore
        assert request.customer_id == "1234567890"
        assert len(request.operations) == 1
        assert request.partial_failure is False
        assert request.validate_only is False
        assert (
            request.response_content_type
            == ResponseContentTypeEnum.ResponseContentType.MUTABLE_RESOURCE
        )

        operation = request.operations[0]
        assert operation.create.name == "Product Category"
        assert operation.create.tag == "product_category"
        assert (
            operation.create.status
            == ConversionCustomVariableStatusEnum.ConversionCustomVariableStatus.ENABLED
        )

        # Verify logging
        mock_context.log.assert_called_with(  # type: ignore
            level="info",
            message="Created conversion custom variable 'Product Category' with tag 'product_category' for customer 1234567890",
        )

    async def test_create_with_tag_normalization(
        self,
        conversion_custom_variable_service: Any,
        mock_context: Any,
        mock_client: Any,
    ):
        """Test that tags are normalized to lowercase and trimmed."""
        conversion_custom_variable_service._client = mock_client

        mock_response = MutateConversionCustomVariablesResponse()
        mock_response.results.append(MutateConversionCustomVariableResult())  # type: ignore
        mock_client.mutate_conversion_custom_variables.return_value = mock_response  # type: ignore

        await conversion_custom_variable_service.create_conversion_custom_variable(
            ctx=mock_context,
            customer_id="1234567890",
            name="  Customer Type  ",
            tag="  CUSTOMER_TYPE  ",
        )

        request = mock_client.mutate_conversion_custom_variables.call_args[1]["request"]  # type: ignore
        operation = request.operations[0]
        assert operation.create.name == "Customer Type"  # Trimmed
        assert operation.create.tag == "customer_type"  # Lowercase and trimmed

    async def test_update_conversion_custom_variable_success(
        self,
        conversion_custom_variable_service: Any,
        mock_context: Any,
        mock_client: Any,
    ):
        """Test successful update of a conversion custom variable."""
        conversion_custom_variable_service._client = mock_client

        # Create mock response
        mock_result = MutateConversionCustomVariableResult()
        mock_result.resource_name = (
            "customers/1234567890/conversionCustomVariables/123456"
        )

        mock_response = MutateConversionCustomVariablesResponse()
        mock_response.results.append(mock_result)  # type: ignore

        mock_client.mutate_conversion_custom_variables.return_value = mock_response  # type: ignore

        # Execute
        _ = await conversion_custom_variable_service.update_conversion_custom_variable(
            ctx=mock_context,
            customer_id="1234567890",
            custom_variable_id=123456,
            name="Updated Product Category",
            status=ConversionCustomVariableStatusEnum.ConversionCustomVariableStatus.PAUSED,
        )

        # Verify request
        request = mock_client.mutate_conversion_custom_variables.call_args[1]["request"]  # type: ignore
        assert request.customer_id == "1234567890"

        operation = request.operations[0]
        assert operation.update.resource_name == (
            "customers/1234567890/conversionCustomVariables/123456"
        )
        assert operation.update.name == "Updated Product Category"
        assert (
            operation.update.status
            == ConversionCustomVariableStatusEnum.ConversionCustomVariableStatus.PAUSED
        )
        assert set(operation.update_mask.paths) == {"name", "status"}

    async def test_update_with_partial_fields(
        self,
        conversion_custom_variable_service: Any,
        mock_context: Any,
        mock_client: Any,
    ):
        """Test update with only some fields specified."""
        conversion_custom_variable_service._client = mock_client

        mock_response = MutateConversionCustomVariablesResponse()
        mock_response.results.append(MutateConversionCustomVariableResult())  # type: ignore
        mock_client.mutate_conversion_custom_variables.return_value = mock_response  # type: ignore

        await conversion_custom_variable_service.update_conversion_custom_variable(
            ctx=mock_context,
            customer_id="1234567890",
            custom_variable_id=123456,
            status=ConversionCustomVariableStatusEnum.ConversionCustomVariableStatus.ENABLED,
        )

        request = mock_client.mutate_conversion_custom_variables.call_args[1]["request"]  # type: ignore
        operation = request.operations[0]
        assert list(operation.update_mask.paths) == ["status"]

    async def test_update_with_no_fields_error(
        self,
        conversion_custom_variable_service: Any,
        mock_context: Any,
        mock_client: Any,
    ):
        """Test update with no fields raises error."""
        conversion_custom_variable_service._client = mock_client

        with pytest.raises(Exception) as exc_info:
            await conversion_custom_variable_service.update_conversion_custom_variable(
                ctx=mock_context,
                customer_id="1234567890",
                custom_variable_id=123456,
            )

        assert "At least one field must be specified for update" in str(exc_info.value)

    async def test_create_with_partial_failure(
        self,
        conversion_custom_variable_service: Any,
        mock_context: Any,
        mock_client: Any,
    ):
        """Test create with partial failure mode."""
        conversion_custom_variable_service._client = mock_client

        # Create response with partial failure error
        mock_response = MutateConversionCustomVariablesResponse()
        mock_response.results.append(MutateConversionCustomVariableResult())  # type: ignore

        partial_error = status_pb2.Status()
        partial_error.code = 3  # INVALID_ARGUMENT
        partial_error.message = "Partial failure occurred"
        mock_response.partial_failure_error.CopyFrom(partial_error)  # type: ignore

        mock_client.mutate_conversion_custom_variables.return_value = mock_response  # type: ignore

        _ = await conversion_custom_variable_service.create_conversion_custom_variable(
            ctx=mock_context,
            customer_id="1234567890",
            name="Test Variable",
            tag="test_var",
            partial_failure=True,
        )

        request = mock_client.mutate_conversion_custom_variables.call_args[1]["request"]  # type: ignore
        assert request.partial_failure is True

    async def test_create_api_error(
        self,
        conversion_custom_variable_service: Any,
        mock_context: Any,
        mock_client: Any,
    ):
        """Test create with API error."""
        conversion_custom_variable_service._client = mock_client

        # Mock API error
        error = GoogleAdsException(None, None, None, None)
        error.failure = Mock()  # type: ignore
        error.failure.__str__ = Mock(return_value="Tag already exists")  # type: ignore
        mock_client.mutate_conversion_custom_variables.side_effect = error  # type: ignore

        with pytest.raises(Exception) as exc_info:
            await conversion_custom_variable_service.create_conversion_custom_variable(
                ctx=mock_context,
                customer_id="1234567890",
                name="Duplicate Variable",
                tag="existing_tag",
            )

        assert "Google Ads API error: Tag already exists" in str(exc_info.value)

    async def test_update_general_error(
        self,
        conversion_custom_variable_service: Any,
        mock_context: Any,
        mock_client: Any,
    ):
        """Test update with general error."""
        conversion_custom_variable_service._client = mock_client
        mock_client.mutate_conversion_custom_variables.side_effect = Exception(  # type: ignore
            "Network error"
        )

        with pytest.raises(Exception) as exc_info:
            await conversion_custom_variable_service.update_conversion_custom_variable(
                ctx=mock_context,
                customer_id="1234567890",
                custom_variable_id=123456,
                name="New Name",
            )

        assert "Failed to update conversion custom variable: Network error" in str(
            exc_info.value
        )


@pytest.mark.asyncio
class TestConversionCustomVariableTools:
    """Test cases for Conversion Custom Variable tool functions."""

    async def test_create_conversion_custom_variable_tool(self, mock_context: Any):
        """Test create_conversion_custom_variable tool function."""
        service = ConversionCustomVariableService()
        tools = create_conversion_custom_variable_tools(service)
        create_tool = tools[0]  # First tool is create_conversion_custom_variable

        # Mock the service method
        with patch.object(service, "create_conversion_custom_variable") as mock_create:
            mock_create.return_value = {  # type: ignore
                "results": [
                    {"resource_name": "customers/123/conversionCustomVariables/456"}
                ]
            }

            await create_tool(
                ctx=mock_context,
                customer_id="1234567890",
                name="Product Category",
                tag="product_category",
                status="ENABLED",
            )

            mock_create.assert_called_once_with(  # type: ignore
                ctx=mock_context,
                customer_id="1234567890",
                name="Product Category",
                tag="product_category",
                status=ConversionCustomVariableStatusEnum.ConversionCustomVariableStatus.ENABLED,
                partial_failure=False,
                validate_only=False,
            )

    async def test_update_conversion_custom_variable_tool(self, mock_context: Any):
        """Test update_conversion_custom_variable tool function."""
        service = ConversionCustomVariableService()
        tools = create_conversion_custom_variable_tools(service)
        update_tool = tools[1]  # Second tool is update_conversion_custom_variable

        with patch.object(service, "update_conversion_custom_variable") as mock_update:
            mock_update.return_value = {"results": [{"resource_name": "test"}]}  # type: ignore

            await update_tool(
                ctx=mock_context,
                customer_id="1234567890",
                custom_variable_id=123456,
                name="Updated Name",
                status="PAUSED",
                validate_only=True,
            )

            mock_update.assert_called_once_with(  # type: ignore
                ctx=mock_context,
                customer_id="1234567890",
                custom_variable_id=123456,
                name="Updated Name",
                status=ConversionCustomVariableStatusEnum.ConversionCustomVariableStatus.PAUSED,
                partial_failure=False,
                validate_only=True,
            )
