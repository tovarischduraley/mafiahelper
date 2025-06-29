import datetime

from pydantic import BaseModel, Field

import core
from usecases.schemas.base import BaseEntity
from usecases.schemas.users import PlayerSchema


class PlayerInGameSchema(PlayerSchema):
    role: core.Roles
    number: int = Field(ge=1, le=10)


class UpdateGameSchema(BaseModel):
    comments: str | None = None
    result: core.GameResults | None = None
    status: core.GameStatuses | None = None


class RawGameSchema(BaseEntity):
    """Game with no nested objects"""

    comments: str
    result: core.GameResults | None
    status: core.GameStatuses
    created_at: datetime.datetime


class GameSchema(BaseEntity):
    """Fulfilled Game"""

    comments: str
    result: core.GameResults | None
    status: core.GameStatuses
    players: set[PlayerInGameSchema]
    created_at: datetime.datetime
    best_move: set[PlayerInGameSchema] | None
    first_killed: PlayerInGameSchema | None


class CreateGameSchema(BaseModel):
    players: set[PlayerInGameSchema]
    status: core.GameStatuses
    result: core.GameResults | None
    comments: str
    created_at: datetime.datetime
    best_move: set[PlayerInGameSchema] | None
    first_killed: PlayerInGameSchema | None
