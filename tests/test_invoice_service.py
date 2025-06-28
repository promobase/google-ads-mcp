"""Tests for InvoiceService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.month_of_year import MonthOfYearEnum
from google.ads.googleads.v20.services.services.invoice_service import (
    InvoiceServiceClient,
)
from google.ads.googleads.v20.services.types.invoice_service import (
    ListInvoicesResponse,
)

from src.services.account.invoice_service import (
    InvoiceService,
    register_invoice_tools,
)


@pytest.fixture
def invoice_service(mock_sdk_client: Any) -> InvoiceService:
    """Create an InvoiceService instance with mocked dependencies."""
    # Mock InvoiceService client
    mock_invoice_client = Mock(spec=InvoiceServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_invoice_client  # type: ignore

    with patch(
        "src.sdk_services.account.invoice_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = InvoiceService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_list_invoices(
    invoice_service: InvoiceService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing invoices."""
    # Arrange
    customer_id = "1234567890"
    billing_setup = "customers/1234567890/billingSetups/999888777"
    issue_year = "2024"
    issue_month = MonthOfYearEnum.MonthOfYear.JANUARY

    # Create mock response
    mock_response = Mock(spec=ListInvoicesResponse)

    # Create mock invoices
    mock_invoices = []
    for i in range(2):
        invoice = Mock()
        invoice.resource_name = f"customers/{customer_id}/invoices/{i + 100}"
        invoice.id = str(i + 100)
        invoice.type = Mock()
        invoice.type.name = "INVOICE"
        invoice.billing_setup = billing_setup
        invoice.issue_date = f"{issue_year}-01-{15 + i}"
        invoice.due_date = f"{issue_year}-02-{15 + i}"
        invoice.currency_code = "USD"
        invoice.service_date_range = Mock()
        invoice.service_date_range.start_date = f"{issue_year}-01-01"
        invoice.service_date_range.end_date = f"{issue_year}-01-31"
        invoice.subtotal_amount_micros = 100000000 * (i + 1)  # $100 and $200
        invoice.tax_amount_micros = 10000000 * (i + 1)  # $10 and $20
        invoice.total_amount_micros = 110000000 * (i + 1)  # $110 and $220
        invoice.corrected_invoice = ""
        invoice.replaced_invoices = []
        invoice.pdf_url = f"https://example.com/invoice_{i + 100}.pdf"

        # Add account budget summaries
        invoice.account_budget_summaries = []
        summary = Mock()
        summary.customer = f"customers/{customer_id}"
        summary.customer_descriptive_name = "Test Customer"
        summary.account_budget = f"customers/{customer_id}/accountBudgets/{i + 200}"
        summary.account_budget_name = f"Budget {i + 1}"
        summary.purchase_order_number = f"PO-{i + 1000}"
        summary.subtotal_amount_micros = 100000000 * (i + 1)
        summary.tax_amount_micros = 10000000 * (i + 1)
        summary.total_amount_micros = 110000000 * (i + 1)
        summary.billable_activity_date_range = Mock()
        summary.billable_activity_date_range.start_date = f"{issue_year}-01-01"
        summary.billable_activity_date_range.end_date = f"{issue_year}-01-31"
        invoice.account_budget_summaries.append(summary)

        mock_invoices.append(invoice)

    mock_response.invoices = mock_invoices

    # Get the mocked invoice service client
    mock_invoice_client = invoice_service.client  # type: ignore
    mock_invoice_client.list_invoices.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "invoices": [
            {
                "resource_name": f"customers/{customer_id}/invoices/{i + 100}",
                "id": str(i + 100),
                "type": "INVOICE",
                "billing_setup": billing_setup,
                "issue_date": f"{issue_year}-01-{15 + i}",
                "due_date": f"{issue_year}-02-{15 + i}",
                "currency_code": "USD",
                "service_date_range": {
                    "start_date": f"{issue_year}-01-01",
                    "end_date": f"{issue_year}-01-31",
                },
                "subtotal_amount_micros": 100000000 * (i + 1),
                "tax_amount_micros": 10000000 * (i + 1),
                "total_amount_micros": 110000000 * (i + 1),
                "corrected_invoice": "",
                "replaced_invoices": [],
                "pdf_url": f"https://example.com/invoice_{i + 100}.pdf",
                "account_budget_summaries": [
                    {
                        "customer": f"customers/{customer_id}",
                        "customer_descriptive_name": "Test Customer",
                        "account_budget": f"customers/{customer_id}/accountBudgets/{i + 200}",
                        "account_budget_name": f"Budget {i + 1}",
                        "purchase_order_number": f"PO-{i + 1000}",
                        "subtotal_amount_micros": 100000000 * (i + 1),
                        "tax_amount_micros": 10000000 * (i + 1),
                        "total_amount_micros": 110000000 * (i + 1),
                        "billable_activity_date_range": {
                            "start_date": f"{issue_year}-01-01",
                            "end_date": f"{issue_year}-01-31",
                        },
                    }
                ],
            }
            for i in range(2)
        ]
    }

    with patch(
        "src.sdk_services.account.invoice_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await invoice_service.list_invoices(
            ctx=mock_ctx,
            customer_id=customer_id,
            billing_setup=billing_setup,
            issue_year=issue_year,
            issue_month=issue_month,
        )

    # Assert
    assert result == expected_result
    assert len(result["invoices"]) == 2

    # Verify the API call
    mock_invoice_client.list_invoices.assert_called_once()  # type: ignore
    call_args = mock_invoice_client.list_invoices.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert request.billing_setup == billing_setup
    assert request.issue_year == issue_year
    assert request.issue_month == issue_month

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Found 2 invoices for {issue_year}-{issue_month}",
    )


@pytest.mark.asyncio
async def test_list_invoices_december(
    invoice_service: InvoiceService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing invoices for December."""
    # Arrange
    customer_id = "1234567890"
    billing_setup = "customers/1234567890/billingSetups/999888777"
    issue_year = "2023"
    issue_month = MonthOfYearEnum.MonthOfYear.DECEMBER

    # Create mock response with empty list
    mock_response = Mock(spec=ListInvoicesResponse)
    mock_response.invoices = []

    # Get the mocked invoice service client
    mock_invoice_client = invoice_service.client  # type: ignore
    mock_invoice_client.list_invoices.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"invoices": []}

    with patch(
        "src.sdk_services.account.invoice_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await invoice_service.list_invoices(
            ctx=mock_ctx,
            customer_id=customer_id,
            billing_setup=billing_setup,
            issue_year=issue_year,
            issue_month=issue_month,
        )

    # Assert
    assert result == expected_result
    assert len(result["invoices"]) == 0

    # Verify December was properly passed
    call_args = mock_invoice_client.list_invoices.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.issue_month == MonthOfYearEnum.MonthOfYear.DECEMBER

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Found 0 invoices for {issue_year}-{issue_month}",
    )


@pytest.mark.asyncio
async def test_list_invoices_with_credit_memo(
    invoice_service: InvoiceService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing invoices including credit memos."""
    # Arrange
    customer_id = "1234567890"
    billing_setup = "customers/1234567890/billingSetups/999888777"
    issue_year = "2024"
    issue_month = MonthOfYearEnum.MonthOfYear.MARCH

    # Create mock response
    mock_response = Mock(spec=ListInvoicesResponse)

    # Create a regular invoice and a credit memo
    invoice = Mock()
    invoice.resource_name = f"customers/{customer_id}/invoices/100"
    invoice.id = "100"
    invoice.type = Mock()
    invoice.type.name = "INVOICE"
    invoice.billing_setup = billing_setup
    invoice.issue_date = f"{issue_year}-03-15"
    invoice.due_date = f"{issue_year}-04-15"
    invoice.currency_code = "USD"
    invoice.subtotal_amount_micros = 200000000  # $200
    invoice.tax_amount_micros = 20000000  # $20
    invoice.total_amount_micros = 220000000  # $220
    invoice.corrected_invoice = ""
    invoice.replaced_invoices = []
    invoice.pdf_url = "https://example.com/invoice_100.pdf"
    invoice.account_budget_summaries = []

    credit_memo = Mock()
    credit_memo.resource_name = f"customers/{customer_id}/invoices/101"
    credit_memo.id = "101"
    credit_memo.type = Mock()
    credit_memo.type.name = "CREDIT_MEMO"
    credit_memo.billing_setup = billing_setup
    credit_memo.issue_date = f"{issue_year}-03-20"
    credit_memo.due_date = f"{issue_year}-04-20"
    credit_memo.currency_code = "USD"
    credit_memo.subtotal_amount_micros = -50000000  # -$50 (credit)
    credit_memo.tax_amount_micros = -5000000  # -$5 (credit)
    credit_memo.total_amount_micros = -55000000  # -$55 (credit)
    credit_memo.corrected_invoice = f"customers/{customer_id}/invoices/100"
    credit_memo.replaced_invoices = []
    credit_memo.pdf_url = "https://example.com/credit_memo_101.pdf"
    credit_memo.account_budget_summaries = []

    mock_response.invoices = [invoice, credit_memo]

    # Get the mocked invoice service client
    mock_invoice_client = invoice_service.client  # type: ignore
    mock_invoice_client.list_invoices.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "invoices": [
            {
                "resource_name": f"customers/{customer_id}/invoices/100",
                "id": "100",
                "type": "INVOICE",
                "billing_setup": billing_setup,
                "total_amount_micros": 220000000,
            },
            {
                "resource_name": f"customers/{customer_id}/invoices/101",
                "id": "101",
                "type": "CREDIT_MEMO",
                "billing_setup": billing_setup,
                "total_amount_micros": -55000000,
                "corrected_invoice": f"customers/{customer_id}/invoices/100",
            },
        ]
    }

    with patch(
        "src.sdk_services.account.invoice_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await invoice_service.list_invoices(
            ctx=mock_ctx,
            customer_id=customer_id,
            billing_setup=billing_setup,
            issue_year=issue_year,
            issue_month=issue_month,
        )

    # Assert
    assert result == expected_result
    assert len(result["invoices"]) == 2

    # Check invoice types
    assert result["invoices"][0]["type"] == "INVOICE"
    assert result["invoices"][1]["type"] == "CREDIT_MEMO"

    # Check credit memo references original invoice
    assert (
        result["invoices"][1]["corrected_invoice"]
        == result["invoices"][0]["resource_name"]
    )

    # Check amounts
    assert result["invoices"][0]["total_amount_micros"] > 0  # Invoice is positive
    assert result["invoices"][1]["total_amount_micros"] < 0  # Credit memo is negative


@pytest.mark.asyncio
async def test_error_handling_list_invoices(
    invoice_service: InvoiceService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when listing invoices fails."""
    # Arrange
    customer_id = "1234567890"
    billing_setup = "customers/1234567890/billingSetups/999888777"
    issue_year = "2024"
    issue_month = MonthOfYearEnum.MonthOfYear.JANUARY

    # Get the mocked invoice service client and make it raise exception
    mock_invoice_client = invoice_service.client  # type: ignore
    mock_invoice_client.list_invoices.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await invoice_service.list_invoices(
            ctx=mock_ctx,
            customer_id=customer_id,
            billing_setup=billing_setup,
            issue_year=issue_year,
            issue_month=issue_month,
        )

    assert "Failed to list invoices" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to list invoices: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_tool_wrapper_list_invoices(
    invoice_service: InvoiceService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test the tool wrapper for list_invoices with string month conversion."""
    # Arrange
    customer_id = "1234567890"
    billing_setup = "customers/1234567890/billingSetups/999888777"
    issue_year = "2024"
    issue_month_str = "JANUARY"  # String input from tool

    # Create mock response
    mock_response = Mock(spec=ListInvoicesResponse)
    mock_response.invoices = []

    # Get the mocked invoice service client
    mock_invoice_client = invoice_service.client  # type: ignore
    mock_invoice_client.list_invoices.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"invoices": []}

    # Import the tool function
    from src.services.account.invoice_service import create_invoice_tools

    tools = create_invoice_tools(invoice_service)
    list_invoices_tool = tools[0]  # First (and only) tool

    with patch(
        "src.sdk_services.account.invoice_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await list_invoices_tool(
            ctx=mock_ctx,
            customer_id=customer_id,
            billing_setup=billing_setup,
            issue_year=issue_year,
            issue_month=issue_month_str,
        )

    # Assert
    assert result == expected_result

    # Verify the enum conversion worked correctly
    call_args = mock_invoice_client.list_invoices.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.issue_month == MonthOfYearEnum.MonthOfYear.JANUARY


@pytest.mark.asyncio
async def test_tool_wrapper_list_invoices_case_insensitive(
    invoice_service: InvoiceService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test the tool wrapper handles case-insensitive month names."""
    # Arrange
    customer_id = "1234567890"
    billing_setup = "customers/1234567890/billingSetups/999888777"
    issue_year = "2024"
    issue_month_str = "december"  # lowercase input

    # Create mock response
    mock_response = Mock(spec=ListInvoicesResponse)
    mock_response.invoices = []

    # Get the mocked invoice service client
    mock_invoice_client = invoice_service.client  # type: ignore
    mock_invoice_client.list_invoices.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"invoices": []}

    # Import the tool function
    from src.services.account.invoice_service import create_invoice_tools

    tools = create_invoice_tools(invoice_service)
    list_invoices_tool = tools[0]

    with patch(
        "src.sdk_services.account.invoice_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        _ = await list_invoices_tool(
            ctx=mock_ctx,
            customer_id=customer_id,
            billing_setup=billing_setup,
            issue_year=issue_year,
            issue_month=issue_month_str,
        )

    # Assert - should work with lowercase input
    call_args = mock_invoice_client.list_invoices.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.issue_month == MonthOfYearEnum.MonthOfYear.DECEMBER


def test_register_invoice_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_invoice_tools(mock_mcp)

    # Assert
    assert isinstance(service, InvoiceService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 1  # Only 1 tool (list_invoices)  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = ["list_invoices"]

    assert set(tool_names) == set(expected_tools)
