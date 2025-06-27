"""Campaign Customizer service implementation with full v20 type safety."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.common.types.customizer_value import CustomizerValue
from google.ads.googleads.v20.enums.types.customizer_attribute_type import (
    CustomizerAttributeTypeEnum,
)
from google.ads.googleads.v20.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v20.resources.types.campaign_customizer import (
    CampaignCustomizer,
)
from google.ads.googleads.v20.services.services.campaign_customizer_service import (
    CampaignCustomizerServiceClient,
)
from google.ads.googleads.v20.services.types.campaign_customizer_service import (
    CampaignCustomizerOperation,
    MutateCampaignCustomizersRequest,
    MutateCampaignCustomizersResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class CampaignCustomizerService:
    """Service for managing campaign customizers in Google Ads.

    Campaign customizers allow you to set campaign-specific values for
    customizer attributes, enabling dynamic ad customization at the campaign level.
    """

    def __init__(self) -> None:
        """Initialize the campaign customizer service."""
        self._client: Optional[CampaignCustomizerServiceClient] = None

    @property
    def client(self) -> CampaignCustomizerServiceClient:
        """Get the campaign customizer service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CampaignCustomizerService")
        assert self._client is not None
        return self._client

    async def create_campaign_customizer(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        customizer_attribute_id: str,
        value: str,
        attribute_type: CustomizerAttributeTypeEnum.CustomizerAttributeType,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: ResponseContentTypeEnum.ResponseContentType = ResponseContentTypeEnum.ResponseContentType.MUTABLE_RESOURCE,
    ) -> Dict[str, Any]:
        """Create a new campaign customizer.

        Links a customizer attribute to a campaign with a specific value.
        Note: Campaign customizers are immutable - to change a value, remove and recreate.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            customizer_attribute_id: The customizer attribute ID
            value: The customizer value (always passed as string)
            attribute_type: The type of the customizer attribute
            partial_failure: If true, valid operations succeed even if others fail
            validate_only: If true, only validates without executing
            response_content_type: What to return in response

        Returns:
            Created campaign customizer details
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"
            attribute_resource = f"customers/{customer_id}/customizerAttributes/{customizer_attribute_id}"

            # Create the customizer value
            customizer_value = CustomizerValue()
            customizer_value.type_ = attribute_type
            customizer_value.string_value = value

            # Create a new campaign customizer
            campaign_customizer = CampaignCustomizer()
            campaign_customizer.campaign = campaign_resource
            campaign_customizer.customizer_attribute = attribute_resource
            campaign_customizer.value = customizer_value

            # Create the operation
            operation = CampaignCustomizerOperation()
            operation.create = campaign_customizer

            # Create the request
            request = MutateCampaignCustomizersRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            request.partial_failure = partial_failure
            request.validate_only = validate_only
            request.response_content_type = response_content_type

            # Execute the mutation
            response: MutateCampaignCustomizersResponse = (
                self.client.mutate_campaign_customizers(request=request)
            )

            await ctx.log(
                level="info",
                message=(
                    f"Created campaign customizer: campaign {campaign_id}, "
                    f"attribute {customizer_attribute_id}, value '{value}'"
                ),
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create campaign customizer: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_campaign_customizer(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        customizer_attribute_id: str,
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Remove a campaign customizer.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            customizer_attribute_id: The customizer attribute ID
            partial_failure: If true, valid operations succeed even if others fail
            validate_only: If true, only validates without executing

        Returns:
            Removal result details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Construct resource name using the ~ delimiter format
            resource_name = (
                f"customers/{customer_id}/campaignCustomizers/"
                f"{campaign_id}~{customizer_attribute_id}"
            )

            # Create the operation
            operation = CampaignCustomizerOperation()
            operation.remove = resource_name

            # Create the request
            request = MutateCampaignCustomizersRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            request.partial_failure = partial_failure
            request.validate_only = validate_only

            # Execute the mutation
            response = self.client.mutate_campaign_customizers(request=request)

            await ctx.log(
                level="info",
                message=(
                    f"Removed campaign customizer: campaign {campaign_id}, "
                    f"attribute {customizer_attribute_id}"
                ),
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove campaign customizer: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_campaign_customizer_tools(
    service: CampaignCustomizerService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the campaign customizer service."""
    tools = []

    async def create_campaign_customizer(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        customizer_attribute_id: str,
        value: str,
        attribute_type: str,
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Create a campaign-specific value for a customizer attribute.

        Campaign customizers enable dynamic ad customization by setting campaign-specific
        values for customizer attributes. These values can be used in ad text templates.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            customizer_attribute_id: The customizer attribute ID
            value: The customizer value (passed as string for all types)
            attribute_type: The type - TEXT, NUMBER, PRICE, or PERCENT
            partial_failure: If true, valid operations succeed even if others fail
            validate_only: If true, only validates without executing

        Returns:
            Created campaign customizer details

        Example:
            # Set a campaign-specific discount percentage
            result = await create_campaign_customizer(
                customer_id="1234567890",
                campaign_id="9876543210",
                customizer_attribute_id="1111111111",
                value="25",
                attribute_type="PERCENT"
            )

            # Set a campaign-specific text value
            result = await create_campaign_customizer(
                customer_id="1234567890",
                campaign_id="9876543210",
                customizer_attribute_id="2222222222",
                value="Summer Sale",
                attribute_type="TEXT"
            )
        """
        # Convert string enum to proper enum type
        attribute_type_enum = getattr(
            CustomizerAttributeTypeEnum.CustomizerAttributeType, attribute_type
        )

        return await service.create_campaign_customizer(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            customizer_attribute_id=customizer_attribute_id,
            value=value,
            attribute_type=attribute_type_enum,
            partial_failure=partial_failure,
            validate_only=validate_only,
        )

    async def remove_campaign_customizer(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        customizer_attribute_id: str,
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Remove a campaign customizer value.

        Note: Campaign customizers are immutable. To change a value, you must
        remove the existing customizer and create a new one.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            customizer_attribute_id: The customizer attribute ID
            partial_failure: If true, valid operations succeed even if others fail
            validate_only: If true, only validates without executing

        Returns:
            Removal result details

        Example:
            result = await remove_campaign_customizer(
                customer_id="1234567890",
                campaign_id="9876543210",
                customizer_attribute_id="1111111111"
            )
        """
        return await service.remove_campaign_customizer(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            customizer_attribute_id=customizer_attribute_id,
            partial_failure=partial_failure,
            validate_only=validate_only,
        )

    tools.extend([create_campaign_customizer, remove_campaign_customizer])
    return tools


def register_campaign_customizer_tools(
    mcp: FastMCP[Any],
) -> CampaignCustomizerService:
    """Register campaign customizer tools with the MCP server.

    Returns the service instance for testing purposes.
    """
    service = CampaignCustomizerService()
    tools = create_campaign_customizer_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
