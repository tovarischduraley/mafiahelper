import core
from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import PlayerStatsSchema


class GetPlayerStatsUseCase:
    def __init__(self, db: DBRepositoryInterface) -> None:
        self._db = db

    async def get_player_stats(self, player_id: int) -> PlayerStatsSchema:
        async with self._db as db:
            user = await db.get_player_by_id(player_id)
            total_games = await db.get_games(
                player_id=player_id,
                status=core.GameStatuses.ENDED
            )
            total_won = await db.get_games(
                player_id=player_id,
                status=core.GameStatuses.ENDED,
                is_won=True
            )
            total_as_black = await db.get_games(
                player_id=player_id,
                status=core.GameStatuses.ENDED,
                role__in=[core.Roles.MAFIA, core.Roles.DON]
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

            return PlayerStatsSchema(
                fio=user.fio,
                nickname=user.nickname,
                games_count_total=len(total_games),
                win_percent_general=self._get_percent(piece=len(total_won), total=len(total_games)),
                win_percent_black_team=self._get_percent(piece=len(won_as_black), total=len(total_as_black)),
                win_percent_red_team=self._get_percent(piece=len(won_as_red), total=len(total_as_red)),
                win_percent_as_civilian=self._get_percent(piece=len(won_as_civilian), total=len(total_as_civilian)),
                win_percent_as_mafia=self._get_percent(piece=len(won_as_mafia), total=len(total_as_mafia)),
                win_percent_as_don=self._get_percent(piece=len(won_as_don), total=len(total_as_don)),
                win_percent_as_sheriff=self._get_percent(piece=len(won_as_sheriff), total=len(total_as_sheriff)),
            )
    @staticmethod
    def _get_percent(piece: int, total: int) -> float | None:
        return round(piece / total * 100, 2) if total > 0 else None
