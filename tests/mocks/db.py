from typing import Self

import core
from usecases.errors import NotFoundError
from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import (
    CreateGameSchema,
    CreateUserSchema,
    GameSchema,
    PlayerSchema,
    RawGameSchema,
    UpdateGameSchema,
    UserSchema,
)


class FakeDBRepository(DBRepositoryInterface):
    def __init__(
        self,
        users: dict[int, UserSchema] | None = None,
        games: dict[int, GameSchema] | None = None,
    ) -> None:
        self._users = users or {}
        self._games = games or {}

    async def __aenter__(self) -> Self:
        return self

    @staticmethod
    def _get_next_id(db: dict) -> int:
        try:
            return max(db.keys())
        except ValueError:
            return 1

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...

    async def create_user(self, user: CreateUserSchema) -> None:
        id_ = self._get_next_id(self._users)
        self._users[id_] = UserSchema(id=id_, **user.model_dump())

    async def get_users(
        self,
        limit: int | None,
        offset: int | None,
    ) -> list[UserSchema]:
        users = list(self._users.values())
        match limit, offset:
            case None, None:
                return users
            case None, _:
                return users[offset:]
            case _, None:
                return users[:limit]
            case _, _:
                return users[offset : offset + limit]

    async def get_user_by_id(self, user_id: int) -> UserSchema:
        try:
            return self._users[user_id]
        except KeyError as e:
            raise NotFoundError(f"TEST user id={user_id} not found") from e

    async def get_users_count(self) -> int:
        return len(self._users)

    async def create_game(self, data: CreateGameSchema) -> RawGameSchema:
        id_ = self._get_next_id(self._games)
        game_to_create = GameSchema(id=id_, **data.model_dump())
        self._games[id_] = game_to_create
        return RawGameSchema.model_validate(game_to_create, from_attributes=True)

    async def get_game_by_id(self, game_id: int) -> GameSchema:
        try:
            return self._games[game_id]
        except KeyError as e:
            raise NotFoundError(f"TEST game id={game_id} not found") from e

    async def add_player(self, game_id: int, user_id: int, seat_number: int, role: core.Roles) -> None:
        game = self._games[game_id]
        user = self._users[user_id]
        game.players.append(PlayerSchema(number=seat_number, role=role, **user.model_dump()))

    async def remove_player(self, game_id: int, user_id: int) -> None:
        for p in self._games[game_id].players:
            if p.id == user_id:
                self._games[game_id].players.remove(p)
                break

    async def remove_player_on_seat(self, game_id: int, seat_number: int) -> None:
        for p in self._games[game_id].players:
            if p.number == seat_number:
                self._games[game_id].players.remove(p)
                break

    async def update_game(self, game_id: int, data: UpdateGameSchema) -> None:
        self._games[game_id] = self._games[game_id].model_copy(update=data.model_dump(exclude_unset=True))

    async def get_games(
        self,
        user_id: int | None = None,
        seat_number: int | None = None,
        role__in: list[core.Roles] | None = None,
        result__in: list[core.GameResults] | None = None,
        status: core.GameStatuses | None = None,
        is_won: bool | None = None,
    ) -> list[GameSchema]:
        games = self._games.values()
        if user_id:
            games = filter(lambda g: user_id in [p.id for p in g.players], games)
        if seat_number:
            games = filter(lambda g: seat_number in [p.number for p in g.players if p.id == user_id], games)
        if role__in:
            games = filter(lambda g: set(role__in) & {p.role for p in g.players if p.id == user_id}, games)
        if result__in:
            games = filter(lambda g: g.result in result__in, games)
        if status:
            games = filter(lambda g: g.status == status, games)
        if is_won:
            if not user_id:
                raise Exception("TEST no user_id in filters")
            games = filter(lambda g: self._user_won(g, user_id), games)
        return list(games)

    @staticmethod
    def _user_won(game: GameSchema, user_id: int) -> bool:
        user = next(filter(lambda p: p.id == user_id, game.players))
        return core.get_win_result_by_user_role(user.role) == game.result
