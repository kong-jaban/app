import sys
import os
import win32gui
import win32con
import psutil
import traceback
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

# 프로젝트 루트 디렉토리를 Python 경로에 추가
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from ui.login_window import LoginWindow

def find_existing_window():
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title == "S-DIA":
                windows.append(hwnd)
        return True
    
    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows[0] if windows else None

def main():
    try:
        print("프로그램 시작")
        
        # 현재 프로세스 정보
        current_process = psutil.Process()
        current_pid = current_process.pid
        current_name = current_process.name()
        
        print(f"현재 프로세스 ID: {current_pid}")
        print(f"현재 프로세스 이름: {current_name}")
        
        # 이미 실행 중인 프로세스 확인
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] == current_name and proc.info['pid'] != current_pid:
                    # 기존 창 찾기
                    hwnd = find_existing_window()
                    if hwnd:
                        print(f"기존 창 발견: {hwnd}")
                        # 창이 최소화되어 있으면 복원
                        if win32gui.IsIconic(hwnd):
                            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                        # 창을 앞으로 가져오기
                        win32gui.SetForegroundWindow(hwnd)
                        return
                    else:
                        # print("기존 창을 찾을 수 없습니다. 새 창을 생성합니다.")
                        continue
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        print("Qt 애플리케이션 초기화")
        # Qt 애플리케이션 초기화
        app = QApplication(sys.argv)
        app.setApplicationName("S-DIA")
        
        
        # 아이콘 설정
        if getattr(sys, 'frozen', False):
            # PyInstaller로 생성된 실행 파일인 경우
            icon_path = os.path.join(sys._MEIPASS, 'resources', 's-dia.ico')
        else:
            # 일반 Python 스크립트로 실행되는 경우
            base_path = os.path.dirname(os.path.dirname(__file__))
            icon_path = os.path.join(base_path, 'src', 'ui', 'resources', 's-dia.ico')
        
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
        
        print("로그인 창 생성")
        # 로그인 창 표시
        login_window = LoginWindow()
        print("로그인 창 표시")
        login_window.show()
        
        print("이벤트 루프 시작")
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        print("상세 오류 정보:")
        traceback.print_exc()
        # 오류 발생 시 잠시 대기하여 로그 확인 가능
        input("계속하려면 아무 키나 누르세요...")
        return

if __name__ == '__main__':
    main() 