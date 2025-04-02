from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

class LoginWindow(QWidget):
    def __init__(self, project_window):
        super().__init__()
        self.setWindowTitle("Login")
        
        self.project_window = project_window  # 프로젝트 창을 열기 위한 참조
        self.layout = QVBoxLayout(self)

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit(self)
        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_input)

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        self.layout.addWidget(self.login_button)

    def login(self):
        # 예시로 로그인 검증
        username = self.username_input.text()
        password = self.password_input.text()
        if username == "user" and password == "password":
            self.project_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials!")
