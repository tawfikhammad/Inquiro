from enum import Enum

class ResponseSignals(Enum):
    SUCCESS_UPLOAD = 'File Uploaded Successfully'
    FAILED_UPLOAD = 'Failed to Upload File'
    INVALID_FILE_TYPE = 'Invalid File Type'
    INVALED_FILE_SIZE = 'File Size Too Large'
    FAILED_PROCESS_FILE = 'Failed to Process File'
    SUCCESS_PROCESS_FILE = 'File Processed Successfully'
    SUCCESS_PROCESS = 'Processing Successful'
    FAILED_PROCESS = 'Processing Failed'
    NO_ATTACHED_FILES = 'No Attached Files'
    FILE_NOT_FOUND = 'No File Found With the ID'

