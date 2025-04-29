from enum import Enum

class WelcomeTheme(Enum):
    WINDOW_SIZE = "600x550"
    WINDOW_TITLE = "Welcome to Inquiro"
    TITLE_FONT = ("Arial", 26)


class MainTheme(Enum):
    WINDOW_SIZE = "1400x800"
    BW_COLOR = "white"


class LibraryTheme(Enum):
    WINDOW_SIZE = "400x800"
    TITLE = "Library"
    FONT = ("Helvetica", 20, "bold")


class LightTheme(Enum):
    BG_COLOR = "#FFFFFF"
    FRAME_COLOR = "#FFFAFA"
    TEXT_COLOR = "#000000"
    HEADING_COLOR = "#78586f"
    BUTTON_COLOR = "#7F8DAD"
    BUTTON_HOVER_COLOR = "#7F8CAC"

class DarkTheme(Enum):
    BG_COLOR = "#1e1e1e"
    FRAME_COLOR = "#151515"
    TEXT_COLOR = "#FFFFFF"
    HEADING_COLOR = "#6C7BFE"
    BUTTON_COLOR = "#6C7BFE"
    BUTTON_HOVER_COLOR = "#7F8DAD"

class TokyoCityDarkerTheme(Enum):
    BG_COLOR = "#181C24"
    FRAME_COLOR = "#181C24"
    TEXT_COLOR = "#FFFFFF"
    HEADING_COLOR = "#e45e91"
    BUTTON_COLOR = "#14a5ae"
    BUTTON_HOVER_COLOR = "#7F8DAD"
 

