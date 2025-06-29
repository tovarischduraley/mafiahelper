import core
from usecases.errors import ValidationError
from usecases.interfaces.db import DBRepositoryInterface
from usecases.schemas.games import PlayerInGameSchema


class AddToBestMoveUseCase:
    def __init__(self, db_repository: DBRepositoryInterface):
        self._db_repository = db_repository

    def _validate_players_count(self, game_players: set[int]) -> None:
        if len(game_players) != core.MAX_PLAYERS:
            raise ValidationError(f"Could not set to 'best move' with less than '{core.MAX_PLAYERS}' players in game")

    def _validate_first_killed(self, first_killed: PlayerInGameSchema | None) -> None:
        if not first_killed:
            raise ValidationError("Could not set 'best move' without first killed assigned")

    def _validate_players_numbers(self, players_numbers: set[int], game_players: set[int]) -> None:
        if len(players_numbers) != core.RolesQuantity.DON + core.RolesQuantity.MAFIA:
            raise ValidationError(
                f"Could not set to 'best move' with '{core.RolesQuantity.DON + core.RolesQuantity.MAFIA}' players"
            )
        for player_number in players_numbers:
            if player_number not in {player.number for player in game_players}:
                raise ValidationError(f"Player with number '{player_number}' not in game")

    async def add_players_to_best_move(self, players_numbers: set[int], game_id: int) -> None:
        async with self._db_repository as db:
            game = await db.get_game_by_id(game_id=game_id)
            self._validate_players_count(game_players=game.players)
            self._validate_first_killed(first_killed=game.first_killed)
            self._validate_players_numbers(players_numbers=players_numbers, game_players=game.players)

            await db.set_game_best_move(players_numbers=players_numbers, game_id=game_id)
