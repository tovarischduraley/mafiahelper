from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import PlayerSchema


class AddPlayersToGameUseCase:
    def __init__(self, db: DBRepositoryInterface) -> None:
        self._db = db

    async def add_players_to_game(self, game_id: int, players: list[PlayerSchema]) -> None:
        ...