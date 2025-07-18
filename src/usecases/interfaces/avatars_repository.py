from abc import ABC, abstractmethod
from io import BytesIO


class AvatarsRepositoryInterface(ABC):
    @abstractmethod
    async def delete_avatar(self, file_name: str) -> None: ...

    @abstractmethod
    async def get_avatars_names_list(self) -> list[str]: ...

    @abstractmethod
    async def create_avatar(self, file: BytesIO, file_name: str) -> str:
        """returns path to file in storage"""
