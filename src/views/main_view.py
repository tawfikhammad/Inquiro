import customtkinter
from tkinter import PanedWindow, HORIZONTAL, BOTH
from views import LibraryView, ChatView, PdfViewerView

class MainView(customtkinter.CTk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("")  # اسم المشروع اللي اخترناه
        self.geometry("1400x800")
        self.resizable(width=True, height=True)
        self.setup_layout()

    def setup_layout(self):
        paned_window = PanedWindow(
            self, orient=HORIZONTAL, bg="white"
        )
        paned_window.pack(fill=BOTH, expand=1)

        # Left, Center, Right frames
        self.library_frame = customtkinter.CTkFrame(paned_window, width=400, corner_radius=0)
        self.content_frame = customtkinter.CTkFrame(paned_window, width=700, corner_radius=0)
        self.chat_frame = customtkinter.CTkFrame(paned_window, width=300, corner_radius=0)

        paned_window.add(self.library_frame, minsize=400)
        paned_window.add(self.content_frame, minsize=700)
        paned_window.add(self.chat_frame, minsize=300)

        # Load Views
        self.library_view = LibraryView(self.library_frame, self.controller)
        self.content_view = PdfViewerView(self.content_frame)
        self.chat_view = ChatView(self.chat_frame, self.controller)

    def show(self):
        self.mainloop()
