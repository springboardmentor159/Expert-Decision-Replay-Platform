from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()

# Keep local development usable when a dotenv editor accidentally joins the
# database URL and the following SECRET_KEY assignment onto one line.
if "SECRET_KEY=" in settings.DATABASE_URL:
    settings.DATABASE_URL = settings.DATABASE_URL.split("SECRET_KEY=", 1)[0].rstrip()