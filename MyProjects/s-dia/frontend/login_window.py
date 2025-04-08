from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from backend.db import check_login  # 로그인 체크 함수
from frontend.sign_up import SignUpWindow  # 회원가입 창 추가
from backend.db import verify_user
from frontend.project_window import ProjectWindow
from PySide6.QtCore import Signal

class LoginWindow(QWidget):
    login_success = Signal(str)  # 사용자 ID 전달 가능
    def __init__(self):
        super().__init__()
        self.setWindowTitle("로그인")

        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("사용자 이름")
        layout.addWidget(QLabel("사용자 이름:"))
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("비밀번호")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("비밀번호:"))
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("로그인")
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        # ✅ 회원가입 버튼 추가
        self.signup_button = QPushButton("회원가입")
        self.signup_button.clicked.connect(self.open_signup_window)
        layout.addWidget(self.signup_button)

        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if verify_user(username, password):
            self.project_window = ProjectWindow()
            self.project_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password")
    def open_signup_window(self):
        self.signup_window = SignUpWindow()
        self.signup_window.show()
