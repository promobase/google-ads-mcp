"""Ad service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.common.types.ad_asset import AdTextAsset
from google.ads.googleads.v20.common.types.ad_type_infos import (
    ExpandedTextAdInfo,
    ResponsiveSearchAdInfo,
)
from google.ads.googleads.v20.enums.types.ad_group_ad_status import (
    AdGroupAdStatusEnum,
)
from google.ads.googleads.v20.resources.types.ad import Ad
from google.ads.googleads.v20.resources.types.ad_group_ad import AdGroupAd
from google.ads.googleads.v20.services.services.ad_group_ad_service import (
    AdGroupAdServiceClient,
)
from google.ads.googleads.v20.services.types.ad_group_ad_service import (
    AdGroupAdOperation,
    MutateAdGroupAdsRequest,
    MutateAdGroupAdsResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class AdService:
    """Ad service for managing Google Ads ads."""

    def __init__(self) -> None:
        """Initialize the ad service."""
        self._client: Optional[AdGroupAdServiceClient] = None

    @property
    def client(self) -> AdGroupAdServiceClient:
        """Get the ad group ad service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AdGroupAdService")
        assert self._client is not None
        return self._client

    async def create_responsive_search_ad(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        headlines: List[str],
        descriptions: List[str],
        final_urls: List[str],
        path1: Optional[str] = None,
        path2: Optional[str] = None,
        status: AdGroupAdStatusEnum.AdGroupAdStatus = AdGroupAdStatusEnum.AdGroupAdStatus.PAUSED,
    ) -> Dict[str, Any]:
        """Create a responsive search ad.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            headlines: List of headline texts (min 3, max 15)
            descriptions: List of description texts (min 2, max 4)
            final_urls: List of landing page URLs
            path1: First path component for display URL
            path2: Second path component for display URL
            status: Ad status enum value

        Returns:
            Created ad details
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource_name = f"customers/{customer_id}/adGroups/{ad_group_id}"

            # Create ad
            ad = Ad()
            ad.final_urls.extend(final_urls)

            if path1:
                ad.display_url_path1 = path1
            if path2:
                ad.display_url_path2 = path2

            # Create responsive search ad info
            responsive_search_ad = ResponsiveSearchAdInfo()

            # Add headlines
            for headline_text in headlines:
                headline = AdTextAsset()
                headline.text = headline_text
                responsive_search_ad.headlines.append(headline)

            # Add descriptions
            for description_text in descriptions:
                description = AdTextAsset()
                description.text = description_text
                responsive_search_ad.descriptions.append(description)

            ad.responsive_search_ad = responsive_search_ad

            # Create ad group ad
            ad_group_ad = AdGroupAd()
            ad_group_ad.ad_group = ad_group_resource_name
            ad_group_ad.ad = ad
            ad_group_ad.status = status

            # Create operation
            operation = AdGroupAdOperation()
            operation.create = ad_group_ad

            # Create request
            request = MutateAdGroupAdsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateAdGroupAdsResponse = self.client.mutate_ad_group_ads(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created responsive search ad in ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create responsive search ad: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_expanded_text_ad(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        headline1: str,
        headline2: str,
        headline3: Optional[str],
        description1: str,
        description2: Optional[str],
        final_urls: List[str],
        path1: Optional[str] = None,
        path2: Optional[str] = None,
        status: AdGroupAdStatusEnum.AdGroupAdStatus = AdGroupAdStatusEnum.AdGroupAdStatus.PAUSED,
    ) -> Dict[str, Any]:
        """Create an expanded text ad.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            headline1: First headline (required)
            headline2: Second headline (required)
            headline3: Third headline (optional)
            description1: First description (required)
            description2: Second description (optional)
            final_urls: List of landing page URLs
            path1: First path component for display URL
            path2: Second path component for display URL
            status: Ad status enum value

        Returns:
            Created ad details
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource_name = f"customers/{customer_id}/adGroups/{ad_group_id}"

            # Create ad
            ad = Ad()
            ad.final_urls.extend(final_urls)

            if path1:
                ad.display_url_path1 = path1
            if path2:
                ad.display_url_path2 = path2

            # Create expanded text ad info
            expanded_text_ad = ExpandedTextAdInfo()
            expanded_text_ad.headline_part1 = headline1
            expanded_text_ad.headline_part2 = headline2
            if headline3:
                expanded_text_ad.headline_part3 = headline3

            expanded_text_ad.description = description1
            if description2:
                expanded_text_ad.description2 = description2

            ad.expanded_text_ad = expanded_text_ad

            # Create ad group ad
            ad_group_ad = AdGroupAd()
            ad_group_ad.ad_group = ad_group_resource_name
            ad_group_ad.ad = ad
            ad_group_ad.status = status

            # Create operation
            operation = AdGroupAdOperation()
            operation.create = ad_group_ad

            # Create request
            request = MutateAdGroupAdsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateAdGroupAdsResponse = self.client.mutate_ad_group_ads(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created expanded text ad in ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create expanded text ad: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_ad_status(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        ad_id: str,
        status: AdGroupAdStatusEnum.AdGroupAdStatus,
    ) -> Dict[str, Any]:
        """Update the status of an ad.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            ad_id: The ad ID
            status: New ad status enum value

        Returns:
            Updated ad details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/adGroupAds/{ad_group_id}~{ad_id}"

            # Create ad group ad with resource name
            ad_group_ad = AdGroupAd()
            ad_group_ad.resource_name = resource_name
            ad_group_ad.status = status

            # Create the operation
            operation = AdGroupAdOperation()
            operation.update = ad_group_ad
            operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))

            # Create the request
            request = MutateAdGroupAdsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_ad_group_ads(request=request)

            await ctx.log(
                level="info",
                message=f"Updated ad {ad_id} status to {status}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update ad status: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_ad_tools(service: AdService) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the ad service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_responsive_search_ad(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        headlines: List[str],
        descriptions: List[str],
        final_urls: List[str],
        path1: Optional[str] = None,
        path2: Optional[str] = None,
        status: str = "PAUSED",
    ) -> Dict[str, Any]:
        """Create a responsive search ad.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            headlines: List of headline texts (min 3, max 15, each max 30 chars)
            descriptions: List of description texts (min 2, max 4, each max 90 chars)
            final_urls: List of landing page URLs
            path1: First path component for display URL (max 15 chars)
            path2: Second path component for display URL (max 15 chars)
            status: Ad status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created ad details
        """
        # Convert string enum to proper enum type
        status_enum = getattr(AdGroupAdStatusEnum.AdGroupAdStatus, status)

        return await service.create_responsive_search_ad(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headlines=headlines,
            descriptions=descriptions,
            final_urls=final_urls,
            path1=path1,
            path2=path2,
            status=status_enum,
        )

    async def create_expanded_text_ad(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        headline1: str,
        headline2: str,
        headline3: Optional[str],
        description1: str,
        description2: Optional[str],
        final_urls: List[str],
        path1: Optional[str] = None,
        path2: Optional[str] = None,
        status: str = "PAUSED",
    ) -> Dict[str, Any]:
        """Create an expanded text ad.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            headline1: First headline (max 30 chars)
            headline2: Second headline (max 30 chars)
            headline3: Third headline (optional, max 30 chars)
            description1: First description (max 90 chars)
            description2: Second description (optional, max 90 chars)
            final_urls: List of landing page URLs
            path1: First path component for display URL (max 15 chars)
            path2: Second path component for display URL (max 15 chars)
            status: Ad status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created ad details
        """
        # Convert string enum to proper enum type
        status_enum = getattr(AdGroupAdStatusEnum.AdGroupAdStatus, status)

        return await service.create_expanded_text_ad(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headline1=headline1,
            headline2=headline2,
            headline3=headline3,
            description1=description1,
            description2=description2,
            final_urls=final_urls,
            path1=path1,
            path2=path2,
            status=status_enum,
        )

    async def update_ad_status(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        ad_id: str,
        status: str,
    ) -> Dict[str, Any]:
        """Update the status of an ad.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            ad_id: The ad ID
            status: New ad status (ENABLED, PAUSED, REMOVED)

        Returns:
            Updated ad details
        """
        # Convert string enum to proper enum type
        status_enum = getattr(AdGroupAdStatusEnum.AdGroupAdStatus, status)

        return await service.update_ad_status(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            ad_id=ad_id,
            status=status_enum,
        )

    tools.extend(
        [create_responsive_search_ad, create_expanded_text_ad, update_ad_status]
    )
    return tools


def register_ad_tools(mcp: FastMCP[Any]) -> AdService:
    """Register ad tools with the MCP server.

    Returns the AdService instance for testing purposes.
    """
    service = AdService()
    tools = create_ad_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
