from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    APP_NAME: str 
    APP_VERSION: str

    ALLOWWED_FILE_TYPES: list[str]
    MAX_FILE_SIZE : int
    CHUNK_SIZE : int

    MONGO_URL: str
    MONGO_DB: str
    
    class Config:
        env_file = "src/.env"  

def app_settings() -> AppSettings:
    return AppSettings()
