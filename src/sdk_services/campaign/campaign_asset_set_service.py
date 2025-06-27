"""Campaign Asset Set Service for Google Ads API v20.

This service manages asset set associations with campaigns, allowing asset sets
to be linked to campaigns for use in advertising.
"""

from typing import List

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


class CampaignAssetSetService:
    """Service for managing campaign asset sets in Google Ads.

    Campaign asset sets link asset sets to campaigns, enabling the use of
    asset sets in campaign advertising.
    """

    def __init__(self, client: CampaignAssetSetServiceClient):
        self._client = client

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
            return self._client.mutate_campaign_asset_sets(request=request)
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
