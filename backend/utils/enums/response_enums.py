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

    # Paper Responses
    PAPER_NOT_FOUND = "Paper Not Found"
    # Project Responses
    PROJECT_CREATED_SUCCESS = 'Project Created Successfully'
    PROJECT_UPDATED_SUCCESS = 'Project Updated Successfully'
    PROJECT_NOT_FOUND = 'Project Not Found'
    PROJECT_CREATION_FAILED = 'Failed to Create Project'
    #Vector DB Responses
    VDB_CONNECTION_ERROR = 'Failed to Connect to Vector DB'
    VDB_INSERT_ERROR = 'Failed to Insert Into Vector DB'
    VDB_INSERT_SUCCESS = 'Inserted Into Vector DB Successfully'
    VDB_COLLECTION_RETRIEVED = 'Vector DB Collection Retrieved Successfully'
    VDB_SEARCH_ERROR = 'Failed to Search Vector DB'
    VDB_SEARCH_SUCCESS = 'Vector DB Search Successful'
    VDB_UNSUPPORTED_PROVIDER = 'Unsupported Vector DB Provider'

    #RAG Responses
    RAG_ANSWER_ERROR = 'Failed to Generate Answer'
    RAG_ANSWER_SUCCESS = 'Answer Generated Successfully'
