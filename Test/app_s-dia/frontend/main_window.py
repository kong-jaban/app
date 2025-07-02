from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

class MainWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle("메인 화면")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        self.label_welcome = QLabel(f"환영합니다, {username}님!")
        layout.addWidget(self.label_welcome)

        self.setLayout(layout)
