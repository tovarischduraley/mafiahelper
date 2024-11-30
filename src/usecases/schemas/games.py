import datetime

from pydantic import BaseModel, Field

import core
from usecases.schemas.users import PlayerSchema


class PlayerInGameSchema(PlayerSchema):
    role: core.Roles
    number: int = Field(ge=1, le=10)


class UpdateGameSchema(BaseModel):
    comments: str | None = None
    result: core.GameResults | None = None
    status: core.GameStatuses | None = None


class RawGameSchema(BaseModel):
    """Game with no nested objects"""

    id: int
    comments: str
    result: core.GameResults | None
    status: core.GameStatuses
    created_at: datetime.datetime


class GameSchema(BaseModel):
    """Fulfilled Game"""

    id: int
    comments: str
    result: core.GameResults | None
    status: core.GameStatuses
    players: list[PlayerInGameSchema]
    created_at: datetime.datetime


class CreateGameSchema(BaseModel):
    players: list[PlayerInGameSchema]
    status: core.GameStatuses
    result: core.GameResults | None
    comments: str
    created_at: datetime.datetime
