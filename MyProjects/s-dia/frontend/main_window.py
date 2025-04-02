from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QCheckBox, QLabel, QFileDialog, QMessageBox
import dask.dataframe as dd
from backend.data_processor import anonymize_columns
from backend.project_manager import get_project_csv_path, save_processed_data

class MainWindow(QWidget):
    def __init__(self, project_name):
        super().__init__()
        self.setWindowTitle(f"Data Processing - {project_name}")
        self.project_name = project_name
        self.layout = QVBoxLayout(self)

        self.load_button = QPushButton("Load CSV")
        self.load_button.clicked.connect(self.load_csv)
        self.layout.addWidget(self.load_button)

        self.label = QLabel("Select columns to anonymize:")
        self.layout.addWidget(self.label)

        self.checkboxes = {}
        self.process_button = QPushButton("Anonymize Data")
        self.process_button.clicked.connect(self.process_data)
        self.layout.addWidget(self.process_button)

        self.df = None
        self.csv_path = get_project_csv_path(self.project_name)

        # 프로젝트에 기존 CSV가 있으면 로드
        self.load_existing_csv()

    def load_existing_csv(self):
        if os.path.exists(self.csv_path):
            self.df = dd.read_csv(self.csv_path)
            self.update_checkboxes(self.df.columns)

    def load_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.df = dd.read_csv(file_path)
            self.df.to_csv(self.csv_path, single_file=True, index=False)
            self.update_checkboxes(self.df.columns)
            QMessageBox.information(self, "Success", "CSV file loaded and saved to project.")

    def update_checkboxes(self, columns):
        for checkbox in self.checkboxes.values():
            self.layout.removeWidget(checkbox)
            checkbox.deleteLater()
        self.checkboxes.clear()

        for col in columns:
            checkbox = QCheckBox(col)
            self.checkboxes[col] = checkbox
            self.layout.addWidget(checkbox)

    def process_data(self):
        if self.df is None:
            QMessageBox.warning(self, "Error", "No CSV file loaded!")
            return
        
        selected_columns = [col for col, checkbox in self.checkboxes.items() if checkbox.isChecked()]
        if not selected_columns:
            QMessageBox.warning(self, "Error", "No columns selected for anonymization!")
            return

        processed_df = anonymize_columns(self.df, selected_columns)
        save_processed_data(self.project_name, processed_df.compute())  # Dask 데이터프레임을 저장
        QMessageBox.information(self, "Success", "Data anonymized and saved!")
