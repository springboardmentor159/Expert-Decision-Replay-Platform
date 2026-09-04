from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    APP_NAME: str = "Expert Decision Replay Platform"
    DATABASE_URL: str = "sqlite:///./expert_decision_replay.db"
    SECRET_KEY: str = "development-only-change-this-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def app_name(self) -> str:
        return self.APP_NAME

    @property
    def database_url(self) -> str:
        return self.DATABASE_URL


settings = Settings()
