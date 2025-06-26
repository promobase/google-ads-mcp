#!/bin/bash
# Type checking script for Google Ads MCP

set -e

echo "Running ruff linter..."
uv run ruff check . --fix

echo -e "\nRunning pyright type checker..."
uv run pyright

echo -e "\nAll checks passed!"