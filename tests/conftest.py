import datetime
import random
from collections.abc import Generator
from typing import Callable

from core import GameResults, GameStatuses, Roles, get_win_result_by_player_role
from usecases.schemas import GameSchema, PlayerInGameSchema, PlayerSchema

TEST_FIOS = [
    "John",
    "Steve",
    "Bob",
    "Rob",
    "Michel",
    "Govard",
    "Mathew",
    "Isaac",
    "Alex",
    "Robin",
    "Cormoran",
    "Victor",
]

TEST_NICKNAMES = [
    "Cat",
    "Hellcat",
    "Pencil",
    "Dog",
    "Queen",
    "The King",
    "Maf",
    "NLNLIP",
    "Karkarich",
    "Gospodin",
    "Red",
    "Second",
]

GAME_SEATS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


def _id_gen():
    i = 0
    while True:
        i += 1
        yield i


def _gen_player(fios: list[str], nicknames: list[str]) -> Generator[tuple[str, str], None, None]:
    while True:
        fio = random.choice(fios)
        fios.remove(fio)
        nick = random.choice(nicknames)
        nicknames.remove(nick)
        yield fio, nick


def _seat_gen(seats: list[int]):
    while True:
        seat = random.choice(seats)
        seats.remove(seat)
        yield seat


id_g = _id_gen()


def valid_player() -> PlayerSchema:
    player_gen = _gen_player(fios=TEST_FIOS.copy(), nicknames=TEST_NICKNAMES.copy())
    fio, nickname = next(player_gen)
    return PlayerSchema(id=next(id_g), fio=fio, nickname=nickname)


def mafia_player(
    seat_generator: Generator[int, None, None],
    player_generator: Generator[tuple[str, str], None, None],
) -> PlayerInGameSchema:
    fio, nick = next(player_generator)
    return PlayerInGameSchema(
        id=next(id_g),
        role=Roles.MAFIA,
        number=next(seat_generator),
        fio=fio,
        nickname=nick,
    )


def civilian_player(
    seat_generator: Generator[int, None, None],
    player_generator: Generator[tuple[str, str], None, None],
) -> PlayerInGameSchema:
    fio, nick = next(player_generator)
    return PlayerInGameSchema(
        id=next(id_g),
        role=Roles.CIVILIAN,
        number=next(seat_generator),
        fio=fio,
        nickname=nick,
    )


def sheriff_player(
    seat_generator: Generator[int, None, None],
    player_generator: Generator[tuple[str, str], None, None],
) -> PlayerInGameSchema:
    fio, nick = next(player_generator)
    return PlayerInGameSchema(
        id=next(id_g),
        role=Roles.SHERIFF,
        number=next(seat_generator),
        fio=fio,
        nickname=nick,
    )


def don_player(
    seat_generator: Generator[int, None, None],
    player_generator: Generator[tuple[str, str], None, None],
) -> PlayerInGameSchema:
    fio, nick = next(player_generator)
    return PlayerInGameSchema(
        id=next(id_g),
        role=Roles.DON,
        number=next(seat_generator),
        fio=fio,
        nickname=nick,
    )


def valid_game() -> GameSchema:
    seats_generator = _seat_gen(seats=GAME_SEATS.copy())
    players_generator = _gen_player(fios=TEST_FIOS.copy(), nicknames=TEST_NICKNAMES.copy())
    return GameSchema(
        id=next(id_g),
        comments="",
        result=None,
        status=GameStatuses.DRAFT,
        created_at=datetime.datetime.now(),
        players=[
            don_player(seats_generator, players_generator),
            sheriff_player(seats_generator, players_generator),
            *[mafia_player(seats_generator, players_generator) for _ in range(2)],
            *[civilian_player(seats_generator, players_generator) for _ in range(6)],
        ],
    )


def game_with_invalid_roles_distribution() -> GameSchema:
    seats_generator = _seat_gen(seats=GAME_SEATS.copy())
    players_generator = _gen_player(fios=TEST_FIOS.copy(), nicknames=TEST_NICKNAMES.copy())
    return GameSchema(
        id=next(id_g),
        comments="",
        result=None,
        status=GameStatuses.DRAFT,
        created_at=datetime.datetime.now(),
        players=[
            don_player(seats_generator, players_generator),
            sheriff_player(seats_generator, players_generator),
            *[mafia_player(seats_generator, players_generator) for _ in range(3)],
            *[civilian_player(seats_generator, players_generator) for _ in range(5)],
        ],
    )


def game_with_invalid_players_quantity() -> GameSchema:
    seats_generator = _seat_gen(seats=GAME_SEATS.copy())
    players_generator = _gen_player(fios=TEST_FIOS.copy(), nicknames=TEST_NICKNAMES.copy())
    return GameSchema(
        id=next(id_g),
        comments="",
        result=None,
        status=GameStatuses.DRAFT,
        created_at=datetime.datetime.now(),
        players=[
            don_player(seats_generator, players_generator),
            sheriff_player(seats_generator, players_generator),
            *[mafia_player(seats_generator, players_generator) for _ in range(3)],
            *[civilian_player(seats_generator, players_generator) for _ in range(2)],
        ],
    )


def game_with_nine_players() -> GameSchema:
    def _seq_seats_gen():
        yield from range(1, 11)

    seats_generator = _seq_seats_gen()
    players_generator = _gen_player(fios=TEST_FIOS.copy(), nicknames=TEST_NICKNAMES.copy())
    return GameSchema(
        id=next(id_g),
        comments="",
        result=None,
        status=GameStatuses.DRAFT,
        created_at=datetime.datetime.now(),
        players=[
            don_player(seats_generator, players_generator),
            sheriff_player(seats_generator, players_generator),
            *[mafia_player(seats_generator, players_generator) for _ in range(2)],
            *[civilian_player(seats_generator, players_generator) for _ in range(5)],
        ],
    )


def _get_other_players(role: Roles) -> list[PlayerInGameSchema]:
    roles = {
        Roles.DON: 1,
        Roles.SHERIFF: 1,
        Roles.MAFIA: 2,
        Roles.CIVILIAN: 6,
    }

    def _seq_seats_gen():
        yield from range(2, 11)

    seats_generator = _seq_seats_gen()
    players_generator = _gen_player(fios=TEST_FIOS.copy(), nicknames=TEST_NICKNAMES.copy())

    def _get_gen_by_role(role: Roles) -> Callable:
        match role:
            case Roles.CIVILIAN:
                return civilian_player
            case Roles.MAFIA:
                return mafia_player
            case Roles.SHERIFF:
                return sheriff_player
            case Roles.DON:
                return don_player
            case _:
                raise Exception("Got unknown role")

    roles[role] -= 1
    players = []
    for k, v in roles.items():
        player_gen = _get_gen_by_role(k)
        for _ in range(v):
            players.append(player_gen(seats_generator, players_generator))
    return players


def ended_game_with_player(player: PlayerInGameSchema, result: GameResults) -> GameSchema:
    other_players = _get_other_players(player.role)
    return GameSchema(
        id=next(id_g),
        comments="",
        result=result,
        status=GameStatuses.ENDED,
        created_at=datetime.datetime.now(),
        players=[
            player,
            *other_players,
        ],
    )


def won_game(player: PlayerInGameSchema) -> GameSchema:
    res = get_win_result_by_player_role(player.role)
    return ended_game_with_player(player, res)


def lost_game(player: PlayerInGameSchema) -> GameSchema:
    if get_win_result_by_player_role(player.role) == GameResults.MAFIA_WON:
        return ended_game_with_player(player, GameResults.CIVILIANS_WON)
    return ended_game_with_player(player, GameResults.MAFIA_WON)
