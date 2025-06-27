"""Asset Group Signal Service for Google Ads API v20.

This service manages audience and search theme signals for Performance Max asset groups.
Signals help Performance Max campaigns identify users most likely to convert.
"""

from typing import Any, List, Optional

from fastmcp import FastMCP
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

from src.sdk_client import get_sdk_client

# Exception handling


class AssetGroupSignalService:
    """Service for managing asset group signals in Google Ads.

    Asset group signals help Performance Max campaigns identify users most likely to convert
    by providing audience and search theme signals.
    """

    def __init__(self) -> None:
        """Initialize the asset group signal service."""
        self._client: Optional[AssetGroupSignalServiceClient] = None

    @property
    def client(self) -> AssetGroupSignalServiceClient:
        """Get the asset group signal service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AssetGroupSignalService")
        assert self._client is not None
        return self._client

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
            return self.client.mutate_asset_group_signals(request=request)
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


def register_asset_group_signal_tools(mcp: FastMCP[Any]) -> None:
    """Register asset group signal tools with the MCP server."""

    @mcp.tool
    async def mutate_asset_group_signals(
        customer_id: str,
        operations: list[dict[str, Any]],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: str = "RESOURCE_NAME_ONLY",
    ) -> dict[str, Any]:
        """Create or remove asset group signals for Performance Max campaigns.

        Args:
            customer_id: The customer ID
            operations: List of asset group signal operations
            partial_failure: Enable partial failure
            validate_only: Only validate the request
            response_content_type: Response content type (RESOURCE_NAME_ONLY, MUTABLE_RESOURCE)

        Returns:
            Response with results and any partial failure errors
        """
        service = AssetGroupSignalService()

        # Convert response content type string to enum
        response_content_type_enum = getattr(
            ResponseContentTypeEnum.ResponseContentType, response_content_type
        )

        ops = []
        for op_data in operations:
            op_type = op_data["operation_type"]

            if op_type == "create":
                audience_info = None
                search_theme_info = None

                if "audience_resource_name" in op_data:
                    audience_info = AudienceInfo(
                        audience=op_data["audience_resource_name"]
                    )
                elif "search_theme" in op_data:
                    search_theme_info = SearchThemeInfo(text=op_data["search_theme"])

                operation = service.create_asset_group_signal_operation(
                    asset_group=op_data["asset_group"],
                    audience_info=audience_info,
                    search_theme_info=search_theme_info,
                )
            elif op_type == "remove":
                operation = service.create_remove_operation(
                    resource_name=op_data["resource_name"]
                )
            else:
                raise ValueError(f"Invalid operation type: {op_type}")

            ops.append(operation)

        response = service.mutate_asset_group_signals(
            customer_id=customer_id,
            operations=ops,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type_enum,
        )

        # Format response
        results = []
        for result in response.results:
            result_data = {
                "resource_name": result.resource_name,
            }
            if result.asset_group_signal:
                signal = result.asset_group_signal
                result_data["asset_group_signal"] = {
                    "resource_name": signal.resource_name,
                    "asset_group": signal.asset_group,
                    "approval_status": signal.approval_status.name
                    if signal.approval_status
                    else None,
                }
                if signal.audience:
                    result_data["asset_group_signal"]["audience"] = (
                        signal.audience.audience
                    )
                elif signal.search_theme:
                    result_data["asset_group_signal"]["search_theme"] = (
                        signal.search_theme.text
                    )
            results.append(result_data)

        return {
            "results": results,
            "partial_failure_error": str(response.partial_failure_error)
            if response.partial_failure_error
            else None,
        }

    @mcp.tool
    async def create_audience_signal(
        customer_id: str,
        asset_group: str,
        audience_resource_name: str,
        validate_only: bool = False,
    ) -> dict[str, Any]:
        """Create an audience signal for a Performance Max asset group.

        Args:
            customer_id: The customer ID
            asset_group: The asset group resource name
            audience_resource_name: The audience resource name
            validate_only: Only validate the request

        Returns:
            Created signal details
        """
        service = AssetGroupSignalService()

        operation = service.create_audience_signal(
            asset_group=asset_group,
            audience_resource_name=audience_resource_name,
        )

        response = service.mutate_asset_group_signals(
            customer_id=customer_id,
            operations=[operation],
            validate_only=validate_only,
        )

        result = response.results[0] if response.results else None
        return {
            "resource_name": result.resource_name if result else None,
            "operation": "create_audience_signal",
            "asset_group": asset_group,
            "audience": audience_resource_name,
        }

    @mcp.tool
    async def create_search_theme_signal(
        customer_id: str,
        asset_group: str,
        search_theme: str,
        validate_only: bool = False,
    ) -> dict[str, Any]:
        """Create a search theme signal for a Performance Max asset group.

        Args:
            customer_id: The customer ID
            asset_group: The asset group resource name
            search_theme: The search theme text
            validate_only: Only validate the request

        Returns:
            Created signal details
        """
        service = AssetGroupSignalService()

        operation = service.create_search_theme_signal(
            asset_group=asset_group,
            search_theme=search_theme,
        )

        response = service.mutate_asset_group_signals(
            customer_id=customer_id,
            operations=[operation],
            validate_only=validate_only,
        )

        result = response.results[0] if response.results else None
        return {
            "resource_name": result.resource_name if result else None,
            "operation": "create_search_theme_signal",
            "asset_group": asset_group,
            "search_theme": search_theme,
        }

    @mcp.tool
    async def remove_asset_group_signal(
        customer_id: str,
        resource_name: str,
        validate_only: bool = False,
    ) -> dict[str, Any]:
        """Remove an asset group signal.

        Args:
            customer_id: The customer ID
            resource_name: The asset group signal resource name to remove
            validate_only: Only validate the request

        Returns:
            Removal result details
        """
        service = AssetGroupSignalService()

        operation = service.create_remove_operation(resource_name=resource_name)

        response = service.mutate_asset_group_signals(
            customer_id=customer_id,
            operations=[operation],
            validate_only=validate_only,
        )

        result = response.results[0] if response.results else None
        return {
            "resource_name": result.resource_name if result else None,
            "operation": "remove",
            "removed_resource_name": resource_name,
        }
