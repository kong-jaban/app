import sys
from PySide6.QtWidgets import QApplication
from frontend.login_window import LoginWindow
from backend.db import create_users_table
from frontend.project_window import ProjectWindow
import sys
import locale
import os

# 강제 UTF-8 설정
os.environ["PYTHONIOENCODING"] = "utf-8"
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
def main():
    # DB 초기화 (테이블 생성)
    create_users_table()

    app = QApplication(sys.argv)
    login_window = LoginWindow()

    def on_login_success(username):
        # 로그인 성공 시 프로젝트 화면 열기
        project_window = ProjectWindow(username=username)
        project_window.show()

    login_window.login_success.connect(on_login_success)
    login_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()