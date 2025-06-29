from pydantic import BaseModel

from usecases.schemas.base import BaseEntity


class CreatePlayerSchema(BaseModel):
    fio: str | None = None
    nickname: str | None = None


class UserSchema(BaseModel):
    telegram_id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None


class PlayerSchema(BaseEntity):
    fio: str | None
    nickname: str | None
    avatar_path: str | None = None


class PlayerStatsSchema(BaseModel):
    fio: str | None
    nickname: str | None
    games_count_total: int
    won_games_count_total: int
    win_percent_general: float | None

    won_games_count_black_team: int
    games_count_black_team: int
    win_percent_black_team: float | None

    won_games_count_red_team: int
    games_count_red_team: int
    win_percent_red_team: float | None

    won_games_count_as_civilian: int
    games_count_as_civilian: int
    win_percent_as_civilian: float | None

    won_games_count_as_mafia: int
    games_count_as_mafia: int
    win_percent_as_mafia: float | None

    won_games_count_as_don: int
    games_count_as_don: int
    win_percent_as_don: float | None

    won_games_count_as_sheriff: int
    games_count_as_sheriff: int
    win_percent_as_sheriff: float | None

    first_killed_count: int
    best_move_count_total: int
    zero_mafia_best_move_count: int
    one_mafia_best_move_count: int
    two_mafia_best_move_count: int
    three_mafia_best_move_count: int
