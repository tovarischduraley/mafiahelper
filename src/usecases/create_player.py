from usecases.errors import ValidationError
from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import CreatePlayerSchema


class CreatePlayerService:
    def __init__(self, db: DBRepositoryInterface) -> None:
        self._db = db

    async def create_player(self, player: CreatePlayerSchema) -> None:
        if player.nickname is None and player.fio is None:
            raise ValidationError("Player should have nickname or fio")
        await self._db.create_player(player)
