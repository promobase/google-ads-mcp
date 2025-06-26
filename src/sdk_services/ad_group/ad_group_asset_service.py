"""Ad group asset service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.asset_field_type import AssetFieldTypeEnum
from google.ads.googleads.v20.enums.types.asset_link_status import AssetLinkStatusEnum
from google.ads.googleads.v20.resources.types.ad_group_asset import AdGroupAsset
from google.ads.googleads.v20.services.services.ad_group_asset_service import (
    AdGroupAssetServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.ad_group_asset_service import (
    AdGroupAssetOperation,
    MutateAdGroupAssetsRequest,
    MutateAdGroupAssetsResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class AdGroupAssetService:
    """Ad group asset service for managing assets at the ad group level."""

    def __init__(self) -> None:
        """Initialize the ad group asset service."""
        self._client: Optional[AdGroupAssetServiceClient] = None

    @property
    def client(self) -> AdGroupAssetServiceClient:
        """Get the ad group asset service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AdGroupAssetService")
        assert self._client is not None
        return self._client

    async def link_asset_to_ad_group(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        asset_id: str,
        field_type: str,
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Link an asset to an ad group for a specific field type.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            asset_id: The asset ID to link
            field_type: The field type for the asset (e.g., HEADLINE, DESCRIPTION)
            status: Asset link status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created ad group asset link details
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"
            asset_resource = f"customers/{customer_id}/assets/{asset_id}"

            # Create ad group asset
            ad_group_asset = AdGroupAsset()
            ad_group_asset.ad_group = ad_group_resource
            ad_group_asset.asset = asset_resource
            ad_group_asset.field_type = getattr(
                AssetFieldTypeEnum.AssetFieldType, field_type
            )
            ad_group_asset.status = getattr(AssetLinkStatusEnum.AssetLinkStatus, status)

            # Create operation
            operation = AdGroupAssetOperation()
            operation.create = ad_group_asset

            # Create request
            request = MutateAdGroupAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateAdGroupAssetsResponse = self.client.mutate_ad_group_assets(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Linked asset {asset_id} to ad group {ad_group_id} for field type {field_type}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to link asset to ad group: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def link_multiple_assets_to_ad_group(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        asset_links: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """Link multiple assets to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            asset_links: List of dicts with 'asset_id', 'field_type', and optional 'status'

        Returns:
            List of created ad group asset links
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            # Create operations
            operations = []
            for link in asset_links:
                asset_id = link["asset_id"]
                field_type = link["field_type"]
                status = link.get("status", "ENABLED")
                asset_resource = f"customers/{customer_id}/assets/{asset_id}"

                # Create ad group asset
                ad_group_asset = AdGroupAsset()
                ad_group_asset.ad_group = ad_group_resource
                ad_group_asset.asset = asset_resource
                ad_group_asset.field_type = getattr(
                    AssetFieldTypeEnum.AssetFieldType, field_type
                )
                ad_group_asset.status = getattr(
                    AssetLinkStatusEnum.AssetLinkStatus, status
                )

                # Create operation
                operation = AdGroupAssetOperation()
                operation.create = ad_group_asset
                operations.append(operation)

            # Create request
            request = MutateAdGroupAssetsRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Make the API call
            response: MutateAdGroupAssetsResponse = self.client.mutate_ad_group_assets(
                request=request
            )

            # Process results
            results = []
            for i, result in enumerate(response.results):
                link = asset_links[i]
                results.append(
                    {
                        "resource_name": result.resource_name,
                        "ad_group_id": ad_group_id,
                        "asset_id": link["asset_id"],
                        "field_type": link["field_type"],
                        "status": link.get("status", "ENABLED"),
                    }
                )

            await ctx.log(
                level="info",
                message=f"Linked {len(results)} assets to ad group {ad_group_id}",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to link assets to ad group: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_ad_group_asset_status(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        asset_id: str,
        field_type: str,
        status: str,
    ) -> Dict[str, Any]:
        """Update the status of an ad group asset link.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            asset_id: The asset ID
            field_type: The field type
            status: New status (ENABLED, PAUSED, REMOVED)

        Returns:
            Updated ad group asset details
        """
        try:
            customer_id = format_customer_id(customer_id)
            # Ad group asset resource names use ~ as separator
            resource_name = f"customers/{customer_id}/adGroupAssets/{ad_group_id}~{asset_id}~{field_type}"

            # Create ad group asset with updated status
            ad_group_asset = AdGroupAsset()
            ad_group_asset.resource_name = resource_name
            ad_group_asset.status = getattr(AssetLinkStatusEnum.AssetLinkStatus, status)

            # Create operation
            operation = AdGroupAssetOperation()
            operation.update = ad_group_asset
            operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))

            # Create request
            request = MutateAdGroupAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_ad_group_assets(request=request)

            await ctx.log(
                level="info",
                message=f"Updated ad group asset status to {status}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update ad group asset status: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_ad_group_assets(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: Optional[str] = None,
        field_type: Optional[str] = None,
        campaign_id: Optional[str] = None,
        include_system_managed: bool = False,
    ) -> List[Dict[str, Any]]:
        """List ad group assets.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: Optional ad group ID to filter by
            field_type: Optional field type to filter by
            campaign_id: Optional campaign ID to filter by
            include_system_managed: Whether to include system-managed assets

        Returns:
            List of ad group assets
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service: GoogleAdsServiceClient = sdk_client.client.get_service(
                "GoogleAdsService"
            )

            # Build query
            query = """
                SELECT
                    ad_group_asset.resource_name,
                    ad_group_asset.ad_group,
                    ad_group_asset.asset,
                    ad_group_asset.field_type,
                    ad_group_asset.status,
                    ad_group.id,
                    ad_group.name,
                    ad_group.campaign,
                    campaign.id,
                    campaign.name,
                    asset.id,
                    asset.name,
                    asset.type
                FROM ad_group_asset
            """

            conditions = []
            if ad_group_id:
                conditions.append(f"ad_group.id = {ad_group_id}")
            if field_type:
                conditions.append(f"ad_group_asset.field_type = '{field_type}'")
            if campaign_id:
                conditions.append(f"campaign.id = {campaign_id}")
            if not include_system_managed:
                conditions.append("ad_group_asset.source = 'ADVERTISER'")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY ad_group.id, asset.id"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            ad_group_assets = []
            for row in response:
                ad_group_asset = row.ad_group_asset
                ad_group = row.ad_group
                campaign = row.campaign
                asset = row.asset

                asset_dict = {
                    "resource_name": ad_group_asset.resource_name,
                    "ad_group_resource": ad_group_asset.ad_group,
                    "asset_resource": ad_group_asset.asset,
                    "ad_group_id": str(ad_group.id),
                    "ad_group_name": ad_group.name,
                    "campaign_id": str(campaign.id),
                    "campaign_name": campaign.name,
                    "asset_id": str(asset.id),
                    "asset_name": asset.name,
                    "asset_type": asset.type_.name if asset.type_ else "UNKNOWN",
                    "field_type": ad_group_asset.field_type.name
                    if ad_group_asset.field_type
                    else "UNKNOWN",
                    "status": ad_group_asset.status.name
                    if ad_group_asset.status
                    else "UNKNOWN",
                }

                ad_group_assets.append(asset_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(ad_group_assets)} ad group assets",
            )

            return ad_group_assets

        except Exception as e:
            error_msg = f"Failed to list ad group assets: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_asset_from_ad_group(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        asset_id: str,
        field_type: str,
    ) -> Dict[str, Any]:
        """Remove an asset from an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            asset_id: The asset ID to remove
            field_type: The field type of the asset

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)
            # Ad group asset resource names use ~ as separator
            ad_group_asset_resource = f"customers/{customer_id}/adGroupAssets/{ad_group_id}~{asset_id}~{field_type}"

            # Create operation
            operation = AdGroupAssetOperation()
            operation.remove = ad_group_asset_resource

            # Create request
            request = MutateAdGroupAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_ad_group_assets(request=request)

            await ctx.log(
                level="info",
                message=f"Removed asset {asset_id} from ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove asset from ad group: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_ad_group_asset_tools(
    service: AdGroupAssetService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the ad group asset service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def link_asset_to_ad_group(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        asset_id: str,
        field_type: str,
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Link an asset to an ad group for a specific field type.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            asset_id: The asset ID to link
            field_type: The field type for the asset:
                - HEADLINE, DESCRIPTION (for text assets in responsive ads)
                - SITELINK (for sitelink extensions)
                - CALL (for call extensions)
                - CALLOUT (for callout extensions)
                - STRUCTURED_SNIPPET (for structured snippet extensions)
                - PROMOTION (for promotion extensions)
                - PRICE (for price extensions)
                - MOBILE_APP (for app extensions)
                - LEAD_FORM (for lead form extensions)
                - BUSINESS_LOGO, MARKETING_IMAGE (for image assets)
                - YOUTUBE_VIDEO (for video assets)
            status: Asset link status - ENABLED, PAUSED, or REMOVED

        Returns:
            Created ad group asset link details including resource_name
        """
        return await service.link_asset_to_ad_group(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            asset_id=asset_id,
            field_type=field_type,
            status=status,
        )

    async def link_multiple_assets_to_ad_group(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        asset_links: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """Link multiple assets to an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            asset_links: List of dicts with:
                - asset_id: The asset ID to link
                - field_type: The field type for the asset
                - status: Optional status (defaults to ENABLED)

        Returns:
            List of created ad group asset links
        """
        return await service.link_multiple_assets_to_ad_group(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            asset_links=asset_links,
        )

    async def update_ad_group_asset_status(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        asset_id: str,
        field_type: str,
        status: str,
    ) -> Dict[str, Any]:
        """Update the status of an ad group asset link.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            asset_id: The asset ID
            field_type: The field type
            status: New status - ENABLED, PAUSED, or REMOVED

        Returns:
            Updated ad group asset details
        """
        return await service.update_ad_group_asset_status(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            asset_id=asset_id,
            field_type=field_type,
            status=status,
        )

    async def list_ad_group_assets(
        ctx: Context,
        customer_id: str,
        ad_group_id: Optional[str] = None,
        field_type: Optional[str] = None,
        campaign_id: Optional[str] = None,
        include_system_managed: bool = False,
    ) -> List[Dict[str, Any]]:
        """List ad group assets.

        Args:
            customer_id: The customer ID
            ad_group_id: Optional ad group ID to filter by
            field_type: Optional field type to filter by (e.g., SITELINK, CALLOUT)
            campaign_id: Optional campaign ID to filter by
            include_system_managed: Whether to include system-managed assets

        Returns:
            List of ad group assets with details
        """
        return await service.list_ad_group_assets(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            field_type=field_type,
            campaign_id=campaign_id,
            include_system_managed=include_system_managed,
        )

    async def remove_asset_from_ad_group(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        asset_id: str,
        field_type: str,
    ) -> Dict[str, Any]:
        """Remove an asset from an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            asset_id: The asset ID to remove
            field_type: The field type of the asset

        Returns:
            Removal result with status
        """
        return await service.remove_asset_from_ad_group(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            asset_id=asset_id,
            field_type=field_type,
        )

    tools.extend(
        [
            link_asset_to_ad_group,
            link_multiple_assets_to_ad_group,
            update_ad_group_asset_status,
            list_ad_group_assets,
            remove_asset_from_ad_group,
        ]
    )
    return tools


def register_ad_group_asset_tools(mcp: FastMCP[Any]) -> AdGroupAssetService:
    """Register ad group asset tools with the MCP server.

    Returns the AdGroupAssetService instance for testing purposes.
    """
    service = AdGroupAssetService()
    tools = create_ad_group_asset_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
