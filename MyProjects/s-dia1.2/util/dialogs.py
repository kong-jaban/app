# util/dialogs.py

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QTextEdit, QPushButton

class AddProjectDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("프로젝트 추가")
        self.setFixedSize(300, 200)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("프로젝트 이름")

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("프로젝트 설명")
        self.desc_input.setFixedHeight(80)

        self.ok_button = QPushButton("확인")
        self.ok_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(self.name_input)
        layout.addWidget(self.desc_input)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)

    def get_data(self):
        return self.name_input.text(), self.desc_input.toPlainText()
