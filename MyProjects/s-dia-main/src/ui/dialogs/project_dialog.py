import os
import json
import platform
import logging
import uuid
from PySide6.QtWidgets import QDialog, QFileDialog, QMenu, QMessageBox, QLineEdit, QTextEdit, QPushButton
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from ..common.context_menu import CustomContextMenuFilter
from datetime import datetime

class ProjectDialog(QDialog):
    def __init__(self, parent=None, project_data=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.project_data = project_data
        
        # UI 로드
        loader = QUiLoader()
        self.ui = loader.load("src/ui/dialogs/project_dialog.ui")
        
        # 다이얼로그 설정
        self.setFixedSize(self.ui.size())
        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
        
        # 스타일시트 설정
        self.setStyleSheet("""
            QDialog {
                background-color: #e9ecef;
            }
            QLabel {
                color: #000000;
                font-size: 14px;
                background-color: transparent;
            }
            QLineEdit, QTextEdit {
                padding: 8px 12px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: #ffffff;
                font-size: 14px;
                min-height: 20px;
                color: #495057;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #80bdff;
                border-color: #80bdff;
                outline: 0;
            }
            QPushButton {
                color: #495057;
                background-color: #ffffff;
                border: 1px solid #ced4da;
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
            }
            QPushButton#create_button {
                color: #fff;
                background-color: #007bff;
                border-color: #007bff;
                font-weight: bold;
            }
            QPushButton#create_button:hover {
                color: #fff;
                background-color: #0069d9;
                border-color: #0062cc;
            }
            QPushButton#create_button:pressed {
                background-color: #0062cc;
                border-color: #005cbf;
            }
            QFrame#form_container {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #dee2e6;
            }
        """)
        
        # UI를 현재 다이얼로그의 레이아웃으로 설정
        if self.layout() is None:
            self.setLayout(self.ui.layout())
            
        # UI 요소 참조 저장
        self.name_input = self.ui.name_input
        self.description_input = self.ui.description_input
        self.data_directory_input = self.ui.data_input
        
        # 버튼 연결
        self.ui.browse_button.clicked.connect(self.browse_directory)
        self.ui.create_button.clicked.connect(self.validate_and_accept)
        self.ui.cancel_button.clicked.connect(self.reject)
        self.ui.cancel_button.setStyleSheet("""
            QPushButton {
                color: #495057;
                background-color: #ffffff;
                border: 1px solid #ced4da;
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
            }
        """)
        self.ui.create_button.setStyleSheet("""
            QPushButton#create_button {
                color: #fff;
                background-color: #007bff;
                border-color: #007bff;
                /* box-shadow: none; */
                font-weight: bold;
            }
            QPushButton#create_button:hover {
                color: #fff;
                background-color: #0069d9;
                border-color: #0062cc;
            }
            QPushButton#create_button:pressed {
                background-color: #0062cc;
                border-color: #005cbf;
            }
        """)
        
        # 컨텍스트 메뉴 필터 설정
        self.context_menu_filter = CustomContextMenuFilter()
        self.name_input.installEventFilter(self.context_menu_filter)
        self.data_directory_input.installEventFilter(self.context_menu_filter)
        self.description_input.installEventFilter(self.context_menu_filter)
        
        # 프로젝트 파일 경로 설정
        if platform.system() == 'Windows':
            self.projects_dir = os.path.join(os.getenv('LOCALAPPDATA', ''), 'UPSDATA', 'S-DIA')
        else:
            self.projects_dir = os.path.expanduser('~/.upsdata/s-dia')
            
        self.projects_file = os.path.join(self.projects_dir, 'projects.json')
        
        # 프로젝트 디렉토리 생성
        os.makedirs(self.projects_dir, exist_ok=True)
        
        if project_data:
            # 기존 프로젝트 데이터로 필드 초기화
            self.name_input.setText(project_data.get('name', ''))
            self.description_input.setPlainText(project_data.get('description', ''))
            self.data_directory_input.setText(project_data.get('data_directory', ''))
            self.setWindowTitle("프로젝트 수정")
            self.ui.title_label.setText("프로젝트 수정")  # 제목 라벨 수정
            self.ui.create_button.setText("수정")
            
            # 커서를 처음으로 이동
            self.name_input.setCursorPosition(0)
        else:
            self.setWindowTitle("새 프로젝트")
            self.ui.title_label.setText("새 프로젝트")  # 제목 라벨 수정
            self.ui.create_button.setText("생성")
        
    def browse_directory(self):
        """데이터 폴더 선택"""
        # 현재 입력된 경로가 있으면 해당 경로에서 시작
        start_path = self.ui.data_input.text().strip()
        
        # 현재 경로가 없거나 유효하지 않은 경우
        if not start_path or not os.path.exists(start_path):
            # 이전에 선택한 경로가 있는지 확인
            if os.path.exists(self.projects_file):
                try:
                    with open(self.projects_file, 'r', encoding='utf-8') as f:
                        projects = json.load(f)
                        if projects and isinstance(projects, list):
                            # 가장 최근 프로젝트의 데이터 폴더 경로
                            last_path = projects[-1].get('data_directory', '')
                            if last_path and os.path.exists(os.path.dirname(last_path)):
                                start_path = os.path.dirname(last_path)
                except Exception:
                    pass
        
        # 시작 경로가 없으면 기본 경로 사용
        if not start_path or not os.path.exists(start_path):
            start_path = os.path.expanduser('~')
        
        directory = QFileDialog.getExistingDirectory(self, "데이터 폴더 선택", start_path)
        if directory:
            # Windows인 경우 구분자를 백슬래시로 변경
            if platform.system() == 'Windows':
                directory = directory.replace('/', '\\')
            self.ui.data_input.setText(directory)
            
    def check_directory_permissions(self, directory):
        """디렉토리 권한 확인"""
        # 디렉토리 존재 여부 확인
        if not os.path.exists(directory):
            QMessageBox.critical(self, "경로 오류", 
                               "데이터 디렉토리가 존재하지 않습니다.\n"
                               "디렉토리를 먼저 생성해주세요.")
            return False
            
        # Windows에서는 실제 파일 생성/삭제로 권한 테스트
        if platform.system() == 'Windows':
            test_file = os.path.join(directory, '.write_test')
            try:
                # 파일 생성 시도
                with open(test_file, 'w') as f:
                    f.write('test')
                # 성공하면 파일 삭제
                os.remove(test_file)
                return True
            except (IOError, OSError, PermissionError):
                QMessageBox.critical(self, "권한 오류", 
                                   "데이터 디렉토리에 쓰기 권한이 없습니다.\n"
                                   "디렉토리의 권한을 확인해주세요.")
                return False
        else:
            # 다른 OS에서는 access() 사용
            if not os.access(directory, os.W_OK):
                QMessageBox.critical(self, "권한 오류", 
                                   "데이터 디렉토리에 쓰기 권한이 없습니다.\n"
                                   "디렉토리의 권한을 확인해주세요.")
                return False
            
        return True
            
    def validate_and_accept(self):
        """필수 입력 항목 검증 및 프로젝트 저장"""
        try:
            # 입력값 검증
            name = self.name_input.text().strip()
            description = self.description_input.toPlainText().strip()
            data_directory = self.data_directory_input.text().strip()
            
            if not name:
                QMessageBox.warning(self, "입력 오류", "프로젝트 명을 입력하세요.")
                self.name_input.setFocus()
                return
                
            if not data_directory:
                QMessageBox.warning(self, "입력 오류", "데이터 폴더를 선택하세요.")
                self.data_directory_input.setFocus()
                return
            
            # 디렉토리 권한 확인
            if not self.check_directory_permissions(data_directory):
                self.data_directory_input.setFocus()
                return
            
            # 프로젝트 데이터 준비
            project_data = {
                'name': name,
                'description': description,
                'data_directory': data_directory,
                'modified_at': datetime.now().isoformat()
            }
            
            # 프로젝트 수정 시 기존 UUID 유지
            if self.project_data and 'uuid' in self.project_data:
                project_data['uuid'] = self.project_data['uuid']
            else:
                project_data['uuid'] = str(uuid.uuid4())
            
            # 기존 프로젝트 목록 로드
            projects = []
            if os.path.exists(self.projects_file):
                with open(self.projects_file, 'r', encoding='utf-8') as f:
                    projects = json.load(f)
                    
            if self.project_data:
                # 프로젝트 수정 모드
                for i, project in enumerate(projects):
                    if project.get('uuid') == self.project_data.get('uuid'):
                        # 기존 프로젝트 정보 유지
                        project_data['created_at'] = project.get('created_at', datetime.now().isoformat())
                        projects[i] = project_data
                        break
            else:
                # 새 프로젝트 생성 모드
                project_data['created_at'] = datetime.now().isoformat()
                projects.append(project_data)
                
            # 프로젝트 목록 저장
            with open(self.projects_file, 'w', encoding='utf-8') as f:
                json.dump(projects, f, ensure_ascii=False, indent=2)
                
            super().accept()
            
        except Exception as e:
            self.logger.error(f"프로젝트 저장 중 오류 발생: {str(e)}")
            QMessageBox.critical(self, "오류", f"프로젝트 저장 중 오류가 발생했습니다.\n{str(e)}") 