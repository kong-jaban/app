from PySide6.QtWidgets import (QMainWindow, QWidget, QMessageBox, QMenu, QDialog,
                              QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QDialogButtonBox, 
                              QCheckBox, QFrame, QApplication, QScrollArea, QGridLayout, QSizePolicy,
                              QLayout, QTextEdit)
from PySide6.QtCore import Qt, QFile, QIODevice, QEvent, QPoint, QRect, QSize, QTimer
from PySide6.QtGui import QPalette, QColor, QIcon, QPixmap, QCursor, QScreen, QFont, QFontMetrics
from PySide6.QtUiTools import QUiLoader
import os
import sys
import logging
from utils.crypto import CryptoUtil, SecretStorage
from .common.context_menu import CustomContextMenuFilter
from .dialogs.project_dialog import ProjectDialog
from .components.project_card import ProjectCard
from .components.confirm_dialog import ConfirmDialog
from .panels.project_panel import ProjectPanel
from .dialogs.user_info_dialog import UserInfoDialog
import json
import platform
from src.ui.components.message_dialog import MessageDialog

class ModifiedLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._original_text = ""
        self._is_modified = False
        self.textChanged.connect(self._handle_text_change)

    def _handle_text_change(self, text):
        self._is_modified = text != self._original_text

    def setText(self, text):
        super().setText(text)
        self._original_text = text
        self._is_modified = False

    def isModified(self):
        return self._is_modified

class PasswordLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._password = ""
        self._is_modified = False
        self.textChanged.connect(self._handle_text_change)
        self.setEchoMode(QLineEdit.Password)

    def _handle_text_change(self, text):
        # 읽기 전용이거나 마스킹된 텍스트인 경우 무시
        if self.isReadOnly() or text == "*" * 10:
            return
        
        # 실제 입력이 있는 경우 비밀번호 업데이트
        if text != self._password:
            self._password = text
            self._is_modified = True
            super().setText(text)  # 실제 입력한 문자 수만큼 마스킹

    def text(self):
        return self._password

    def setText(self, text):
        self._password = text
        self._is_modified = False
        if self.echoMode() == QLineEdit.Password:
            super().setText("*" * 10)  # 항상 10개의 마스킹으로 시작
        else:
            super().setText(text)

    def getPassword(self):
        return self._password

    def isModified(self):
        return self._is_modified

    def setReadOnly(self, readonly):
        super().setReadOnly(readonly)
        # 읽기 전용으로 변경될 때는 항상 10개의 마스킹
        if readonly and self.echoMode() == QLineEdit.Password:
            super().setText("*" * 10)

class MainWindow(QMainWindow):
    def __init__(self, user_info):
        super().__init__()
        
        # QApplication 인스턴스 저장
        self.app = QApplication.instance()
        
        # 로거 설정
        self.logger = logging.getLogger(__name__)
        self.logger.info("MainWindow 초기화 시작")
        
        # 사용자 정보 저장
        self.user_info = user_info
        self.login_id = user_info['user_id']
        
        # 네비게이션 경로 초기화
        self.navigation_path = ["홈"]
        
        # 창 상태 관리자 초기화
        self.secret_storage = SecretStorage()
        
        # 창 제목 설정
        self.setWindowTitle("S-DIA")
        
        # 아이콘 설정
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        # 윈도우 아이콘 설정
        icon_path = os.path.join(base_path, 'src', 'ui', 'resources', 'images', 's-dia.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            # 작업 표시줄 아이콘 설정
            if platform.system() == 'Windows':
                import ctypes
                myappid = 'upsdata.s-dia.1.0'  # 임의의 고유 문자열
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        
        # UI 파일 로드
        loader = QUiLoader()
        self.ui = loader.load("src/ui/main.ui")
        
        if not self.ui:
            self.logger.error("UI 파일을 로드할 수 없습니다.")
            MessageDialog.critical(self, "오류", "UI 파일을 로드할 수 없습니다.")
            return
            
        # 중앙 위젯 설정
        self.setCentralWidget(self.ui.centralwidget)
        
        # 네비게이션 레이블 설정
        self.ui.breadcrumb_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.ui.breadcrumb_label.setMinimumWidth(0)
        
        # 최소 윈도우 크기 설정 (카드 최소 크기 + 여백 + 스크롤바 + 메뉴 영역)
        min_width = 300 + (20 * 2) + 8 + 250  # 카드 최소 너비 + 좌우 여백 + 스크롤바 + 메뉴 영역
        min_height = 600  # 최소 높이 655px
        self.setMinimumSize(min_width, min_height)
        
        # 아이콘 설정
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        # 로고 이미지 설정
        logo_path = os.path.join(base_path, 'src', 'ui', 'resources', 'images', 'logo.png')
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            if not logo_pixmap.isNull():
                scaled_pixmap = logo_pixmap.scaled(250, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.ui.menu_logo.setPixmap(scaled_pixmap)
            
        # 사용자 정보 표시 및 메뉴 설정
        self.ui.header_user.setText(f"{self.user_info['user_id']}({self.user_info['name']})")
        self.ui.header_user.setCursor(Qt.PointingHandCursor)
        self.ui.header_user.clicked.connect(self.show_user_menu)
            
        # 버튼 이벤트 연결
        self.ui.btn_projects.clicked.connect(self.show_projects)
        self.ui.btn_new_project.clicked.connect(self.show_new_project_dialog)
        self.ui.btn_settings.clicked.connect(self.show_settings)
        
        # 네비게이션 초기화
        self.update_navigation()
        
        # 창 크기 복원 또는 전체화면으로 시작
        self.restore_window_state()
        
        # 창 크기 변경 이벤트 연결
        self.installEventFilter(self)
        
        # 컨텍스트 메뉴 필터 설정
        self.context_filter = CustomContextMenuFilter(self)
        
        # 모든 QLineEdit에 컨텍스트 메뉴 필터 적용
        for widget in self.findChildren(QLineEdit):
            widget.installEventFilter(self.context_filter)
            
        # 프로젝트 레이아웃 초기화
        self.init_projects_layout()
        
        self.logger.info("메인 윈도우 초기화 완료")
    
    def init_projects_layout(self):
        """프로젝트 레이아웃 초기화"""
        try:
            # projects.json에서 프로젝트 목록 로드
            self.projects = self.load_projects_from_json()
            
            # 기존 레이아웃 제거
            if self.ui.projects_container.layout():
                QWidget().setLayout(self.ui.projects_container.layout())

            # 새 레이아웃 생성
            new_layout = QVBoxLayout(self.ui.projects_container)
            new_layout.setContentsMargins(0, 0, 0, 0)

            if not self.projects:
                # UI 파일 로드
                loader = QUiLoader()
                no_projects_widget = loader.load("src/ui/no_projects.ui")
                if not no_projects_widget:
                    self.logger.error("no_projects.ui 파일을 로드할 수 없습니다.")
                    return
                
                # 메인 레이아웃에 위젯 추가
                new_layout.addWidget(no_projects_widget)
                return

            # 스크롤 영역 생성
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setStyleSheet("""
                QScrollArea {
                    border: none;
                    background: transparent;
                }
                QWidget#scrollAreaWidgetContents {
                    background: transparent;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #e7f5ff;
                    width: 8px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background: #d0ebff;
                    border-radius: 4px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #339af0;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: transparent;
                }
            """)

            # 스크롤 영역에 들어갈 컨테이너 위젯
            outer_container = QWidget()
            outer_layout = QHBoxLayout(outer_container)
            outer_layout.setContentsMargins(20, 20, 20, 20)
            outer_layout.setSpacing(0)

            # 내부 컨테이너 (카드를 포함할 위젯)
            container = QWidget()
            container.setObjectName("scrollAreaWidgetContents")
            
            # 플로우 레이아웃 설정
            flow_layout = FlowLayout(container)
            flow_layout.setSpacing(20)
            flow_layout.setContentsMargins(0, 0, 0, 0)
            
            # 카드 생성 및 레이아웃에 추가
            for project in self.projects:
                card = self.create_project_card(project)
                flow_layout.addWidget(card)

            # 컨테이너를 외부 레이아웃에 추가
            outer_layout.addWidget(container)
            
            # 스크롤 영역에 외부 컨테이너 설정
            scroll_area.setWidget(outer_container)
            
            # 새 레이아웃 생성 및 스크롤 영역 추가
            new_layout.addWidget(scroll_area)
            
            # 스크롤바가 필요한지 확인
            content_height = flow_layout.heightForWidth(container.width())
            scroll_needed = content_height > scroll_area.height()
            
            if scroll_needed:
                # 스크롤바가 필요한 경우 우측 마진 조정
                outer_layout.setContentsMargins(20, 20, 10, 20)
                
                # 우측 여백을 위한 더미 위젯 추가
                spacer = QWidget()
                spacer.setFixedWidth(10)
                outer_layout.addWidget(spacer)
                
                # 스크롤바 우측 여백 설정
                new_layout.setContentsMargins(0, 0, 2, 0)
            
            self.logger.info("프로젝트 카드가 레이아웃에 추가되었습니다.")
            
        except Exception as e:
            self.logger.error(f"프로젝트 레이아웃 초기화 중 오류 발생: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())

    def load_projects_from_json(self):
        """projects.json 파일에서 프로젝트 목록을 로드합니다."""
        try:
            # 파일 경로 설정
            if os.name == 'nt':  # Windows
                data_dir = os.path.join(os.getenv('LOCALAPPDATA', ''), 'UPSDATA', 'S-DIA')
            else:  # Linux/Mac
                data_dir = os.path.expanduser('~/.upsdata/s-dia')
            
            projects_path = os.path.join(data_dir, 'projects.json')
            
            # 파일이 없으면 빈 리스트 반환
            if not os.path.exists(projects_path):
                return []
            
            # 파일 읽기
            with open(projects_path, 'r', encoding='utf-8') as f:
                projects = json.load(f)
            
            return projects if isinstance(projects, list) else []
            
        except Exception as e:
            self.logger.error(f"프로젝트 목록 로드 중 오류 발생: {str(e)}")
            return []

    def create_project_card(self, project):
        """프로젝트 카드 위젯 생성"""
        try:
            card = ProjectCard(project, self)
            return card
        except Exception as e:
            self.logger.error(f"프로젝트 카드 생성 중 오류 발생: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None

    def on_project_click(self, card):
        """프로젝트 카드 클릭 이벤트 처리"""
        self.on_project_open(card)
        
    def on_project_open(self, card):
        """프로젝트 열기 메뉴 처리"""
        self.logger.info("열기 선택됨")
        self.show_project_panel(card)
        # 네비게이션 경로 업데이트
        project_name = card.project_data.get('name', '')
        project_uuid = card.project_data.get('uuid', '')
        self.current_project = project_name
        self.current_project_uuid = project_uuid
        self.update_navigation(project_name)
        
    def on_project_edit(self, card):
        """프로젝트 수정 메뉴 처리"""
        self.logger.info("수정 선택됨")
        if card.project_data:
            # 프로젝트 수정 다이얼로그 표시
            dialog = ProjectDialog(self, card.project_data)
            if dialog.exec() == ProjectDialog.Accepted:
                self.init_projects_layout()  # 프로젝트 목록 새로고침
                
    def on_project_delete(self, card):
        """프로젝트 삭제 메뉴 처리"""
        self.logger.info("삭제 선택됨")
        # 공통 확인 다이얼로그 사용
        if ConfirmDialog.confirm(self, "프로젝트 삭제", 
                           f"'{card.project_data.get('name', '')}' 프로젝트를 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다."):
            try:
                # 프로젝트 목록에서 제거
                self.projects = self.load_projects_from_json()
                self.projects = [p for p in self.projects if p.get('name') != card.project_data.get('name', '')]
                # 파일 경로 설정
                if os.name == 'nt':  # Windows
                    data_dir = os.path.join(os.getenv('LOCALAPPDATA', ''), 'UPSDATA', 'S-DIA')
                else:  # Linux/Mac
                    data_dir = os.path.expanduser('~/.upsdata/s-dia')
                projects_path = os.path.join(data_dir, 'projects.json')
                # 파일 저장
                with open(projects_path, 'w', encoding='utf-8') as f:
                    json.dump(self.projects, f, ensure_ascii=False, indent=4)
                self.init_projects_layout()  # 프로젝트 목록 새로고침
            except Exception as e:
                self.logger.error(f"프로젝트 삭제 중 오류 발생: {str(e)}")
                MessageDialog.critical(self, "오류", "프로젝트 삭제 중 오류가 발생했습니다.")

    def show_project_panel(self, card_widget):
        """프로젝트 메뉴 패널을 표시합니다."""
        try:
            # 기존 메뉴 위젯 제거
            if self.ui.menu_frame and self.ui.menu_frame.layout():
                old_layout = self.ui.menu_frame.layout()
                while old_layout.count():
                    item = old_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                QWidget().setLayout(old_layout)
            
            # 프로젝트 패널 생성
            project_panel = ProjectPanel(card_widget.project_data, self)
            
            # 새 메뉴 설정
            self.ui.menu_frame.setLayout(project_panel.layout())

            # 프로젝트 카드 영역 재구성
            if self.ui.projects_container.layout():
                old_layout = self.ui.projects_container.layout()
                while old_layout.count():
                    item = old_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                QWidget().setLayout(old_layout)

            # 새로운 레이아웃 생성
            new_layout = QHBoxLayout(self.ui.projects_container)
            new_layout.setContentsMargins(0, 0, 0, 0)
            new_layout.setSpacing(0)

            # 좌측 영역 (300px 고정)
            left_frame = QFrame()
            left_frame.setObjectName("left_frame")
            left_frame.setFixedWidth(300)
            left_frame.setStyleSheet("""
                QFrame#left_frame {
                    background-color: #e7f5ff;
                    border: none;
                }
            """)
            left_layout = QVBoxLayout(left_frame)
            left_layout.setContentsMargins(0, 0, 0, 0)
            left_layout.setSpacing(0)

            # 우측 영역 (동적 크기)
            right_frame = QFrame()
            right_frame.setObjectName("right_frame")
            right_frame.setStyleSheet("""
                QFrame#right_frame {
                    background-color: #f8f9fa;
                    border: none;
                }
            """)
            right_layout = QVBoxLayout(right_frame)
            right_layout.setContentsMargins(0, 0, 0, 0)
            right_layout.setSpacing(0)

            # 레이아웃에 프레임 추가
            new_layout.addWidget(left_frame)
            new_layout.addWidget(right_frame)
            
        except Exception as e:
            self.logger.error(f"프로젝트 메뉴 패널 표시 중 오류 발생: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())

    def _on_add_data_source(self, project_data):
        """데이터 소스 추가 처리"""
        self.logger.info("데이터 소스 추가")
        # TODO: 데이터 소스 추가 로직 구현

    def _on_add_flow(self, project_data):
        """플로우 추가 처리"""
        self.logger.info("플로우 추가")
        # TODO: 플로우 추가 로직 구현

    def close_project_panel(self):
        """프로젝트 메뉴 패널을 닫고 기본 메뉴로 돌아갑니다."""
        try:
            # 기존 메뉴 위젯 제거
            if self.ui.menu_frame and self.ui.menu_frame.layout():
                old_layout = self.ui.menu_frame.layout()
                while old_layout.count():
                    item = old_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                    elif item.layout():
                        # 중첩된 레이아웃의 위젯들도 제거
                        nested_layout = item.layout()
                        while nested_layout.count():
                            nested_item = nested_layout.takeAt(0)
                            if nested_item.widget():
                                nested_item.widget().deleteLater()
                QWidget().setLayout(old_layout)

            # 기본 메뉴 레이아웃 생성
            menu_layout = QVBoxLayout()
            menu_layout.setContentsMargins(0, 0, 0, 0)
            menu_layout.setSpacing(0)

            # 새로운 기본 메뉴 버튼들 생성
            self.ui.btn_projects = QPushButton("프로젝트")
            self.ui.btn_projects.clicked.connect(self.show_projects)
            self.ui.btn_new_project = QPushButton("새 프로젝트")
            self.ui.btn_new_project.clicked.connect(self.show_new_project_dialog)
            self.ui.btn_settings = QPushButton("설정")
            self.ui.btn_settings.clicked.connect(self.show_settings)

            # 버튼 스타일 설정
            button_style = """
                QPushButton {
                    text-align: left;
                    padding: 12px 20px;
                    border: none;
                    color: white;
                    background: transparent;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #5c636a;
                }
            """
            self.ui.btn_projects.setStyleSheet(button_style)
            self.ui.btn_new_project.setStyleSheet(button_style)
            self.ui.btn_settings.setStyleSheet(button_style)

            # 버튼들을 새 레이아웃에 추가
            menu_layout.addWidget(self.ui.btn_projects)
            menu_layout.addWidget(self.ui.btn_new_project)
            menu_layout.addWidget(self.ui.btn_settings)
            menu_layout.addStretch()

            # 새 레이아웃을 menu_frame에 설정
            self.ui.menu_frame.setLayout(menu_layout)
            
            # 프로젝트 카드 영역 복원
            self.init_projects_layout()
            
            # 네비게이션 업데이트
            self.current_project = None
            self.update_navigation(None)  # 홈으로 돌아가기

        except Exception as e:
            self.logger.error(f"프로젝트 메뉴 패널 닫기 중 오류 발생: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())

    def show_user_menu(self):
        """사용자 메뉴를 표시합니다."""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                color: #495057;
            }
            QMenu::item:selected {
                background-color: #e9ecef;
                color: #000;
            }
        """)
        
        # 메뉴 항목 추가
        user_info_action = menu.addAction("사용자 정보")
        logout_action = menu.addAction("로그아웃")
        
        # 버튼 위치에 메뉴 표시
        pos = self.ui.header_user.mapToGlobal(self.ui.header_user.rect().bottomRight())
        action = menu.exec_(pos)
        
        # 선택된 메뉴 처리
        if action == user_info_action:
            self.show_user_info()
        elif action == logout_action:
            self.logout()
            
    def show_user_info(self):
        """사용자 정보를 표시합니다."""
        self.logger.info("사용자 정보 표시")
        dialog = UserInfoDialog(self.user_info, self)
        dialog.exec()

    def logout(self):
        """로그아웃을 처리합니다."""
        self.logger.info("로그아웃")
        confirmed = ConfirmDialog.confirm(self, "로그아웃", "로그아웃 하시겠습니까?")
        if confirmed:
            from .login_window import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()

    def update_user_info(self, user_info):
        """사용자 정보를 업데이트합니다."""
        self.user_info = user_info
        self.ui.header_user.setText(f"{self.user_info['user_id']}({self.user_info['name']})")
        self.logger.info("사용자 정보 업데이트 완료") 

    def show_settings(self):
        """설정 화면 표시"""
        self.logger.info("설정 화면 표시 요청")
        # TODO: 설정 다이얼로그 표시

    def open_project(self, project_name):
        """프로젝트를 엽니다."""
        self.logger.info(f"프로젝트 열기: {project_name}")
        self.navigate_to(project_name)
        # TODO: 프로젝트 화면 표시 로직 추가

    def open_project_feature(self, feature_name):
        """프로젝트 내 특정 기능으로 이동합니다."""
        self.logger.info(f"프로젝트 기능 열기: {feature_name}")
        self.navigate_to(feature_name)
        # TODO: 프로젝트 기능 화면 표시 로직 추가 

    def restore_window_state(self):
        """저장된 창 상태를 복원하거나 전체화면으로 시작합니다."""
        window_state = self.secret_storage.load_window_state()
        
        if window_state is None:
            # 처음 실행 시 전체화면으로 시작
            self.showMaximized()
        else:
            x, y, width, height, is_maximized = window_state
            
            # 저장된 위치와 크기로 창 영역 생성
            window_rect = QRect(x, y, width, height)
            window_center = window_rect.center()
            
            # 모든 모니터의 전체 영역 계산
            total_screen_geometry = QRect()
            for screen in self.app.screens():
                total_screen_geometry = total_screen_geometry.united(screen.geometry())
            
            # 저장된 위치가 현재 모니터 구성에서 벗어났는지 확인
            if not total_screen_geometry.contains(window_center):
                # 주 화면에 표시
                primary_screen = self.app.primaryScreen()
                screen_geometry = primary_screen.availableGeometry()
                
                # 주 화면 중앙에 위치시킴
                adjusted_x = screen_geometry.x() + (screen_geometry.width() - width) // 2
                adjusted_y = screen_geometry.y() + (screen_geometry.height() - height) // 2
                
                # 크기가 화면을 벗어나는 경우 전체화면으로 표시
                if width > screen_geometry.width() or height > screen_geometry.height():
                    self.setGeometry(screen_geometry)
                    self.showMaximized()
                    self.logger.info("화면 구성이 변경되어 주 화면에 전체화면으로 표시됩니다.")
                else:
                    self.setGeometry(adjusted_x, adjusted_y, width, height)
                    if is_maximized:
                        self.showMaximized()
                    else:
                        self.show()
                    self.logger.info("화면 구성이 변경되어 주 화면에 표시됩니다.")
            else:
                # 저장된 위치가 포함된 모니터 찾기
                target_screen = None
                for screen in self.app.screens():
                    if screen.geometry().contains(window_center):
                        target_screen = screen
                        break
                
                if target_screen is None:
                    target_screen = self.app.primaryScreen()
                
                screen_geometry = target_screen.availableGeometry()
                
                # 창이 현재 모니터 크기를 벗어나는지 확인
                if width > screen_geometry.width() or height > screen_geometry.height():
                    # 모니터 크기를 벗어나면 전체화면으로 표시
                    self.setGeometry(screen_geometry)
                    self.showMaximized()
                    self.logger.info("화면 크기를 벗어나 전체화면으로 표시됩니다.")
                else:
                    # 창이 모니터 영역을 벗어났는지 확인하고 조정
                    adjusted_x = x
                    adjusted_y = y
                    
                    # 창이 모니터 왼쪽이나 위쪽으로 벗어난 경우
                    if x < screen_geometry.left():
                        adjusted_x = screen_geometry.left()
                    if y < screen_geometry.top():
                        adjusted_y = screen_geometry.top()
                    
                    # 창이 모니터 오른쪽이나 아래쪽으로 벗어난 경우
                    if x + width > screen_geometry.right():
                        adjusted_x = screen_geometry.right() - width
                    if y + height > screen_geometry.bottom():
                        adjusted_y = screen_geometry.bottom() - height
                    
                    if is_maximized:
                        self.setGeometry(adjusted_x, adjusted_y, width, height)
                        self.showMaximized()
                    else:
                        self.setGeometry(adjusted_x, adjusted_y, width, height)
                        self.show()
                    
                    if adjusted_x != x or adjusted_y != y:
                        self.logger.info("창 위치가 화면 범위를 벗어나 조정되었습니다.")

    def eventFilter(self, obj, event):
        """이벤트 필터"""
        if obj == self and event.type() == QEvent.Type.WindowStateChange:
            # 창 상태가 변경될 때 (최대화/복원)
            self.save_window_state()
        elif obj == self and event.type() == QEvent.Type.Resize:
            # 창 크기가 변경될 때
            self.save_window_state()
        elif obj == self and event.type() == QEvent.Type.Move:
            # 창 위치가 변경될 때
            self.save_window_state()
        return super().eventFilter(obj, event)

    def save_window_state(self):
        """현재 창 상태를 저장합니다."""
        if self.isMaximized():
            # 최대화 상태일 때는 이전 일반 창 상태를 저장
            self.secret_storage.save_window_state(
                self.normalGeometry().x(),
                self.normalGeometry().y(),
                self.normalGeometry().width(),
                self.normalGeometry().height(),
                True
            )
        else:
            # 일반 창 상태일 때
            self.secret_storage.save_window_state(
                self.geometry().x(),
                self.geometry().y(),
                self.geometry().width(),
                self.geometry().height(),
                False
            )

    def update_navigation(self, project_name=None):
        """네비게이션 바를 업데이트합니다."""
        if project_name:
            # 네비게이션 바의 전체 너비 계산
            header_width = self.ui.header_frame.width()
            user_button_width = self.ui.header_user.width()
            spacer_width = 40  # 우측 여백
            
            # 사용 가능한 너비 계산
            available_width = header_width - user_button_width - spacer_width - 40  # 40은 좌우 마진
            
            # "홈 > " 텍스트 너비 계산
            metrics = QFontMetrics(self.ui.breadcrumb_label.font())
            home_text = "홈 > "
            home_width = metrics.horizontalAdvance(home_text)
            
            # 프로젝트 이름이 들어갈 수 있는 최대 너비
            max_width = available_width - home_width - 20  # 20은 여유 공간
            
            # 프로젝트 이름이 너무 길면 말줄임표로 처리
            if metrics.horizontalAdvance(project_name) > max_width:
                # 말줄임표를 포함한 최대 길이 계산
                ellipsis = "..."
                ellipsis_width = metrics.horizontalAdvance(ellipsis)
                max_text_width = max_width - ellipsis_width
                
                # 프로젝트 이름을 잘라내고 말줄임표 추가
                truncated_name = ""
                for i in range(len(project_name)):
                    test_text = project_name[:i+1]
                    if metrics.horizontalAdvance(test_text) > max_text_width:
                        break
                    truncated_name = test_text
                
                display_name = truncated_name + ellipsis
                self.ui.breadcrumb_label.setText(f"{home_text}<b>{display_name}</b>")
                self.ui.breadcrumb_label.setToolTip(project_name)  # 전체 이름을 툴팁으로 표시
            else:
                self.ui.breadcrumb_label.setText(f"{home_text}<b>{project_name}</b>")
                self.ui.breadcrumb_label.setToolTip("")  # 툴팁 제거
        else:
            # 홈으로 돌아갈 때는 '홈'만 굵게 표시
            self.ui.breadcrumb_label.setText("<b>홈</b>")
            self.ui.breadcrumb_label.setToolTip("")

    def resizeEvent(self, event):
        """창 크기 변경 이벤트 처리"""
        super().resizeEvent(event)
        # 창 크기가 변경될 때 네비게이션 텍스트 업데이트
        if hasattr(self, 'current_project') and self.current_project:
            QTimer.singleShot(0, lambda: self.update_navigation(self.current_project))

    def showEvent(self, event):
        """창이 처음 표시될 때 호출됩니다."""
        super().showEvent(event)
        # 네비게이션 텍스트 업데이트
        if hasattr(self, 'current_project') and self.current_project:
            QTimer.singleShot(0, lambda: self.update_navigation(self.current_project))

    def navigate_to(self, path_item):
        """새로운 경로로 이동합니다."""
        if path_item not in self.navigation_path:
            self.navigation_path.append(path_item)
            self.update_navigation(path_item)  # 현재 경로 아이템 전달
            self.logger.info(f"네비게이션 경로 추가: {path_item}")

    def navigate_home(self):
        """홈으로 돌아갑니다."""
        self.navigation_path = ["홈"]
        self.update_navigation(None)  # 홈으로 돌아가기
        self.logger.info("홈으로 이동")
        # TODO: 홈 화면 표시 로직 추가

    def navigate_back(self):
        """이전 경로로 돌아갑니다."""
        if len(self.navigation_path) > 1:
            self.navigation_path.pop()
            # 이전 경로 아이템을 전달
            prev_item = self.navigation_path[-1] if len(self.navigation_path) > 1 else None
            self.update_navigation(prev_item)
            self.logger.info("이전 경로로 이동")
            # TODO: 이전 화면 표시 로직 추가

    def show_new_project_dialog(self):
        """새 프로젝트 다이얼로그 표시"""
        dialog = ProjectDialog(self)
        if dialog.exec() == ProjectDialog.Accepted:
            self.init_projects_layout()  # 프로젝트 목록 새로고침

    def show_projects(self):
        """프로젝트 목록 표시 및 새로고침"""
        self.logger.info("프로젝트 목록 새로고침")
        self.init_projects_layout()
        
        # 네비게이션 업데이트
        self.current_project = None
        self.update_navigation(None)  # 홈으로 돌아가기

    def reorder_cards(self, source_card, target_card):
        """프로젝트 카드 순서 변경"""
        try:
            # 스크롤 영역과 컨테이너 찾기
            scroll_area = self.ui.projects_container.findChild(QScrollArea)
            if not scroll_area:
                return
                
            outer_container = scroll_area.widget()
            if not outer_container:
                return
                
            container = outer_container.findChild(QWidget, "scrollAreaWidgetContents")
            if not container:
                return
                
            layout = container.layout()
            if not layout:
                return
            
            # 현재 레이아웃에서 카드들의 순서를 가져옴
            cards = []
            for i in range(layout.count()):
                widget = layout.itemAt(i).widget()
                if isinstance(widget, ProjectCard):
                    cards.append(widget)
            
            # 소스 카드와 타겟 카드의 인덱스 찾기
            source_idx = cards.index(source_card)
            target_idx = cards.index(target_card)
            
            # 카드 순서 변경
            cards.insert(target_idx, cards.pop(source_idx))
            
            # 레이아웃 재구성
            for i in reversed(range(layout.count())):
                layout.itemAt(i).widget().setParent(None)
            
            for card in cards:
                layout.addWidget(card)
                
            # 프로젝트 데이터 순서도 변경
            self.projects = self.load_projects_from_json()
            self.projects.insert(target_idx, self.projects.pop(source_idx))
            
            # 파일 경로 설정
            if os.name == 'nt':  # Windows
                data_dir = os.path.join(os.getenv('LOCALAPPDATA', ''), 'UPSDATA', 'S-DIA')
            else:  # Linux/Mac
                data_dir = os.path.expanduser('~/.upsdata/s-dia')
            
            projects_path = os.path.join(data_dir, 'projects.json')
            
            # 프로젝트 목록 저장
            with open(projects_path, 'w', encoding='utf-8') as f:
                json.dump(self.projects, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            self.logger.error(f"카드 순서 변경 중 오류 발생: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())

    def load_projects(self):
        """프로젝트 목록 로드"""
        try:
            with open('projects.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
            
    def save_projects(self, projects):
        """프로젝트 목록 저장"""
        with open('projects.json', 'w', encoding='utf-8') as f:
            json.dump(projects, f, ensure_ascii=False, indent=2)

class FlowLayout(QLayout):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._item_list = []
        self._spacing = 0

    def addItem(self, item):
        self._item_list.append(item)

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)
        return None

    def setSpacing(self, spacing):
        self._spacing = spacing

    def spacing(self):
        return self._spacing

    def expandingDirections(self):
        return Qt.Orientations()

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())
        return size

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 200  # 카드 높이 고정
        spacing = self._spacing

        # 사용 가능한 전체 너비
        available_width = rect.width()
        
        # 최소 카드 너비
        min_card_width = 300
        
        # 전체 아이템 수
        total_items = len(self._item_list)
        if total_items == 0:
            return 0
            
        # 최대로 가능한 열 수 계산 (최소 크기 기준)
        max_columns = max(1, (available_width + spacing) // (min_card_width + spacing))
        
        # 현재 줄에 들어갈 수 있는 최적의 열 수 계산
        optimal_columns = max_columns
        while optimal_columns > 1:
            card_width = (available_width - (optimal_columns - 1) * spacing) // optimal_columns
            if card_width >= min_card_width:
                break
            optimal_columns -= 1
            
        # 카드 너비 계산 (모든 카드가 동일한 크기)
        card_width = (available_width - (optimal_columns - 1) * spacing) // optimal_columns
        card_width = max(min_card_width, card_width)
        
        if not test_only:
            # 카드 배치
            current_row = 0
            current_col = 0
            
            for item in self._item_list:
                widget = item.widget()
                if not widget:
                    continue
                    
                # 현재 위치 계산
                x = rect.x() + current_col * (card_width + spacing)
                y_pos = rect.y() + current_row * (line_height + spacing)
                
                # 위젯 크기 설정
                item.setGeometry(QRect(x, y_pos, card_width, line_height))
                
                # 다음 위치 계산
                current_col += 1
                if current_col >= optimal_columns:
                    current_col = 0
                    current_row += 1
        
        # 전체 높이 계산
        total_rows = (total_items + optimal_columns - 1) // optimal_columns
        total_height = total_rows * line_height + (total_rows - 1) * spacing
        
        return total_height 