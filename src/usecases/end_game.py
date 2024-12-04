import core
from usecases.errors import ValidationError
from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import PlayerInGameSchema, UpdateGameSchema


class EndGameUseCase:
    def __init__(self, db: DBRepositoryInterface) -> None:
        self._db = db

    @staticmethod
    def _validate_unique_players(players: list[PlayerInGameSchema]) -> None:
        if len(players) != len({p.id for p in players}):
            raise ValidationError("Some player is duplicated in game")

    @staticmethod
    def _validate_roles_quantity(players: list[PlayerInGameSchema]) -> None:
        roles_in_game = {
            core.Roles.MAFIA: 0,
            core.Roles.DON: 0,
            core.Roles.CIVILIAN: 0,
            core.Roles.SHERIFF: 0,
        }
        for player in players:
            roles_in_game[player.role] += 1
        if (
            roles_in_game[core.Roles.SHERIFF] != core.RolesQuantity.SHERIFF
            or roles_in_game[core.Roles.DON] != core.RolesQuantity.DON
            or roles_in_game[core.Roles.MAFIA] != core.RolesQuantity.MAFIA
            or roles_in_game[core.Roles.CIVILIAN] not in [core.RolesQuantity.CIVILIAN, core.RolesQuantity.CIVILIAN - 1]
        ):
            raise ValidationError(f"Roles distribution is not correct {roles_in_game=}")

    @staticmethod
    def _validate_players_quantity(players: list[PlayerInGameSchema]) -> None:
        if not (core.MIN_PLAYERS <= (players_quantity := len(players)) <= core.MAX_PLAYERS):
            raise ValidationError(f"Can't create game with {players_quantity} players")

    @staticmethod
    def _validate_game_result(result: core.GameResults | None) -> None:
        if result is None:
            raise ValidationError("Can't create game with no result")

    @staticmethod
    def _validate_players_numbers(players: list[PlayerInGameSchema]) -> None:
        if len({p.number for p in players}) != len(players):
            raise ValidationError("Players seat numbers are not valid")

    async def end_game(self, game_id: int, result: core.GameResults) -> None:
        async with self._db as db:
            await self._db.update_game(
                game_id=game_id,
                data=UpdateGameSchema(result=result, status=core.GameStatuses.ENDED),
            )
            game = await db.get_game_by_id(game_id)
            self._validate_game_result(game.result)
            self._validate_players_numbers(game.players)
            self._validate_players_quantity(game.players)
            self._validate_roles_quantity(game.players)
