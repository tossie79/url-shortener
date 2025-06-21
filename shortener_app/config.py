from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):
    env_name: str = "Local"
    base_url: str = "http://localhost:8000"
    db_url: str = "sqlite:///./db.shortener.db"

    class Config:
        env_file = ".env"
        # env_file_encoding = "utf-8"
        # case_sensitive = True
        # # Allow the use of environment variables to override settings
        # env_nested_delimiter = "__"




# ✅ Define this OUTSIDE the class
@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    print(f"Loading settings for {settings.env_name} environment")
    return settings
