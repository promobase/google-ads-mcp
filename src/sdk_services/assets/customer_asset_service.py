"""Customer Asset Service for Google Ads API v20.

This service manages customer-level asset associations, allowing assets to be linked
to customers for use across campaigns.
"""

from typing import List, Optional

from google.ads.googleads.v20.services.services.customer_asset_service import (
    CustomerAssetServiceClient,
)
from google.ads.googleads.v20.services.types.customer_asset_service import (
    CustomerAssetOperation,
    MutateCustomerAssetsRequest,
    MutateCustomerAssetsResponse,
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

# Exception handling


class CustomerAssetService:
    """Service for managing customer assets in Google Ads.

    Customer assets are assets linked at the customer level that can be used
    across multiple campaigns.
    """

    def __init__(self, client: CustomerAssetServiceClient):
        self._client = client

    def mutate_customer_assets(
        self,
        customer_id: str,
        operations: List[CustomerAssetOperation],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: ResponseContentTypeEnum.ResponseContentType = ResponseContentTypeEnum.ResponseContentType.RESOURCE_NAME_ONLY,
    ) -> MutateCustomerAssetsResponse:
        """Create, update, or remove customer assets.

        Args:
            customer_id: The customer ID.
            operations: List of operations to perform.
            partial_failure: If true, successful operations will be carried out and invalid
                operations will return errors.
            validate_only: If true, the request is validated but not executed.
            response_content_type: The response content type setting.

        Returns:
            MutateCustomerAssetsResponse: The response containing results.

        Raises:
            GoogleAdsException: If the request fails.
        """
        try:
            request = MutateCustomerAssetsRequest(
                customer_id=customer_id,
                operations=operations,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )
            return self._client.mutate_customer_assets(request=request)
        except Exception as e:
            raise Exception(f"Failed to mutate customer assets: {e}") from e

    def create_customer_asset_operation(
        self,
        asset: str,
        field_type: AssetFieldTypeEnum.AssetFieldType,
        status: AssetLinkStatusEnum.AssetLinkStatus = AssetLinkStatusEnum.AssetLinkStatus.ENABLED,
    ) -> CustomerAssetOperation:
        """Create a customer asset operation for creation.

        Args:
            asset: The asset resource name.
            field_type: The asset field type (role of the asset).
            status: The status of the asset link.

        Returns:
            CustomerAssetOperation: The operation to create the customer asset.
        """
        customer_asset = CustomerAsset(
            asset=asset,
            field_type=field_type,
            status=status,
        )

        return CustomerAssetOperation(create=customer_asset)

    def create_update_operation(
        self,
        resource_name: str,
        status: Optional[AssetLinkStatusEnum.AssetLinkStatus] = None,
        update_mask: Optional[field_mask_pb2.FieldMask] = None,
    ) -> CustomerAssetOperation:
        """Create a customer asset operation for update.

        Args:
            resource_name: The resource name of the customer asset to update.
            status: The new status of the asset link.
            update_mask: The field mask specifying which fields to update.

        Returns:
            CustomerAssetOperation: The operation to update the customer asset.
        """
        customer_asset = CustomerAsset(resource_name=resource_name)

        if status is not None:
            customer_asset.status = status

        # Create update mask if not provided
        if update_mask is None:
            paths = []
            if status is not None:
                paths.append("status")
            update_mask = field_mask_pb2.FieldMask(paths=paths)

        return CustomerAssetOperation(
            update=customer_asset,
            update_mask=update_mask,
        )

    def create_remove_operation(self, resource_name: str) -> CustomerAssetOperation:
        """Create a customer asset operation for removal.

        Args:
            resource_name: The resource name of the customer asset to remove.
                Format: customers/{customer_id}/customerAssets/{asset_id}~{field_type}

        Returns:
            CustomerAssetOperation: The operation to remove the customer asset.
        """
        return CustomerAssetOperation(remove=resource_name)

    def create_customer_asset(
        self,
        customer_id: str,
        asset: str,
        field_type: AssetFieldTypeEnum.AssetFieldType,
        status: AssetLinkStatusEnum.AssetLinkStatus = AssetLinkStatusEnum.AssetLinkStatus.ENABLED,
        validate_only: bool = False,
    ) -> MutateCustomerAssetsResponse:
        """Create a single customer asset.

        Args:
            customer_id: The customer ID.
            asset: The asset resource name.
            field_type: The asset field type.
            status: The status of the asset link.
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateCustomerAssetsResponse: The response containing the result.
        """
        operation = self.create_customer_asset_operation(
            asset=asset,
            field_type=field_type,
            status=status,
        )

        return self.mutate_customer_assets(
            customer_id=customer_id,
            operations=[operation],
            validate_only=validate_only,
        )

    def update_customer_asset_status(
        self,
        customer_id: str,
        resource_name: str,
        status: AssetLinkStatusEnum.AssetLinkStatus,
        validate_only: bool = False,
    ) -> MutateCustomerAssetsResponse:
        """Update the status of a customer asset.

        Args:
            customer_id: The customer ID.
            resource_name: The resource name of the customer asset.
            status: The new status.
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateCustomerAssetsResponse: The response containing the result.
        """
        operation = self.create_update_operation(
            resource_name=resource_name,
            status=status,
        )

        return self.mutate_customer_assets(
            customer_id=customer_id,
            operations=[operation],
            validate_only=validate_only,
        )

    def remove_customer_asset(
        self,
        customer_id: str,
        resource_name: str,
        validate_only: bool = False,
    ) -> MutateCustomerAssetsResponse:
        """Remove a customer asset.

        Args:
            customer_id: The customer ID.
            resource_name: The resource name of the customer asset to remove.
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateCustomerAssetsResponse: The response containing the result.
        """
        operation = self.create_remove_operation(resource_name=resource_name)

        return self.mutate_customer_assets(
            customer_id=customer_id,
            operations=[operation],
            validate_only=validate_only,
        )
