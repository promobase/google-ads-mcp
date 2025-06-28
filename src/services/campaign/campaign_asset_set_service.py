"""Campaign Asset Set Service for Google Ads API v20.

This service manages asset set associations with campaigns, allowing asset sets
to be linked to campaigns for use in advertising.
"""

from typing import Any, List, Optional

from fastmcp import FastMCP
from google.ads.googleads.v20.services.services.campaign_asset_set_service import (
    CampaignAssetSetServiceClient,
)
from google.ads.googleads.v20.services.types.campaign_asset_set_service import (
    CampaignAssetSetOperation,
    MutateCampaignAssetSetsRequest,
    MutateCampaignAssetSetsResponse,
)
from google.ads.googleads.v20.resources.types.campaign_asset_set import CampaignAssetSet
from google.ads.googleads.v20.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)

from src.sdk_client import get_sdk_client


class CampaignAssetSetService:
    """Service for managing campaign asset sets in Google Ads.

    Campaign asset sets link asset sets to campaigns, enabling the use of
    asset sets in campaign advertising.
    """

    def __init__(self) -> None:
        """Initialize the campaign asset set service."""
        self._client: Optional[CampaignAssetSetServiceClient] = None

    @property
    def client(self) -> CampaignAssetSetServiceClient:
        """Get the campaign asset set service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CampaignAssetSetService")
        assert self._client is not None
        return self._client

    def mutate_campaign_asset_sets(
        self,
        customer_id: str,
        operations: List[CampaignAssetSetOperation],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: ResponseContentTypeEnum.ResponseContentType = ResponseContentTypeEnum.ResponseContentType.RESOURCE_NAME_ONLY,
    ) -> MutateCampaignAssetSetsResponse:
        """Create or remove campaign asset sets.

        Args:
            customer_id: The customer ID.
            operations: List of operations to perform.
            partial_failure: If true, successful operations will be carried out and invalid
                operations will return errors.
            validate_only: If true, the request is validated but not executed.
            response_content_type: The response content type setting.

        Returns:
            MutateCampaignAssetSetsResponse: The response containing results.

        Raises:
            Exception: If the request fails.
        """
        try:
            request = MutateCampaignAssetSetsRequest(
                customer_id=customer_id,
                operations=operations,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )
            return self.client.mutate_campaign_asset_sets(request=request)
        except Exception as e:
            raise Exception(f"Failed to mutate campaign asset sets: {e}") from e

    def create_campaign_asset_set_operation(
        self,
        campaign: str,
        asset_set: str,
    ) -> CampaignAssetSetOperation:
        """Create a campaign asset set operation for creation.

        Args:
            campaign: The campaign resource name.
            asset_set: The asset set resource name.

        Returns:
            CampaignAssetSetOperation: The operation to create the campaign asset set.
        """
        campaign_asset_set = CampaignAssetSet(
            campaign=campaign,
            asset_set=asset_set,
        )

        return CampaignAssetSetOperation(create=campaign_asset_set)

    def create_remove_operation(self, resource_name: str) -> CampaignAssetSetOperation:
        """Create a campaign asset set operation for removal.

        Args:
            resource_name: The resource name of the campaign asset set to remove.
                Format: customers/{customer_id}/campaignAssetSets/{campaign_id}~{asset_set_id}

        Returns:
            CampaignAssetSetOperation: The operation to remove the campaign asset set.
        """
        return CampaignAssetSetOperation(remove=resource_name)

    def link_asset_set_to_campaign(
        self,
        customer_id: str,
        campaign: str,
        asset_set: str,
        validate_only: bool = False,
    ) -> MutateCampaignAssetSetsResponse:
        """Link an asset set to a campaign.

        Args:
            customer_id: The customer ID.
            campaign: The campaign resource name.
            asset_set: The asset set resource name.
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateCampaignAssetSetsResponse: The response containing the result.
        """
        operation = self.create_campaign_asset_set_operation(
            campaign=campaign,
            asset_set=asset_set,
        )

        return self.mutate_campaign_asset_sets(
            customer_id=customer_id,
            operations=[operation],
            validate_only=validate_only,
        )

    def unlink_asset_set_from_campaign(
        self,
        customer_id: str,
        resource_name: str,
        validate_only: bool = False,
    ) -> MutateCampaignAssetSetsResponse:
        """Unlink an asset set from a campaign.

        Args:
            customer_id: The customer ID.
            resource_name: The resource name of the campaign asset set to remove.
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateCampaignAssetSetsResponse: The response containing the result.
        """
        operation = self.create_remove_operation(resource_name=resource_name)

        return self.mutate_campaign_asset_sets(
            customer_id=customer_id,
            operations=[operation],
            validate_only=validate_only,
        )

    def link_multiple_asset_sets_to_campaign(
        self,
        customer_id: str,
        campaign: str,
        asset_sets: List[str],
        validate_only: bool = False,
    ) -> MutateCampaignAssetSetsResponse:
        """Link multiple asset sets to a campaign.

        Args:
            customer_id: The customer ID.
            campaign: The campaign resource name.
            asset_sets: List of asset set resource names.
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateCampaignAssetSetsResponse: The response containing the results.
        """
        operations = []
        for asset_set in asset_sets:
            operation = self.create_campaign_asset_set_operation(
                campaign=campaign,
                asset_set=asset_set,
            )
            operations.append(operation)

        return self.mutate_campaign_asset_sets(
            customer_id=customer_id,
            operations=operations,
            validate_only=validate_only,
        )

    def link_asset_set_to_multiple_campaigns(
        self,
        customer_id: str,
        campaigns: List[str],
        asset_set: str,
        validate_only: bool = False,
    ) -> MutateCampaignAssetSetsResponse:
        """Link an asset set to multiple campaigns.

        Args:
            customer_id: The customer ID.
            campaigns: List of campaign resource names.
            asset_set: The asset set resource name.
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateCampaignAssetSetsResponse: The response containing the results.
        """
        operations = []
        for campaign in campaigns:
            operation = self.create_campaign_asset_set_operation(
                campaign=campaign,
                asset_set=asset_set,
            )
            operations.append(operation)

        return self.mutate_campaign_asset_sets(
            customer_id=customer_id,
            operations=operations,
            validate_only=validate_only,
        )


def register_campaign_asset_set_tools(mcp: FastMCP[Any]) -> None:
    """Register campaign asset set tools with the MCP server."""

    @mcp.tool
    async def mutate_campaign_asset_sets(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        operations: list[dict[str, Any]],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: str = "RESOURCE_NAME_ONLY",
    ) -> dict[str, Any]:
        """Create or remove campaign asset set associations.

        Args:
            customer_id: The customer ID
            operations: List of campaign asset set operations
            partial_failure: Enable partial failure
            validate_only: Only validate the request
            response_content_type: Response content type (RESOURCE_NAME_ONLY, MUTABLE_RESOURCE)

        Returns:
            Response with results and any partial failure errors
        """
        service = CampaignAssetSetService()

        # Convert response content type string to enum
        response_content_type_enum = getattr(
            ResponseContentTypeEnum.ResponseContentType, response_content_type
        )

        ops = []
        for op_data in operations:
            op_type = op_data["operation_type"]

            if op_type == "create":
                operation = service.create_campaign_asset_set_operation(
                    campaign=op_data["campaign"],
                    asset_set=op_data["asset_set"],
                )
            elif op_type == "remove":
                operation = service.create_remove_operation(
                    resource_name=op_data["resource_name"]
                )
            else:
                raise ValueError(f"Invalid operation type: {op_type}")

            ops.append(operation)

        response = service.mutate_campaign_asset_sets(
            customer_id=customer_id,
            operations=ops,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type_enum,
        )

        # Format response
        results = []
        for result in response.results:
            result_data: dict[str, Any] = {
                "resource_name": result.resource_name,
            }
            if result.campaign_asset_set:
                result_data["campaign_asset_set"] = {
                    "resource_name": result.campaign_asset_set.resource_name,
                    "campaign": result.campaign_asset_set.campaign,
                    "asset_set": result.campaign_asset_set.asset_set,
                    "status": result.campaign_asset_set.status.name
                    if result.campaign_asset_set.status
                    else None,
                }
            results.append(result_data)

        return {
            "results": results,
            "partial_failure_error": str(response.partial_failure_error)
            if response.partial_failure_error
            else None,
        }

    @mcp.tool
    async def link_asset_set_to_campaign(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        campaign: str,
        asset_set: str,
        validate_only: bool = False,
    ) -> dict[str, Any]:
        """Link an asset set to a campaign.

        Args:
            customer_id: The customer ID
            campaign: The campaign resource name
            asset_set: The asset set resource name
            validate_only: Only validate the request

        Returns:
            Created campaign asset set details
        """
        service = CampaignAssetSetService()

        response = service.link_asset_set_to_campaign(
            customer_id=customer_id,
            campaign=campaign,
            asset_set=asset_set,
            validate_only=validate_only,
        )

        result = response.results[0] if response.results else None
        return {
            "resource_name": result.resource_name if result else None,
            "operation": "link_asset_set_to_campaign",
            "campaign": campaign,
            "asset_set": asset_set,
        }

    @mcp.tool
    async def unlink_asset_set_from_campaign(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        resource_name: str,
        validate_only: bool = False,
    ) -> dict[str, Any]:
        """Unlink an asset set from a campaign.

        Args:
            customer_id: The customer ID
            resource_name: The campaign asset set resource name to remove
            validate_only: Only validate the request

        Returns:
            Removal result details
        """
        service = CampaignAssetSetService()

        response = service.unlink_asset_set_from_campaign(
            customer_id=customer_id,
            resource_name=resource_name,
            validate_only=validate_only,
        )

        result = response.results[0] if response.results else None
        return {
            "resource_name": result.resource_name if result else None,
            "operation": "unlink",
            "removed_resource_name": resource_name,
        }

    @mcp.tool
    async def link_multiple_asset_sets_to_campaign(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        campaign: str,
        asset_sets: list[str],
        validate_only: bool = False,
    ) -> dict[str, Any]:
        """Link multiple asset sets to a campaign.

        Args:
            customer_id: The customer ID
            campaign: The campaign resource name
            asset_sets: List of asset set resource names
            validate_only: Only validate the request

        Returns:
            Results with count of linked asset sets
        """
        service = CampaignAssetSetService()

        response = service.link_multiple_asset_sets_to_campaign(
            customer_id=customer_id,
            campaign=campaign,
            asset_sets=asset_sets,
            validate_only=validate_only,
        )

        return {
            "operation": "link_multiple_asset_sets",
            "campaign": campaign,
            "asset_sets_count": len(asset_sets),
            "results_count": len(response.results),
        }

    @mcp.tool
    async def link_asset_set_to_multiple_campaigns(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        campaigns: list[str],
        asset_set: str,
        validate_only: bool = False,
    ) -> dict[str, Any]:
        """Link an asset set to multiple campaigns.

        Args:
            customer_id: The customer ID
            campaigns: List of campaign resource names
            asset_set: The asset set resource name
            validate_only: Only validate the request

        Returns:
            Results with count of linked campaigns
        """
        service = CampaignAssetSetService()

        response = service.link_asset_set_to_multiple_campaigns(
            customer_id=customer_id,
            campaigns=campaigns,
            asset_set=asset_set,
            validate_only=validate_only,
        )

        return {
            "operation": "link_to_multiple_campaigns",
            "asset_set": asset_set,
            "campaigns_count": len(campaigns),
            "results_count": len(response.results),
        }
