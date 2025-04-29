import os
import json
from pathlib import Path


class ProjectModel:
    def __init__(self, project_name, project_path=None):
        self.project_name = project_name
        self.project_path = project_path

    def save_project_info(self, project_info_list, file_path="src/assets/projects.json"):
        project_names = {project["project_name"] for project in project_info_list}

        if self.project_name not in project_names:
            project_info_list.append({
                "project_name": self.project_name,
                "project_path": self.project_path
            })

        with open(file_path, "w") as f:
            json.dump(project_info_list, f, indent=4)

    @staticmethod
    def load_projects_info(file_path="src/assets/projects.json"):
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            with open(file_path, "w") as f:
                json.dump([], f)
            return []

        with open(file_path, "r") as f:
            return json.load(f)
        
    def load_project_config(self):
        config_path = os.path.join(self.project_path, "src/assets/project_config.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f).get("config", {})
        return {}
