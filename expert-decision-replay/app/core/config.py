from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):

    APP_NAME: str = "Expert Decision Replay Platform"

    DATABASE_URL: str = (
        "postgresql+psycopg2://postgres:1255@localhost:5432/"
        "expert_decision_replay"
    )

    SECRET_KEY: str = "your-secret-key-change-this"

    ALGORITHM: str = "HS256"

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

    @property
    def secret_key(self) -> str:
        return self.SECRET_KEY

    @property
    def algorithm(self) -> str:
        return self.ALGORITHM


settings = Settings()