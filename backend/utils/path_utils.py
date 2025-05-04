import os
from pathlib import Path

class PathUtils:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.assets_dir = self.base_dir / "assets"
        self.library_dir = self.assets_dir / "library"
        
        # Ensure base directories exist
        os.makedirs(self.assets_dir, exist_ok=True)
        os.makedirs(self.library_dir, exist_ok=True)

    def get_project_dir(self, project_title: str):
        
        project_dir = self.library_dir / project_title
        papers_dir = project_dir / "papers"
        summaries_dir = project_dir / "summaries"

        os.makedirs(project_dir, exist_ok=True)
        os.makedirs(papers_dir, exist_ok=True)
        os.makedirs(summaries_dir, exist_ok=True)
        
        return project_dir, papers_dir, summaries_dir
    

    def get_file_path(self, project_title: str, file_name: str) -> Path:
        """Get path for a paper file"""
        project_dir, papers_dir, _ = self.get_project_dir(project_title=project_title)
        return papers_dir / file_name
    
    def get_summary_path(self, project_title: str, file_name: str) -> Path:
        """Get path for a summary file"""
        project_dir, _, summaries_dir = self.get_project_dir(project_title=project_title)
        
        # Ensure the filename ends with .md for summaries
        if not file_name.lower().endswith('.md'):
            file_name = os.path.splitext(file_name)[0] + '.md'
            
        return summaries_dir / file_name
        
        
    def get_project_files(self, project_title: str):
        """Get all files in a project directory"""
        _, papers_dir, summaries_dir = self.get_project_dir(project_title)
        
        paper_files = [f.name for f in papers_dir.glob('*') if f.is_file()]
        summary_files = [f.name for f in summaries_dir.glob('*') if f.is_file()]
        
        return paper_files, summary_files