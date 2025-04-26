from models import ProjectModel
from views import MainView

class MainController:
    def __init__(self, project_info):
        self.project_info = project_info
        self.project_model = ProjectModel(project_name=project_info["project_name"], project_path=project_info["project_path"])
        self.config = self.project_model.load_project_config()

        self.view = MainView(controller=self)
        self.view.show()

    def get_theme(self):
        return self.config.get("theme", "Dark")

    def get_project_path(self):
        return self.project_info["project_path"]
