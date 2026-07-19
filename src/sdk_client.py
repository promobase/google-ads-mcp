"""Google Ads SDK client for MCP server."""

from pathlib import Path
from typing import Optional

from google.ads.googleads.client import GoogleAdsClient

from src.utils import get_logger

logger = get_logger(__name__)

# If this path exists, it is loaded via the SDK's YAML loader (same format as
# ~/google-ads.yaml). Otherwise configuration is read from environment
# variables GOOGLE_ADS_* (see google.ads.googleads.config.load_from_env).
_DEFAULT_CONFIG_PATH = "./env/google-ads.yaml"


class GoogleAdsSdkClient:
    """SDK client for Google Ads (OAuth installed app or service account).

    Configuration resolution order:
    1. If ``config_path`` points to an existing file, that YAML is loaded
       (``GoogleAdsClient.load_from_storage``).
    2. Otherwise ``GoogleAdsClient.load_from_env()`` is used. After
       ``load_dotenv()`` in ``main.py``, variables from ``.env`` are visible
       here. You may also set ``GOOGLE_ADS_CONFIGURATION_FILE_PATH`` to a YAML
       file path; the SDK then loads that file instead of inline env keys.
    """

    def __init__(self, config_path: Optional[str] = _DEFAULT_CONFIG_PATH):
        self.config_path = config_path
        self._client: Optional[GoogleAdsClient] = None

    def _build_client(self) -> GoogleAdsClient:
        if self.config_path:
            path = Path(self.config_path)
            if path.is_file():
                resolved = str(path.resolve())
                logger.info("Google Ads config: YAML file %s", resolved)
                client = GoogleAdsClient.load_from_storage(resolved)
                logger.info("login_customer_id=%s", client.login_customer_id)
                return client

        logger.info("Google Ads config: environment (GOOGLE_ADS_*)")
        client = GoogleAdsClient.load_from_env()
        logger.info("login_customer_id=%s", client.login_customer_id)
        return client

    @property
    def client(self) -> GoogleAdsClient:
        """Get or create the Google Ads client."""
        if self._client is None:
            self._client = self._build_client()
            logger.info("Google Ads SDK client initialized successfully")
        return self._client

    def validate(self) -> None:
        """Eagerly build the client and verify credentials.

        Calls ``list_accessible_customers`` which is lightweight, free, and
        proves that the OAuth / service-account token is valid.
        """
        try:
            customer_service = self.client.get_service("CustomerService", version="v23")
            customer_service.list_accessible_customers()
            logger.info("Credential validation passed")
        except Exception:
            logger.error("Credential validation FAILED – check your config")
            raise

    def close(self) -> None:
        """Close the client and clean up resources."""
        if self._client:
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
