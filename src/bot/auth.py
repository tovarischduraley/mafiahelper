from config import get_settings
from usecases.errors import ForbiddenError


def validate_admin(user_id: int):
    if not user_id == get_settings().ADMIN_ID:
        raise ForbiddenError("Not allowed")

def is_admin(user_id: int):
    return user_id == get_settings().ADMIN_ID
