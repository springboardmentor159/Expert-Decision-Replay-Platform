from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file="app/.env",
        extra="ignore"
    )


settings = Settings()