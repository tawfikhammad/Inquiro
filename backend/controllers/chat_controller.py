from .base_controller import BaseController
from AI.LLM import LLMProviderFactory, LLMModel
from fastapi import HTTPException
import logging

logger = logging.getLogger("unicorn.errors")

class ChatController(BaseController):
    def __init__(self):
        super().__init__()
        self.llm_provider = LLMProviderFactory(self.app_settings).create(LLMModel.COHERE.value)  # Or use from config/env

    async def chat(self, prompt: str, chat_history: list = []):
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required.")
        
        try:
            response = await self.llm_provider.generate(prompt=prompt, chat_history=chat_history)
            return response
        except Exception as e:
            logger.error(f"Chat generation error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error.")
