from .base_controller import BaseController
from fastapi import UploadFile
from utils.enums import ResponseSignals
from utils import PathUtils
import os
import re

class PaperController(BaseController):
    def __init__(self):
        super().__init__()
        self.path_utils = PathUtils()

    def validfile(self, file: UploadFile):
        if file.content_type not in self.app_settings.ALLOWWED_FILE_TYPES:
            return False, ResponseSignals.INVALID_FILE_TYPE.value
        
        if file.size > self.app_settings.MAX_FILE_SIZE:
            return False, ResponseSignals.INVALED_FILE_SIZE.value
        
        return True, ResponseSignals.SUCCESS_UPLOAD.value
    

    def paper_path(self, project_title: str, paper_name: str):
        cleaned_filename = self.clean_name(paper_name)
        paper_filename = f'{cleaned_filename}.pdf'
        
        file_path = self.path_utils.get_file_path(project_title=project_title, file_name=paper_filename)
        return file_path, cleaned_filename

    def clean_name(self, filename: str):
        cleaned_filename = re.sub(r"[^\w.]", "", filename)
        cleaned_filename = os.path.splitext(cleaned_filename)[0]
        return cleaned_filename