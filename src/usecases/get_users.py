from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import UserSchema


class GetUsersUseCase:
    def __init__(self, db: DBRepositoryInterface) -> None:
        self._db = db

    async def get_users(self, fio_or_nickname__in: str | None = None) -> list[UserSchema]:
        async with self._db as db:
            return await db.get_users(fio_or_nickname__in=fio_or_nickname__in)
