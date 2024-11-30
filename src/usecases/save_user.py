from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import UserSchema


class SaveUserUseCase:
    def __init__(self, db: DBRepositoryInterface)-> None:
        self._db = db

    async def save_user(self, user: UserSchema) -> None:
        async with self._db as db:
            await db.create_user(user)
