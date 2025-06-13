from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    APP_NAME: str 
    APP_VERSION: str

    ALLOWWED_FILE_TYPES: list[str]
    MAX_FILE_SIZE : int
    CHUNK_SIZE : int

    MONGO_URL: str
    MONGO_DB: str

    GENERATION_BACKEND : str
    EMBEDDING_BACKEND : str
    SUMMARY_BACKEND : str
    
    OPENAI_API_KEY: str
    OPENAI_API_URL: str
    COHERE_API_KEY: str
    GEMINI_API_KEY : str

    GENERATION_MODEL_ID : str
    EMBEDDING_MODEL_ID : str
    EMBEDDING_MODEL_SIZE : int
    SUMMARY_MODEL_ID : str

    INPUT_DAFAULT_MAX_CHARACTERS : int
    GENERATION_DAFAULT_MAX_TOKENS : int
    GENERATION_DAFAULT_TEMPERATURE : float

    VECTOR_DB_BACKEND : str
    VECTOR_DB_PATH : str
    VECTOR_DB_DISTANCE_METHOD :str
    class Config:
        env_file = "backend/.env"  

def app_settings() -> AppSettings:
    return AppSettings()
