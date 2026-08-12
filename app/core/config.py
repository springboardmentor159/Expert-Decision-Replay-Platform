from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    APP_NAME: str = "Expert Decision Replay Platform"
    DATABASE_URL: str = "postgresql+psycopg2://postgres:1234@localhost:5432/expert_decision_replay"
    SECRET_KEY: str = "a_super_secret_key_change_me"
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
