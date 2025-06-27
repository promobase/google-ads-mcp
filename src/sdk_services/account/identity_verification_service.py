"""Identity verification service implementation using Google Ads SDK."""

from typing import Any, Dict, List, Optional, Callable, Awaitable

from fastmcp import Context, FastMCP
from google.ads.googleads.v20.services.services.identity_verification_service import (
    IdentityVerificationServiceClient,
)
from google.ads.googleads.v20.services.types.identity_verification_service import (
    StartIdentityVerificationRequest,
    GetIdentityVerificationRequest,
    GetIdentityVerificationResponse,
)
from google.ads.googleads.v20.enums.types.identity_verification_program import (
    IdentityVerificationProgramEnum,
)
from google.ads.googleads.errors import GoogleAdsException

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger

logger = get_logger(__name__)


class IdentityVerificationService:
    """Identity verification service for managing account identity verification."""

    def __init__(self) -> None:
        """Initialize the identity verification service."""
        self._client: Optional[IdentityVerificationServiceClient] = None

    @property
    def client(self) -> IdentityVerificationServiceClient:
        """Get the identity verification service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("IdentityVerificationService")
        assert self._client is not None
        return self._client

    async def start_identity_verification(
        self,
        ctx: Context,
        customer_id: str,
        verification_program: str,
    ) -> Dict[str, Any]:
        """Start identity verification for a customer.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            verification_program: Verification program type (ADVERTISER_IDENTITY_VERIFICATION, ADVERTISER_LEGAL_ENTITY_VERIFICATION)

        Returns:
            Identity verification start result
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create request
            request = StartIdentityVerificationRequest()
            request.customer_id = customer_id
            request.verification_program = getattr(
                IdentityVerificationProgramEnum.IdentityVerificationProgram,
                verification_program,
            )

            # Make the API call
            self.client.start_identity_verification(request=request)

            await ctx.log(
                level="info",
                message=f"Started identity verification for program: {verification_program}",
            )

            return {
                "customer_id": customer_id,
                "verification_program": verification_program,
                "status": "STARTED",
                "message": "Identity verification process has been initiated",
            }

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to start identity verification: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def get_identity_verification(
        self,
        ctx: Context,
        customer_id: str,
    ) -> List[Dict[str, Any]]:
        """Get identity verification status for a customer.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID

        Returns:
            List of identity verification details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create request
            request = GetIdentityVerificationRequest()
            request.customer_id = customer_id

            # Make the API call
            response: GetIdentityVerificationResponse = (
                self.client.get_identity_verification(request=request)
            )

            # Process results
            verifications = []
            for verification in response.identity_verification:
                verification_dict: dict[str, Any] = {
                    "verification_program": verification.verification_program.name
                    if verification.verification_program
                    else "UNKNOWN",
                }

                # Add requirement details if available
                if verification.identity_verification_requirement:
                    requirement = verification.identity_verification_requirement
                    verification_dict["requirement"] = {
                        "verification_start_deadline_time": requirement.verification_start_deadline_time,
                        "verification_completion_deadline_time": requirement.verification_completion_deadline_time,
                    }

                # Add progress details if available
                if verification.verification_progress:
                    progress = verification.verification_progress
                    verification_dict["progress"] = {
                        "program_status": progress.program_status.name
                        if progress.program_status
                        else "UNKNOWN",
                        "invitation_link_expiration_time": progress.invitation_link_expiration_time,
                        "action_url": progress.action_url,
                    }

                verifications.append(verification_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(verifications)} identity verifications",
            )

            return verifications

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to get identity verification: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_identity_verification_tools(
    service: IdentityVerificationService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the identity verification service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def start_identity_verification(
        ctx: Context,
        customer_id: str,
        verification_program: str,
    ) -> Dict[str, Any]:
        """Start identity verification process for a customer account.

        Args:
            customer_id: The customer ID
            verification_program: Verification program type (ADVERTISER_IDENTITY_VERIFICATION, ADVERTISER_LEGAL_ENTITY_VERIFICATION)

        Returns:
            Identity verification start result with status
        """
        return await service.start_identity_verification(
            ctx=ctx,
            customer_id=customer_id,
            verification_program=verification_program,
        )

    async def get_identity_verification(
        ctx: Context,
        customer_id: str,
    ) -> List[Dict[str, Any]]:
        """Get identity verification status and requirements for a customer.

        Args:
            customer_id: The customer ID

        Returns:
            List of identity verification details including status, deadlines, and action URLs
        """
        return await service.get_identity_verification(
            ctx=ctx,
            customer_id=customer_id,
        )

    tools.extend([start_identity_verification, get_identity_verification])
    return tools


def register_identity_verification_tools(
    mcp: FastMCP[Any],
) -> IdentityVerificationService:
    """Register identity verification tools with the MCP server.

    Returns the IdentityVerificationService instance for testing purposes.
    """
    service = IdentityVerificationService()
    tools = create_identity_verification_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
