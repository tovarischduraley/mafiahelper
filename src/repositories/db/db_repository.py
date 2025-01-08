from typing import Self

from sqlalchemy import Row, and_, case, delete, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import joinedload

import core
from usecases.errors import NotFoundError
from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import (
    CreateGameSchema,
    CreatePlayerSchema,
    GameSchema,
    PlayerSchema,
    UpdateGameSchema,
    UserSchema,
)
from usecases.schemas.games import PlayerInGameSchema, RawGameSchema

from .models import Game, Player, PlayerGame, User


class DBRepository(DBRepositoryInterface):
    def __init__(self, session_factory: async_sessionmaker) -> None:
        self._session_maker = session_factory

    async def __aenter__(self) -> Self:
        self._session = self._session_maker()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            await self._session.commit()
        except Exception as e:
            await self._session.rollback()
            raise e
        finally:
            await self._session.close()

    async def create_player(self, player: CreatePlayerSchema) -> None:
        new_user = Player(fio=player.fio, nickname=player.nickname)
        self._session.add(new_user)
        await self._session.flush()

    async def create_user(self, user: UserSchema) -> None:
        self._session.add(User(**user.model_dump()))
        await self._session.flush()

    async def get_users(self) -> list[UserSchema]:
        return [
            UserSchema.model_validate(u, from_attributes=True)
            for u in (await self._session.scalars(select(User))).all()
        ]

    async def get_players(
        self,
        limit: int | None,
        offset: int | None,
    ) -> list[PlayerSchema]:
        query = (
            select(
                Player.id,
                Player.fio,
                Player.nickname,
                func.coalesce(func.sum(case((Game.status == "ended", 1), else_=0)), 0).label("ended_games_count"),
            )
            .outerjoin(PlayerGame, Player.id == PlayerGame.player_id)
            .outerjoin(Game, PlayerGame.game_id == Game.id)
            .group_by(Player.id, Player.nickname)
            .order_by(desc("ended_games_count"))
        )
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        raw_players = (await self._session.execute(query)).all()
        return [self._format_player(p) for p in raw_players]

    @staticmethod
    def _format_player(raw_player: Row) -> PlayerSchema:
        return PlayerSchema(id=raw_player[0], fio=raw_player[1], nickname=raw_player[2])

    async def get_player_by_id(self, player_id: int) -> PlayerSchema:
        query = select(Player).where(Player.id == player_id)
        user = await self._session.scalar(query)
        if not user:
            raise NotFoundError(f"User id={player_id} not found")
        return PlayerSchema.model_validate(user, from_attributes=True)

    @staticmethod
    def _format_game(game: Game) -> GameSchema:
        return GameSchema(
            id=game.id,
            comments=game.comments,
            result=game.result,
            status=game.status,
            players=[
                PlayerInGameSchema(
                    id=p.player.id,
                    fio=p.player.fio,
                    nickname=p.player.nickname,
                    role=p.role,
                    number=p.number,
                )
                for p in game.players
            ],
            created_at=game.created_at,
        )

    async def get_game_by_id(self, game_id: int) -> GameSchema:
        query = select(Game).where(Game.id == game_id).options(joinedload(Game.players).joinedload(PlayerGame.player))
        game = (await self._session.scalars(query)).first()
        if not game:
            raise NotFoundError(f"Game id={game_id} not found")
        return self._format_game(game)

    async def get_games(
        self,
        player_id: int | None = None,
        seat_number: int | None = None,
        role__in: list[core.Roles] | None = None,
        result__in: list[core.GameResults] | None = None,
        status: core.GameStatuses | None = None,
        is_won: bool | None = None,
    ) -> list[GameSchema]:
        query = (
            select(Game).join(PlayerGame).join(Player).options(joinedload(Game.players).joinedload(PlayerGame.player))
        )
        if player_id is not None:
            query = query.where(PlayerGame.player_id == player_id)
        if role__in is not None:
            query = query.where(PlayerGame.role.in_(role__in))
        if result__in is not None:
            query = query.where(Game.result.in_(result__in))
        if seat_number is not None:
            query = query.where(PlayerGame.number == seat_number)
        if status is not None:
            query = query.where(Game.status == status)
        if is_won is not None:
            if player_id is None:
                raise Exception("player_id must be defined to use filter 'is_won'")
            query = query.where(
                or_(
                    and_(
                        PlayerGame.role.in_([core.Roles.SHERIFF, core.Roles.CIVILIAN]),
                        Game.result == core.GameResults.CIVILIANS_WON,
                    ),
                    and_(
                        PlayerGame.role.in_([core.Roles.MAFIA, core.Roles.DON]),
                        Game.result == core.GameResults.MAFIA_WON,
                    ),
                )
            )
        games = (await self._session.execute(query)).scalars().unique().all()
        return [self._format_game(g) for g in games]

    async def add_player(self, game_id: int, player_id: int, seat_number: int, role: core.Roles) -> None:
        player_in_game = PlayerGame(
            player_id=player_id,
            number=seat_number,
            role=role,
            game_id=game_id,
        )
        self._session.add(player_in_game)
        await self._session.flush()

    async def get_players_count(self) -> int:
        query = select(func.count(Player.id))
        return await self._session.scalar(query)

    async def remove_player_from_game(self, game_id: int, player_id: int) -> None:
        query = delete(PlayerGame).where(and_(PlayerGame.player_id == player_id, PlayerGame.game_id == game_id))
        await self._session.execute(query)
        await self._session.flush()

    async def remove_player_on_seat(self, game_id: int, seat_number: int) -> None:
        query = delete(PlayerGame).where(and_(PlayerGame.number == seat_number, PlayerGame.game_id == game_id))
        await self._session.execute(query)
        await self._session.flush()

    async def update_game(self, game_id: int, data: UpdateGameSchema) -> None:
        query = update(Game).where(Game.id == game_id).values(**data.model_dump(exclude_none=True))
        await self._session.execute(query)
        await self._session.flush()

    async def create_game(self, data: CreateGameSchema) -> RawGameSchema:
        game = Game(
            created_at=data.created_at,
            status=data.status,
            result=data.result,
            comments=data.comments,
        )
        self._session.add(game)
        await self._session.flush()
        game_players = [PlayerGame(game_id=game.id, player_id=p.id, role=p.role, number=p.number) for p in data.players]
        self._session.add_all(game_players)
        await self._session.flush()
        return RawGameSchema(
            id=game.id,
            created_at=game.created_at,
            status=game.status,
            result=game.result,
            comments=game.comments,
        )
