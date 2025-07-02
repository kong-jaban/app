import sys
import os
from PySide6.QtWidgets import QApplication
from ui.login_window import LoginWindow
from util.database import create_users_table
from util.settings import load_stylesheet

def main():
    # DB 테이블 생성
    create_users_table()

    app = QApplication(sys.argv)

    # QSS 스타일 적용
    current_dir = os.path.dirname(os.path.abspath(__file__))
    qss_path = os.path.join(current_dir, "frontend", "style.qss")
    app.setStyleSheet(load_stylesheet(qss_path))

    # 로그인 창 실행
    login_window = LoginWindow()
    login_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
