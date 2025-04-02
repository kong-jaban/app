import sys
from PySide6.QtWidgets import QApplication
from frontend.login_window import LoginWindow
from frontend.project_window import ProjectWindow

def main():
    app = QApplication(sys.argv)
    project_window = ProjectWindow()
    login_window = LoginWindow(project_window)
    login_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
