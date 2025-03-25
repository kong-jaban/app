from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, QListWidget, QComboBox, QSpinBox, QLineEdit, QLabel
import sys
import shutil
import os
from data_loader import load_csv, save_csv
from anonymizer import anonymize_data
from visualizer import plot_distribution
from project_manager import create_project, list_projects, get_project_path

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("프로젝트 관리")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        
        self.projectInput = QLineEdit()
        self.projectInput.setPlaceholderText("프로젝트 이름 입력")
        layout.addWidget(self.projectInput)
        
        self.createProjectButton = QPushButton("프로젝트 생성")
        self.createProjectButton.clicked.connect(self.createProject)
        layout.addWidget(self.createProjectButton)
        
        self.projectList = QListWidget()
        self.projectList.itemClicked.connect(self.selectProject)
        layout.addWidget(self.projectList)
        
        self.loadProjects()
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def createProject(self):
        project_name = self.projectInput.text().strip()
        if project_name:
            create_project(project_name)
            self.loadProjects()
    
    def loadProjects(self):
        self.projectList.clear()
        self.projectList.addItems(list_projects())
    
    def selectProject(self, item):
        project_name = item.text()
        self.projectWindow = ProjectWindow(project_name)
        self.projectWindow.show()

class ProjectWindow(QMainWindow):
    def __init__(self, project_name):
        super().__init__()
        self.setWindowTitle(f"프로젝트: {project_name}")
        self.setGeometry(200, 200, 800, 600)
        self.project_name = project_name
        self.df = None
        
        layout = QVBoxLayout()
        
        self.loadButton = QPushButton("CSV 파일 불러오기")
        self.loadButton.clicked.connect(self.loadFile)
        layout.addWidget(self.loadButton)
        
        self.tableWidget = QTableWidget()
        layout.addWidget(self.tableWidget)
        
        self.anonymizeButton = QPushButton("비식별 처리 실행")
        self.anonymizeButton.clicked.connect(self.applyAnonymization)
        layout.addWidget(self.anonymizeButton)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def loadFile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "CSV 파일 선택", "", "CSV Files (*.csv)")
        if file_path:
            project_path = get_project_path(self.project_name)
            saved_path = os.path.join(project_path, "data.csv")
            shutil.copy(file_path, saved_path)
            self.df = load_csv(saved_path)
            self.displayData(self.df)
    
    def displayData(self, df):
        sample_df = df.head(10)  # .compute() 제거
        self.tableWidget.setRowCount(sample_df.shape[0])
        self.tableWidget.setColumnCount(sample_df.shape[1])
        self.tableWidget.setHorizontalHeaderLabels(sample_df.columns.tolist())

        for row_idx, row in sample_df.iterrows():
            for col_idx, value in enumerate(row):
                self.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def applyAnonymization(self):
        if self.df is not None:
            self.df = anonymize_data(self.df)
            save_csv(self.df, os.path.join(get_project_path(self.project_name), "anonymized.csv"))
            self.displayData(self.df)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())