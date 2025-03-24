from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, QListWidget, QComboBox, QSpinBox, QLineEdit
import sys
from data_loader import load_csv
from anonymizer import anonymize_data
from visualizer import plot_distribution
from project_manager import create_project, list_projects
import matplotlib
matplotlib.use("QtAgg")  # Qt 기반 백엔드 명확히 지정

class DataAnonymizerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        self.projectInput = QLineEdit()
        self.projectInput.setPlaceholderText("프로젝트 이름 입력")
        layout.addWidget(self.projectInput)
        
        self.createProjectButton = QPushButton("프로젝트 생성")
        self.createProjectButton.clicked.connect(self.createProject)
        layout.addWidget(self.createProjectButton)
        
        self.projectList = QListWidget()
        layout.addWidget(self.projectList)
        self.loadProjects()
        
        self.loadButton = QPushButton("CSV 파일 불러오기")
        self.loadButton.clicked.connect(self.loadFile)
        layout.addWidget(self.loadButton)
        
        self.columnList = QListWidget()
        self.columnList.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.columnList)
        
        self.binColumnCombo = QComboBox()
        layout.addWidget(self.binColumnCombo)
        
        self.binSizeSpin = QSpinBox()
        self.binSizeSpin.setMinimum(2)
        self.binSizeSpin.setMaximum(100)
        layout.addWidget(self.binSizeSpin)
        
        self.anonymizeButton = QPushButton("비식별 처리 실행")
        self.anonymizeButton.clicked.connect(self.applyAnonymization)
        layout.addWidget(self.anonymizeButton)
        
        self.plotButton = QPushButton("데이터 분포 확인")
        self.plotButton.clicked.connect(self.plotDataDistribution)
        layout.addWidget(self.plotButton)
        
        self.tableWidget = QTableWidget()
        layout.addWidget(self.tableWidget)
        
        self.setLayout(layout)
        self.setWindowTitle("Dask 기반 데이터 비식별화")
        self.resize(800, 600)
    
    def createProject(self):
        project_name = self.projectInput.text().strip()
        if project_name:
            create_project(project_name)
            self.loadProjects()
    
    def loadProjects(self):
        self.projectList.clear()
        self.projectList.addItems(list_projects())
    
    def loadFile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "CSV 파일 선택", "", "CSV Files (*.csv)")
        if file_path:
            self.df = load_csv(file_path)
            self.displayData(self.df)
            self.populateColumns()
    
    def displayData(self, df):
        sample_df = df.head(10).compute()
        self.tableWidget.setRowCount(sample_df.shape[0])
        self.tableWidget.setColumnCount(sample_df.shape[1])
        self.tableWidget.setHorizontalHeaderLabels(sample_df.columns.tolist())
        
        for row_idx, row in sample_df.iterrows():
            for col_idx, value in enumerate(row):
                self.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
    
    def populateColumns(self):
        self.columnList.clear()
        self.binColumnCombo.clear()
        
        if hasattr(self, 'df'):
            columns = self.df.columns.tolist()
            self.columnList.addItems(columns)
            self.binColumnCombo.addItems(columns)
    
    def applyAnonymization(self):
        if hasattr(self, 'df'):
            selected_columns = [item.text() for item in self.columnList.selectedItems()]
            bin_column = self.binColumnCombo.currentText()
            bin_size = self.binSizeSpin.value()
            
            self.df = anonymize_data(self.df, drop_columns=selected_columns, bin_columns=[bin_column], bin_sizes={bin_column: bin_size})
            self.displayData(self.df)
    
    def plotDataDistribution(self):
        if hasattr(self, 'df'):
            selected_column = self.binColumnCombo.currentText()
            plot_distribution(self.df, selected_column, f"{selected_column} 컬럼 데이터 분포")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DataAnonymizerApp()
    window.show()
    sys.exit(app.exec())
