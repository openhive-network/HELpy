from __future__ import annotations

from pathlib import Path

from schemas.apis.api_client_generator.api_description_generator.json_rpc import generate_api_description
from schemas.apis.api_client_generator.asynchronous.single_api_generator import (
    generate_api_client as async_generate_api_client,
)
from schemas.apis.api_client_generator.synchronous.single_api_generator import generate_api_client

if __name__ == "__main__":
    abstract_api_source = "beekeepy._remote_handle.abc.api"
    output_path = Path(__file__).parent / "api_description.py"
    openapi_path = Path(__file__).parent / "openapi.json"
    async_api_output_path = Path(__file__).parent / "async_api_generated.py"
    sync_api_output_path = Path(__file__).parent / "sync_api_generated.py"

    generate_api_description(openapi_path, output_path, (("ImportKeysResponseItem", str),))

    assert output_path.exists()

    from beekeepy._remote_handle.api.api_description import beekeeper_api_description

    generate_api_client(beekeeper_api_description, "AbstractSyncApi", abstract_api_source, sync_api_output_path)
    async_generate_api_client(beekeeper_api_description, "AbstractAsyncApi", abstract_api_source, async_api_output_path)
