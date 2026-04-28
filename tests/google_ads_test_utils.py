"""Shared helpers for Google Ads-related tests."""

from typing import cast
from unittest.mock import Mock

import grpc
from google.ads.googleads.errors import GoogleAdsException
from proto import Message


def make_google_ads_exception_stub() -> GoogleAdsException:
    """Build GoogleAdsException with typed mocks (constructor requires non-optional args)."""
    return GoogleAdsException(
        cast(grpc.RpcError, Mock()),
        cast(grpc.Call, Mock()),
        cast(Message, Mock()),
        "",
    )
