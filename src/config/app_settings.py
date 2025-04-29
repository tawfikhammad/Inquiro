from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    APP_NAME: str 
    APP_VERSION: str

    class Config:
        env_file = "src/.env"  

def app_settings() -> AppSettings:
    return AppSettings()
