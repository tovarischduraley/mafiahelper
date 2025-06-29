from config import settings
from usecases.errors import ForbiddenError


def validate_admin(user_id: int):
    if not user_id == settings.ADMIN_ID:
        raise ForbiddenError("Not allowed")
