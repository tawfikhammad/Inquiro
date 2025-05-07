import pymupdf 
import io
import logging

logger = logging.getLogger('unicorn.errors')

class PDFUtils:
    @staticmethod
    def extract_text_from_pdf(file_path):

        try:
            doc = pymupdf.open(file_path) 
            text = ""
            for page in doc: 
                text += page.get_text() 
            return text
        
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return "Error extracting text from PDF"