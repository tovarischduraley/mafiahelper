from io import BytesIO

import aiofiles.os

from usecases.errors import ValidationError
from usecases.interfaces.avatars_repository import AvatarsRepositoryInterface


class AvatarsRepository(AvatarsRepositoryInterface):
    def __init__(self) -> None:
        self._static_folder_path = "api/static/"
        self._avatar_folder_path = "img/avatars/"
        self._default_avatar_name = "default.png"

    async def delete_avatar(self, file_name: str) -> None:
        if file_name == self._default_avatar_name:
            raise ValidationError("Could not delete default avatar")
        path = self._static_folder_path + self._avatar_folder_path + file_name
        await aiofiles.os.unlink(path)

    async def create_avatar(self, file: BytesIO, file_name: str) -> str:
        if file_name == self._default_avatar_name:
            raise ValidationError("Could not save avatar as default")
        path = self._static_folder_path + self._avatar_folder_path + file_name
        async with aiofiles.open(path, "wb") as f:
            await f.write(file.read())
        return self._avatar_folder_path + file_name

    async def get_avatars_names_list(self) -> list[str]:
        return await aiofiles.os.listdir(path=self._static_folder_path + self._avatar_folder_path)
