from punq import Container
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import DBConfig
from repositories.db import DBRepository
from usecases import CreateUserUseCase, GetUsersUseCase
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
container.register(CreateUserUseCase, factory=CreateUserUseCase)
container.register(GetUsersUseCase, factory=GetUsersUseCase)
