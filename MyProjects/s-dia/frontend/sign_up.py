from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from backend.db import register_user  # 회원가입 DB 저장 함수

class SignUpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("회원가입")

        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("사용자 이름")
        layout.addWidget(QLabel("사용자 이름:"))
        layout.addWidget(self.username_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("이메일")
        layout.addWidget(QLabel("이메일:"))
        layout.addWidget(self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("비밀번호")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("비밀번호:"))
        layout.addWidget(self.password_input)

        self.signup_button = QPushButton("회원가입")
        self.signup_button.clicked.connect(self.handle_signup)
        layout.addWidget(self.signup_button)

        self.setLayout(layout)

    def handle_signup(self):
        username = self.username_input.text()
        email = self.email_input.text()
        password = self.password_input.text()

        if username and email and password:
            success = register_user(username, email, password)
            if success:
                QMessageBox.information(self, "회원가입 성공", "회원가입이 완료되었습니다.")
                self.close()  # 회원가입 창 닫기
            else:
                QMessageBox.warning(self, "회원가입 실패", "이미 존재하는 사용자입니다.")
        else:
            QMessageBox.warning(self, "입력 오류", "모든 필드를 입력하세요.")
