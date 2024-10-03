from enum import StrEnum


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