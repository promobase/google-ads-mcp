"""Tests for Google Ads Product Link Service"""

import pytest
from unittest.mock import Mock

from google.ads.googleads.v20.resources.types.product_link import (
    ProductLink,
    DataPartnerIdentifier,
    GoogleAdsIdentifier,
    MerchantCenterIdentifier,
)
from google.ads.googleads.v20.services.types.product_link_service import (
    CreateProductLinkRequest,
    CreateProductLinkResponse,
    RemoveProductLinkRequest,
    RemoveProductLinkResponse,
)

from src.sdk_services.product_integration.product_link_service import ProductLinkService


class TestProductLinkService:
    """Test cases for ProductLinkService"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Google Ads client"""
        client = Mock()
        service = Mock()
        client.get_service.return_value = service
        return client

    @pytest.fixture
    def product_link_service(self, mock_client):
        """Create ProductLinkService instance with mock client"""
        return ProductLinkService(mock_client)

    def test_create_product_link(self, product_link_service, mock_client):
        """Test creating a product link"""
        # Setup
        customer_id = "1234567890"
        product_link = ProductLink()

        mock_response = CreateProductLinkResponse(
            resource_name="customers/1234567890/productLinks/123"
        )
        mock_client.get_service.return_value.create_product_link.return_value = (
            mock_response
        )

        # Execute
        response = product_link_service.create_product_link(
            customer_id=customer_id, product_link=product_link
        )

        # Verify
        assert response == mock_response
        mock_client.get_service.assert_called_with("ProductLinkService")

        # Verify request
        call_args = mock_client.get_service.return_value.create_product_link.call_args
        request = call_args.kwargs["request"]
        assert request.customer_id == customer_id
        assert request.product_link == product_link

    def test_remove_product_link(self, product_link_service, mock_client):
        """Test removing a product link"""
        # Setup
        customer_id = "1234567890"
        resource_name = "customers/1234567890/productLinks/123"

        mock_response = RemoveProductLinkResponse(resource_name=resource_name)
        mock_client.get_service.return_value.remove_product_link.return_value = (
            mock_response
        )

        # Execute
        response = product_link_service.remove_product_link(
            customer_id=customer_id, resource_name=resource_name
        )

        # Verify
        assert response == mock_response

        # Verify request
        call_args = mock_client.get_service.return_value.remove_product_link.call_args
        request = call_args.kwargs["request"]
        assert request.customer_id == customer_id
        assert request.resource_name == resource_name

    def test_create_merchant_center_link(self, product_link_service, mock_client):
        """Test creating a Merchant Center link"""
        # Setup
        customer_id = "1234567890"
        merchant_center_id = 123456789

        mock_response = CreateProductLinkResponse(
            resource_name="customers/1234567890/productLinks/123"
        )
        mock_client.get_service.return_value.create_product_link.return_value = (
            mock_response
        )

        # Execute
        response = product_link_service.create_merchant_center_link(
            customer_id=customer_id, merchant_center_id=merchant_center_id
        )

        # Verify
        assert response == mock_response

        # Verify request
        call_args = mock_client.get_service.return_value.create_product_link.call_args
        request = call_args.kwargs["request"]
        assert request.customer_id == customer_id
        assert (
            request.product_link.merchant_center.merchant_center_id
            == merchant_center_id
        )

    def test_create_google_ads_link(self, product_link_service, mock_client):
        """Test creating a Google Ads link"""
        # Setup
        customer_id = "1234567890"
        linked_customer_id = 9876543210

        mock_response = CreateProductLinkResponse(
            resource_name="customers/1234567890/productLinks/123"
        )
        mock_client.get_service.return_value.create_product_link.return_value = (
            mock_response
        )

        # Execute
        response = product_link_service.create_google_ads_link(
            customer_id=customer_id, linked_customer_id=linked_customer_id
        )

        # Verify
        assert response == mock_response

        # Verify request
        call_args = mock_client.get_service.return_value.create_product_link.call_args
        request = call_args.kwargs["request"]
        assert request.customer_id == customer_id
        assert (
            request.product_link.google_ads.customer
            == f"customers/{linked_customer_id}"
        )

    def test_create_data_partner_link(self, product_link_service, mock_client):
        """Test creating a data partner link"""
        # Setup
        customer_id = "1234567890"
        data_partner_id = 555666777

        mock_response = CreateProductLinkResponse(
            resource_name="customers/1234567890/productLinks/123"
        )
        mock_client.get_service.return_value.create_product_link.return_value = (
            mock_response
        )

        # Execute
        response = product_link_service.create_data_partner_link(
            customer_id=customer_id, data_partner_id=data_partner_id
        )

        # Verify
        assert response == mock_response

        # Verify request
        call_args = mock_client.get_service.return_value.create_product_link.call_args
        request = call_args.kwargs["request"]
        assert request.customer_id == customer_id
        assert request.product_link.data_partner.data_partner_id == data_partner_id
