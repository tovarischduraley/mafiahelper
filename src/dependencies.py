from punq import Container
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import DBConfig
from repositories.avatars import AvatarsRepository
from repositories.db import DBRepository
from usecases import (
    AddToBestMoveUseCase,
    AssignAsFirstKilledUseCase,
    AssignPlayerToSeatUseCase,
    CreateGameUseCase,
    CreatePlayerUseCase,
    DeletePlayerUseCase,
    EndGameUseCase,
    GetGamesUseCase,
    GetPlayerStatsUseCase,
    GetPlayersUseCase,
    GetSeatUseCase,
    SetPlayerAvatarUseCase,
    SetPlayerNicknameUseCase,
    UsersUseCase,
)
from usecases.interfaces import AvatarsRepositoryInterface, DBRepositoryInterface

container = Container()

def get_db_session_factory(config: DBConfig = DBConfig()):
    engine = create_async_engine(
        config.db_url,
        echo=False,
        pool_size=7,
        max_overflow=20,
        pool_pre_ping=True,
    )

    return async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


container.register(DBRepositoryInterface, factory=DBRepository, session_factory=get_db_session_factory())
container.register(DBRepository, factory=DBRepository, session_factory=get_db_session_factory())
container.register(AvatarsRepositoryInterface, factory=AvatarsRepository)
container.register(CreatePlayerUseCase)
container.register(GetPlayersUseCase)
container.register(CreateGameUseCase)
container.register(GetGamesUseCase)
container.register(EndGameUseCase)
container.register(AssignPlayerToSeatUseCase)
container.register(GetPlayerStatsUseCase)
container.register(GetSeatUseCase)
container.register(UsersUseCase)
container.register(AssignAsFirstKilledUseCase)
container.register(AddToBestMoveUseCase)
container.register(DeletePlayerUseCase)
container.register(SetPlayerNicknameUseCase)
container.register(SetPlayerAvatarUseCase)
