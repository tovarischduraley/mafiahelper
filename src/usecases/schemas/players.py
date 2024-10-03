from pydantic import BaseModel


class CreatePlayerSchema(BaseModel):
    fio: str | None = None
    nickname: str | None = None


class PlayerSchema(BaseModel):
    id: int
    fio: str | None
    nickname: str | None
