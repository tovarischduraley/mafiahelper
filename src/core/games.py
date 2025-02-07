from enum import IntEnum, StrEnum

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


class Teams(StrEnum):
    RED = "red"
    BLACK = "black"


def get_result_text(result: GameResults) -> str:
    match result:
        case GameResults.MAFIA_WON:
            return "ПОБЕДА МАФИИ"
        case GameResults.CIVILIANS_WON:
            return "ПОБЕДА ГОРОДА"
        case GameResults.DRAW:
            return "НИЧЬЯ"
        case _:
            raise Exception(f"Game result <{result}> is invalid")


def get_win_result_by_player_role(role: Roles) -> GameResults:
    match role:
        case Roles.CIVILIAN | Roles.SHERIFF:
            return GameResults.CIVILIANS_WON
        case Roles.MAFIA | Roles.DON:
            return GameResults.MAFIA_WON
        case _:
            raise Exception(f"Role <{role}> is invalid")
