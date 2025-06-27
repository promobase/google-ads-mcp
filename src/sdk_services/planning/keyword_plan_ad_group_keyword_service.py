"""Google Ads Keyword Plan Ad Group Keyword Service

This module provides functionality for managing keyword plan ad group keywords in Google Ads.
Keyword plan ad group keywords define the keywords within keyword plan ad groups for planning purposes.
"""

from typing import Any, List, Optional

from fastmcp import FastMCP
from google.ads.googleads.v20.enums.types.keyword_match_type import KeywordMatchTypeEnum
from google.ads.googleads.v20.resources.types.keyword_plan_ad_group_keyword import (
    KeywordPlanAdGroupKeyword,
)
from google.ads.googleads.v20.services.services.keyword_plan_ad_group_keyword_service import (
    KeywordPlanAdGroupKeywordServiceClient,
)
from google.ads.googleads.v20.services.types.keyword_plan_ad_group_keyword_service import (
    KeywordPlanAdGroupKeywordOperation,
    MutateKeywordPlanAdGroupKeywordsRequest,
    MutateKeywordPlanAdGroupKeywordsResponse,
)

from src.sdk_client import get_sdk_client


class KeywordPlanAdGroupKeywordService:
    """Service for managing Google Ads keyword plan ad group keywords."""

    def __init__(self) -> None:
        """Initialize the keyword plan ad group keyword service."""
        self._client: Optional[KeywordPlanAdGroupKeywordServiceClient] = None

    @property
    def client(self) -> KeywordPlanAdGroupKeywordServiceClient:
        """Get the keyword plan ad group keyword service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service(
                "KeywordPlanAdGroupKeywordService"
            )
        assert self._client is not None
        return self._client

    def mutate_keyword_plan_ad_group_keywords(
        self,
        customer_id: str,
        operations: List[KeywordPlanAdGroupKeywordOperation],
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> MutateKeywordPlanAdGroupKeywordsResponse:
        """Mutate keyword plan ad group keywords.

        Args:
            customer_id: The customer ID
            operations: List of keyword plan ad group keyword operations
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate the request

        Returns:
            MutateKeywordPlanAdGroupKeywordsResponse: The response containing results
        """
        request = MutateKeywordPlanAdGroupKeywordsRequest(
            customer_id=customer_id,
            operations=operations,
            partial_failure=partial_failure,
            validate_only=validate_only,
        )
        return self.client.mutate_keyword_plan_ad_group_keywords(request=request)

    def create_keyword_plan_ad_group_keyword_operation(
        self,
        keyword_plan_ad_group: str,
        text: str,
        match_type: KeywordMatchTypeEnum.KeywordMatchType,
        cpc_bid_micros: Optional[int] = None,
        negative: bool = False,
    ) -> KeywordPlanAdGroupKeywordOperation:
        """Create a keyword plan ad group keyword operation for creation.

        Args:
            keyword_plan_ad_group: The keyword plan ad group resource name
            text: The keyword text
            match_type: The keyword match type
            cpc_bid_micros: CPC bid in micros
            negative: Whether this is a negative keyword

        Returns:
            KeywordPlanAdGroupKeywordOperation: The operation to create the keyword plan ad group keyword
        """
        keyword_plan_ad_group_keyword = KeywordPlanAdGroupKeyword(
            keyword_plan_ad_group=keyword_plan_ad_group,
            text=text,
            match_type=match_type,
            negative=negative,
        )

        if cpc_bid_micros is not None:
            keyword_plan_ad_group_keyword.cpc_bid_micros = cpc_bid_micros

        return KeywordPlanAdGroupKeywordOperation(create=keyword_plan_ad_group_keyword)

    def update_keyword_plan_ad_group_keyword_operation(
        self,
        resource_name: str,
        text: Optional[str] = None,
        match_type: Optional[KeywordMatchTypeEnum.KeywordMatchType] = None,
        cpc_bid_micros: Optional[int] = None,
    ) -> KeywordPlanAdGroupKeywordOperation:
        """Create a keyword plan ad group keyword operation for update.

        Args:
            resource_name: The keyword plan ad group keyword resource name
            text: The keyword text
            match_type: The keyword match type
            cpc_bid_micros: CPC bid in micros

        Returns:
            KeywordPlanAdGroupKeywordOperation: The operation to update the keyword plan ad group keyword
        """
        keyword_plan_ad_group_keyword = KeywordPlanAdGroupKeyword(
            resource_name=resource_name
        )

        update_mask = []
        if text is not None:
            keyword_plan_ad_group_keyword.text = text
            update_mask.append("text")
        if match_type is not None:
            keyword_plan_ad_group_keyword.match_type = match_type
            update_mask.append("match_type")
        if cpc_bid_micros is not None:
            keyword_plan_ad_group_keyword.cpc_bid_micros = cpc_bid_micros
            update_mask.append("cpc_bid_micros")

        return KeywordPlanAdGroupKeywordOperation(
            update=keyword_plan_ad_group_keyword,
            update_mask={"paths": update_mask},
        )

    def remove_keyword_plan_ad_group_keyword_operation(
        self, resource_name: str
    ) -> KeywordPlanAdGroupKeywordOperation:
        """Create a keyword plan ad group keyword operation for removal.

        Args:
            resource_name: The keyword plan ad group keyword resource name

        Returns:
            KeywordPlanAdGroupKeywordOperation: The operation to remove the keyword plan ad group keyword
        """
        return KeywordPlanAdGroupKeywordOperation(remove=resource_name)


def register_keyword_plan_ad_group_keyword_tools(mcp: FastMCP[Any]) -> None:
    """Register keyword plan ad group keyword tools with the MCP server."""

    @mcp.tool
    async def mutate_keyword_plan_ad_group_keywords(
        customer_id: str,
        operations: list[dict[str, Any]],
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> str:
        """Create, update, or remove keyword plan ad group keywords.

        Args:
            customer_id: The customer ID
            operations: List of keyword plan ad group keyword operations
            partial_failure: Enable partial failure
            validate_only: Only validate the request

        Returns:
            Success message with operation count
        """
        service = KeywordPlanAdGroupKeywordService()

        def _get_match_type_enum(
            match_type_str: str,
        ) -> KeywordMatchTypeEnum.KeywordMatchType:
            """Convert string to match type enum."""
            if match_type_str == "EXACT":
                return KeywordMatchTypeEnum.KeywordMatchType.EXACT
            elif match_type_str == "PHRASE":
                return KeywordMatchTypeEnum.KeywordMatchType.PHRASE
            elif match_type_str == "BROAD":
                return KeywordMatchTypeEnum.KeywordMatchType.BROAD
            else:
                raise ValueError(f"Invalid match type: {match_type_str}")

        ops = []
        for op_data in operations:
            op_type = op_data["operation_type"]

            if op_type == "create":
                operation = service.create_keyword_plan_ad_group_keyword_operation(
                    keyword_plan_ad_group=op_data["keyword_plan_ad_group"],
                    text=op_data["text"],
                    match_type=_get_match_type_enum(op_data["match_type"]),
                    cpc_bid_micros=op_data.get("cpc_bid_micros"),
                    negative=op_data.get("negative", False),
                )
            elif op_type == "update":
                match_type = None
                if "match_type" in op_data:
                    match_type = _get_match_type_enum(op_data["match_type"])

                operation = service.update_keyword_plan_ad_group_keyword_operation(
                    resource_name=op_data["resource_name"],
                    text=op_data.get("text"),
                    match_type=match_type,
                    cpc_bid_micros=op_data.get("cpc_bid_micros"),
                )
            elif op_type == "remove":
                operation = service.remove_keyword_plan_ad_group_keyword_operation(
                    resource_name=op_data["resource_name"]
                )
            else:
                raise ValueError(f"Invalid operation type: {op_type}")

            ops.append(operation)

        response = service.mutate_keyword_plan_ad_group_keywords(
            customer_id=customer_id,
            operations=ops,
            partial_failure=partial_failure,
            validate_only=validate_only,
        )

        return f"Successfully processed {len(response.results)} keyword plan ad group keyword operations"

    @mcp.tool
    async def create_keyword_plan_ad_group_keyword(
        customer_id: str,
        keyword_plan_ad_group: str,
        text: str,
        match_type: str,
        cpc_bid_micros: Optional[int] = None,
        negative: bool = False,
    ) -> str:
        """Create a new keyword plan ad group keyword.

        Args:
            customer_id: The customer ID
            keyword_plan_ad_group: The keyword plan ad group resource name
            text: The keyword text
            match_type: The keyword match type (EXACT, PHRASE, or BROAD)
            cpc_bid_micros: CPC bid in micros
            negative: Whether this is a negative keyword

        Returns:
            The created keyword plan ad group keyword resource name
        """
        service = KeywordPlanAdGroupKeywordService()

        def _get_match_type_enum(
            match_type_str: str,
        ) -> KeywordMatchTypeEnum.KeywordMatchType:
            """Convert string to match type enum."""
            if match_type_str == "EXACT":
                return KeywordMatchTypeEnum.KeywordMatchType.EXACT
            elif match_type_str == "PHRASE":
                return KeywordMatchTypeEnum.KeywordMatchType.PHRASE
            elif match_type_str == "BROAD":
                return KeywordMatchTypeEnum.KeywordMatchType.BROAD
            else:
                raise ValueError(f"Invalid match type: {match_type_str}")

        operation = service.create_keyword_plan_ad_group_keyword_operation(
            keyword_plan_ad_group=keyword_plan_ad_group,
            text=text,
            match_type=_get_match_type_enum(match_type),
            cpc_bid_micros=cpc_bid_micros,
            negative=negative,
        )

        response = service.mutate_keyword_plan_ad_group_keywords(
            customer_id=customer_id, operations=[operation]
        )

        result = response.results[0]
        return f"Created keyword plan ad group keyword: {result.resource_name}"

    @mcp.tool
    async def update_keyword_plan_ad_group_keyword(
        customer_id: str,
        resource_name: str,
        text: Optional[str] = None,
        match_type: Optional[str] = None,
        cpc_bid_micros: Optional[int] = None,
    ) -> str:
        """Update an existing keyword plan ad group keyword.

        Args:
            customer_id: The customer ID
            resource_name: The keyword plan ad group keyword resource name
            text: The keyword text
            match_type: The keyword match type (EXACT, PHRASE, or BROAD)
            cpc_bid_micros: CPC bid in micros

        Returns:
            The updated keyword plan ad group keyword resource name
        """
        service = KeywordPlanAdGroupKeywordService()

        def _get_match_type_enum(
            match_type_str: str,
        ) -> KeywordMatchTypeEnum.KeywordMatchType:
            """Convert string to match type enum."""
            if match_type_str == "EXACT":
                return KeywordMatchTypeEnum.KeywordMatchType.EXACT
            elif match_type_str == "PHRASE":
                return KeywordMatchTypeEnum.KeywordMatchType.PHRASE
            elif match_type_str == "BROAD":
                return KeywordMatchTypeEnum.KeywordMatchType.BROAD
            else:
                raise ValueError(f"Invalid match type: {match_type_str}")

        match_type_enum = None
        if match_type is not None:
            match_type_enum = _get_match_type_enum(match_type)

        operation = service.update_keyword_plan_ad_group_keyword_operation(
            resource_name=resource_name,
            text=text,
            match_type=match_type_enum,
            cpc_bid_micros=cpc_bid_micros,
        )

        response = service.mutate_keyword_plan_ad_group_keywords(
            customer_id=customer_id, operations=[operation]
        )

        result = response.results[0]
        return f"Updated keyword plan ad group keyword: {result.resource_name}"

    @mcp.tool
    async def remove_keyword_plan_ad_group_keyword(
        customer_id: str,
        resource_name: str,
    ) -> str:
        """Remove a keyword plan ad group keyword.

        Args:
            customer_id: The customer ID
            resource_name: The keyword plan ad group keyword resource name

        Returns:
            Success message
        """
        service = KeywordPlanAdGroupKeywordService()

        operation = service.remove_keyword_plan_ad_group_keyword_operation(
            resource_name=resource_name
        )

        service.mutate_keyword_plan_ad_group_keywords(
            customer_id=customer_id, operations=[operation]
        )

        return f"Removed keyword plan ad group keyword: {resource_name}"
