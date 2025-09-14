from abc import ABC, abstractmethod


class FileStorageService(ABC):
    @abstractmethod
    async def create_file(self):
        pass

    @abstractmethod
    async def list_files(self):
        pass

    @abstractmethod
    async def get_file(self):
        pass

    @abstractmethod
    async def delete_file(self):
        pass

    @abstractmethod
    async def list_containers(self):
        pass

    @abstractmethod
    async def get_container(self):
        pass

    @abstractmethod
    async def create_container(self):
        raise Exception("cannot create container")

    @abstractmethod
    async def delete_container(self):
        pass
