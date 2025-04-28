from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QCheckBox, QMessageBox
from PySide6.QtCore import Signal
from util.auth import authenticate_user

class LoginWindow(QWidget):
    login_success = Signal(str)  # 로그인 성공 시 유저이름 보내는 시그널

    def __init__(self):
        super().__init__()
        self.setWindowTitle("S-DIA 로그인")
        self.setFixedSize(300, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("아이디 입력")
        layout.addWidget(self.id_input)

        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("비밀번호 입력")
        self.pw_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pw_input)

        self.remember_id = QCheckBox("아이디 저장")
        layout.addWidget(self.remember_id)

        self.login_button = QPushButton("로그인")
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def handle_login(self):
        username = self.id_input.text()
        password = self.pw_input.text()

        if authenticate_user(username, password):
            QMessageBox.information(self, "로그인 성공", f"{username}님 환영합니다.")
            self.login_success.emit(username)
            self.close()
        else:
            QMessageBox.warning(self, "로그인 실패", "아이디 또는 비밀번호가 틀렸습니다.")
