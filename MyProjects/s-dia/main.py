import sys
from PySide6.QtWidgets import QApplication
from frontend.login_window import LoginWindow
from backend.db import create_users_table

def main():
    # DB 초기화 (테이블 생성)
    create_users_table()

    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()