from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settigns(BaseSettings):
    POSTGRES_USER: str = "your_db_user"
    POSTGRES_PASSWORD: str = "your_db_password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_HOST_ASYNC: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "your_db_name"

    PORT: int = 8000
    HOST: str = "0.0.0.0"
    RELOAD: bool = True
    STR_ALLOWED_ORIGINS: str = "*,example.url"

    AUTH_SECRET_KEY: str = "secret key"
    AUTH_ALGORITHM: str = "algorithm"

    CLOUDINARY_NAME: str = "cloudinary_name"
    CLOUDINARY_API_KEY: str = "cloudinary_api_key"
    CLOUDINARY_API_SECRET: str = "cloudinary_api_secret"

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST_ASYNC}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    @property
    def SYNC_DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def ALLOWED_ORIGINS_LIST(self) -> list:
        return self.STR_ALLOWED_ORIGINS.split(",")

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8"
    )

config = Settigns()
