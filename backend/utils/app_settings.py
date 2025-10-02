from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    APP_NAME: str 
    APP_VERSION: str

    ALLOWED_FILE_TYPES: list[str]
    MAX_FILE_SIZE: int
    CHUNK_SIZE: int

    MONGO_URL: str
    MONGO_DB: str

    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str
    SUMMARY_BACKEND: str
    
    GEMINI_API_KEY: str

    GENERATION_MODEL_ID: str
    EMBEDDING_MODEL_ID: str
    EMBEDDING_SIZE: int
    SUMMARY_MODEL_ID: str

    DEFAULT_MAX_INPUT_CHARACTERS: int
    DEFAULT_MAX_TOKENS: int
    DEFAULT_TEMPERATURE: float

    VECTOR_DB_BACKEND: str
    VECTOR_DB_HOST: str
    VECTOR_DB_PORT: int
    VECTOR_DB_GRPC_PORT: int
    VECTOR_DB_DISTANCE_METHOD: str

    LANG: str
    DEFAULT_LANG: str

    TRANSLATION_SUPPORTED_LANGUAGES: list[str] = ["English", "Spanish", "French", "German", "Arabic", "Italian"]
    TRANSLATION_MAX_INPUT_CHARACTERS: int = 5000
    class Config:
        env_file = "backend/.env"  

def get_settings() -> AppSettings:
    return AppSettings()
