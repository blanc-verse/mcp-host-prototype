from typing import Any, Dict, Union
from typing_extensions import override
from chainlit.data.storage_clients.base import BaseStorageClient
from rich import print


class LocalDiskStorageProvider(BaseStorageClient):
    def to_string(self):
        return "LocalDiskStorageProvider"

    @override
    async def upload_file(
        self,
        object_key: str,
        data: Union[bytes, str],
        mime: str = "application/octet-stream",
        overwrite: bool = True,
        content_disposition: str | None = None,
    ) -> Dict[str, Any]:
        print("Object Key: ", object_key)
        print("Data: ", data)
        print("Mime: ", mime)
        print("Overwrite?: ", overwrite)
        print("Content Disposition?: ", content_disposition)

        return {"object_key": object_key, "url": "url file-nya"}

    @override
    async def delete_file(self, object_key: str) -> bool:
        return True

    @override
    async def get_read_url(self, object_key: str) -> str:
        return "placeholder path"
