"""Asset Group Signal Service for Google Ads API v20.

This service manages audience and search theme signals for Performance Max asset groups.
Signals help Performance Max campaigns identify users most likely to convert.
"""

from typing import List, Optional

from google.ads.googleads.v20.services.services.asset_group_signal_service import (
    AssetGroupSignalServiceClient,
)
from google.ads.googleads.v20.services.types.asset_group_signal_service import (
    AssetGroupSignalOperation,
    MutateAssetGroupSignalsRequest,
    MutateAssetGroupSignalsResponse,
)
from google.ads.googleads.v20.resources.types.asset_group_signal import AssetGroupSignal
from google.ads.googleads.v20.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v20.common.types.criteria import AudienceInfo, SearchThemeInfo
from google.ads.googleads.v20.common.types.policy import PolicyViolationKey

# Exception handling


class AssetGroupSignalService:
    """Service for managing asset group signals in Google Ads.

    Asset group signals help Performance Max campaigns identify users most likely to convert
    by providing audience and search theme signals.
    """

    def __init__(self, client: AssetGroupSignalServiceClient):
        self._client = client

    def mutate_asset_group_signals(
        self,
        customer_id: str,
        operations: List[AssetGroupSignalOperation],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: ResponseContentTypeEnum.ResponseContentType = ResponseContentTypeEnum.ResponseContentType.RESOURCE_NAME_ONLY,
    ) -> MutateAssetGroupSignalsResponse:
        """Create or remove asset group signals.

        Args:
            customer_id: The customer ID.
            operations: List of operations to perform.
            partial_failure: If true, successful operations will be carried out and invalid
                operations will return errors.
            validate_only: If true, the request is validated but not executed.
            response_content_type: The response content type setting.

        Returns:
            MutateAssetGroupSignalsResponse: The response containing results.

        Raises:
            GoogleAdsException: If the request fails.
        """
        try:
            request = MutateAssetGroupSignalsRequest(
                customer_id=customer_id,
                operations=operations,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )
            return self._client.mutate_asset_group_signals(request=request)
        except Exception as e:
            raise Exception(f"Failed to mutate asset group signals: {e}") from e

    def create_asset_group_signal_operation(
        self,
        asset_group: str,
        audience_info: Optional[AudienceInfo] = None,
        search_theme_info: Optional[SearchThemeInfo] = None,
        exempt_policy_violation_keys: Optional[List[PolicyViolationKey]] = None,
    ) -> AssetGroupSignalOperation:
        """Create an asset group signal operation for creation.

        Args:
            asset_group: The asset group resource name.
            audience_info: The audience signal (mutually exclusive with search_theme_info).
            search_theme_info: The search theme signal (mutually exclusive with audience_info).
            exempt_policy_violation_keys: Policy violation keys to exempt.

        Returns:
            AssetGroupSignalOperation: The operation to create the signal.

        Raises:
            ValueError: If both or neither signal types are provided.
        """
        if (audience_info is None) == (search_theme_info is None):
            raise ValueError(
                "Exactly one of audience_info or search_theme_info must be provided"
            )

        signal = AssetGroupSignal(asset_group=asset_group)

        if audience_info:
            signal.audience = audience_info
        elif search_theme_info:
            signal.search_theme = search_theme_info

        operation = AssetGroupSignalOperation(create=signal)

        if exempt_policy_violation_keys:
            operation.exempt_policy_violation_keys.extend(exempt_policy_violation_keys)

        return operation

    def create_remove_operation(
        self,
        resource_name: str,
        exempt_policy_violation_keys: Optional[List[PolicyViolationKey]] = None,
    ) -> AssetGroupSignalOperation:
        """Create an asset group signal operation for removal.

        Args:
            resource_name: The resource name of the signal to remove.
                Format: customers/{customer_id}/assetGroupSignals/{asset_group_id}~{criterion_id}
            exempt_policy_violation_keys: Policy violation keys to exempt.

        Returns:
            AssetGroupSignalOperation: The operation to remove the signal.
        """
        operation = AssetGroupSignalOperation(remove=resource_name)

        if exempt_policy_violation_keys:
            operation.exempt_policy_violation_keys.extend(exempt_policy_violation_keys)

        return operation

    def create_audience_signal(
        self,
        asset_group: str,
        audience_resource_name: str,
        exempt_policy_violation_keys: Optional[List[PolicyViolationKey]] = None,
    ) -> AssetGroupSignalOperation:
        """Create an audience signal operation.

        Args:
            asset_group: The asset group resource name.
            audience_resource_name: The audience resource name.
            exempt_policy_violation_keys: Policy violation keys to exempt.

        Returns:
            AssetGroupSignalOperation: The operation to create the audience signal.
        """
        audience_info = AudienceInfo(audience=audience_resource_name)
        return self.create_asset_group_signal_operation(
            asset_group=asset_group,
            audience_info=audience_info,
            exempt_policy_violation_keys=exempt_policy_violation_keys,
        )

    def create_search_theme_signal(
        self,
        asset_group: str,
        search_theme: str,
        exempt_policy_violation_keys: Optional[List[PolicyViolationKey]] = None,
    ) -> AssetGroupSignalOperation:
        """Create a search theme signal operation.

        Args:
            asset_group: The asset group resource name.
            search_theme: The search theme text.
            exempt_policy_violation_keys: Policy violation keys to exempt.

        Returns:
            AssetGroupSignalOperation: The operation to create the search theme signal.
        """
        search_theme_info = SearchThemeInfo(text=search_theme)
        return self.create_asset_group_signal_operation(
            asset_group=asset_group,
            search_theme_info=search_theme_info,
            exempt_policy_violation_keys=exempt_policy_violation_keys,
        )
