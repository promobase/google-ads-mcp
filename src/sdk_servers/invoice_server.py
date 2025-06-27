"""Invoice server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.account.invoice_service import (
    register_invoice_tools,
)

# Create the invoice server
invoice_sdk_server = FastMCP(name="invoice-service")

# Register the tools
register_invoice_tools(invoice_sdk_server)
