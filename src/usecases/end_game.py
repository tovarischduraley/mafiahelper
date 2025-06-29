import core
from core.games import RolesQuantity
from usecases.errors import ValidationError
from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import PlayerInGameSchema, UpdateGameSchema


class EndGameUseCase:
    def __init__(self, db: DBRepositoryInterface) -> None:
        self._db = db

    @staticmethod
    def _validate_roles_quantity(players: set[PlayerInGameSchema]) -> None:
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
    def _validate_players_quantity(players: set[PlayerInGameSchema]) -> None:
        if not (core.MIN_PLAYERS <= (players_quantity := len(players)) <= core.MAX_PLAYERS):
            raise ValidationError(f"Can't create game with {players_quantity} players")

    @staticmethod
    def _validate_game_result(result: core.GameResults | None) -> None:
        if result is None:
            raise ValidationError("Can't create game with no result")

    @staticmethod
    def _validate_players_numbers(players: set[PlayerInGameSchema]) -> None:
        if len({p.number for p in players}) != len(players):
            raise ValidationError("Players seat numbers are not valid")

    @staticmethod
    def _validate_best_move(
        best_move: set[PlayerInGameSchema] | None,
        first_killed: PlayerInGameSchema | None,
    ) -> None:
        if best_move is not None and first_killed is None:
            raise ValidationError("First killed player must be specified to register 'best move'")
        if best_move is not None and len(best_move) != (expected := RolesQuantity.MAFIA + RolesQuantity.DON):
            raise ValidationError(f"Wrong best move players count. got {len(best_move)} != {expected} expected")

    async def end_game(self, game_id: int, result: core.GameResults) -> None:
        async with self._db as db:
            game = await db.get_game_by_id(game_id)
            self._validate_players_numbers(game.players)
            self._validate_best_move(game.best_move, game.first_killed)
            self._validate_players_quantity(game.players)
            self._validate_roles_quantity(game.players)
            await self._db.update_game(
                game_id=game_id,
                data=UpdateGameSchema(result=result, status=core.GameStatuses.ENDED),
            )
