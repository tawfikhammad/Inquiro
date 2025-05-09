from ..LLMInterface import LLMInterface
from ..LLMEnums import CoHereEnums, DocumentTypeEnum
import cohere
import logging

class CoHereProvider(LLMInterface):

    def __init__(self, api_key: str,
                       default_max_input_characters: int=1000,
                       default_generation_max_output_tokens: int=1000,
                       default_generation_temperature: float=0.1):
        
        self.api_key = api_key

        self.default_max_input_characters = default_max_input_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        self.summary_model_id = None

        self.client = cohere.Client(api_key=self.api_key)

        self.logger = logging.getLogger(__name__)

    async def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    async def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    async def set_summary_model(self, summary_model_id: str):
        self.summary_model_id = summary_model_id

    def process_text(self, text: str):
        return text[:self.default_max_input_characters].strip()

    async def generate(self, prompt: str, chat_history: list=[], max_output_tokens: int=None,
                            temperature: float = None):

        if not self.client:
            self.logger.error("CoHere client was not set")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for CoHere was not set")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        try:
            response = self.client.chat(
                model=self.generation_model_id,
                chat_history=chat_history,
                message=self.process_text(prompt),
                temperature=temperature,
                max_tokens=max_output_tokens
            )

            if not response or not response.text:
                self.logger.error("Error while generating text with CoHere")
                return None
            
            return response.text
        except Exception as e:
            self.logger.error(f"Error generating text with CoHere: {str(e)}")
            return None
    
    async def embed(self, text: str, document_type: str = None):
        if not self.client:
            self.logger.error("CoHere client was not set")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model for CoHere was not set")
            return None
        
        input_type = CoHereEnums.DOCUMENT.value
        if document_type == DocumentTypeEnum.QUERY.value:
            input_type = CoHereEnums.QUERY.value

        try:
            response = self.client.embed(
                model=self.embedding_model_id,
                texts=[self.process_text(text)],
                input_type=input_type,
                embedding_types=['float'],
            )

            if not response or not response.embeddings or not response.embeddings.float:
                self.logger.error("Error while embedding text with CoHere")
                return None
            
            return response.embeddings.float[0]
        except Exception as e:
            self.logger.error(f"Error embedding text with CoHere: {str(e)}")
            return None

    async def summarize(self, text: str):
        if not self.client:
            self.logger.error("CoHere client was not set")
            return None

        # generation model for summarization if no summary model is set
        model_id = self.summary_model_id if self.summary_model_id else self.generation_model_id
        
        if not model_id:
            self.logger.error("No model set for summarization with CoHere")
            return None
        
        try:
            summarization_prompt = f"Please summarize the following text concisely while maintaining key information: {self.process_text(text)}"
            
            response = self.client.chat(
                model=model_id,
                message=summarization_prompt,
                temperature=0.3,  # Lower temperature for more focused summarization
                max_tokens=self.default_generation_max_output_tokens
            )

            if not response or not response.text:
                self.logger.error("Error while summarizing text with CoHere")
                return None
            
            return response.text
        except Exception as e:
            self.logger.error(f"Error summarizing text with CoHere: {str(e)}")
            return None
    
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "text": self.process_text(prompt)
        }