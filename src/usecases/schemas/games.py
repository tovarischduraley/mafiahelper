import datetime

from pydantic import BaseModel

from core.games import GameStatuses, GameResults
from usecases.schemas.players import PlayerSchema


class UpdateGameSchema(BaseModel):
    comment: str | None = None
    result: GameResults | None = None
    status: GameStatuses | None = None
    players: list[PlayerSchema] | None = None

class GameSchema(BaseModel):
    comment: str
    result: GameResults | None
    status: GameStatuses
    players: list[PlayerSchema]
    date: datetime.date

class CreateGameSchema(BaseModel):
    players: list[PlayerSchema]
    status: GameStatuses
    result: GameResults | None
    comment: str | None



