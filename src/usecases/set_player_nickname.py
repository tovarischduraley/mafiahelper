from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import UpdatePlayerSchema


class SetPlayerNicknameUseCase:
    def __init__(self, db_repository: DBRepositoryInterface) -> None:
        self.db_repository = db_repository

    async def set_player_nickname(self, player_id: int, nickname: str) -> None:
        async with self.db_repository as db:
            await db.update_player(player_id=player_id, data=UpdatePlayerSchema(nickname=nickname))
