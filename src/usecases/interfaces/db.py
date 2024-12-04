from abc import ABC, abstractmethod
from typing import Self

import core
from usecases.schemas import (
    CreateGameSchema,
    CreatePlayerSchema,
    GameSchema,
    PlayerSchema,
    UpdateGameSchema,
    UserSchema,
)
from usecases.schemas.games import RawGameSchema


class DBRepositoryInterface(ABC):
    @abstractmethod
    async def __aenter__(self) -> Self: ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...

    @abstractmethod
    async def create_player(self, player: CreatePlayerSchema) -> None: ...

    @abstractmethod
    async def create_user(self, user: UserSchema) -> None: ...

    @abstractmethod
    async def get_players(
        self,
        limit: int | None,
        offset: int | None,
    ) -> list[PlayerSchema]: ...

    @abstractmethod
    async def get_users(self) -> list[UserSchema]: ...

    @abstractmethod
    async def get_player_by_id(self, player_id: int) -> PlayerSchema: ...

    @abstractmethod
    async def add_player(self, game_id: int, player_id: int, seat_number: int, role: core.Roles) -> None: ...

    @abstractmethod
    async def get_players_count(self) -> int: ...

    @abstractmethod
    async def remove_player_from_game(self, game_id: int, player_id: int) -> None: ...

    @abstractmethod
    async def remove_player_on_seat(self, game_id: int, seat_number: int) -> None: ...

    @abstractmethod
    async def create_game(self, data: CreateGameSchema) -> RawGameSchema: ...

    @abstractmethod
    async def update_game(self, game_id: int, data: UpdateGameSchema) -> None: ...

    @abstractmethod
    async def get_game_by_id(self, game_id: int) -> GameSchema: ...

    @abstractmethod
    async def get_games(
        self,
        player_id: int | None = None,
        seat_number: int | None = None,
        role__in: list[core.Roles] | None = None,
        result__in: list[core.GameResults] | None = None,
        status: core.GameStatuses | None = None,
        is_won: bool | None = None,
    ) -> list[GameSchema]: ...
