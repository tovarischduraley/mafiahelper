from punq import Container
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import DBConfig
from repositories.db import DBRepository
from usecases.interfaces import DBRepositoryInterface

container = Container()
pg_config = DBConfig()

engine = create_async_engine(
    pg_config.DATABASE_URL,
    echo=False,
    pool_size=7,
    max_overflow=20,
    pool_pre_ping=True,
)

session_factory = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


container.register(DBRepositoryInterface, DBRepository, session_factory=session_factory)
