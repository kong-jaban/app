from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import psycopg2
import hashlib

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("로그인")
        self.resize(300, 150)

        layout = QVBoxLayout()

        self.label_username = QLabel("아이디:")
        self.input_username = QLineEdit()
        layout.addWidget(self.label_username)
        layout.addWidget(self.input_username)

        self.label_password = QLabel("비밀번호:")
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.label_password)
        layout.addWidget(self.input_password)

        self.login_button = QPushButton("로그인")
        self.login_button.clicked.connect(self.login_user)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def login_user(self):
        username = self.input_username.text().strip()
        password = self.input_password.text()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, hashed_password))
            user = cur.fetchone()
            cur.close()
            conn.close()

            if user:
                QMessageBox.information(self, "성공", "로그인 성공!")
                self.accept()
            else:
                QMessageBox.warning(self, "실패", "아이디 또는 비밀번호가 잘못되었습니다.")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"로그인 실패: {e}")
