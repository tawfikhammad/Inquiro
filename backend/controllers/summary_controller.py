from .base_controller import BaseController
import aiofiles
import os, re
from utils import get_logger
logger = get_logger(__name__)
class SummaryController(BaseController):
    def __init__(self, summary_client, template_parser):
        super().__init__()

        self.summary_client = summary_client
        self.template_parser = template_parser
    
    async def generate_summary(self, paper_text, paper_name):
        try:
            logger.info("get prompts for summary generation")
            system_prompt = self.template_parser.get("summarizer", "system_prompt")
            documents_prompts = self.template_parser.get("summarizer", "document_prompt", {"extracted_text":paper_text})
            footer_prompt = self.template_parser.get("summarizer", "footer_prompt")

            full_prompt = "\n\n".join([documents_prompts, footer_prompt])

            summary_content = await self.summary_client.summarize_text(
                user_prompt=full_prompt,
                system_prompt=system_prompt,
                temperature=0.2
            )
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