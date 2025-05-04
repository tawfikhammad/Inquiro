from .base_controller import BaseController
from fastapi import UploadFile
from utils.enums import ResponseSignals
from utils import PathUtils
import os
import re

class DataController(BaseController):
    def __init__(self):
        super().__init__()

    def validfile(self, file: UploadFile):
        if file.content_type not in self.app_settings.ALLOWWED_FILE_TYPES:
            return False, ResponseSignals.INVALID_FILE_TYPE.value
        
        if file.size > self.app_settings.MAX_FILE_SIZE:
            return False, ResponseSignals.INVALED_FILE_SIZE.value
        
        return True, ResponseSignals.SUCCESS_UPLOAD.value
    

    def file_path(self, project_title: str, filename: str):
        clean_filename = self.clean_name(filename)
        
        path_utils = PathUtils()
        file_path = path_utils.get_file_path(project_title=project_title, file_name=clean_filename)
        return file_path, clean_filename
    
    def summary_path(self, project_title: str, filename: str):
        clean_filename = self.clean_name(filename)
        
        path_utils = PathUtils()
        summary_path = path_utils.get_summary_path(project_title=project_title, file_name=clean_filename)
        return summary_path, clean_filename
    
    def clean_name(self, name: str):

        # Remove special chars
        clean_name = re.sub(r"[^\w.]", "", name)
        return clean_name