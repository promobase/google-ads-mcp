"""Tests for GoogleAdsSdkClient configuration resolution."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.sdk_client import GoogleAdsSdkClient


@pytest.fixture
def mock_google_ads_client() -> MagicMock:
    return MagicMock()


def test_uses_load_from_storage_when_yaml_exists(
    tmp_path: Path, mock_google_ads_client: MagicMock
) -> None:
    cfg = tmp_path / "google-ads.yaml"
    cfg.write_text(
        "developer_token: t\n"
        "use_proto_plus: true\n"
        "client_id: x\n"
        "client_secret: y\n"
        "refresh_token: z\n",
        encoding="utf-8",
    )
    with patch(
        "src.sdk_client.GoogleAdsClient.load_from_storage",
        return_value=mock_google_ads_client,
    ) as load_storage:
        with patch("src.sdk_client.GoogleAdsClient.load_from_env") as load_env:
            client = GoogleAdsSdkClient(config_path=str(cfg))
            assert client.client is mock_google_ads_client
            load_storage.assert_called_once()
            load_env.assert_not_called()


def test_uses_load_from_env_when_yaml_missing(
    mock_google_ads_client: MagicMock,
) -> None:
    with patch("src.sdk_client.GoogleAdsClient.load_from_storage") as load_storage:
        with patch(
            "src.sdk_client.GoogleAdsClient.load_from_env",
            return_value=mock_google_ads_client,
        ) as load_env:
            client = GoogleAdsSdkClient(config_path="/nonexistent/google-ads.yaml")
            assert client.client is mock_google_ads_client
            load_storage.assert_not_called()
            load_env.assert_called_once()


def test_close_clears_client(mock_google_ads_client: MagicMock) -> None:
    with patch(
        "src.sdk_client.GoogleAdsClient.load_from_env",
        return_value=mock_google_ads_client,
    ) as load_env:
        client = GoogleAdsSdkClient(config_path="/nonexistent/google-ads.yaml")
        _ = client.client
        client.close()
        _ = client.client
        assert load_env.call_count == 2
