from langchain_community.document_loaders import PyMuPDFLoader
from utils import get_logger
logger = get_logger(__name__)
class PDFUtils:
    @staticmethod
    async def get_pdf_content(file_path):

        try:
            loader = PyMuPDFLoader(file_path)
            return await loader.load()
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise