from pydantic import BaseModel


class CreateUserSchema(BaseModel):
    fio: str | None = None
    nickname: str | None = None


class UserSchema(BaseModel):
    id: int
    fio: str | None
    nickname: str | None

