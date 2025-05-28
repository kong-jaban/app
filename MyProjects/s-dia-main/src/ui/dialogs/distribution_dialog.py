from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import dask.dataframe as dd
import os


class DistributionDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("컬럼 분포 시각화")
        self.resize(800, 600)

        self.data = data or {}
        self.canvas = FigureCanvas(Figure(figsize=(6, 4)))
        self.ax = self.canvas.figure.subplots()

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel(f"데이터 소스: {self.data.get('name', '알 수 없음')}"))

        self.column_selector = QComboBox()
        self.column_selector.currentTextChanged.connect(self.update_plot)
        self.layout.addWidget(self.column_selector)

        chart_type_layout = QHBoxLayout()
        self.chart_type_selector = QComboBox()
        self.chart_type_selector.addItems(["막대그래프", "히스토그램", "파이차트"])
        self.chart_type_selector.currentTextChanged.connect(self.update_plot)
        chart_type_layout.addWidget(QLabel("시각화 유형:"))
        chart_type_layout.addWidget(self.chart_type_selector)
        self.layout.addLayout(chart_type_layout)

        self.layout.addWidget(self.canvas)

        self.df = None
        self.load_data()

    def load_data(self):
        try:
            csv_path = self.data.get('path')
            if not csv_path or not os.path.exists(csv_path):
                self.column_selector.addItem("CSV 파일을 찾을 수 없습니다")
                return

            self.df = dd.read_csv(csv_path, assume_missing=True)
            self.columns = list(self.df.columns)
            self.column_selector.addItems(self.columns)
        except Exception as e:
            self.column_selector.addItem("데이터 로드 오류")
            print(f"Error loading data: {e}")

    def update_plot(self):
        if self.df is None:
            return

        column = self.column_selector.currentText()
        chart_type = self.chart_type_selector.currentText()

        if not column or column not in self.df.columns:
            return

        try:
            self.ax.clear()
            series = self.df[column].dropna()

            if chart_type == "막대그래프":
                counts = series.value_counts().compute()
                counts = counts.sort_index()
                self.ax.bar(counts.index.astype(str), counts.values)
                self.ax.set_xticklabels(counts.index.astype(str), rotation=45, ha='right')

            elif chart_type == "히스토그램":
                self.ax.hist(series.compute(), bins=20, edgecolor='black')

            elif chart_type == "파이차트":
                counts = series.value_counts().compute().nlargest(10)
                self.ax.pie(counts.values, labels=counts.index.astype(str), autopct="%1.1f%%")

            self.ax.set_title(f"{column} - {chart_type}")
            self.canvas.draw()

        except Exception as e:
            print(f"Error updating plot: {e}")
