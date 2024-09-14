from os.path import dirname, abspath, join
from pydantic import ConfigDict, model_validator
from pydantic_settings import BaseSettings


BASE_DIR = dirname(dirname(dirname(abspath(__file__))))
ENV_FILE = join(BASE_DIR, ".env")


class Settings(BaseSettings):
    # Основные параметры
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URL: str = ""

    @model_validator(mode="after")
    def get_database_url(self):
        self.DATABASE_URL = (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?async_fallback=True"
        )
        return self

    model_config = ConfigDict(env_file=ENV_FILE)


settings = Settings()

print(BASE_DIR)
print(ENV_FILE)