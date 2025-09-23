from langchain_community.document_loaders import PyMuPDFLoader
from pathlib import Path
class PDFUtils:
    @staticmethod
    async def get_pdf_content(file_path):

        try:
            loader = PyMuPDFLoader(file_path, extract_tables="markdown")
            documents = loader.load()
            raw_text = []
            for doc in documents:
                raw_text.append(doc.page_content)
            raw_text = "\n".join(raw_text)

            txt_path = Path(file_path).with_suffix(".txt")
            txt_path.write_text(raw_text, encoding="utf-8")

            return documents
        except Exception as e:
            raise