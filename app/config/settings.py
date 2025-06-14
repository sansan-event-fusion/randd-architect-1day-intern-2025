# external imports
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# internal imports


class Settings(BaseSettings):
    """Base settings class for the application."""

    # Secret key for the application
    # API_KEY: SecretStr # noqa: ERA001

    # General settings
    APP_NAME: str = "Sansan 1day Intern"

    # Data
    ROOT_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = ROOT_DIR / "data"
    API_BASE_URL: str = "https://circuit-trial.stg.rd.ds.sansan.com/api"

    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Get the settings object."""
    return Settings()
