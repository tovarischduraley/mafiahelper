from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import PlayerSchema


class GetPlayersUseCase:
    def __init__(self, db: DBRepositoryInterface) -> None:
        self._db = db

    async def get_players(self, name_or_nickname__in: str | None) -> list[PlayerSchema]:

