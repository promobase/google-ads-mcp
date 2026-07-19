"""Tests for AssetService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v23.enums.types.asset_type import AssetTypeEnum
from google.ads.googleads.v23.enums.types.mime_type import MimeTypeEnum
from google.ads.googleads.v23.services.services.asset_service import (
    AssetServiceClient,
)
from google.ads.googleads.v23.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v23.services.types.asset_service import (
    MutateAssetsResponse,
)

from src.services.assets.asset_service import (
    AssetService,
    register_asset_tools,
)


@pytest.fixture
def asset_service(mock_sdk_client: Any) -> AssetService:
    """Create an AssetService instance with mocked dependencies."""
    # Mock AssetService client
    mock_asset_service_client = Mock(spec=AssetServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_asset_service_client  # type: ignore

    with patch(
        "src.services.assets.asset_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = AssetService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_text_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a text asset."""
    # Arrange
    customer_id = "1234567890"
    text = "This is a test headline"
    name = "Test Text Asset"

    # Create mock response
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"

    # Get the mocked asset service client
    mock_asset_service_client = asset_service.client  # type: ignore
    mock_asset_service_client.mutate_assets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/assets/123"}]
    }

    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await asset_service.create_text_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            text=text,
            name=name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_asset_service_client.mutate_assets.assert_called_once()  # type: ignore
    call_args = mock_asset_service_client.mutate_assets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert operation.create.type_ == AssetTypeEnum.AssetType.TEXT
    assert operation.create.text_asset.text == text


@pytest.mark.asyncio
async def test_create_text_asset_without_name(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a text asset without explicit name."""
    # Arrange
    customer_id = "1234567890"
    text = "This is a very long test headline that should be truncated in the name"

    # Create mock response
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/124"

    # Get the mocked asset service client
    mock_asset_service_client = asset_service.client  # type: ignore
    mock_asset_service_client.mutate_assets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/assets/124"}]
    }

    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await asset_service.create_text_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            text=text,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_asset_service_client.mutate_assets.assert_called_once()  # type: ignore
    call_args = mock_asset_service_client.mutate_assets.call_args  # type: ignore
    request = call_args[1]["request"]

    operation = request.operations[0]
    # Should use first 50 chars of text as name
    assert operation.create.name == f"Text: {text[:50]}"


@pytest.mark.asyncio
async def test_create_image_asset_base64(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating an image asset from base64 data."""
    import base64

    customer_id = "1234567890"
    raw_bytes = b"fake_image_data"
    b64_str = base64.b64encode(raw_bytes).decode()
    name = "Test Image Asset"

    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/125"

    mock_asset_service_client = asset_service.client  # type: ignore
    mock_asset_service_client.mutate_assets.return_value = mock_response  # type: ignore

    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/assets/125"}]
    }

    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await asset_service.create_image_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            image_data_base64=b64_str,
        )

    assert result == expected_result

    mock_asset_service_client.mutate_assets.assert_called_once()  # type: ignore
    call_args = mock_asset_service_client.mutate_assets.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    assert operation.create.name == name
    assert operation.create.type_ == AssetTypeEnum.AssetType.IMAGE
    assert operation.create.image_asset.data == raw_bytes
    assert operation.create.image_asset.mime_type == MimeTypeEnum.MimeType.IMAGE_JPEG


@pytest.mark.asyncio
async def test_create_image_asset_requires_source(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test that create_image_asset fails without base64 or URL."""
    with pytest.raises(
        Exception, match="image_file_path, image_url, or image_data_base64"
    ):
        await asset_service.create_image_asset(
            ctx=mock_ctx,
            customer_id="1234567890",
            name="No Source",
        )


@pytest.mark.asyncio
async def test_create_youtube_video_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a YouTube video asset."""
    # Arrange
    customer_id = "1234567890"
    youtube_video_id = "dQw4w9WgXcQ"
    name = "Test Video Asset"

    # Create mock response
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/126"

    # Get the mocked asset service client
    mock_asset_service_client = asset_service.client  # type: ignore
    mock_asset_service_client.mutate_assets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/assets/126"}]
    }

    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await asset_service.create_youtube_video_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            youtube_video_id=youtube_video_id,
            name=name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_asset_service_client.mutate_assets.assert_called_once()  # type: ignore
    call_args = mock_asset_service_client.mutate_assets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert operation.create.type_ == AssetTypeEnum.AssetType.YOUTUBE_VIDEO
    assert operation.create.youtube_video_asset.youtube_video_id == youtube_video_id


@pytest.mark.asyncio
async def test_search_assets(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test searching for assets."""
    # Arrange
    customer_id = "1234567890"
    asset_types = ["TEXT", "IMAGE"]
    limit = 10

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []
    for i in range(3):
        row = Mock()
        row.asset = Mock()
        row.asset.id = f"100{i}"
        row.asset.name = f"Asset {i}"
        row.asset.resource_name = f"customers/{customer_id}/assets/100{i}"

        if i == 0:
            # Use actual enum value
            row.asset.type_ = AssetTypeEnum.AssetType.TEXT
            row.asset.text_asset = Mock()
            row.asset.text_asset.text = "Text content"
        elif i == 1:
            row.asset.type_ = AssetTypeEnum.AssetType.IMAGE
            row.asset.image_asset = Mock()
            row.asset.image_asset.file_size = 12345
        else:
            row.asset.type_ = AssetTypeEnum.AssetType.YOUTUBE_VIDEO
            row.asset.youtube_video_asset = Mock()
            row.asset.youtube_video_asset.youtube_video_id = "abc123"

        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return asset_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    # Act
    with patch(
        "src.services.assets.asset_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        result = await asset_service.search_assets(
            ctx=mock_ctx,
            customer_id=customer_id,
            asset_types=asset_types,
            limit=limit,
        )

    # Assert
    assert len(result) == 3
    assert result[0]["asset_id"] == "1000"
    assert result[0]["type"] == "TEXT"
    assert result[0]["text"] == "Text content"
    assert result[1]["asset_id"] == "1001"
    assert result[1]["type"] == "IMAGE"
    assert result[1]["file_size"] == "12345"
    assert result[2]["asset_id"] == "1002"
    assert result[2]["type"] == "YOUTUBE_VIDEO"
    assert result[2]["youtube_video_id"] == "abc123"

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert "asset.type = 'TEXT'" in query
    assert "asset.type = 'IMAGE'" in query
    assert f"LIMIT {limit}" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 3 assets",
    )


@pytest.mark.asyncio
async def test_error_handling(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    customer_id = "1234567890"

    # Get the mocked asset service client and make it raise exception
    mock_asset_service_client = asset_service.client  # type: ignore
    mock_asset_service_client.mutate_assets.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await asset_service.create_text_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            text="Test text",
        )

    assert "Failed to create text asset" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create text asset: Test Google Ads Exception",
    )


def test_mime_type_conversion() -> None:
    """Test MIME type conversion."""
    service = AssetService()

    # Test supported MIME types
    assert service.get_mime_type_enum("image/jpeg") == MimeTypeEnum.MimeType.IMAGE_JPEG
    assert service.get_mime_type_enum("image/png") == MimeTypeEnum.MimeType.IMAGE_PNG
    assert service.get_mime_type_enum("image/gif") == MimeTypeEnum.MimeType.IMAGE_GIF

    # Test case insensitive
    assert service.get_mime_type_enum("IMAGE/JPEG") == MimeTypeEnum.MimeType.IMAGE_JPEG

    # Test default fallback
    assert service.get_mime_type_enum("image/webp") == MimeTypeEnum.MimeType.IMAGE_JPEG


@pytest.mark.asyncio
async def test_create_sitelink_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a sitelink asset."""
    customer_id = "1234567890"

    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/200"

    mock_asset_client = asset_service.client  # type: ignore
    mock_asset_client.mutate_assets.return_value = mock_response  # type: ignore

    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/200"}]}

    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_sitelink_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            link_text="Contact Us",
            final_urls=["https://example.com/contact"],
            description1="Get in touch",
            description2="We are here to help",
        )

    assert result == expected
    mock_asset_client.mutate_assets.assert_called_once()  # type: ignore
    request = mock_asset_client.mutate_assets.call_args[1]["request"]  # type: ignore
    op = request.operations[0]
    assert op.create.type_ == AssetTypeEnum.AssetType.SITELINK
    assert op.create.sitelink_asset.link_text == "Contact Us"
    assert op.create.sitelink_asset.description1 == "Get in touch"
    assert list(op.create.final_urls) == ["https://example.com/contact"]


@pytest.mark.asyncio
async def test_create_callout_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a callout asset."""
    customer_id = "1234567890"

    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/201"

    mock_asset_client = asset_service.client  # type: ignore
    mock_asset_client.mutate_assets.return_value = mock_response  # type: ignore

    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/201"}]}

    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_callout_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            callout_text="Free Shipping",
        )

    assert result == expected
    request = mock_asset_client.mutate_assets.call_args[1]["request"]  # type: ignore
    op = request.operations[0]
    assert op.create.type_ == AssetTypeEnum.AssetType.CALLOUT
    assert op.create.callout_asset.callout_text == "Free Shipping"


@pytest.mark.asyncio
async def test_create_structured_snippet_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a structured snippet asset."""
    customer_id = "1234567890"

    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/202"

    mock_asset_client = asset_service.client  # type: ignore
    mock_asset_client.mutate_assets.return_value = mock_response  # type: ignore

    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/202"}]}

    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_structured_snippet_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            header="Brands",
            values=["Brand A", "Brand B", "Brand C"],
        )

    assert result == expected
    request = mock_asset_client.mutate_assets.call_args[1]["request"]  # type: ignore
    op = request.operations[0]
    assert op.create.type_ == AssetTypeEnum.AssetType.STRUCTURED_SNIPPET
    assert op.create.structured_snippet_asset.header == "Brands"
    assert list(op.create.structured_snippet_asset.values) == [
        "Brand A",
        "Brand B",
        "Brand C",
    ]


@pytest.mark.asyncio
async def test_create_call_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a call asset."""
    customer_id = "1234567890"

    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/203"

    mock_asset_client = asset_service.client  # type: ignore
    mock_asset_client.mutate_assets.return_value = mock_response  # type: ignore

    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/203"}]}

    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_call_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            country_code="US",
            phone_number="1234567890",
        )

    assert result == expected
    request = mock_asset_client.mutate_assets.call_args[1]["request"]  # type: ignore
    op = request.operations[0]
    assert op.create.type_ == AssetTypeEnum.AssetType.CALL
    assert op.create.call_asset.country_code == "US"
    assert op.create.call_asset.phone_number == "1234567890"


def test_register_asset_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    service = register_asset_tools(mock_mcp)

    assert isinstance(service, AssetService)
    assert mock_mcp.tool.call_count == 8  # type: ignore

    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_text_asset",
        "create_image_asset",
        "create_youtube_video_asset",
        "create_sitelink_asset",
        "create_callout_asset",
        "create_structured_snippet_asset",
        "create_call_asset",
        "search_assets",
    ]

    assert set(tool_names) == set(expected_tools)
