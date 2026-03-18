from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    app_env: str = 'development'
    app_secret_key: str = Field(..., alias='APP_SECRET_KEY')
    database_url: str = Field(..., alias='DATABASE_URL')
    cors_origins: list[AnyHttpUrl] | list[str] = Field(default=['http://localhost:3000'], alias='CORS_ORIGINS')
    access_token_expire_minutes: int = Field(default=30, alias='ACCESS_TOKEN_EXPIRE_MINUTES')
    refresh_token_expire_minutes: int = Field(default=60 * 24 * 7, alias='REFRESH_TOKEN_EXPIRE_MINUTES')
    frontend_url: AnyHttpUrl | str = Field(default='http://localhost:3000', alias='FRONTEND_URL')


@lru_cache
def get_settings() -> Settings:
    return Settings()
