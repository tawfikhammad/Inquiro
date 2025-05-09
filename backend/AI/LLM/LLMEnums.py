from enum import Enum

class LLMModel(Enum):
    OPENAI="openai"
    COHERE="cohere"
    GEMINI="gemini"

class OpenAIEnums(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class CoHereEnums(Enum):
    SYSTEM = "SYSTEM"
    USER = "USER"
    ASSISTANT = "CHATBOT"

    DOCUMENT = "search_document"
    QUERY = "search_query"

class GeminiEnums(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "model"

    DOCUMENT = "RETRIEVAL_DOCUMENT"
    QUERY = "RETRIEVAL_QUERY"

class DocumentTypeEnum(Enum):
    DOCUMENT = "document"
    QUERY = "query"

