import os
import customtkinter

class WelcomeView(customtkinter.CTk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Welcome - Inquiro")
        self.geometry("600x550")
        self.setup_ui()

    def setup_ui(self):
        # Title
        self.label = customtkinter.CTkLabel(self, text="Welcome to Inquiro", font=("Arial", 26))
        self.label.pack(pady=20)

        # Load Existing Project Section
        self.load_label = customtkinter.CTkLabel(self, text="Load Existing Project", font=("Arial", 18))
        self.load_label.pack(pady=(10, 5))

        self.project_listbox = customtkinter.CTkComboBox(
            self, 
            values=[p["project_name"] for p in self.controller.project_info_list],
            width=300
        )
        self.project_listbox.pack(pady=10)

        load_button = customtkinter.CTkButton(self, text="Load Project", command=self.load_project)
        load_button.pack(pady=10)

        # OR Separator
        self.or_label = customtkinter.CTkLabel(self, text="─ OR ─", font=("Arial", 14))
        self.or_label.pack(pady=20)

        # Create New Project Section
        self.create_label = customtkinter.CTkLabel(self, text="Create New Project", font=("Arial", 18))
        self.create_label.pack(pady=(10, 5))

        self.project_name_entry = customtkinter.CTkEntry(self, placeholder_text="Enter project name", width=300)
        self.project_name_entry.pack(pady=10)

        self.project_path_entry = customtkinter.CTkEntry(self, placeholder_text="Enter project path (optional)", width=300)
        self.project_path_entry.pack(pady=10)

        create_button = customtkinter.CTkButton(self, text="Create Project", command=self.create_project)
        create_button.pack(pady=10)

    def load_project(self):
        selected_project = self.project_listbox.get()
        if selected_project:
            self.controller.load_project(selected_project)

    def create_project(self):
        name = self.project_name_entry.get()
        path = self.project_path_entry.get() or os.getcwd()
        if name:
            self.controller.create_new_project(name, path)

    def show(self):
        self.mainloop()
