"""Conversion adjustment upload service implementation using Google Ads SDK."""

from typing import Any, Dict, List, Optional, Callable, Awaitable

from fastmcp import Context, FastMCP
from google.ads.googleads.v20.services.services.conversion_adjustment_upload_service import (
    ConversionAdjustmentUploadServiceClient,
)
from google.ads.googleads.v20.services.types.conversion_adjustment_upload_service import (
    UploadConversionAdjustmentsRequest,
    UploadConversionAdjustmentsResponse,
    ConversionAdjustment,
    GclidDateTimePair,
    RestatementValue,
)
from google.ads.googleads.v20.enums.types.conversion_adjustment_type import (
    ConversionAdjustmentTypeEnum,
)
from google.ads.googleads.errors import GoogleAdsException

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class ConversionAdjustmentUploadService:
    """Conversion adjustment upload service for adjusting conversion values."""

    def __init__(self) -> None:
        """Initialize the conversion adjustment upload service."""
        self._client: Optional[ConversionAdjustmentUploadServiceClient] = None

    @property
    def client(self) -> ConversionAdjustmentUploadServiceClient:
        """Get the conversion adjustment upload service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service(
                "ConversionAdjustmentUploadService"
            )
        assert self._client is not None
        return self._client

    async def upload_conversion_adjustments(
        self,
        ctx: Context,
        customer_id: str,
        adjustments: List[Dict[str, Any]],
        partial_failure: bool = True,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Upload conversion adjustments to modify previously uploaded conversions.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            adjustments: List of conversion adjustments to upload
            partial_failure: Whether to allow partial failure
            validate_only: Whether to only validate without uploading

        Returns:
            Upload results with success/failure counts
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create conversion adjustments
            conversion_adjustments = []
            for adj in adjustments:
                adjustment = ConversionAdjustment()

                # Set conversion action
                adjustment.conversion_action = adj["conversion_action"]

                # Set adjustment type
                adjustment.adjustment_type = getattr(
                    ConversionAdjustmentTypeEnum.ConversionAdjustmentType,
                    adj["adjustment_type"],
                )

                # Set adjustment date time
                adjustment.adjustment_date_time = adj["adjustment_date_time"]

                # Set GCLID and conversion date time
                if "gclid" in adj and "conversion_date_time" in adj:
                    gclid_pair = GclidDateTimePair()
                    gclid_pair.gclid = adj["gclid"]
                    gclid_pair.conversion_date_time = adj["conversion_date_time"]
                    adjustment.gclid_date_time_pair = gclid_pair

                # Set order ID if provided
                if "order_id" in adj:
                    adjustment.order_id = adj["order_id"]

                # Set restatement value if this is a restatement
                if (
                    adj["adjustment_type"] == "RESTATEMENT"
                    and "restatement_value" in adj
                ):
                    restatement = RestatementValue()
                    restatement.adjusted_value = adj["restatement_value"][
                        "adjusted_value"
                    ]
                    restatement.currency_code = adj["restatement_value"][
                        "currency_code"
                    ]
                    adjustment.restatement_value = restatement

                # Set user identifiers if provided for enhanced conversions
                if "user_identifiers" in adj:
                    for identifier in adj["user_identifiers"]:
                        user_id = adjustment.user_identifiers.add()  # type: ignore
                        if "hashed_email" in identifier:
                            user_id.hashed_email = identifier["hashed_email"]
                        if "hashed_phone_number" in identifier:
                            user_id.hashed_phone_number = identifier[
                                "hashed_phone_number"
                            ]
                        if "address_info" in identifier:
                            addr = user_id.address_info
                            addr_info = identifier["address_info"]
                            if "hashed_first_name" in addr_info:
                                addr.hashed_first_name = addr_info["hashed_first_name"]
                            if "hashed_last_name" in addr_info:
                                addr.hashed_last_name = addr_info["hashed_last_name"]
                            if "country_code" in addr_info:
                                addr.country_code = addr_info["country_code"]
                            if "postal_code" in addr_info:
                                addr.postal_code = addr_info["postal_code"]

                conversion_adjustments.append(adjustment)

            # Create request
            request = UploadConversionAdjustmentsRequest()
            request.customer_id = customer_id
            request.conversion_adjustments = conversion_adjustments
            request.partial_failure = partial_failure
            request.validate_only = validate_only

            # Upload adjustments
            response: UploadConversionAdjustmentsResponse = (
                self.client.upload_conversion_adjustments(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Uploaded {len(adjustments)} conversion adjustments",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to upload conversion adjustments: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_restatement_adjustment(
        self,
        ctx: Context,
        customer_id: str,
        conversion_action: str,
        gclid: str,
        conversion_date_time: str,
        adjustment_date_time: str,
        adjusted_value: float,
        currency_code: str,
        order_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a restatement adjustment for a specific conversion.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            conversion_action: Conversion action resource name
            gclid: Google click ID
            conversion_date_time: Original conversion date time (YYYY-MM-DD HH:MM:SS)
            adjustment_date_time: Adjustment date time (YYYY-MM-DD HH:MM:SS)
            adjusted_value: New conversion value
            currency_code: Currency code (e.g., "USD")
            order_id: Optional order ID for the conversion

        Returns:
            Upload result
        """
        adjustment = {
            "conversion_action": conversion_action,
            "adjustment_type": "RESTATEMENT",
            "gclid": gclid,
            "conversion_date_time": conversion_date_time,
            "adjustment_date_time": adjustment_date_time,
            "restatement_value": {
                "adjusted_value": adjusted_value,
                "currency_code": currency_code,
            },
        }

        if order_id:
            adjustment["order_id"] = order_id

        return await self.upload_conversion_adjustments(
            ctx=ctx,
            customer_id=customer_id,
            adjustments=[adjustment],
        )

    async def create_retraction_adjustment(
        self,
        ctx: Context,
        customer_id: str,
        conversion_action: str,
        gclid: str,
        conversion_date_time: str,
        adjustment_date_time: str,
        order_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a retraction adjustment to remove a conversion.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            conversion_action: Conversion action resource name
            gclid: Google click ID
            conversion_date_time: Original conversion date time (YYYY-MM-DD HH:MM:SS)
            adjustment_date_time: Adjustment date time (YYYY-MM-DD HH:MM:SS)
            order_id: Optional order ID for the conversion

        Returns:
            Upload result
        """
        adjustment = {
            "conversion_action": conversion_action,
            "adjustment_type": "RETRACTION",
            "gclid": gclid,
            "conversion_date_time": conversion_date_time,
            "adjustment_date_time": adjustment_date_time,
        }

        if order_id:
            adjustment["order_id"] = order_id

        return await self.upload_conversion_adjustments(
            ctx=ctx,
            customer_id=customer_id,
            adjustments=[adjustment],
        )


def create_conversion_adjustment_upload_tools(
    service: ConversionAdjustmentUploadService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the conversion adjustment upload service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def upload_conversion_adjustments(
        ctx: Context,
        customer_id: str,
        adjustments: List[Dict[str, Any]],
        partial_failure: bool = True,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Upload conversion adjustments to modify previously uploaded conversions.

        Args:
            customer_id: The customer ID
            adjustments: List of conversion adjustments. Each adjustment dict should contain:
                - conversion_action: Conversion action resource name
                - adjustment_type: RESTATEMENT or RETRACTION
                - gclid: Google click ID
                - conversion_date_time: Original conversion date (YYYY-MM-DD HH:MM:SS)
                - adjustment_date_time: When adjustment occurred (YYYY-MM-DD HH:MM:SS)
                - order_id: Optional order ID
                - restatement_value: For RESTATEMENT type, dict with:
                    - adjusted_value: New conversion value
                    - currency_code: Currency code (e.g., "USD")
                - user_identifiers: Optional for enhanced conversions, list of dicts with:
                    - hashed_email: SHA256 hashed email
                    - hashed_phone_number: SHA256 hashed phone
                    - address_info: Dict with hashed_first_name, hashed_last_name, country_code, postal_code
            partial_failure: Whether to allow partial failure
            validate_only: Whether to only validate without uploading

        Returns:
            Upload results with success/failure counts and job_id
        """
        return await service.upload_conversion_adjustments(
            ctx=ctx,
            customer_id=customer_id,
            adjustments=adjustments,
            partial_failure=partial_failure,
            validate_only=validate_only,
        )

    async def create_restatement_adjustment(
        ctx: Context,
        customer_id: str,
        conversion_action: str,
        gclid: str,
        conversion_date_time: str,
        adjustment_date_time: str,
        adjusted_value: float,
        currency_code: str,
        order_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a restatement adjustment to change a conversion's value.

        Args:
            customer_id: The customer ID
            conversion_action: Conversion action resource name (e.g., "customers/123/conversionActions/456")
            gclid: Google click ID from the original conversion
            conversion_date_time: Original conversion date time (YYYY-MM-DD HH:MM:SS format)
            adjustment_date_time: When this adjustment occurred (YYYY-MM-DD HH:MM:SS format)
            adjusted_value: New conversion value to replace the original
            currency_code: Currency code (e.g., "USD", "EUR")
            order_id: Optional order ID to match the original conversion

        Returns:
            Upload result with success/failure information
        """
        return await service.create_restatement_adjustment(
            ctx=ctx,
            customer_id=customer_id,
            conversion_action=conversion_action,
            gclid=gclid,
            conversion_date_time=conversion_date_time,
            adjustment_date_time=adjustment_date_time,
            adjusted_value=adjusted_value,
            currency_code=currency_code,
            order_id=order_id,
        )

    async def create_retraction_adjustment(
        ctx: Context,
        customer_id: str,
        conversion_action: str,
        gclid: str,
        conversion_date_time: str,
        adjustment_date_time: str,
        order_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a retraction adjustment to remove a conversion entirely.

        Args:
            customer_id: The customer ID
            conversion_action: Conversion action resource name (e.g., "customers/123/conversionActions/456")
            gclid: Google click ID from the original conversion
            conversion_date_time: Original conversion date time (YYYY-MM-DD HH:MM:SS format)
            adjustment_date_time: When this adjustment occurred (YYYY-MM-DD HH:MM:SS format)
            order_id: Optional order ID to match the original conversion

        Returns:
            Upload result with success/failure information
        """
        return await service.create_retraction_adjustment(
            ctx=ctx,
            customer_id=customer_id,
            conversion_action=conversion_action,
            gclid=gclid,
            conversion_date_time=conversion_date_time,
            adjustment_date_time=adjustment_date_time,
            order_id=order_id,
        )

    tools.extend(
        [
            upload_conversion_adjustments,
            create_restatement_adjustment,
            create_retraction_adjustment,
        ]
    )
    return tools


def register_conversion_adjustment_upload_tools(
    mcp: FastMCP[Any],
) -> ConversionAdjustmentUploadService:
    """Register conversion adjustment upload tools with the MCP server.

    Returns the ConversionAdjustmentUploadService instance for testing purposes.
    """
    service = ConversionAdjustmentUploadService()
    tools = create_conversion_adjustment_upload_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
