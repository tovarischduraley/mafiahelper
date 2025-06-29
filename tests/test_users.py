import pytest

from tests.mocks import FakeDBRepository
from usecases import UsersUseCase
from usecases.schemas import UserSchema

user = UserSchema(
    telegram_id=1,
    first_name="John",
    last_name="Doe",
    username="JohnDoe",
)


@pytest.mark.asyncio
async def test_save_user():
    db = FakeDBRepository()
    uc = UsersUseCase(db=db)
    users_count_before = len(db._users)
    await uc.save_user(user)
    assert users_count_before + 1 == len(db._users)


@pytest.mark.asyncio
async def test_get_users():
    db = FakeDBRepository(users={user.telegram_id: user})
    uc = UsersUseCase(db=db)
    users = await uc.get_users()
    assert len(users) == 1
    assert users[0] == user
