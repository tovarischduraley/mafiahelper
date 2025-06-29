from collections.abc import Iterable

import core
from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import GameSchema, PlayerStatsSchema


class GetPlayerStatsUseCase:
    def __init__(self, db: DBRepositoryInterface) -> None:
        self._db = db

    async def get_player_stats(self, player_id: int) -> PlayerStatsSchema:
        async with self._db as db:
            user = await db.get_player_by_id(player_id)
            total_games = await db.get_games(player_id=player_id, status=core.GameStatuses.ENDED)
            total_won = await db.get_games(player_id=player_id, status=core.GameStatuses.ENDED, is_won=True)
            total_as_black = await db.get_games(
                player_id=player_id, status=core.GameStatuses.ENDED, role__in=[core.Roles.MAFIA, core.Roles.DON]
            )
            won_as_black = await db.get_games(
                player_id=player_id,
                status=core.GameStatuses.ENDED,
                is_won=True,
                role__in=[core.Roles.MAFIA, core.Roles.DON],
            )
            total_as_red = await db.get_games(
                player_id=player_id,
                status=core.GameStatuses.ENDED,
                role__in=[core.Roles.CIVILIAN, core.Roles.SHERIFF],
            )
            won_as_red = await db.get_games(
                player_id=player_id,
                status=core.GameStatuses.ENDED,
                is_won=True,
                role__in=[core.Roles.CIVILIAN, core.Roles.SHERIFF],
            )
            total_as_civilian = await db.get_games(
                player_id=player_id,
                status=core.GameStatuses.ENDED,
                role__in=[core.Roles.CIVILIAN],
            )
            won_as_civilian = await db.get_games(
                player_id=player_id,
                status=core.GameStatuses.ENDED,
                is_won=True,
                role__in=[core.Roles.CIVILIAN],
            )
            total_as_sheriff = await db.get_games(
                player_id=player_id,
                status=core.GameStatuses.ENDED,
                role__in=[core.Roles.SHERIFF],
            )
            won_as_sheriff = await db.get_games(
                player_id=player_id,
                status=core.GameStatuses.ENDED,
                is_won=True,
                role__in=[core.Roles.SHERIFF],
            )
            total_as_mafia = await db.get_games(
                player_id=player_id,
                status=core.GameStatuses.ENDED,
                role__in=[core.Roles.MAFIA],
            )
            won_as_mafia = await db.get_games(
                player_id=player_id,
                status=core.GameStatuses.ENDED,
                is_won=True,
                role__in=[core.Roles.MAFIA],
            )
            total_as_don = await db.get_games(
                player_id=player_id,
                status=core.GameStatuses.ENDED,
                role__in=[core.Roles.DON],
            )
            won_as_don = await db.get_games(
                player_id=player_id,
                status=core.GameStatuses.ENDED,
                is_won=True,
                role__in=[core.Roles.DON],
            )
            first_killed_games = list(filter(
                lambda g: g.first_killed and g.first_killed.id == player_id,
                total_as_civilian + total_as_sheriff
            ))
            result = self.get_best_move_stats(first_killed_games)
            best_move_count_total = result[0]
            zero_mafia_best_move_count = result[1]
            one_mafia_best_move_count = result[2]
            two_mafia_best_move_count = result[3]
            three_mafia_best_move_count = result[4]

            return PlayerStatsSchema(
                fio=user.fio,
                nickname=user.nickname,
                won_games_count_total=len(total_won),
                games_count_total=len(total_games),
                win_percent_general=self._get_percent(piece=len(total_won), total=len(total_games)),
                ########################################################################################################
                won_games_count_black_team=len(won_as_black),
                games_count_black_team=len(total_as_black),
                win_percent_black_team=self._get_percent(piece=len(won_as_black), total=len(total_as_black)),
                ########################################################################################################
                won_games_count_red_team=len(won_as_red),
                games_count_red_team=len(total_as_red),
                win_percent_red_team=self._get_percent(piece=len(won_as_red), total=len(total_as_red)),
                ########################################################################################################
                won_games_count_as_civilian=len(won_as_civilian),
                games_count_as_civilian=len(total_as_civilian),
                win_percent_as_civilian=self._get_percent(piece=len(won_as_civilian), total=len(total_as_civilian)),
                ########################################################################################################
                won_games_count_as_mafia=len(won_as_mafia),
                games_count_as_mafia=len(total_as_mafia),
                win_percent_as_mafia=self._get_percent(piece=len(won_as_mafia), total=len(total_as_mafia)),
                ########################################################################################################
                won_games_count_as_don=len(won_as_don),
                games_count_as_don=len(total_as_don),
                win_percent_as_don=self._get_percent(piece=len(won_as_don), total=len(total_as_don)),
                ########################################################################################################
                won_games_count_as_sheriff=len(won_as_sheriff),
                games_count_as_sheriff=len(total_as_sheriff),
                win_percent_as_sheriff=self._get_percent(piece=len(won_as_sheriff), total=len(total_as_sheriff)),
                ########################################################################################################
                first_killed_count=len(first_killed_games),
                best_move_count_total=best_move_count_total,
                zero_mafia_best_move_count=zero_mafia_best_move_count,
                one_mafia_best_move_count=one_mafia_best_move_count,
                two_mafia_best_move_count=two_mafia_best_move_count,
                three_mafia_best_move_count=three_mafia_best_move_count,
            )

    @staticmethod
    def get_best_move_stats(games_as_first_killed: Iterable[GameSchema]) -> tuple[int, int, int, int, int]:
        best_move_count_total = 0
        zero_mafia_best_move_count = 0
        one_mafia_best_move_count = 0
        two_mafia_best_move_count = 0
        three_mafia_best_move_count = 0
        for game in games_as_first_killed:
            if game.best_move is None:
                continue

            best_move_count_total += 1
            black_in_best_move = 0
            for player_in_best_move in game.best_move:
                if player_in_best_move.role in {core.Roles.MAFIA, core.Roles.DON}:
                    black_in_best_move += 1

            match black_in_best_move:
                case 0:
                    zero_mafia_best_move_count += 1
                case 1:
                    one_mafia_best_move_count += 1
                case 2:
                    two_mafia_best_move_count += 1
                case 3:
                    three_mafia_best_move_count += 1
        return (
            best_move_count_total,
            zero_mafia_best_move_count,
            one_mafia_best_move_count,
            two_mafia_best_move_count,
            three_mafia_best_move_count,
        )

    @staticmethod
    def _get_percent(piece: int, total: int) -> float | None:
        return round(piece / total * 100, 2) if total > 0 else None
