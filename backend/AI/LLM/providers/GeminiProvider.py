from ..LLMInterface import LLMInterface
from ..LLMEnums import GeminiEnums, DocumentTypeEnum
import google.generativeai as genai
import logging


class GeminiProvider(LLMInterface):
    def __init__(self, api_key: str,
                 default_max_input_characters: int=1000,
                 default_generation_max_output_tokens: int=1000,
                 default_generation_temperature: float=0.7):
        
        self.api_key = api_key
        
        self.default_max_input_characters = default_max_input_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature
        
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        self.summary_model_id = None
        
        genai.configure(api_key=self.api_key)
        
        self.logger = logging.getLogger(__name__)
    
    async def set_generation_model(self, generation_model_id: str):
        self.generation_model_id = generation_model_id
    
    async def set_embedding_model(self, embedding_model_id: str, embedding_size: int):
        self.embedding_model_id = embedding_model_id
        self.embedding_size = embedding_size
    
    async def set_summary_model(self, summary_model_id: str):
        self.summary_model_id = summary_model_id
    
    def process_text(self, text: str):
        return text[:self.default_max_input_characters].strip()
    
    async def generate(self, prompt: str, chat_history: list=[], max_output_tokens: int=None, temperature: float=None):
        if not self.generation_model_id:
            self.logger.error("Generation model for Gemini was not set")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature
        
        try:
            model = genai.GenerativeModel(model_name=self.generation_model_id)
            
            chat_history.append({self.construct_prompt(prompt, GeminiEnums.USER.value)})

            chat = model.start_chat(history=chat_history)
            response = chat.send_message(
                self.process_text(prompt),
                generation_config={
                    'max_output_tokens': max_output_tokens,
                    'temperature': temperature})
            
            if not response or not response.text:
                self.logger.error("Error while generating text with Gemini")
                return None
            
            return response.text
        
        except Exception as e:
            self.logger.error(f"Error generating text with Gemini: {str(e)}")
            return None
    
    async def embed(self, text: str, document_type: str = None):
        if not self.embedding_model_id:
            self.logger.error("Embedding model for Gemini was not set")
            return None
        
        try:
            task_type= GeminiEnums.DOCUMENT.value
            if document_type == DocumentTypeEnum.QUERY.value:
                task_type= GeminiEnums.QUERY.value
            
            embeddings= genai.embed_content(
                model= self.embedding_model_id,
                content= self.process_text(text),
                task_type= task_type)
            
            if not embeddings or not embeddings.embedding:
                self.logger.error("Error while embedding text with Gemini")
                return None
            
            return embeddings.embedding
        
        except Exception as e:
            self.logger.error(f"Error embedding text with Gemini: {str(e)}")
            return None
    
    async def summarize(self, text: str):
        model_id = self.summary_model_id if self.summary_model_id else self.generation_model_id
        
        if not model_id:
            self.logger.error("No model set for summarization with Gemini")
            return None
        
        try:
            model = genai.GenerativeModel(model_name=model_id)
            
            summarization_prompt = f"Please summarize the following text concisely while maintaining key information: {self.process_text(text)}"
            
            response = model.generate_content(
                summarization_prompt,
                generation_config={
                    'max_output_tokens': self.default_generation_max_output_tokens,
                    'temperature': 0.3}
                    )
            
            if not response or not response.text:
                self.logger.error("Error while summarizing text with Gemini")
                return None
            
            return response.text
        
        except Exception as e:
            self.logger.error(f"Error summarizing text with Gemini: {str(e)}")
            return None
    
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "parts": [self.process_text(prompt)]
        }