from pydantic_settings import BaseSettings


class DBConfig(BaseSettings):
    DB_HOST: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_PORT: int

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class Settings(BaseSettings):
    db_config: DBConfig = DBConfig()
    TELEGRAM_BOT_TOKEN: str
    ADMIN_ID: int

def get_settings():
    return Settings()
