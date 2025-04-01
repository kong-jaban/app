from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
from PySide6.QtCore import Qt
from backend.db import authenticate_user  # db.py에서 만든 함수 가져오기

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        
        # Layout
        self.layout = QVBoxLayout(self)

        # 사용자 이름 입력
        self.username_label = QLabel("Username", self)
        self.username_input = QLineEdit(self)

        # 비밀번호 입력
        self.password_label = QLabel("Password", self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)  # 비밀번호 입력 시 숨김 처리

        # 로그인 버튼
        self.login_button = QPushButton("Login", self)
        self.login_button.clicked.connect(self.login)

        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button)

    def login(self):
        # 사용자 이름과 비밀번호 입력 값 가져오기
        username = self.username_input.text()
        password = self.password_input.text()

        # 로그인 인증
        user = authenticate_user(username, password)
        if user:
            print(f"Welcome, {username}!")  # 로그인 성공 시 환영 메시지
            self.close()  # 로그인 창 닫기

            # MainWindow로 이동
            self.parent().open_main_window()  # 부모 클래스의 open_main_window 호출
        else:
            print("Invalid username or password.")  # 실패 시 메시지 출력
