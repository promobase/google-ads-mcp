"""Live test for KeywordPlanIdeaService.GenerateKeywordIdeas.

Usage:
    uv run python scripts/keyword_planner_live.py --customer-id 1234567890
    GOOGLE_ADS_CUSTOMER_ID=1234567890 uv run python scripts/keyword_planner_live.py
"""

import argparse
import os
import sys

import grpc
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

from src.utils import load_dotenv


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--customer-id",
        default=os.environ.get("GOOGLE_ADS_CUSTOMER_ID"),
        help="Client account customer ID (no hyphens)",
    )
    parser.add_argument(
        "--keywords",
        nargs="+",
        default=["trademark registration"],
        help="Seed keywords",
    )
    args = parser.parse_args()

    if os.path.exists(".env"):
        load_dotenv()

    if not args.customer_id:
        parser.error("Provide --customer-id or set GOOGLE_ADS_CUSTOMER_ID")

    customer_id = args.customer_id.replace("-", "")

    # --- Build client from env ---
    print("Loading Google Ads client from environment...")
    client = GoogleAdsClient.load_from_env()
    print(f"  login_customer_id = {client.login_customer_id}")
    print(f"  customer_id (request) = {customer_id}")
    print()

    # --- Build request ---
    kw_service = client.get_service("KeywordPlanIdeaService", version="v20")

    request = client.get_type("GenerateKeywordIdeasRequest", version="v20")
    request.customer_id = customer_id
    request.language = "languageConstants/1000"  # English
    request.geo_target_constants.append("geoTargetConstants/2840")  # US
    request.page_size = 5

    keyword_seed = client.get_type("KeywordSeed", version="v20")
    keyword_seed.keywords.extend(args.keywords)
    request.keyword_seed = keyword_seed

    request.keyword_plan_network = (
        client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH_AND_PARTNERS
    )

    print(f"Calling GenerateKeywordIdeas with seeds: {args.keywords}")
    print("-" * 60)

    # --- Call API ---
    try:
        response = kw_service.generate_keyword_ideas(request=request)

        count = 0
        for idea in response:
            metrics = idea.keyword_idea_metrics
            print(
                f"  {idea.text:<40} "
                f"avg_searches={metrics.avg_monthly_searches if metrics else 'N/A':>8}  "
                f"competition={metrics.competition.name if metrics and metrics.competition else 'N/A'}"
            )
            count += 1
            if count >= 5:
                break

        print("-" * 60)
        print(f"OK — received {count} keyword ideas")

    except GoogleAdsException as ex:
        print(f"\nGoogle Ads API error (request_id={ex.request_id}):")
        for error in ex.failure.errors:
            print(f"  [{error.error_code}] {error.message}")
        sys.exit(1)

    except grpc.RpcError as ex:
        code = ex.code() if hasattr(ex, "code") else "?"
        details = ex.details() if hasattr(ex, "details") else str(ex)
        print(f"\ngRPC error: {code}")
        print(f"  {details}")
        sys.exit(1)

    except Exception as ex:
        print(f"\nUnexpected error: {type(ex).__name__}: {ex}")
        sys.exit(1)


if __name__ == "__main__":
    main()
