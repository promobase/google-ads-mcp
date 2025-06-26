"""User list server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.audiences.user_list_service import register_user_list_tools

# Create the user list server
user_list_sdk_server = FastMCP(
    name="user_list",
    instructions="""This server provides tools for managing Google Ads remarketing user lists.

    Available tools:
    - create_basic_user_list: Create a basic remarketing list
    - create_crm_based_user_list: Create a customer match list for CRM data
    - create_similar_user_list: Create a similar audiences list
    - create_logical_user_list: Create a combined list with logical rules
    - update_user_list: Update user list properties

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
user_list_service = register_user_list_tools(user_list_sdk_server)
