from pydantic import BaseModel
from pydantic_settings import BaseSettings


class DBConfig(BaseSettings):
    db_host: str
    db_name: str
    db_user: str
    db_password: str
    db_port: int

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


class Settings(BaseModel):
    db_config: DBConfig = DBConfig()


settings = Settings()