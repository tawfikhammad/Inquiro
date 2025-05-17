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
    NO_ATTACHED_FILE = 'No Attached File'
    FILE_NOT_FOUND = 'No File Found With the ID'
    SUMMARY_GENERATION_FAILED = 'Failed to Generate Summary'
    SUMMARY_GENERATION_SUCCESS = 'Summary Generated Successfully'
    PAPER_EXISTS = 'Paper Already Exists'

