import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from repositories.db import DBRepository
from tests.integration.db import test_db_config
from usecases import GetPlayerStatsUseCase, GetPlayersUseCase
from usecases.schemas import PlayerSchema, PlayerStatsSchema


@pytest.mark.asyncio
async def test_get_players():
    engine = create_async_engine(test_db_config.db_url)
    maker = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
    uc = GetPlayersUseCase(DBRepository(maker))
    players, count = await uc.get_players()
    assert isinstance(players, list)
    assert isinstance(players[0], PlayerSchema)
    assert isinstance(count, int)


@pytest.mark.asyncio
async def test_get_player_detail():
    engine = create_async_engine(test_db_config.db_url)
    maker = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
    uc = GetPlayersUseCase(DBRepository(maker))
    players, _ = await uc.get_players()
    uc = GetPlayerStatsUseCase(DBRepository(maker))
    player_stats = await uc.get_player_stats(player_id=players[0].id)
    assert isinstance(player_stats, PlayerStatsSchema)
