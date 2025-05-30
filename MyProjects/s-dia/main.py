import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QCheckBox, QFrame
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from config import APP_NAME, APP_VERSION, COPYRIGHT
from frontend.login_window import LoginWindow
from backend.db import create_users_table
from frontend.project_window import ProjectWindow
import locale
import os

# 강제 UTF-8 설정
os.environ["PYTHONIOENCODING"] = "utf-8"
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

def load_stylesheet(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
def main():
    # DB 초기화 (테이블 생성)
    print("#####Create user table...#######")
    create_users_table()
    print("#####Success Create user table..(or 이미있음).#######")


    app = QApplication(sys.argv)
    login_window = LoginWindow()
    # 상대 경로로 QSS 파일 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    qss_path = os.path.join(current_dir, "frontend", "style.qss")
    stylesheet = load_stylesheet(qss_path)
    app.setStyleSheet(stylesheet)

    def on_login_success(username):
        # 로그인 성공 시 프로젝트 화면 열기
        project_window = ProjectWindow(username=username)
        project_window.show()

    login_window.login_success.connect(on_login_success)
    login_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()