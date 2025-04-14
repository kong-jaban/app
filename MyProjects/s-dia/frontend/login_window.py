from PySide6.QtWidgets import QMessageBox, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QCheckBox, QFrame
from PySide6.QtCore import Qt, Signal
from config import APP_NAME, APP_VERSION
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
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel(APP_NAME)
        title.setObjectName("titleLabel")
        version = QLabel(APP_VERSION)
        version.setObjectName("versionLabel")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)

        login_frame = QFrame()
        login_layout = QVBoxLayout()

        login_label = QLabel("로그인")
        login_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("아이디를 입력하세요")

        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("비밀번호를 입력하세요")
        self.pw_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.save_id = QCheckBox("아이디 저장")
        login_btn = QPushButton("로그인")
        login_btn.clicked.connect(self.handle_login)

        login_layout.addWidget(login_label)
        login_layout.addWidget(self.id_input)
        login_layout.addWidget(self.pw_input)
        login_layout.addWidget(self.save_id)
        login_layout.addWidget(login_btn)

        login_frame.setLayout(login_layout)

        footer = QLabel("ⓒ 유피에스데이터 (UPSDATA)")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setObjectName("versionLabel")

        layout.addWidget(title)
        layout.addWidget(version)
        layout.addSpacing(20)
        layout.addWidget(login_frame)
        layout.addSpacing(20)
        layout.addWidget(footer)

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
