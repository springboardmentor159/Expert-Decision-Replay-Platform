from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Expert Decision Replay Platform"
    DATABASE_URL: str

    # JWT settings (preserved from existing implementation)
    SECRET_KEY: str = "changeme-please-set-strong-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    # Lowercase aliases for backward compatibility with existing code
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

    @property
    def access_token_expire_minutes(self) -> int:
        return self.ACCESS_TOKEN_EXPIRE_MINUTES


settings = Settings()