from utils import get_settings, AppSettings

class BaseController:

    def __init__(self):
        self.app_settings = get_settings()