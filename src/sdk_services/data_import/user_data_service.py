"""User data service implementation using Google Ads SDK."""

from typing import Any, Dict, List, Optional, Callable, Awaitable

from fastmcp import Context, FastMCP
from google.ads.googleads.v20.services.services.user_data_service import (
    UserDataServiceClient,
)
from google.ads.googleads.v20.services.types.user_data_service import (
    UploadUserDataRequest,
    UploadUserDataResponse,
    UserDataOperation,
)
from google.ads.googleads.v20.common.types.offline_user_data import (
    UserData,
    UserIdentifier,
    TransactionAttribute,
    StoreAttribute,
    UserAttribute,
    ShoppingLoyalty,
    CustomerMatchUserListMetadata,
    OfflineUserAddressInfo,
)
from google.ads.googleads.v20.enums.types.user_identifier_source import (
    UserIdentifierSourceEnum,
)
from google.ads.googleads.errors import GoogleAdsException

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger

logger = get_logger(__name__)


class UserDataService:
    """User data service for enhanced conversions and customer match uploads."""

    def __init__(self) -> None:
        """Initialize the user data service."""
        self._client: Optional[UserDataServiceClient] = None

    @property
    def client(self) -> UserDataServiceClient:
        """Get the user data service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("UserDataService")
        assert self._client is not None
        return self._client

    async def upload_enhanced_conversions(
        self,
        ctx: Context,
        customer_id: str,
        conversion_adjustments: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Upload enhanced conversions with user data.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            conversion_adjustments: List of conversion adjustments with user data

        Returns:
            Upload result with success/failure details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create user data operations
            operations = []
            for adjustment in conversion_adjustments:
                operation = UserDataOperation()

                # Create user data
                user_data = UserData()

                # Set user identifiers
                if "user_identifiers" in adjustment:
                    for identifier_dict in adjustment["user_identifiers"]:
                        identifier = UserIdentifier()

                        # Set identifier based on type
                        if "hashed_email" in identifier_dict:
                            identifier.hashed_email = identifier_dict["hashed_email"]
                            identifier.user_identifier_source = UserIdentifierSourceEnum.UserIdentifierSource.FIRST_PARTY
                        elif "hashed_phone_number" in identifier_dict:
                            identifier.hashed_phone_number = identifier_dict[
                                "hashed_phone_number"
                            ]
                            identifier.user_identifier_source = UserIdentifierSourceEnum.UserIdentifierSource.FIRST_PARTY
                        elif "address_info" in identifier_dict:
                            address_info = OfflineUserAddressInfo()
                            addr = identifier_dict["address_info"]

                            if "hashed_first_name" in addr:
                                address_info.hashed_first_name = addr[
                                    "hashed_first_name"
                                ]
                            if "hashed_last_name" in addr:
                                address_info.hashed_last_name = addr["hashed_last_name"]
                            if "country_code" in addr:
                                address_info.country_code = addr["country_code"]
                            if "postal_code" in addr:
                                address_info.postal_code = addr["postal_code"]
                            if "hashed_street_address" in addr:
                                address_info.hashed_street_address = addr[
                                    "hashed_street_address"
                                ]

                            identifier.address_info = address_info
                            identifier.user_identifier_source = UserIdentifierSourceEnum.UserIdentifierSource.FIRST_PARTY

                        user_data.user_identifiers.append(identifier)

                # Set transaction attribute for enhanced conversions
                if "transaction_attribute" in adjustment:
                    trans_attr_dict = adjustment["transaction_attribute"]
                    trans_attr = TransactionAttribute()

                    if "conversion_action" in trans_attr_dict:
                        trans_attr.conversion_action = trans_attr_dict[
                            "conversion_action"
                        ]
                    if "currency_code" in trans_attr_dict:
                        trans_attr.currency_code = trans_attr_dict["currency_code"]
                    if "transaction_amount_micros" in trans_attr_dict:
                        trans_attr.transaction_amount_micros = trans_attr_dict[
                            "transaction_amount_micros"
                        ]
                    if "transaction_date_time" in trans_attr_dict:
                        trans_attr.transaction_date_time = trans_attr_dict[
                            "transaction_date_time"
                        ]
                    if "order_id" in trans_attr_dict:
                        trans_attr.order_id = trans_attr_dict["order_id"]

                    user_data.transaction_attribute = trans_attr

                operation.create = user_data
                operations.append(operation)

            # Create request
            request = UploadUserDataRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Make the API call
            response: UploadUserDataResponse = self.client.upload_user_data(
                request=request
            )

            # Process results
            result = {
                "received_operations_count": response.received_operations_count,
                "upload_date_time": response.upload_date_time,
                "partial_failure_error": str(response.partial_failure_error)
                if response.partial_failure_error
                else None,
            }

            await ctx.log(
                level="info",
                message=f"Uploaded {response.received_operations_count} enhanced conversion operations",
            )

            return result

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to upload enhanced conversions: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def upload_customer_match_data(
        self,
        ctx: Context,
        customer_id: str,
        user_list_id: str,
        user_data_list: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Upload customer match data to a user list.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            user_list_id: The user list ID to upload to
            user_data_list: List of user data to upload

        Returns:
            Upload result with success/failure details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create user data operations
            operations = []
            for user_data_dict in user_data_list:
                operation = UserDataOperation()

                # Create user data
                user_data = UserData()

                # Set user identifiers
                if "user_identifiers" in user_data_dict:
                    for identifier_dict in user_data_dict["user_identifiers"]:
                        identifier = UserIdentifier()

                        # Set identifier based on type
                        if "hashed_email" in identifier_dict:
                            identifier.hashed_email = identifier_dict["hashed_email"]
                        elif "hashed_phone_number" in identifier_dict:
                            identifier.hashed_phone_number = identifier_dict[
                                "hashed_phone_number"
                            ]
                        elif "mobile_id" in identifier_dict:
                            identifier.mobile_id = identifier_dict["mobile_id"]
                        elif "third_party_user_id" in identifier_dict:
                            identifier.third_party_user_id = identifier_dict[
                                "third_party_user_id"
                            ]
                        elif "address_info" in identifier_dict:
                            address_info = OfflineUserAddressInfo()
                            addr = identifier_dict["address_info"]

                            if "hashed_first_name" in addr:
                                address_info.hashed_first_name = addr[
                                    "hashed_first_name"
                                ]
                            if "hashed_last_name" in addr:
                                address_info.hashed_last_name = addr["hashed_last_name"]
                            if "country_code" in addr:
                                address_info.country_code = addr["country_code"]
                            if "postal_code" in addr:
                                address_info.postal_code = addr["postal_code"]
                            if "hashed_street_address" in addr:
                                address_info.hashed_street_address = addr[
                                    "hashed_street_address"
                                ]

                            identifier.address_info = address_info

                        user_data.user_identifiers.append(identifier)

                # Set user attributes if provided
                if "user_attribute" in user_data_dict:
                    user_attr_dict = user_data_dict["user_attribute"]
                    user_attr = UserAttribute()

                    if "lifetime_value_micros" in user_attr_dict:
                        user_attr.lifetime_value_micros = user_attr_dict[
                            "lifetime_value_micros"
                        ]
                    if "lifetime_value_bucket" in user_attr_dict:
                        user_attr.lifetime_value_bucket = user_attr_dict[
                            "lifetime_value_bucket"
                        ]

                    # Set shopping loyalty if provided
                    if "shopping_loyalty" in user_attr_dict:
                        loyalty_dict = user_attr_dict["shopping_loyalty"]
                        loyalty = ShoppingLoyalty()
                        if "loyalty_tier" in loyalty_dict:
                            loyalty.loyalty_tier = loyalty_dict["loyalty_tier"]
                        user_attr.shopping_loyalty = loyalty

                    user_data.user_attribute = user_attr

                operation.create = user_data
                operations.append(operation)

            # Create request with customer match metadata
            request = UploadUserDataRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Set customer match metadata
            customer_match_metadata = CustomerMatchUserListMetadata()
            customer_match_metadata.user_list = (
                f"customers/{customer_id}/userLists/{user_list_id}"
            )
            request.customer_match_user_list_metadata = customer_match_metadata

            # Make the API call
            response: UploadUserDataResponse = self.client.upload_user_data(
                request=request
            )

            # Process results
            result = {
                "received_operations_count": response.received_operations_count,
                "upload_date_time": response.upload_date_time,
                "partial_failure_error": str(response.partial_failure_error)
                if response.partial_failure_error
                else None,
            }

            await ctx.log(
                level="info",
                message=f"Uploaded {response.received_operations_count} customer match operations to user list {user_list_id}",
            )

            return result

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to upload customer match data: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def upload_store_sales_data(
        self,
        ctx: Context,
        customer_id: str,
        conversion_action: str,
        store_sales_data: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Upload store sales data for enhanced conversions.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            conversion_action: The conversion action resource name
            store_sales_data: List of store sales data

        Returns:
            Upload result with success/failure details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create user data operations
            operations = []
            for sales_data in store_sales_data:
                operation = UserDataOperation()

                # Create user data
                user_data = UserData()

                # Set user identifiers (same as other methods)
                if "user_identifiers" in sales_data:
                    for identifier_dict in sales_data["user_identifiers"]:
                        identifier = UserIdentifier()

                        if "hashed_email" in identifier_dict:
                            identifier.hashed_email = identifier_dict["hashed_email"]
                        elif "hashed_phone_number" in identifier_dict:
                            identifier.hashed_phone_number = identifier_dict[
                                "hashed_phone_number"
                            ]
                        # Add other identifier types as needed

                        user_data.user_identifiers.append(identifier)

                # Set transaction attribute
                if "transaction_attribute" in sales_data:
                    trans_attr_dict = sales_data["transaction_attribute"]
                    trans_attr = TransactionAttribute()

                    trans_attr.conversion_action = conversion_action

                    if "currency_code" in trans_attr_dict:
                        trans_attr.currency_code = trans_attr_dict["currency_code"]
                    if "transaction_amount_micros" in trans_attr_dict:
                        trans_attr.transaction_amount_micros = trans_attr_dict[
                            "transaction_amount_micros"
                        ]
                    if "transaction_date_time" in trans_attr_dict:
                        trans_attr.transaction_date_time = trans_attr_dict[
                            "transaction_date_time"
                        ]
                    if "order_id" in trans_attr_dict:
                        trans_attr.order_id = trans_attr_dict["order_id"]

                    # Set store attribute for store sales
                    if "store_code" in trans_attr_dict:
                        store_attr = StoreAttribute()
                        store_attr.store_code = trans_attr_dict["store_code"]
                        trans_attr.store_attribute = store_attr

                    user_data.transaction_attribute = trans_attr

                operation.create = user_data
                operations.append(operation)

            # Create request
            request = UploadUserDataRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Note: StoreSalesMetadata is not supported as a separate field in v20 API
            # Store sales data is handled through transaction attributes with store_code

            # Make the API call
            response: UploadUserDataResponse = self.client.upload_user_data(
                request=request
            )

            # Process results
            result = {
                "received_operations_count": response.received_operations_count,
                "upload_date_time": response.upload_date_time,
                "partial_failure_error": str(response.partial_failure_error)
                if response.partial_failure_error
                else None,
            }

            await ctx.log(
                level="info",
                message=f"Uploaded {response.received_operations_count} store sales operations",
            )

            return result

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to upload store sales data: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_user_data_tools(
    service: UserDataService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the user data service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def upload_enhanced_conversions(
        ctx: Context,
        customer_id: str,
        conversion_adjustments: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Upload enhanced conversions with user data for better attribution.

        Args:
            customer_id: The customer ID
            conversion_adjustments: List of conversion adjustments with user data. Each should contain:
                - user_identifiers: List of identifiers (hashed_email, hashed_phone_number, address_info)
                - transaction_attribute: Transaction details with conversion_action, currency_code,
                  transaction_amount_micros, transaction_date_time, order_id

        Returns:
            Upload result with received operations count and any failure details
        """
        return await service.upload_enhanced_conversions(
            ctx=ctx,
            customer_id=customer_id,
            conversion_adjustments=conversion_adjustments,
        )

    async def upload_customer_match_data(
        ctx: Context,
        customer_id: str,
        user_list_id: str,
        user_data_list: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Upload customer match data to populate a user list.

        Args:
            customer_id: The customer ID
            user_list_id: The user list ID to upload data to
            user_data_list: List of user data. Each should contain:
                - user_identifiers: List of identifiers (hashed_email, hashed_phone_number, mobile_id, etc.)
                - user_attribute: Optional user attributes (lifetime_value_micros, shopping_loyalty)

        Returns:
            Upload result with received operations count and any failure details
        """
        return await service.upload_customer_match_data(
            ctx=ctx,
            customer_id=customer_id,
            user_list_id=user_list_id,
            user_data_list=user_data_list,
        )

    async def upload_store_sales_data(
        ctx: Context,
        customer_id: str,
        conversion_action: str,
        store_sales_data: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Upload store sales data for enhanced conversions from offline sales.

        Args:
            customer_id: The customer ID
            conversion_action: The conversion action resource name
            store_sales_data: List of store sales data. Each should contain:
                - user_identifiers: List of identifiers (hashed_email, hashed_phone_number)
                - transaction_attribute: Transaction details with store_code, currency_code,
                  transaction_amount_micros, transaction_date_time, order_id

        Returns:
            Upload result with received operations count and any failure details
        """
        return await service.upload_store_sales_data(
            ctx=ctx,
            customer_id=customer_id,
            conversion_action=conversion_action,
            store_sales_data=store_sales_data,
        )

    tools.extend(
        [
            upload_enhanced_conversions,
            upload_customer_match_data,
            upload_store_sales_data,
        ]
    )
    return tools


def register_user_data_tools(mcp: FastMCP[Any]) -> UserDataService:
    """Register user data tools with the MCP server.

    Returns the UserDataService instance for testing purposes.
    """
    service = UserDataService()
    tools = create_user_data_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
