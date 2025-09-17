from .base_controller import BaseController
from AI.LLM import LLMProviderFactory, LLMModel
from fastapi import UploadFile
from utils.enums import ResponseSignals
from utils import PathUtils, PDFUtils
from fastapi import HTTPException
import aiofiles
import os
import re

import logging
logger = logging.getLogger('unicorn.errors')

class SummaryController(BaseController):
    def __init__(self, summary_client):
        super().__init__()
        self.path_utils = PathUtils()
        self.summary_client = summary_client
    
    async def generate_summary(self, paper_path, paper_name):
        try:
            paper_content = PDFUtils.get_pdf_content(paper_path)
            extracted_text = "\n\n".join([reg.page_content for reg in paper_content])

            summary_content = await self.summary_client.summarize(extracted_text)
            if not summary_content:
                logger.warning(f"Summary generation failed for paper: {paper_name}")
                raise
            logger.info(f"Generated summary for {paper_name}")
            return summary_content
        except Exception as e:
            logger.error(f"Error generating summary for {paper_name}: {e}")
            raise
        
    async def save_summary(self, summary_path, summary_content):        
        try:
            os.makedirs(os.path.dirname(summary_path), exist_ok=True)
            async with aiofiles.open(summary_path, 'w', encoding='utf-8') as f:
                await f.write(summary_content)
                logger.info(f"Summary saved to {summary_path}")
        except Exception as e:
            logger.error(f"Error saving summary to {summary_path}: {e}")
            raise   
            
    async def summary_path(self, project_title, paper_name):
        cleaned_filename = f'{await self.clean_name(paper_name)}_summary'
        summary_filename = f'{cleaned_filename}.md'
        
        summary_path = self.path_utils.get_summary_path(project_title, summary_filename)
        return summary_path, cleaned_filename
    
    async def clean_name(self, filename):
        cleaned_filename = re.sub(r"[^\w.]", "", filename)
        cleaned_filename = os.path.splitext(cleaned_filename)[0]
        return cleaned_filename