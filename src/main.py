from views.welcome_view import WelcomeUI
from config import app_settings, AppSettings

def main():
    settings = app_settings()
    welcome_ui = WelcomeUI(settings)
    welcome_ui.show()

if __name__ == "__main__":
    main()
