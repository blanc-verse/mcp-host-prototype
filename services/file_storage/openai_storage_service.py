from json import JSONDecoder
import os
from dotenv import load_dotenv
import requests
from typing_extensions import override
from services.file_storage.file_storage_service import FileStorageService
from rich import print

load_dotenv()


class OpenAiStorageService(FileStorageService):
    def __init__(self) -> None:
        self.access_token = os.getenv("OPENAI_API_KEY") or ""

    @override
    async def create_file(self):
        pass

    @override
    def list_files(self, container_id):
        response = requests.get(
            f"https://api.openai.com/v1/containers/{container_id}/files",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        return response.json()

    @override
    def get_file(
        self,
        container_id: str = "cntr_68c1b724258c8190a7c9ad86f234125e0fa6a2f190f08a64",
        file_id: str = "cfile_68c1b73f383c8191b5a91cc996ea0b88",
    ):
        response = requests.get(
            f"https://api.openai.com/v1/containers/{container_id}/files/{file_id}/content",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        return response.content

    @override
    async def delete_file(self):
        pass

    @override
    def list_containers(self):
        response = requests.get(
            f"https://api.openai.com/v1/containers",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        return response.json()

    @override
    async def get_container(self):
        pass

    @override
    async def create_container(self):
        raise Exception("cannot create container")

    @override
    async def delete_container(self):
        pass
