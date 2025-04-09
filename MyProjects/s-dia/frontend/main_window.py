from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget, QLabel,
    QListWidget, QComboBox, QHBoxLayout
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import os

class MainWindow(QMainWindow):
    
    def __init__(self, project_path, csv_path):
        super().__init__()
        self.setWindowTitle("프로젝트 메인")
        self.project_path = project_path
        self.csv_path = csv_path
        self.df = pd.read_csv(csv_path)
        self.distribution_data = self._precompute_distributions()
        self._init_ui()

    def _init_ui(self):
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_distribution_tab(), "컬럼 분포 보기")
        self.setCentralWidget(self.tabs)

    def _create_distribution_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # 컬럼 리스트
        self.column_list = QListWidget()
        self.column_list.addItems(self.df.columns)
        self.column_list.currentTextChanged.connect(self.display_distribution)

        # 차트 유형 선택
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["막대그래프", "히스토그램", "파이차트"])
        self.chart_type_combo.currentTextChanged.connect(self.display_distribution)

        # 컨트롤 영역
        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("컬럼 선택:"))
        control_layout.addWidget(self.column_list)
        control_layout.addWidget(QLabel("차트 유형:"))
        control_layout.addWidget(self.chart_type_combo)

        # 그래프 영역
        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addLayout(control_layout)
        layout.addWidget(self.canvas)

        widget.setLayout(layout)
        return widget

    def _precompute_distributions(self):
        dist = {}
        for col in self.df.columns:
            if self.df[col].dtype == object or self.df[col].nunique() < 30:
                dist[col] = self.df[col].value_counts()
            else:
                dist[col] = self.df[col].dropna()
        return dist

    def display_distribution(self, _):
        col = self.column_list.currentItem().text()
        chart_type = self.chart_type_combo.currentText()
        data = self.distribution_data[col]

        self.canvas.figure.clf()
        ax = self.canvas.figure.add_subplot(111)

        if chart_type == "막대그래프" and isinstance(data, pd.Series):
            data.plot(kind='bar', ax=ax, color="#6699cc")
        elif chart_type == "히스토그램":
            data.plot(kind='hist', ax=ax, bins=20, color="#66cc99")
        elif chart_type == "파이차트" and isinstance(data, pd.Series):
            data.plot(kind='pie', ax=ax, autopct='%1.1f%%')
        else:
            ax.text(0.5, 0.5, '시각화할 수 없습니다.', ha='center')

        ax.set_title(f"{col} - {chart_type}")
        self.canvas.draw()
