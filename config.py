from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "./data/app.db"
    WEBHOOK_SECRET: str
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
