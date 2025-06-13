from openai import OpenAI
from ..LLMInterface import LLMInterface
from ..LLMEnums import OpenAIEnums
import logging


class OpenAIProvider(LLMInterface):
    def __init__(self, api_key: str,
                api_url: str = None,
                default_max_output_tokens: int = 1000, 
                default_generation_max_output_tokens: int=1000,
                default_generation_temperature: float = 0.5):
        
        self.api_key = api_key
        self.api_url = api_url
        self.client = OpenAI(api_key=api_key, api_base=api_url)

        self.default_max_output_tokens = default_max_output_tokens
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.genration_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        self.summary_model_id  = None

        self.logger = logging.getLogger(__name__)


    def set_generation_model(self, generation_model_id: str):
        self.generation_model_id = generation_model_id

    def set_embedding_model(self, embedding_model_id: str, embedding_size: int):
        self.embedding_model_id = embedding_model_id
        self.embedding_size = embedding_size

    async def set_summary_model(self, summary_model_id: str):
        self.summary_model_id = summary_model_id

    def process_text(self, text: str):
        return text[:self.default_generation_max_output_tokens].strip()
    
    def generate(self, prompt: str,chat_history: list = [], max_output_tokens: int = None, temperature: float = None):
        if self.genration_model_id is None:
            self.logger.error("Generation model ID is not set.")
            return None

        if self.client is None:
            self.logger.error("OpenAI client is not initialized.")
            return None
        
        temperature = temperature if temperature else self.default_generation_temperature
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_max_output_tokens

        messages = chat_history.copy()
        messages.append(self.construct_prompt(prompt, OpenAIEnums.USER.value))

        try:
            response = self.client.chat.completions.create(
                model=self.generation_model_id,
                messages=messages,
                max_tokens=max_output_tokens,
                temperature=temperature)

            if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
                self.logger.error("Error while generating text with OpenAI")
                return None
            
            return response.choices[0].message.content
        
        except Exception as e:
            self.logger.error(f"Error generating text with OpenAI: {str(e)}")
            return None


    def embed(self, text: str, document_type: str = None):
        if self.embedding_model_id is None:
            self.logger.error("Embedding model ID is not set.")
            return None

        if self.client is None:
            self.logger.error("OpenAI client is not initialized.")
            return None
        
        try:
            response = self.client.embeddings.create(
                input=self.process_text(text),
                model=self.embedding_model_id,
            )
            
            if not response or not response.data or len(response.data) == 0:
                self.logger.error("Error while embedding text with OpenAI")
                return None
            
            return response.data[0].embedding
        
        except Exception as e:
            self.logger.error(f"Error embedding text with OpenAI: {str(e)}")
            return None
        
        
    async def summarize(self, text: str):
        if self.summary_model_id is None:
            self.logger.error("Summary model ID is not set.")
            return None

        if self.client is None:
            self.logger.error("OpenAI client is not initialized.")
            return None
        
        try:
            messages = [
                {"role": OpenAIEnums.SYSTEM.value, "content": "Summarize the following text concisely while maintaining the key information:"},
                {"role": OpenAIEnums.USER.value, "content": self.process_text(text)}
            ]
            
            response = self.client.chat.completions.create(
                model=self.summary_model_id,
                messages=messages,
                max_tokens=self.default_generation_max_output_tokens,
                temperature=0.3  # Lower temperature for more focused summarization
            )

            if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
                self.logger.error("Error while summarizing text with OpenAI")
                return None
            
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error summarizing text with OpenAI: {str(e)}")
            return None
    

    def construct_prompt(self, prompt: str, role: str):
        return [{
            "role": role,
            "content": prompt
        }]