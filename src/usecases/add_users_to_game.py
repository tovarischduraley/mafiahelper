from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import UserSchema


class AddUsersToGameUseCase:
    def __init__(self, db: DBRepositoryInterface) -> None:
        self._db = db

    async def add_users_to_game(self, game_id: int, users: list[UserSchema]) -> None:
        ...
