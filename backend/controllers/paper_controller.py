from langchain_text_splitters import RecursiveCharacterTextSplitter
from .base_controller import BaseController
from utils import PDFUtils
from fastapi import UploadFile
from utils.enums import ResponseSignals
from utils import get_logger
logger = get_logger(__name__)
import os
import re

class PaperController(BaseController):
    def __init__(self):
        super().__init__()

    async def validfile(self, file: UploadFile):
        if file.content_type not in self.app_settings.ALLOWED_FILE_TYPES:
            return False, ResponseSignals.INVALID_FILE_TYPE.value
        
        if file.size > self.app_settings.MAX_FILE_SIZE:
            return False, ResponseSignals.INVALID_FILE_SIZE.value
        
        return True, ResponseSignals.VALID_FILE.value

    async def paper_path(self, project_title: str, paper_name: str):
        cleaned_filename = await self.clean_name(paper_name)
        paper_filename = f'{cleaned_filename}.pdf'
        file_path = self.path_utils.get_file_path(project_title, paper_filename)
        return file_path, cleaned_filename

    async def clean_name(self, filename: str):
        cleaned_filename = re.sub(r"[^\w.]", "", filename)
        cleaned_filename = os.path.splitext(cleaned_filename)[0]
        return cleaned_filename
    
    async def get_chunks(self, project_title: str, paper_name: str, chunk_size: int=1000, chunk_overlap: int=150):
        try:
            paper_filename = f'{paper_name}.pdf'
            paper_path = self.path_utils.get_file_path(project_title, paper_filename)
            paper_content = await PDFUtils.get_pdf_content(paper_path)
            if not paper_content:
                logger.warning(f"No content extracted from PDF: {paper_name} in project {project_title}")
                return []
            
            text = [reg.page_content for reg in paper_content]
            metadata =  [
                {"project_title": project_title, "paper_name": paper_name, "page": reg.metadata['page'], "total_pages": len(paper_content)}
                for reg in paper_content
            ]

            splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len)
            chunks = splitter.create_documents(text, metadatas=metadata)
            if not chunks or len(chunks) == 0:
                logger.warning(f"No chunks created for paper: {paper_name} in project {project_title}")
                return []
            
            logger.info(f"Generated {len(chunks)} chunks for paper '{paper_name}'")
            return chunks
        except Exception as e:
            logger.error(f"Error generating chunks for paper '{paper_name}': {e}")
            raise