from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QMessageBox
from backend.project_manager import list_projects, create_project
from frontend.main_window import MainWindow

class ProjectWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Project")
        self.layout = QVBoxLayout(self)

        self.project_list = QListWidget()
        self.layout.addWidget(self.project_list)

        self.load_projects()

        self.new_project_button = QPushButton("New Project")
        self.new_project_button.clicked.connect(self.create_project)
        self.layout.addWidget(self.new_project_button)

        self.open_project_button = QPushButton("Open Project")
        self.open_project_button.clicked.connect(self.open_project)
        self.layout.addWidget(self.open_project_button)

    def load_projects(self):
        self.project_list.clear()
        for project in list_projects():
            self.project_list.addItem(project)

    def create_project(self):
        project_name, ok = QMessageBox.getText(self, "Create Project", "Enter project name:")
        if ok and project_name:
            if create_project(project_name):
                self.load_projects()
            else:
                QMessageBox.warning(self, "Error", "Project already exists!")

    def open_project(self):
        selected_item = self.project_list.currentItem()
        if selected_item:
            project_name = selected_item.text()
            self.main_window = MainWindow(project_name)
            self.main_window.show()
            self.close()
