"""Identity verification server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.account.identity_verification_service import (
    register_identity_verification_tools,
)

# Create the identity verification server
identity_verification_sdk_server = FastMCP(name="identity-verification-service")

# Register the tools
register_identity_verification_tools(identity_verification_sdk_server)
