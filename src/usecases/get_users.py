from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import UserSchema


class GetUsersUseCase:
    def __init__(self, db: DBRepositoryInterface) -> None:
        self._db = db

    async def get_users(
        self,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[UserSchema]:
        async with self._db as db:
            return await db.get_users(
                limit=limit,
                offset=offset,
            )

    async def get_users_count(self) -> int:
        async with self._db as db:
            return await db.get_users_count()
