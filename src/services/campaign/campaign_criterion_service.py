"""Campaign criterion service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.common.types.criteria import (
    DeviceInfo,
    KeywordInfo,
    LanguageInfo,
    LocationInfo,
)
from google.ads.googleads.v20.enums.types.device import DeviceEnum
from google.ads.googleads.v20.enums.types.keyword_match_type import KeywordMatchTypeEnum
from google.ads.googleads.v20.resources.types.campaign_criterion import (
    CampaignCriterion,
)
from google.ads.googleads.v20.services.services.campaign_criterion_service import (
    CampaignCriterionServiceClient,
)
from google.ads.googleads.v20.services.types.campaign_criterion_service import (
    CampaignCriterionOperation,
    MutateCampaignCriteriaRequest,
    MutateCampaignCriteriaResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class CampaignCriterionService:
    """Campaign criterion service for managing campaign-level targeting."""

    def __init__(self) -> None:
        """Initialize the campaign criterion service."""
        self._client: Optional[CampaignCriterionServiceClient] = None

    @property
    def client(self) -> CampaignCriterionServiceClient:
        """Get the campaign criterion service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CampaignCriterionService")
        assert self._client is not None
        return self._client

    async def add_location_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        location_ids: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Add location targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            location_ids: List of geo target constant IDs
            negative: Whether these are negative criteria
            bid_modifier: Optional bid modifier (e.g., 1.2 for +20%)

        Returns:
            List of created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            # Create operations
            operations = []
            for location_id in location_ids:
                # Create campaign criterion
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = negative

                if bid_modifier is not None and not negative:
                    campaign_criterion.bid_modifier = bid_modifier

                # Create location info
                location_info = LocationInfo()
                location_info.geo_target_constant = f"geoTargetConstants/{location_id}"
                campaign_criterion.location = location_info

                # Create operation
                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            # Create request
            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Make the API call
            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} location criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add location criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_language_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        language_ids: List[str],
    ) -> Dict[str, Any]:
        """Add language targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            language_ids: List of language constant IDs

        Returns:
            List of created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            # Create operations
            operations = []
            for language_id in language_ids:
                # Create campaign criterion
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = (
                    False  # Language targeting can't be negative
                )

                # Create language info
                language_info = LanguageInfo()
                language_info.language_constant = f"languageConstants/{language_id}"
                campaign_criterion.language = language_info

                # Create operation
                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            # Create request
            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Make the API call
            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} language criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add language criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_device_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        device_types: List[DeviceEnum.Device],
        bid_modifiers: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Add device targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            device_types: List of device type enum values
            bid_modifiers: Optional dict of device type to bid modifier

        Returns:
            List of created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            # Create operations
            operations = []
            for device_type in device_types:
                # Create campaign criterion
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = (
                    False  # Device targeting can't be negative
                )

                # Set bid modifier if provided
                device_type_str = device_type.name
                if bid_modifiers and device_type_str in bid_modifiers:
                    campaign_criterion.bid_modifier = bid_modifiers[device_type_str]

                # Create device info
                device_info = DeviceInfo()
                device_info.type_ = device_type
                campaign_criterion.device = device_info

                # Create operation
                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            # Create request
            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Make the API call
            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} device criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add device criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_negative_keyword_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        keywords: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """Add negative keyword criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            keywords: List of dicts with 'text' and 'match_type' keys

        Returns:
            List of created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            # Create operations
            operations = []
            for keyword in keywords:
                # Create campaign criterion
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = True  # Negative keywords

                # Create keyword info
                keyword_info = KeywordInfo()
                keyword_info.text = keyword["text"]
                keyword_info.match_type = getattr(
                    KeywordMatchTypeEnum.KeywordMatchType, keyword["match_type"]
                )
                campaign_criterion.keyword = keyword_info

                # Create operation
                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            # Create request
            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Make the API call
            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} negative keywords to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add negative keyword criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_campaign_criterion(
        self,
        ctx: Context,
        customer_id: str,
        criterion_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove a campaign criterion.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            criterion_resource_name: The resource name of the criterion to remove

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operation
            operation = CampaignCriterionOperation()
            operation.remove = criterion_resource_name

            # Create request
            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Removed campaign criterion: {criterion_resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove campaign criterion: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_campaign_criterion_tools(
    service: CampaignCriterionService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the campaign criterion service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def add_location_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        location_ids: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Add location targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            location_ids: List of geo target constant IDs (e.g., ["1014044"] for California)
            negative: Whether these are negative criteria (exclude locations)
            bid_modifier: Optional bid modifier (e.g., 1.2 for +20%, 0.8 for -20%)

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_location_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            location_ids=location_ids,
            negative=negative,
            bid_modifier=bid_modifier,
        )

    async def add_language_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        language_ids: List[str],
    ) -> Dict[str, Any]:
        """Add language targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            language_ids: List of language constant IDs (e.g., ["1000"] for English)

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_language_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            language_ids=language_ids,
        )

    async def add_device_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        device_types: List[str],
        bid_modifiers: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Add device targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            device_types: List of device types - MOBILE, DESKTOP, TABLET
            bid_modifiers: Optional dict of device type to bid modifier
                Example: {"MOBILE": 1.2, "DESKTOP": 0.9}

        Returns:
            Mutation response with created campaign criteria
        """
        # Convert string enums to proper enum types
        device_type_enums = [
            getattr(DeviceEnum.Device, device_type) for device_type in device_types
        ]

        return await service.add_device_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            device_types=device_type_enums,
            bid_modifiers=bid_modifiers,
        )

    async def add_negative_keyword_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        keywords: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """Add negative keyword criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            keywords: List of keyword dicts with 'text' and 'match_type' keys
                Example: [
                    {"text": "free", "match_type": "BROAD"},
                    {"text": "[cheap]", "match_type": "EXACT"}
                ]

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_negative_keyword_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            keywords=keywords,
        )

    async def remove_campaign_criterion(
        ctx: Context,
        customer_id: str,
        criterion_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove a campaign criterion.

        Args:
            customer_id: The customer ID
            criterion_resource_name: The full resource name of the criterion to remove

        Returns:
            Removal result with status
        """
        return await service.remove_campaign_criterion(
            ctx=ctx,
            customer_id=customer_id,
            criterion_resource_name=criterion_resource_name,
        )

    tools.extend(
        [
            add_location_criteria,
            add_language_criteria,
            add_device_criteria,
            add_negative_keyword_criteria,
            remove_campaign_criterion,
        ]
    )
    return tools


def register_campaign_criterion_tools(mcp: FastMCP[Any]) -> CampaignCriterionService:
    """Register campaign criterion tools with the MCP server.

    Returns the CampaignCriterionService instance for testing purposes.
    """
    service = CampaignCriterionService()
    tools = create_campaign_criterion_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
