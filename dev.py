import logging
import os

from fastmcp import Client
from fastmcp.client.transports import ClientTransportT


def get_logger(name: str):
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)
    log_file = os.path.join(logs_dir, "app.log")

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent adding multiple handlers if get_logger is called multiple times
    if not logger.handlers:
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


logger = get_logger(__name__)

config = {
    "mcpServers": {
        "google-ads-mcp": {
            "command": "uv",
            "args": ["run", "./main.py"],
        }
    }
}


async def test_customer_service_server(c: Client[ClientTransportT]):
    pass


async def main():
    client = Client(config)
    async with client:
        pass


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
