from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Expert Decision Replay Platform"
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/expert_decision_replay"

    @property
    def database_url(self) -> str:
        return self.DATABASE_URL

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
