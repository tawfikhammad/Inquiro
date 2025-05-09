from .base_controller import BaseController
from AI.LLM import LLMProviderFactory, LLMModel
from fastapi import UploadFile
from utils.enums import ResponseSignals
from utils import PathUtils, PDFUtils
import os
import re

class SummaryController(BaseController):
    def __init__(self):
        super().__init__()
        self.path_utils = PathUtils()
        self.llm_provider = LLMProviderFactory(self.app_settings).create(LLMModel.COHERE.value)
    
    async def generate_summary(self, paper_path, paper_name):
        extracted_text = PDFUtils.extract_text_from_pdf(paper_path)

        summary_content = await self.llm_provider.summarize(extracted_text)
        if summary_content is None:
            return ResponseSignals.SUMMARY_GENERATION_FAILED.value
        return summary_content
    
    def save_summary(self, summary_path, summary_content):        
        os.makedirs(os.path.dirname(summary_path), exist_ok=True)
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)
            
    def summary_path(self, project_title, paper_name):
        cleaned_filename = f'{self.clean_name(paper_name)}_summary'
        summary_filename = f'{cleaned_filename}.md'
        
        summary_path = self.path_utils.get_summary_path(project_title=project_title, file_name=summary_filename)
        return summary_path, cleaned_filename
    
    def clean_name(self, filename):
        cleaned_filename = re.sub(r"[^\w.]", "", filename)
        cleaned_filename = os.path.splitext(cleaned_filename)[0]
        return cleaned_filename