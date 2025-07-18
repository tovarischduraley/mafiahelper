import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from repositories.db import DBRepository
from tests.integration.db import test_db_config
from usecases import GetGamesUseCase
from usecases.schemas import GameSchema


@pytest.mark.asyncio
async def test_get_games():
    engine = create_async_engine(test_db_config.db_url)
    maker = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
    uc = GetGamesUseCase(DBRepository(maker))
    games, count = await uc.get_ended_games()
    assert isinstance(games, list)
    assert isinstance(games[0], GameSchema)
    assert isinstance(count, int)


@pytest.mark.asyncio
async def test_get_game_detail():
    engine = create_async_engine(test_db_config.db_url)
    maker = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
    uc = GetGamesUseCase(DBRepository(maker))
    games, count = await uc.get_ended_games()
    g = await uc.get_game(games[0].id)
    assert isinstance(g, GameSchema)
