"""Campaign asset service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.asset_field_type import AssetFieldTypeEnum
from google.ads.googleads.v20.resources.types.campaign_asset import CampaignAsset
from google.ads.googleads.v20.services.services.campaign_asset_service import (
    CampaignAssetServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.campaign_asset_service import (
    CampaignAssetOperation,
    MutateCampaignAssetsRequest,
    MutateCampaignAssetsResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class CampaignAssetService:
    """Campaign asset service for managing assets at the campaign level."""

    def __init__(self) -> None:
        """Initialize the campaign asset service."""
        self._client: Optional[CampaignAssetServiceClient] = None

    @property
    def client(self) -> CampaignAssetServiceClient:
        """Get the campaign asset service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CampaignAssetService")
        assert self._client is not None
        return self._client

    async def link_asset_to_campaign(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        asset_id: str,
        field_type: AssetFieldTypeEnum.AssetFieldType,
    ) -> Dict[str, Any]:
        """Link an asset to a campaign for a specific field type.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            asset_id: The asset ID to link
            field_type: The field type enum value

        Returns:
            Created campaign asset link details
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"
            asset_resource = f"customers/{customer_id}/assets/{asset_id}"

            # Create campaign asset
            campaign_asset = CampaignAsset()
            campaign_asset.campaign = campaign_resource
            campaign_asset.asset = asset_resource
            campaign_asset.field_type = field_type

            # Create operation
            operation = CampaignAssetOperation()
            operation.create = campaign_asset

            # Create request
            request = MutateCampaignAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateCampaignAssetsResponse = self.client.mutate_campaign_assets(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Linked asset {asset_id} to campaign {campaign_id} for field type {field_type}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to link asset to campaign: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def link_multiple_assets_to_campaign(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        asset_links: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """Link multiple assets to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            asset_links: List of dicts with 'asset_id' and 'field_type'

        Returns:
            List of created campaign asset links
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            # Create operations
            operations = []
            for link in asset_links:
                asset_id = link["asset_id"]
                field_type = link["field_type"]
                asset_resource = f"customers/{customer_id}/assets/{asset_id}"

                # Create campaign asset
                campaign_asset = CampaignAsset()
                campaign_asset.campaign = campaign_resource
                campaign_asset.asset = asset_resource
                campaign_asset.field_type = getattr(
                    AssetFieldTypeEnum.AssetFieldType, field_type
                )

                # Create operation
                operation = CampaignAssetOperation()
                operation.create = campaign_asset
                operations.append(operation)

            # Create request
            request = MutateCampaignAssetsRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Make the API call
            response: MutateCampaignAssetsResponse = self.client.mutate_campaign_assets(
                request=request
            )

            # Process results
            results = []
            for i, result in enumerate(response.results):
                link = asset_links[i]
                results.append(
                    {
                        "resource_name": result.resource_name,
                        "campaign_id": campaign_id,
                        "asset_id": link["asset_id"],
                        "field_type": link["field_type"],
                    }
                )

            await ctx.log(
                level="info",
                message=f"Linked {len(results)} assets to campaign {campaign_id}",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to link assets to campaign: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_campaign_assets(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: Optional[str] = None,
        field_type: Optional[AssetFieldTypeEnum.AssetFieldType] = None,
        include_system_managed: bool = False,
    ) -> List[Dict[str, Any]]:
        """List campaign assets.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: Optional campaign ID to filter by
            field_type: Optional field type to filter by
            include_system_managed: Whether to include system-managed assets

        Returns:
            List of campaign assets
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
                    campaign_asset.resource_name,
                    campaign_asset.campaign,
                    campaign_asset.asset,
                    campaign_asset.field_type,
                    campaign_asset.status,
                    campaign.id,
                    campaign.name,
                    asset.id,
                    asset.name,
                    asset.type
                FROM campaign_asset
            """

            conditions = []
            if campaign_id:
                conditions.append(f"campaign.id = {campaign_id}")
            if field_type:
                conditions.append(f"campaign_asset.field_type = '{field_type.name}'")
            if not include_system_managed:
                conditions.append("campaign_asset.source = 'ADVERTISER'")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY campaign.id, asset.id"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            campaign_assets = []
            for row in response:
                campaign_asset = row.campaign_asset
                campaign = row.campaign
                asset = row.asset

                asset_dict = {
                    "resource_name": campaign_asset.resource_name,
                    "campaign_resource": campaign_asset.campaign,
                    "asset_resource": campaign_asset.asset,
                    "campaign_id": str(campaign.id),
                    "campaign_name": campaign.name,
                    "asset_id": str(asset.id),
                    "asset_name": asset.name,
                    "asset_type": asset.type_.name if asset.type_ else "UNKNOWN",
                    "field_type": campaign_asset.field_type.name
                    if campaign_asset.field_type
                    else "UNKNOWN",
                    "status": campaign_asset.status.name
                    if campaign_asset.status
                    else "UNKNOWN",
                }

                campaign_assets.append(asset_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(campaign_assets)} campaign assets",
            )

            return campaign_assets

        except Exception as e:
            error_msg = f"Failed to list campaign assets: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_asset_from_campaign(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        asset_id: str,
        field_type: AssetFieldTypeEnum.AssetFieldType,
    ) -> Dict[str, Any]:
        """Remove an asset from a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            asset_id: The asset ID to remove
            field_type: The field type of the asset

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)
            # Campaign asset resource names use ~ as separator
            campaign_asset_resource = f"customers/{customer_id}/campaignAssets/{campaign_id}~{asset_id}~{field_type}"

            # Create operation
            operation = CampaignAssetOperation()
            operation.remove = campaign_asset_resource

            # Create request
            request = MutateCampaignAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_campaign_assets(request=request)

            await ctx.log(
                level="info",
                message=f"Removed asset {asset_id} from campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove asset from campaign: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_campaign_asset_tools(
    service: CampaignAssetService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the campaign asset service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def link_asset_to_campaign(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        asset_id: str,
        field_type: str,
    ) -> Dict[str, Any]:
        """Link an asset to a campaign for a specific field type.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
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

        Returns:
            Created campaign asset link details including resource_name
        """
        # Convert string enum to proper enum type
        field_type_enum = getattr(AssetFieldTypeEnum.AssetFieldType, field_type)

        return await service.link_asset_to_campaign(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            asset_id=asset_id,
            field_type=field_type_enum,
        )

    async def link_multiple_assets_to_campaign(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        asset_links: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """Link multiple assets to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            asset_links: List of dicts with:
                - asset_id: The asset ID to link
                - field_type: The field type for the asset

        Returns:
            List of created campaign asset links
        """
        return await service.link_multiple_assets_to_campaign(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            asset_links=asset_links,
        )

    async def list_campaign_assets(
        ctx: Context,
        customer_id: str,
        campaign_id: Optional[str] = None,
        field_type: Optional[str] = None,
        include_system_managed: bool = False,
    ) -> List[Dict[str, Any]]:
        """List campaign assets.

        Args:
            customer_id: The customer ID
            campaign_id: Optional campaign ID to filter by
            field_type: Optional field type to filter by (e.g., SITELINK, CALLOUT)
            include_system_managed: Whether to include system-managed assets

        Returns:
            List of campaign assets with details
        """
        # Convert string enum to proper enum type if provided
        field_type_enum = (
            getattr(AssetFieldTypeEnum.AssetFieldType, field_type)
            if field_type
            else None
        )

        return await service.list_campaign_assets(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            field_type=field_type_enum,
            include_system_managed=include_system_managed,
        )

    async def remove_asset_from_campaign(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        asset_id: str,
        field_type: str,
    ) -> Dict[str, Any]:
        """Remove an asset from a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            asset_id: The asset ID to remove
            field_type: The field type of the asset

        Returns:
            Removal result with status
        """
        # Convert string enum to proper enum type
        field_type_enum = getattr(AssetFieldTypeEnum.AssetFieldType, field_type)

        return await service.remove_asset_from_campaign(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            asset_id=asset_id,
            field_type=field_type_enum,
        )

    tools.extend(
        [
            link_asset_to_campaign,
            link_multiple_assets_to_campaign,
            list_campaign_assets,
            remove_asset_from_campaign,
        ]
    )
    return tools


def register_campaign_asset_tools(mcp: FastMCP[Any]) -> CampaignAssetService:
    """Register campaign asset tools with the MCP server.

    Returns the CampaignAssetService instance for testing purposes.
    """
    service = CampaignAssetService()
    tools = create_campaign_asset_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
