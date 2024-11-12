import core
from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import UserStatsSchema


class GetUserStatsUseCase:
    def __init__(self, db: DBRepositoryInterface) -> None:
        self._db = db

    async def get_user_stats(self, user_id: int) -> UserStatsSchema:
        async with self._db as db:
            user = await db.get_user_by_id(user_id)
            total_games = len(await db.get_games(
                user_id=user_id,
                status=core.GameStatuses.ENDED
            ))
            total_won = len(await db.get_games(
                user_id=user_id,
                status=core.GameStatuses.ENDED,
                is_won=True
            ))
            total_as_black = len(await db.get_games(
                user_id=user_id,
                status=core.GameStatuses.ENDED,
                role__in=[core.Roles.MAFIA, core.Roles.DON]
            ))
            won_as_black = len(await db.get_games(
                user_id=user_id,
                status=core.GameStatuses.ENDED,
                is_won=True,
                role__in=[core.Roles.MAFIA, core.Roles.DON],
            ))
            total_as_red = len(await db.get_games(
                user_id=user_id,
                status=core.GameStatuses.ENDED,
                role__in=[core.Roles.CIVILIAN, core.Roles.SHERIFF],
            ))
            won_as_red = len(await db.get_games(
                user_id=user_id,
                status=core.GameStatuses.ENDED,
                is_won=True,
                role__in=[core.Roles.CIVILIAN, core.Roles.SHERIFF],
            ))
            total_as_civilian = len(await db.get_games(
                user_id=user_id,
                status=core.GameStatuses.ENDED,
                role__in=[core.Roles.CIVILIAN],
            ))
            won_as_civilian = len(await db.get_games(
                user_id=user_id,
                status=core.GameStatuses.ENDED,
                is_won=True,
                role__in=[core.Roles.CIVILIAN],
            ))
            total_as_sheriff = len(await db.get_games(
                user_id=user_id,
                status=core.GameStatuses.ENDED,
                role__in=[core.Roles.SHERIFF],
            ))
            won_as_sheriff = len(await db.get_games(
                user_id=user_id,
                status=core.GameStatuses.ENDED,
                is_won=True,
                role__in=[core.Roles.SHERIFF],
            ))
            total_as_mafia = len(await db.get_games(
                user_id=user_id,
                status=core.GameStatuses.ENDED,
                role__in=[core.Roles.MAFIA],
            ))
            won_as_mafia = len(await db.get_games(
                user_id=user_id,
                status=core.GameStatuses.ENDED,
                is_won=True,
                role__in=[core.Roles.MAFIA],
            ))
            total_as_don = len(await db.get_games(
                user_id=user_id,
                status=core.GameStatuses.ENDED,
                role__in=[core.Roles.DON],
            ))
            won_as_don = len(await db.get_games(
                user_id=user_id,
                status=core.GameStatuses.ENDED,
                is_won=True,
                role__in=[core.Roles.DON],
            ))

            return UserStatsSchema(
                fio=user.fio,
                nickname=user.nickname,
                games_count_total=total_games,
                win_percent_general=self._get_percent(piece=total_won, total=total_games),
                win_percent_black_team=self._get_percent(piece=won_as_black, total=total_as_black),
                win_percent_red_team=self._get_percent(piece=won_as_red, total=total_as_red),
                win_percent_as_civilian=self._get_percent(piece=won_as_civilian, total=total_as_civilian),
                win_percent_as_mafia=self._get_percent(piece=won_as_mafia, total=total_as_mafia),
                win_percent_as_don=self._get_percent(piece=won_as_don, total=total_as_don),
                win_percent_as_sheriff=self._get_percent(piece=won_as_sheriff, total=total_as_sheriff),
            )
    def _get_percent(self, piece: int, total: int) -> float | None:
        return round(piece / total * 100, 2) if total > 0 else None
