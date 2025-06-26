"""Google Ads SDK client for MCP server."""

from typing import Optional, Dict, Any

import yaml
from google.ads.googleads.client import GoogleAdsClient

from src.utils import get_logger

logger = get_logger(__name__)


class GoogleAdsSdkClient:
    """SDK client for Google Ads with service account authentication."""

    def __init__(self, config_path: str = "./env/google-ads.yaml"):
        """Initialize the SDK client with configuration."""
        self.config_path = config_path
        self._client: Optional[GoogleAdsClient] = None

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(self.config_path, "r") as f:
            config = yaml.safe_load(f)

        # Ensure required fields are present
        required_fields = ["developer_token", "json_key_file_path"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field in config: {field}")

        return config

    @property
    def client(self) -> GoogleAdsClient:
        """Get or create the Google Ads client."""
        if self._client is None:
            config = self._load_config()

            # Build configuration dictionary for GoogleAdsClient
            client_config = {
                "developer_token": config["developer_token"],
                "use_proto_plus": True,  # Use proto-plus for better type hints
                "json_key_file_path": config["json_key_file_path"],
            }

            # Add optional fields if present
            if "login_customer_id" in config:
                # Remove hyphens from customer ID
                login_customer_id = str(config["login_customer_id"]).replace("-", "")
                client_config["login_customer_id"] = login_customer_id

            # Create client from dictionary
            self._client = GoogleAdsClient.load_from_dict(client_config)
            logger.info("Google Ads SDK client initialized successfully")

        return self._client

    def close(self) -> None:
        """Close the client and clean up resources."""
        if self._client:
            # The SDK client doesn't have an explicit close method
            # but we can clear the reference
            self._client = None
            logger.info("Google Ads SDK client closed")


# Global client instance
_sdk_client: Optional[GoogleAdsSdkClient] = None


def get_sdk_client() -> GoogleAdsSdkClient:
    """Get the global SDK client instance."""
    global _sdk_client
    if _sdk_client is None:
        raise RuntimeError("SDK client not initialized. Call set_sdk_client first.")
    return _sdk_client


def set_sdk_client(client: GoogleAdsSdkClient) -> None:
    """Set the global SDK client instance."""
    global _sdk_client
    _sdk_client = client
