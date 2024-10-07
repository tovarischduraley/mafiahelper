from core.games import Roles
from usecases.interfaces import DBRepositoryInterface


class AssignRoleUseCase:
    def __init__(self, db: DBRepositoryInterface):
        self._db = db

    async def assign_role(self, user_id: int, game_id: int, role: Roles) -> None:
        ...
