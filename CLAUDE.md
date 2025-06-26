You're working on google-ads-mcp project, it's a MCP(model context protocal) server that wraps the google ads api for LLM's interaction. You will use the tools to search, fetch web page contents to read the docs, and implement.

// about google ads api
google ads offers it's own client sdk as well as REST api. Client one has python sdk, built on top of protobuf schema. REST api does not have any existing openapi specs but referenec docs.
we decided to go with python sdk, since it's well maintained and does most of the heavy lifting, i.e. retries, pagination, etc.

// resources
here are some high level resources:

1. read the `./refs/googleads.llms.txt` for resources related to google ads api
2. use the `./refs/fastmcp.llms.txt` for full list of docs on how mcp server works.
3. use the file system to gather the resources under `refs` directory, which contains docs of all the toolings, links to the specific sections. For ones suffixed with `llms.txt`, it's short version with links to proper sections. for `llms-full.txt`, it's full text content. WARNING: it might take significant amount of context window to read the full txt.
4. this is server impl, so the final state will be a working mcp server that has all tools for google ads api.
5. use the cloudflare tools fetch urls via md/html, which is cleaner and easy to digest.
6. you have access to `google-ads-python` which contains source code for the python sdk, as well as all the types generated from pb.
7. we're using `uv` for pagkage management, see `pyproject.toml` for details & configs.
8. for changes, run `uv run ruff format .`and `uv run pyright` to fix the errors & linters. using strongly typed variable declarations.
