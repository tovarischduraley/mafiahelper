from typing import Self

from sqlalchemy import and_, delete, func, or_, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import joinedload

import core
from usecases.errors import NotFoundError
from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import CreateGameSchema, CreateUserSchema, GameSchema, UpdateGameSchema, UserSchema
from usecases.schemas.games import PlayerSchema, RawGameSchema

from .models import Game, User, UserGame


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

    async def create_user(self, user: CreateUserSchema) -> None:
        new_user = User(fio=user.fio, nickname=user.nickname)
        self._session.add(new_user)
        await self._session.flush()

    async def get_users(
        self,
        limit: int | None,
        offset: int | None,
    ) -> list[UserSchema]:
        query = select(User)
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        raw_users = (await self._session.scalars(query)).all()
        return [UserSchema.model_validate(u, from_attributes=True) for u in raw_users]

    async def get_user_by_id(self, user_id: int) -> UserSchema:
        query = select(User).where(User.id == user_id)
        user = await self._session.scalar(query)
        if not user:
            raise NotFoundError(f"User id={user_id} not found")
        return UserSchema.model_validate(user, from_attributes=True)

    @staticmethod
    def _format_game(game: Game) -> GameSchema:
        return GameSchema(
            id=game.id,
            comments=game.comments,
            result=game.result,
            status=game.status,
            players=[
                PlayerSchema(
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
        query = select(Game).where(Game.id == game_id).options(joinedload(Game.players).joinedload(UserGame.player))
        game = (await self._session.scalars(query)).first()
        if not game:
            raise NotFoundError(f"Game id={game_id} not found")
        return self._format_game(game)

    async def get_games(
            self,
            user_id: int | None = None,
            seat_number: int | None = None,
            role__in: list[core.Roles] | None = None,
            result__in: list[core.GameResults] | None = None,
            status: core.GameStatuses | None = None,
            is_won: bool | None = None,
    ) -> list[GameSchema]:
        query = select(Game).join(UserGame).join(User).options(joinedload(Game.players).joinedload(UserGame.player))
        if user_id is not None:
            query = query.where(UserGame.user_id == user_id)
        if role__in is not None:
            query = query.where(UserGame.role.in_(role__in))
        if result__in is not None:
            query = query.where(Game.result.in_(result__in))
        if seat_number is not None:
            query = query.where(UserGame.number == seat_number)
        if status is not None:
            query = query.where(Game.status == status)
        if is_won is not None:
            if user_id is None:
                raise Exception("user_id must be defined to use filter 'is_won'")
            query = query.where(
                or_(
                    and_(
                        UserGame.role.in_([core.Roles.SHERIFF, core.Roles.CIVILIAN]),
                        Game.result == core.GameResults.CIVILIANS_WON,
                    ),
                    and_(
                        UserGame.role.in_([core.Roles.MAFIA, core.Roles.DON]),
                        Game.result == core.GameResults.MAFIA_WON,
                    ),
                )
            )
        games = (await self._session.execute(query)).scalars().unique().all()
        return [self._format_game(g) for g in games]

        # return games
    async def add_player(self, game_id: int, user_id: int, seat_number: int, role: core.Roles) -> None:
        player = UserGame(
            user_id=user_id,
            number=seat_number,
            role=role,
            game_id=game_id,
        )
        self._session.add(player)
        await self._session.flush()

    async def get_users_count(self) -> int:
        query = select(func.count(User.id))
        return await self._session.scalar(query)

    async def remove_player(self, game_id: int, user_id: int) -> None:
        query = delete(UserGame).where(and_(UserGame.user_id == user_id, UserGame.game_id == game_id))
        await self._session.execute(query)
        await self._session.flush()

    async def remove_player_on_seat(self, game_id: int, seat_number: int) -> None:
        query = delete(UserGame).where(and_(UserGame.number == seat_number, UserGame.game_id == game_id))
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
        game_players = [UserGame(game_id=game.id, user_id=p.id, role=p.role, number=p.number) for p in data.players]
        self._session.add_all(game_players)
        await self._session.flush()
        return RawGameSchema(
            id=game.id,
            created_at=game.created_at,
            status=game.status,
            result=game.result,
            comments=game.comments,
        )
