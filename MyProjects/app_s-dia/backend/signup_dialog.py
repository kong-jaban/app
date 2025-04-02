from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import psycopg2
import hashlib

DB_CONFIG = {
    "dbname": "your_db",
    "user": "your_user",
    "password": "your_password",
    "host": "localhost",
    "port": 5432
}

class SignupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("회원가입")
        self.resize(300, 200)

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

        self.label_confirm = QLabel("비밀번호 확인:")
        self.input_confirm = QLineEdit()
        self.input_confirm.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.label_confirm)
        layout.addWidget(self.input_confirm)

        self.signup_button = QPushButton("회원가입")
        self.signup_button.clicked.connect(self.register_user)
        layout.addWidget(self.signup_button)

        self.setLayout(layout)

    def register_user(self):
        username = self.input_username.text().strip()
        password = self.input_password.text()
        confirm_password = self.input_confirm.text()

        if not username or not password:
            QMessageBox.warning(self, "경고", "아이디와 비밀번호를 입력하세요.")
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "경고", "비밀번호가 일치하지 않습니다.")
            return
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()
            cur.close()
            conn.close()
            QMessageBox.information(self, "성공", "회원가입이 완료되었습니다.")
            self.accept()
        except psycopg2.IntegrityError:
            QMessageBox.warning(self, "경고", "이미 존재하는 아이디입니다.")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"회원가입 실패: {e}")

