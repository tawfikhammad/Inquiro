from abc import ABC, abstractmethod

class LLMInterface(ABC):

    @abstractmethod
    async def set_genration_model(self, genration_model_id: str ):
        pass

    @abstractmethod
    async def set_embedding_model(self, embedding_model_id: str, embedding_size: int):
        pass

    @abstractmethod
    async def set_summary_model(self, summary_model_id: str):
        pass

    @abstractmethod
    async def generate(self, prompt: str, chat_history: list=[], max_output_tokens: int=None,
                            temperature: float = None):
        pass

    @abstractmethod
    async def embed(self, text: str, document_type: str = None):
        pass

    @abstractmethod
    async def summarize(self, text: str):
        pass

    @abstractmethod
    def construct_prompt(self, prompt: str, role: str):
        pass
