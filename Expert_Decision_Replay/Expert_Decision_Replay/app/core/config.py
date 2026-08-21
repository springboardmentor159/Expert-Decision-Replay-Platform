from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# .env is located in the outer Expert_Decision_Replay folder
ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    APP_NAME: str = "Expert Decision Replay Platform"
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
