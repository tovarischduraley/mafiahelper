from punq import Container
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import DBConfig
from repositories.db import DBRepository
from usecases import (
    AddToBestMoveUseCase,
    AssignAsFirstKilledUseCase,
    AssignPlayerToSeatUseCase,
    CreateGameUseCase,
    CreatePlayerUseCase,
    EndGameUseCase,
    GetGamesUseCase,
    GetPlayerStatsUseCase,
    GetPlayersUseCase,
    GetSeatUseCase,
    UsersUseCase,
)
from usecases.interfaces import DBRepositoryInterface

container = Container()
db_config = DBConfig()

engine = create_async_engine(
    db_config.db_url,
    echo=False,
    pool_size=7,
    max_overflow=20,
    pool_pre_ping=True,
)

session_factory = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


container.register(DBRepositoryInterface, factory=DBRepository, session_factory=session_factory)
container.register(DBRepository, factory=DBRepository, session_factory=session_factory)
container.register(CreatePlayerUseCase, factory=CreatePlayerUseCase)
container.register(GetPlayersUseCase, factory=GetPlayersUseCase)
container.register(CreateGameUseCase, factory=CreateGameUseCase)
container.register(GetGamesUseCase, factory=GetGamesUseCase)
container.register(EndGameUseCase, factory=EndGameUseCase)
container.register(AssignPlayerToSeatUseCase, factory=AssignPlayerToSeatUseCase)
container.register(GetPlayerStatsUseCase, factory=GetPlayerStatsUseCase)
container.register(GetSeatUseCase, factory=GetSeatUseCase)
container.register(UsersUseCase, factory=UsersUseCase)
container.register(AssignAsFirstKilledUseCase, factory=AssignAsFirstKilledUseCase)
container.register(AddToBestMoveUseCase, factory=AddToBestMoveUseCase)
