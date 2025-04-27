from models.project_model import ProjectModel
from views.welcome_view import WelcomeView

class WelcomeController:
    def __init__(self):
        self.project_info_list = ProjectModel.load_projects_info()
        self.view = WelcomeView(controller=self)
        self.view.show()

    def create_new_project(self, project_name, project_path):
        project = ProjectModel(project_name=project_name, project_path=project_path)
        project.save_project_info(self.project_info_list)
        print(f"Project {project_name} created at {project_path}")

    def load_project(self, selected_project_name):
        project = next((p for p in self.project_info_list if p["project_name"] == selected_project_name), None)
        if project:
            print(f"Loading project {project['project_name']}")
