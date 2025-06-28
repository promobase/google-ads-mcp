"""Conversion upload service implementation using Google Ads SDK."""

import hashlib
from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.common.types.offline_user_data import (
    UserIdentifier,
)
from google.ads.googleads.v20.services.services.conversion_upload_service import (
    ConversionUploadServiceClient,
)
from google.ads.googleads.v20.services.types.conversion_upload_service import (
    CallConversion,
    ClickConversion,
    UploadCallConversionsRequest,
    UploadCallConversionsResponse,
    UploadClickConversionsRequest,
    UploadClickConversionsResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class ConversionUploadService:
    """Conversion upload service for offline conversion tracking."""

    def __init__(self) -> None:
        """Initialize the conversion upload service."""
        self._client: Optional[ConversionUploadServiceClient] = None

    @property
    def client(self) -> ConversionUploadServiceClient:
        """Get the conversion upload service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("ConversionUploadService")
        assert self._client is not None
        return self._client

    def _normalize_and_hash(self, value: str) -> str:
        """Normalize and hash a value for user matching.

        Args:
            value: The value to normalize and hash

        Returns:
            SHA256 hash of the normalized value
        """
        # Normalize: lowercase and strip whitespace
        normalized = value.lower().strip()
        # Hash with SHA256
        return hashlib.sha256(normalized.encode()).hexdigest()

    async def upload_click_conversions(
        self,
        ctx: Context,
        customer_id: str,
        conversions: List[Dict[str, Any]],
        partial_failure: bool = True,
    ) -> Dict[str, Any]:
        """Upload click conversions from offline sources.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            conversions: List of conversions to upload, each containing:
                - gclid: Google Click ID (required)
                - conversion_action_id: Conversion action ID (required)
                - conversion_date_time: ISO format datetime string (required)
                - conversion_value: Conversion value (optional)
                - currency_code: Currency code (optional)
                - order_id: Order ID for deduplication (optional)
                - user_identifiers: User identifiers for enhanced conversions (optional)
                    Can include: email, phone_number, address info
            partial_failure: Whether to process valid conversions if some fail

        Returns:
            Upload results including successful and failed conversions
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create click conversions
            click_conversions = []
            for conv_data in conversions:
                conversion = ClickConversion()
                conversion.gclid = conv_data["gclid"]
                conversion.conversion_action = f"customers/{customer_id}/conversionActions/{conv_data['conversion_action_id']}"
                conversion.conversion_date_time = conv_data["conversion_date_time"]

                if "conversion_value" in conv_data:
                    conversion.conversion_value = float(conv_data["conversion_value"])

                if "currency_code" in conv_data:
                    conversion.currency_code = conv_data["currency_code"]

                if "order_id" in conv_data:
                    conversion.order_id = conv_data["order_id"]

                # Add user identifiers for enhanced conversions
                if "user_identifiers" in conv_data:
                    for identifier_data in conv_data["user_identifiers"]:
                        identifier = UserIdentifier()

                        if "email" in identifier_data:
                            identifier.hashed_email = self._normalize_and_hash(
                                identifier_data["email"]
                            )
                        elif "phone_number" in identifier_data:
                            identifier.hashed_phone_number = self._normalize_and_hash(
                                identifier_data["phone_number"]
                            )
                        elif "address" in identifier_data:
                            addr = identifier_data["address"]
                            if "first_name" in addr:
                                identifier.address_info.hashed_first_name = (
                                    self._normalize_and_hash(addr["first_name"])
                                )
                            if "last_name" in addr:
                                identifier.address_info.hashed_last_name = (
                                    self._normalize_and_hash(addr["last_name"])
                                )
                            if "postal_code" in addr:
                                identifier.address_info.postal_code = addr[
                                    "postal_code"
                                ]
                            if "country_code" in addr:
                                identifier.address_info.country_code = addr[
                                    "country_code"
                                ]

                        conversion.user_identifiers.append(identifier)

                click_conversions.append(conversion)

            # Create request
            request = UploadClickConversionsRequest()
            request.customer_id = customer_id
            request.conversions = click_conversions
            request.partial_failure = partial_failure

            # Make the API call
            response: UploadClickConversionsResponse = (
                self.client.upload_click_conversions(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Uploaded {len(conversions)} click conversions",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to upload click conversions: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def upload_call_conversions(
        self,
        ctx: Context,
        customer_id: str,
        conversions: List[Dict[str, Any]],
        partial_failure: bool = True,
    ) -> Dict[str, Any]:
        """Upload call conversions from offline sources.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            conversions: List of call conversions to upload, each containing:
                - caller_id: Phone number that called (required)
                - call_start_date_time: ISO format datetime string (required)
                - conversion_action_id: Conversion action ID (required)
                - conversion_date_time: ISO format datetime string (required)
                - conversion_value: Conversion value (optional)
                - currency_code: Currency code (optional)
            partial_failure: Whether to process valid conversions if some fail

        Returns:
            Upload results including successful and failed conversions
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create call conversions
            call_conversions = []
            for conv_data in conversions:
                conversion = CallConversion()
                conversion.caller_id = conv_data["caller_id"]
                conversion.call_start_date_time = conv_data["call_start_date_time"]
                conversion.conversion_action = f"customers/{customer_id}/conversionActions/{conv_data['conversion_action_id']}"
                conversion.conversion_date_time = conv_data["conversion_date_time"]

                if "conversion_value" in conv_data:
                    conversion.conversion_value = float(conv_data["conversion_value"])

                if "currency_code" in conv_data:
                    conversion.currency_code = conv_data["currency_code"]

                call_conversions.append(conversion)

            # Create request
            request = UploadCallConversionsRequest()
            request.customer_id = customer_id
            request.conversions = call_conversions
            request.partial_failure = partial_failure

            # Make the API call
            response: UploadCallConversionsResponse = (
                self.client.upload_call_conversions(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Uploaded {len(conversions)} call conversions",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to upload call conversions: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_conversion_upload_tools(
    service: ConversionUploadService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the conversion upload service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def upload_click_conversions(
        ctx: Context,
        customer_id: str,
        conversions: List[Dict[str, Any]],
        partial_failure: bool = True,
    ) -> Dict[str, Any]:
        """Upload click conversions from offline sources.

        Use this to upload conversions that happened offline after a user clicked your ad.

        Args:
            customer_id: The customer ID
            conversions: List of conversions to upload, each containing:
                - gclid: Google Click ID from the ad click (required)
                - conversion_action_id: ID of the conversion action to credit (required)
                - conversion_date_time: When the conversion happened, ISO format (required)
                    Example: "2024-01-15 10:30:00-08:00"
                - conversion_value: Value of the conversion (optional)
                - currency_code: Currency code like "USD" (optional)
                - order_id: Order ID for deduplication (optional)
                - user_identifiers: For enhanced conversions (optional), list of:
                    - {"email": "user@example.com"}
                    - {"phone_number": "+1234567890"}
                    - {"address": {"first_name": "John", "last_name": "Doe",
                                   "postal_code": "12345", "country_code": "US"}}
            partial_failure: Process valid conversions even if some fail

        Returns:
            Upload results with:
            - successful_conversions: Count of successful uploads
            - failed_conversions: Count of failed uploads
            - results: Details for each conversion
            - partial_failure_error: Error details if any
        """
        return await service.upload_click_conversions(
            ctx=ctx,
            customer_id=customer_id,
            conversions=conversions,
            partial_failure=partial_failure,
        )

    async def upload_call_conversions(
        ctx: Context,
        customer_id: str,
        conversions: List[Dict[str, Any]],
        partial_failure: bool = True,
    ) -> Dict[str, Any]:
        """Upload call conversions from offline sources.

        Use this to upload conversions from phone calls that resulted in sales.

        Args:
            customer_id: The customer ID
            conversions: List of call conversions to upload, each containing:
                - caller_id: Phone number that called (required)
                    Example: "+1234567890"
                - call_start_date_time: When the call started, ISO format (required)
                    Example: "2024-01-15 10:00:00-08:00"
                - conversion_action_id: ID of the conversion action to credit (required)
                - conversion_date_time: When the conversion happened, ISO format (required)
                    Example: "2024-01-15 10:30:00-08:00"
                - conversion_value: Value of the conversion (optional)
                - currency_code: Currency code like "USD" (optional)
            partial_failure: Process valid conversions even if some fail

        Returns:
            Upload results with:
            - successful_conversions: Count of successful uploads
            - failed_conversions: Count of failed uploads
            - results: Details for each conversion
            - partial_failure_error: Error details if any
        """
        return await service.upload_call_conversions(
            ctx=ctx,
            customer_id=customer_id,
            conversions=conversions,
            partial_failure=partial_failure,
        )

    tools.extend([upload_click_conversions, upload_call_conversions])
    return tools


def register_conversion_upload_tools(mcp: FastMCP[Any]) -> ConversionUploadService:
    """Register conversion upload tools with the MCP server.

    Returns the ConversionUploadService instance for testing purposes.
    """
    service = ConversionUploadService()
    tools = create_conversion_upload_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
