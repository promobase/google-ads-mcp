"""Google Ads Product Link Service

This module provides functionality for managing product links in Google Ads.
Product links connect Google Ads accounts with other Google products like Merchant Center.
"""

from typing import Optional

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


class ProductLinkService:
    """Service for managing Google Ads product links."""

    def __init__(self, client):
        self.client = client
        self.service = self.client.get_service("ProductLinkService")

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
        return self.service.create_product_link(request=request)

    def remove_product_link(
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
        return self.service.remove_product_link(request=request)

    def create_merchant_center_link(
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

    def create_google_ads_link(
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

    def create_data_partner_link(
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
