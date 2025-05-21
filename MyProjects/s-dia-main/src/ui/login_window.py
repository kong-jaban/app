from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QLineEdit, QMessageBox, QFrame,
                             QCheckBox, QMenu)
from PySide6.QtCore import Qt, QUrl, QFile, QIODevice, QTimer, QObject, QEvent
from PySide6.QtGui import QFont, QIcon, QPalette, QColor, QDesktopServices, QAction
from PySide6.QtUiTools import QUiLoader
from .main_window import MainWindow
from .common.context_menu import CustomContextMenuFilter
from utils.crypto import CryptoUtil
import json
import os
import platform
import sys
import traceback
import logging
import logging.config
import logging.handlers
from datetime import datetime
import base64

def setup_logger(data_dir):
    """로깅 설정을 초기화합니다."""
    # 로깅 설정 파일 경로 찾기
    if getattr(sys, 'frozen', False):
        # PyInstaller로 생성된 실행 파일인 경우
        base_path = os.path.dirname(sys.executable)
    else:
        # 일반 Python 스크립트로 실행되는 경우
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    config_path = os.path.join(base_path, 'logging.json')
    
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
            # 운영체제에 따른 로그 경로 설정
            system = platform.system().lower()
            log_path = config['log_path'].get(system, config['log_path']['windows'])
            
            # 환경 변수 치환
            if system == 'windows':
                log_path = os.path.expandvars(log_path)
            else:
                log_path = os.path.expanduser(log_path)
            
            # 로그 디렉토리 생성
            os.makedirs(log_path, exist_ok=True)
            
            # 로그 파일 경로 설정
            log_file = os.path.join(log_path, 'S-DIA.log')
            config['handlers']['file']['filename'] = log_file
            
            logging.config.dictConfig(config)
    else:
        # 설정 파일이 없는 경우 기본 설정 사용
        # 로그 디렉토리 생성
        log_dir = os.path.join(data_dir, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # 로그 파일 경로
        log_file = os.path.join(log_dir, 'S-DIA.log')
        
        logger = logging.getLogger('S-DIA')
        logger.setLevel(logging.DEBUG)
        
        # 파일 핸들러 설정
        file_handler = logging.handlers.TimedRotatingFileHandler(
            log_file,
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        file_handler.suffix = "%Y%m%d"
        
        # 콘솔 핸들러 설정
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        
        # 포맷터 설정
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 핸들러 추가
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logging.getLogger('S-DIA')

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # QApplication 인스턴스 저장
        from PySide6.QtWidgets import QApplication
        self.app = QApplication.instance()
        
        # 데이터 디렉토리 설정
        if platform.system() == 'Windows':
            self.data_dir = os.path.join(os.getenv('LOCALAPPDATA', ''), 'UPSDATA', 'S-DIA')
        else:
            self.data_dir = os.path.expanduser('~/.upsdata/s-dia')
            
        # 데이터 디렉토리 생성
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 로거 설정
        self.logger = setup_logger(self.data_dir)
        self.logger.info("LoginWindow 초기화 시작")
        
        # CryptoUtil 초기화
        self.crypto = CryptoUtil("S-DIA")  # 고정된 암호화 키 사용
        
        # 사용자 정보 파일 경로
        self.user_info_path = os.path.join(self.data_dir, 'userinfo.json')
        
        # 사용자 정보 파일이 없으면 생성
        if not os.path.exists(self.user_info_path):
            self.create_default_user_info()
        
        # 창 제목 설정
        self.setWindowTitle("S-DIA")
        
        # 아이콘 설정
        if getattr(sys, 'frozen', False):
            # PyInstaller로 생성된 실행 파일인 경우
            icon_path = os.path.join(sys._MEIPASS, 'resources', 's-dia.ico')
        else:
            # 일반 Python 스크립트로 실행되는 경우
            icon_path = os.path.join(os.path.dirname(__file__), 'resources', 's-dia.ico')
        
        if os.path.exists(icon_path):
            self.logger.debug(f"아이콘 경로: {icon_path}")
            self.setWindowIcon(QIcon(icon_path))
        else:
            self.logger.warning(f"아이콘 파일을 찾을 수 없습니다: {icon_path}")
        
        # 배경색 설정
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor('#e9ecef'))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        
        # 입력창 스타일 설정
        self.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
                color: #495057;
            }
            QLineEdit:focus {
                border: 1px solid #80bdff;
                background-color: white;
            }
            QCheckBox {
                color: #495057;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                color: white;
                background-color: #0d6efd;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
            QLabel {
                color: #495057;
            }
            QMessageBox {
                background-color: #f4f6f8;
            }
            QMessageBox QLabel {
                color: #212529;
                font-size: 13px;
            }
            QMessageBox QPushButton {
                min-width: 80px;
                min-height: 24px;
                padding: 4px 8px;
            }
        """)
        
        # 창 크기 고정
        self.setFixedSize(400, 450)
        
        self.logger.debug(f"데이터 디렉토리: {self.data_dir}")
        
        # PyInstaller로 생성된 실행 파일의 경로 확인
        if getattr(sys, 'frozen', False):
            # PyInstaller로 생성된 실행 파일인 경우
            base_path = sys._MEIPASS
            self.logger.debug(f"PyInstaller 실행 파일 경로: {base_path}")
        else:
            # 일반 Python 스크립트로 실행되는 경우
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.logger.debug(f"프로젝트 루트 경로: {base_path}")
        
        # UI 파일 경로 설정
        ui_paths = [
            os.path.join(base_path, 'src', 'ui', 'login.ui'),
            os.path.join(base_path, 'ui', 'login.ui'),
            os.path.join(base_path, 'login.ui'),
            os.path.join(os.path.dirname(__file__), 'login.ui')
        ]
        
        self.logger.debug("UI 파일 경로 시도:")
        ui_file_found = False
        for ui_path in ui_paths:
            self.logger.debug(f"UI 파일 경로 시도: {ui_path}")
            if os.path.exists(ui_path):
                self.logger.info(f"UI 파일을 찾았습니다: {ui_path}")
                
                ui_file = QFile(ui_path)
                if not ui_file.open(QIODevice.ReadOnly):
                    self.logger.error(f"UI 파일을 열 수 없습니다: {ui_path}")
                    continue
                
                loader = QUiLoader()
                self.ui = loader.load(ui_file)
                ui_file.close()
                
                if self.ui is None:
                    self.logger.error(f"UI 파일을 로드할 수 없습니다: {ui_path}")
                    continue
                
                ui_file_found = True
                break
        
        if not ui_file_found:
            self.logger.critical("UI 파일을 찾을 수 없습니다.")
            QMessageBox.critical(None, "오류", "UI 파일을 찾을 수 없습니다.")
            sys.exit(1)
        
        # UI 파일 로드
        if ui_file_found:
            ui_file = QFile(ui_path)
            if not ui_file.open(QIODevice.ReadOnly):
                self.logger.error(f"UI 파일을 열 수 없습니다: {ui_path}")
                sys.exit(1)
            
            loader = QUiLoader()
            self.ui = loader.load(ui_file)
            ui_file.close()
            
            if self.ui is None:
                self.logger.error(f"UI 파일을 로드할 수 없습니다: {ui_path}")
                sys.exit(1)
            
            # border 제거
            if hasattr(self.ui, 'login_subtitle'):
                self.ui.login_subtitle.setStyleSheet("border: none;")
            
            # 중앙 위젯 설정
            self.setCentralWidget(self.ui)
            
            # 위젯 존재 여부 확인
            required_widgets = [
                'id_input', 'pw_input', 'save_id_checkbox',
                'login_button', 'copyright_label'
            ]
            
            for widget_name in required_widgets:
                widget = getattr(self.ui, widget_name, None)
                if widget is None:
                    self.logger.error(f"필수 위젯이 없습니다: {widget_name}")
                    QMessageBox.critical(None, "오류", f"필수 위젯이 없습니다: {widget_name}")
                    sys.exit(1)
            
            # 입력 필드에 이벤트 필터 설치
            self.context_filter = CustomContextMenuFilter(self)
            self.ui.id_input.installEventFilter(self.context_filter)
            self.ui.pw_input.installEventFilter(self.context_filter)
            
            # 이벤트 연결
            self.ui.login_button.clicked.connect(self.login)
            self.ui.id_input.returnPressed.connect(self.login)
            self.ui.pw_input.returnPressed.connect(self.login)
            
            # 저장된 ID 로드
            self.load_saved_id()
            
            # 창 위치 설정
            self.center_window()
            
            self.logger.info("LoginWindow 초기화 완료")
    
    def center_window(self):
        """창을 화면 중앙에 위치시킵니다."""
        frame = self.frameGeometry()
        screen = self.screen().availableGeometry().center()
        frame.moveCenter(screen)
        self.move(frame.topLeft())
    
    def load_saved_id(self):
        """저장된 ID를 로드합니다."""
        try:
            config_path = os.path.join(self.data_dir, 'config.json')
            self.logger.debug(f"설정 파일 경로: {config_path}")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.logger.debug(f"로드된 설정: {config}")
                    if config.get('save_id', False):
                        saved_id = config.get('saved_id', '')
                        self.logger.debug(f"저장된 ID: {saved_id}")
                        self.ui.id_input.setText(saved_id)
                        self.ui.save_id_checkbox.setChecked(True)
        except Exception as e:
            self.logger.error(f"설정 파일 로드 중 오류: {e}")
            self.logger.error(traceback.format_exc())
    
    def save_id(self):
        """ID를 저장합니다."""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            config_path = os.path.join(self.data_dir, 'config.json')
            config = {}
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            config['save_id'] = self.ui.save_id_checkbox.isChecked()
            if config['save_id']:
                config['saved_id'] = self.ui.id_input.text()
            elif 'saved_id' in config:
                del config['saved_id']
            
            self.logger.debug(f"저장할 설정: {config}")
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            self.logger.info("설정 저장 완료")
        except Exception as e:
            self.logger.error(f"설정 파일 저장 중 오류: {e}")
            self.logger.error(traceback.format_exc())
    
    def create_default_user_info(self):
        """기본 사용자 정보 파일을 생성합니다."""
        try:
            default_data = {
                "user_id": "admin",
                "password": "changeit!",
                "name": "UPSDATA",
                "email": "admin@upsdata.co.kr",
                "role": "admin",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_login": ""
            }
            self.crypto.save_encrypted_data(default_data, self.user_info_path)
            self.logger.info("기본 사용자 정보 파일 생성 완료")
            return default_data
        except Exception as e:
            self.logger.error(f"기본 사용자 정보 파일 생성 실패: {e}")
            self.logger.error(traceback.format_exc())
            return None
    
    def login(self):
        """로그인을 처리합니다."""
        try:
            login_id = self.ui.id_input.text().strip()
            password = self.ui.pw_input.text().strip()
            
            if not login_id or not password:
                QMessageBox.warning(self, '로그인 오류', '아이디와 비밀번호를 입력하세요.')
                return
            
            try:
                # 사용자 정보 파일이 없으면 생성
                if not os.path.exists(self.user_info_path):
                    default_data = self.create_default_user_info()
                    if default_data is None:
                        QMessageBox.critical(self, '오류', '사용자 정보 파일 생성에 실패했습니다.')
                        return
                    user_info = default_data
                else:
                    # CryptoUtil을 사용하여 암호화된 사용자 정보 로드
                    user_info = self.crypto.load_encrypted_data(self.user_info_path)
                
                if user_info['user_id'] == login_id and user_info['password'] == password:
                    self.logger.info(f"로그인 성공: {login_id}")
                    
                    # 로그인 성공 시에만 ID 저장
                    if self.ui.save_id_checkbox.isChecked():
                        self.save_id()
                    
                    # 마지막 로그인 시간 업데이트
                    user_info['last_login'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.crypto.save_encrypted_data(user_info, self.user_info_path)
                    
                    try:
                        # MainWindow 생성 전에 로그
                        self.logger.debug("MainWindow 생성 시작")
                        self.main_window = MainWindow(user_info)  # user_info 전체를 전달
                        self.logger.debug("MainWindow 생성 완료")
                        
                        # show 전에 로그
                        self.logger.debug("MainWindow.show() 호출 전")
                        self.main_window.show()
                        self.logger.debug("MainWindow.show() 호출 완료")
                        
                        # 로그인 창 숨기기
                        self.logger.debug("로그인 창 숨기기 전")
                        self.hide()
                        self.logger.debug("로그인 창 숨기기 완료")
                    except Exception as e:
                        self.logger.error("MainWindow 생성 또는 표시 중 오류 발생")
                        self.logger.error(f"오류 내용: {str(e)}")
                        self.logger.error("상세 오류:", exc_info=True)
                        self.show()  # 로그인 창 다시 표시
                        QMessageBox.critical(self, '오류', '메인 창을 생성하는 중 오류가 발생했습니다.')
                else:
                    self.logger.warning(f"로그인 실패: {login_id}")
                    QMessageBox.warning(self, '로그인 오류', '아이디 또는 비밀번호가 일치하지 않습니다.')
                    
            except Exception as e:
                self.logger.error(f"사용자 정보 처리 중 오류: {str(e)}")
                self.logger.error("상세 오류:", exc_info=True)
                QMessageBox.critical(self, '오류', '사용자 정보를 처리하는 중 오류가 발생했습니다.')
                
        except Exception as e:
            self.logger.error(f"로그인 처리 중 오류 발생: {str(e)}")
            self.logger.error("상세 오류:", exc_info=True)
            QMessageBox.critical(self, '오류', '로그인 처리 중 오류가 발생했습니다.')
    
    def closeEvent(self, event):
        """창이 닫힐 때의 이벤트를 처리합니다."""
        self.save_id()
        event.accept()

    def open_website(self, event):
        """웹사이트 열기"""
        QDesktopServices.openUrl(QUrl("https://www.upsdata.co.kr/")) 