from enum import StrEnum, IntEnum

MIN_PLAYERS = 9
MAX_PLAYERS = 10


class RolesQuantity(IntEnum):
    CIVILIAN = 6
    MAFIA = 2
    SHERIFF = 1
    DON = 1


class GameResults(StrEnum):
    DRAW = "draw"
    MAFIA_WON = "mafia_won"
    CIVILIANS_WON = "civilians_won"


class GameStatuses(StrEnum):
    DRAFT = "draft"
    ENDED = "ended"


class Roles(StrEnum):
    MAFIA = "mafia"
    CIVILIAN = "civilian"
    SHERIFF = "sheriff"
    DON = "don"
