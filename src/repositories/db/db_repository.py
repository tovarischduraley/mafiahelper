from typing import Self

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import joinedload

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
        await self._session.close()

    async def create_user(self, user: CreateUserSchema) -> None:
        new_user = User(fio=user.fio, nickname=user.nickname)
        self._session.add(new_user)
        await self._session.commit()

    async def get_users(
        self,
        fio_or_nickname__ilike: str | None,
        limit: int | None,
        offset: int | None,
    ) -> list[UserSchema]:
        query = select(User)
        if fio_or_nickname__ilike is not None:
            query = query.where(User.fio.in_(fio_or_nickname__ilike))
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        raw_users = (await self._session.scalars(query)).all()
        return [UserSchema.model_validate(u, from_attributes=True) for u in raw_users]

    async def get_game_by_id(self, game_id: int) -> GameSchema:
        query = select(Game).where(Game.id == game_id).options(joinedload(Game.players).joinedload(UserGame.player))
        game = (await self._session.scalars(query)).first()
        if not game:
            raise NotFoundError(f"Game id={game_id} not found")
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

    async def update_game(self, data: UpdateGameSchema) -> None: ...

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
        result = RawGameSchema(
            id=game.id,
            created_at=game.created_at,
            status=game.status,
            result=game.result,
            comments=game.comments,
        )
        await self._session.commit()
        return result
