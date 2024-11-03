import datetime

from pydantic import BaseModel, Field

import core
from usecases.schemas.users import UserSchema


class PlayerSchema(UserSchema):
    role: core.Roles
    number: int = Field(ge=1, le=10)


class UpdateGameSchema(BaseModel):
    comments: str | None = None
    result: core.GameResults | None = None
    status: core.GameStatuses | None = None
    players: list[PlayerSchema] | None = None
    created_at: datetime.datetime | None = None


class RawGameSchema(BaseModel):
    """Game with no nested objects"""

    id: int
    comments: str
    result: core.GameResults | None
    status: core.GameStatuses
    created_at: datetime.datetime


class GameSchema(BaseModel):
    """Fullfilled Game"""

    id: int
    comments: str
    result: core.GameResults | None
    status: core.GameStatuses
    players: list[PlayerSchema]
    created_at: datetime.datetime


class CreateGameSchema(BaseModel):
    players: list[PlayerSchema]
    status: core.GameStatuses
    result: core.GameResults | None
    comments: str
    created_at: datetime.datetime
