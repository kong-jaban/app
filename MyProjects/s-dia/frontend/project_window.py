import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QListWidget, QHBoxLayout, QFileDialog, QInputDialog, QMessageBox
)
from frontend.main_window import MainWindow
from PySide6.QtCore import QFileInfo

PROJECTS_DIR = os.path.join(os.path.dirname(__file__), "..", "projects")

class ProjectWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("프로젝트 선택")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()

        # 프로젝트 목록
        self.project_list = QListWidget()
        self.load_projects()
        layout.addWidget(self.project_list)

        # 버튼 영역
        button_layout = QHBoxLayout()
        self.new_project_btn = QPushButton("새 프로젝트")
        self.open_project_btn = QPushButton("열기")
        button_layout.addWidget(self.new_project_btn)
        button_layout.addWidget(self.open_project_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.new_project_btn.clicked.connect(self.create_new_project)
        self.open_project_btn.clicked.connect(self.open_selected_project)

    def load_projects(self):
        self.project_list.clear()
        if not os.path.exists(PROJECTS_DIR):
            os.makedirs(PROJECTS_DIR)
        for name in os.listdir(PROJECTS_DIR):
            if os.path.isdir(os.path.join(PROJECTS_DIR, name)):
                self.project_list.addItem(name)

    def create_new_project(self):
        name, ok = QInputDialog.getText(self, "새 프로젝트", "프로젝트 이름:")
        if ok and name:
            folder = os.path.join(PROJECTS_DIR, name)
            if os.path.exists(folder):
                QMessageBox.warning(self, "오류", "이미 존재하는 프로젝트입니다.")
                return
            os.makedirs(folder)

            # CSV 선택
            file_path, _ = QFileDialog.getOpenFileName(self, "CSV 파일 선택", "", "CSV Files (*.csv)")
            if not file_path:
                return

            dest_csv = os.path.join(folder, "data.csv")
            QFileInfo(file_path).absoluteFilePath()
            with open(file_path, "rb") as src, open(dest_csv, "wb") as dst:
                dst.write(src.read())

            self.load_projects()

    def open_selected_project(self):
        selected_items = self.project_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "오류", "프로젝트를 선택해주세요.")
            return

        project_name = selected_items[0].text()
        project_path = os.path.join(PROJECTS_DIR, project_name)
        csv_path = os.path.join(project_path, "data.csv")

        if not os.path.exists(csv_path):
            QMessageBox.warning(self, "오류", "CSV 파일이 존재하지 않습니다.")
            return

        self.main_window = MainWindow(project_path, csv_path)
        self.main_window.show()
        self.close()
