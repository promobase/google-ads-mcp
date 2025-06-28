"""Google Ads Product Link Service

This module provides functionality for managing product links in Google Ads.
Product links connect Google Ads accounts with other Google products like Merchant Center.
"""

from typing import Any, Optional

from fastmcp import FastMCP
from google.ads.googleads.v20.resources.types.product_link import (
    ProductLink,
    DataPartnerIdentifier,
    GoogleAdsIdentifier,
    MerchantCenterIdentifier,
)
from google.ads.googleads.v20.services.services.product_link_service import (
    ProductLinkServiceClient,
)
from google.ads.googleads.v20.services.types.product_link_service import (
    CreateProductLinkRequest,
    CreateProductLinkResponse,
    RemoveProductLinkRequest,
    RemoveProductLinkResponse,
)

from src.sdk_client import get_sdk_client


class ProductLinkService:
    """Service for managing Google Ads product links."""

    def __init__(self) -> None:
        """Initialize the product link service."""
        self._client: Optional[ProductLinkServiceClient] = None

    @property
    def client(self) -> ProductLinkServiceClient:
        """Get the product link service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("ProductLinkService")
        assert self._client is not None
        return self._client

    def create_product_link(
        self,
        customer_id: str,
        product_link: ProductLink,
    ) -> CreateProductLinkResponse:
        """Create a product link.

        Args:
            customer_id: The customer ID
            product_link: The product link to create

        Returns:
            CreateProductLinkResponse: The response containing the created product link resource name
        """
        request = CreateProductLinkRequest(
            customer_id=customer_id,
            product_link=product_link,
        )
        return self.client.create_product_link(request=request)

    def remove_product_link(  # pyright: ignore[reportUnusedFunction]
        self,
        customer_id: str,
        resource_name: str,
    ) -> RemoveProductLinkResponse:
        """Remove a product link.

        Args:
            customer_id: The customer ID
            resource_name: The product link resource name to remove

        Returns:
            RemoveProductLinkResponse: The response containing the removed product link resource name
        """
        request = RemoveProductLinkRequest(
            customer_id=customer_id,
            resource_name=resource_name,
        )
        return self.client.remove_product_link(request=request)

    def create_merchant_center_link(  # pyright: ignore[reportUnusedFunction]
        self,
        customer_id: str,
        merchant_center_id: int,
    ) -> CreateProductLinkResponse:
        """Create a Merchant Center product link.

        Args:
            customer_id: The customer ID
            merchant_center_id: The Merchant Center account ID

        Returns:
            CreateProductLinkResponse: The response containing the created product link resource name
        """
        merchant_center_identifier = MerchantCenterIdentifier(
            merchant_center_id=merchant_center_id
        )

        product_link = ProductLink(merchant_center=merchant_center_identifier)

        return self.create_product_link(
            customer_id=customer_id, product_link=product_link
        )

    def create_google_ads_link(  # pyright: ignore[reportUnusedFunction]
        self,
        customer_id: str,
        linked_customer_id: int,
    ) -> CreateProductLinkResponse:
        """Create a Google Ads product link.

        Args:
            customer_id: The customer ID
            linked_customer_id: The linked Google Ads customer ID

        Returns:
            CreateProductLinkResponse: The response containing the created product link resource name
        """
        google_ads_identifier = GoogleAdsIdentifier(
            customer=f"customers/{linked_customer_id}"
        )

        product_link = ProductLink(google_ads=google_ads_identifier)

        return self.create_product_link(
            customer_id=customer_id, product_link=product_link
        )

    def create_data_partner_link(  # pyright: ignore[reportUnusedFunction]
        self,
        customer_id: str,
        data_partner_id: int,
    ) -> CreateProductLinkResponse:
        """Create a Data Partner product link.

        Args:
            customer_id: The customer ID
            data_partner_id: The data partner ID

        Returns:
            CreateProductLinkResponse: The response containing the created product link resource name
        """
        data_partner_identifier = DataPartnerIdentifier(data_partner_id=data_partner_id)

        product_link = ProductLink(data_partner=data_partner_identifier)

        return self.create_product_link(
            customer_id=customer_id, product_link=product_link
        )


def register_product_link_tools(mcp: FastMCP[Any]) -> None:
    """Register product link tools with the MCP server."""

    @mcp.tool
    async def create_merchant_center_link(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        merchant_center_id: int,
    ) -> str:
        """Create a Merchant Center product link.

        Args:
            customer_id: The customer ID
            merchant_center_id: The Merchant Center account ID

        Returns:
            The created product link resource name
        """
        service = ProductLinkService()

        response = service.create_merchant_center_link(
            customer_id=customer_id,
            merchant_center_id=merchant_center_id,
        )

        return f"Created Merchant Center link: {response.resource_name}"

    @mcp.tool
    async def create_google_ads_link(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        linked_customer_id: int,
    ) -> str:
        """Create a Google Ads product link.

        Args:
            customer_id: The customer ID
            linked_customer_id: The linked Google Ads customer ID

        Returns:
            The created product link resource name
        """
        service = ProductLinkService()

        response = service.create_google_ads_link(
            customer_id=customer_id,
            linked_customer_id=linked_customer_id,
        )

        return f"Created Google Ads link: {response.resource_name}"

    @mcp.tool
    async def create_data_partner_link(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        data_partner_id: int,
    ) -> str:
        """Create a Data Partner product link.

        Args:
            customer_id: The customer ID
            data_partner_id: The data partner ID

        Returns:
            The created product link resource name
        """
        service = ProductLinkService()

        response = service.create_data_partner_link(
            customer_id=customer_id,
            data_partner_id=data_partner_id,
        )

        return f"Created Data Partner link: {response.resource_name}"

    @mcp.tool
    async def remove_product_link(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        resource_name: str,
    ) -> str:
        """Remove a product link.

        Args:
            customer_id: The customer ID
            resource_name: The product link resource name to remove

        Returns:
            Success message
        """
        service = ProductLinkService()

        response = service.remove_product_link(
            customer_id=customer_id,
            resource_name=resource_name,
        )

        return f"Removed product link: {response.resource_name}"
