from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str
    DATABASE_URL: str
    SECRET_KEY: str = "kslxmUT21DDS7rElQRYx62uVVjnj6V9Ccg5ANqVKIJg"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(
        env_file="app/.env",
        extra="ignore"
    )


settings = Settings()