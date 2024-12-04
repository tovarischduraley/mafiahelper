from pydantic import BaseModel


class CreatePlayerSchema(BaseModel):
    fio: str | None = None
    nickname: str | None = None


class UserSchema(BaseModel):
    telegram_id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None


class PlayerSchema(BaseModel):
    id: int
    fio: str | None
    nickname: str | None


class PlayerStatsSchema(BaseModel):
    fio: str | None
    nickname: str | None
    games_count_total: int
    win_percent_general: float | None
    win_percent_black_team: float | None
    win_percent_red_team: float | None
    win_percent_as_civilian: float | None
    win_percent_as_mafia: float | None
    win_percent_as_don: float | None
    win_percent_as_sheriff: float | None
