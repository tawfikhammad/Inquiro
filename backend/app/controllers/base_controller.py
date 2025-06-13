from config import app_settings, AppSettings

class BaseController:

    def __init__(self):
        self.app_settings = app_settings()