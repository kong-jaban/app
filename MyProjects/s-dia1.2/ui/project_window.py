from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame
)
from PySide6.QtCore import Qt
from util.dialogs import AddProjectDialog

class ProjectWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle("프로젝트 관리")
        self.resize(1000, 700)

        self.layout = QVBoxLayout(self)

        self.add_button = QPushButton("+ 프로젝트 추가")
        self.add_button.clicked.connect(self.show_add_dialog)
        self.layout.addWidget(self.add_button)

        self.project_layout = QVBoxLayout()
        self.layout.addLayout(self.project_layout)

    def show_add_dialog(self):
        dialog = AddProjectDialog()
        if dialog.exec():
            name, desc = dialog.get_data()
            if name.strip():  # 이름이 비어있지 않으면
                self.add_project_card(name, desc)

    def add_project_card(self, name, desc):
        card = QFrame()
        card.setFrameShape(QFrame.Box)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #ccc;
            }
        """)
        card.setFixedSize(300, 150)

        layout = QVBoxLayout()
        title = QLabel(name)
        title.setStyleSheet("font-weight: bold; font-size: 16px;")

        desc_label = QLabel(desc)
        desc_label.setWordWrap(True)

        open_btn = QPushButton("열기")
        open_btn.setFixedWidth(80)

        layout.addWidget(title)
        layout.addWidget(desc_label)
        layout.addStretch()
        layout.addWidget(open_btn, alignment=Qt.AlignRight)
        card.setLayout(layout)

        self.project_layout.addWidget(card, alignment=Qt.AlignCenter)
