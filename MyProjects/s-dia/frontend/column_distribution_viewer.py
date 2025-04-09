from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class ColumnDistributionViewer(QWidget):
    def __init__(self, column_name, values, counts):
        super().__init__()
        self.setWindowTitle(f"{column_name} 분포")
        layout = QVBoxLayout()
        fig = Figure(figsize=(6, 4))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        ax.bar(values, counts)
        ax.set_title(f"{column_name} 값 분포")
        ax.tick_params(axis='x', rotation=45)
        layout.addWidget(canvas)
        self.setLayout(layout)
