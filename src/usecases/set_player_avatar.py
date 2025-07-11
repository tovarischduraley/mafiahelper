import random
from contextlib import suppress
from io import BytesIO

from usecases.interfaces import AvatarsRepositoryInterface, DBRepositoryInterface
from usecases.schemas import UpdatePlayerSchema


class SetPlayerAvatarUseCase:
    def __init__(
        self,
        db_repository: DBRepositoryInterface,
        avatars_repository: AvatarsRepositoryInterface
    ) -> None:
        self._db = db_repository
        self._avatars_repo = avatars_repository

    async def set_player_avatar(self, player_id: int, file: BytesIO, file_name: str) -> None:
        async with self._db as db:
            player = await db.get_player_by_id(player_id=player_id)
        existing = await self._avatars_repo.get_avatars_names_list()
        if file_name in existing:
            file_name = f"{round(random.random() * 1000)}_{file_name}"
        if player.avatar_path:
            with suppress(FileNotFoundError):
                await self._avatars_repo.delete_avatar(player.avatar_path.split("/")[-1])
        path = await self._avatars_repo.create_avatar(file=file, file_name=file_name)
        async with self._db as db:
            await db.update_player(player_id=player_id, data=UpdatePlayerSchema(avatar_path=path))
