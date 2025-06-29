from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import UserSchema


class UsersUseCase:
    def __init__(self, db: DBRepositoryInterface)-> None:
        self._db = db

    async def save_user(self, user: UserSchema) -> None:
        async with self._db as db:
            await db.create_user(user)

    async def get_users(self) -> list[UserSchema]:
        async with self._db as db:
            return await db.get_users()
