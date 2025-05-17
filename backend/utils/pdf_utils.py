from langchain_community.document_loaders import PyMuPDFLoader
import io
import logging

logger = logging.getLogger('unicorn.errors')

class PDFUtils:
    @staticmethod
    def get_pdf_content(file_path):

        try:
            loader = PyMuPDFLoader(file_path)
            return loader.load()
        
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return None