from usecases.errors import ValidationError
from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import CreateUserSchema


class CreateUserService:
    def __init__(self, db: DBRepositoryInterface) -> None:
        self._db = db

    async def create_user(self, user: CreateUserSchema) -> None:
        if user.nickname is None and user.fio is None:
            raise ValidationError("User should have nickname or fio")
        async with self._db as db:
            await db.create_user(user)
