from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_BASE_URL: str = "https://circuit-trial.stg.rd.ds.sansan.com/api"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
