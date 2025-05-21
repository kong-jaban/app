from PySide6.QtWidgets import (QWidget, QMessageBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDialogButtonBox,
                              QTextEdit, QPushButton, QFrame, QListWidget, QListWidgetItem, QDialog,
                              QMainWindow, QComboBox, QFileDialog, QButtonGroup, QRadioButton, QMenu, QSizePolicy)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QTimer
from PySide6.QtUiTools import QUiLoader
import os
import sys
import logging
import json
import uuid
import platform

from utils.string_utils import get_file_extension

class DataSourceDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)

        self.data = data
        self.logger = logging.getLogger(__name__)
        self.setup_ui()

    def setup_ui(self):
        try:
            # UI 파일 로드
            loader = QUiLoader()
            self.ui = loader.load("src/ui/dialogs/data_source_dialog.ui")
            if not self.ui:
                self.logger.error("데이터 소스 다이얼로그 UI 파일을 로드할 수 없습니다.")
                return
            
            # 위젯 참조
            self.name_input = self.ui.findChild(QLineEdit, "name_input")
            self.data_path_input = self.ui.findChild(QLineEdit, "data_path_input")
            self.charset_input = self.ui.findChild(QComboBox, "charset_input")
            self.separator_input = self.ui.findChild(QComboBox, "separator_input")
            self.has_header_input = self.ui.findChild(QComboBox, "has_header_input")
            self.save_button = self.ui.findChild(QPushButton, "save_button")
            self.cancel_button = self.ui.findChild(QPushButton, "cancel_button")
            self.fs_explorer = self.ui.findChild(QPushButton, "fs_explorer")
            
            self.title_label = self.ui.findChild(QLabel, "title_label")
           
            # 콤보박스 스타일 적용
            for combo in [self.charset_input, self.separator_input, self.has_header_input]:

                view = combo.view()
                view.setItemAlignment(Qt.AlignCenter)

            # 수정 모드인 경우 기존 데이터 설정
            if self.data:
                self.title_label.setText("데이터 소스 수정")
                self.name_input.setText(self.data.get('name', ''))
                self.data_path_input.setText(self.data.get('data_path', ''))
                self.charset_input.setCurrentText(self.data.get('charset', 'UTF-8'))
                self.separator_input.setCurrentText(self.data.get('separator', ','))
                self.has_header_input.setCurrentText(self.data.get('has_header', '있음'))
                self.uuid = self.data.get('uuid', str(uuid.uuid4()))
            else:
                self.uuid = str(uuid.uuid4())
                self.title_label.setText("데이터 소스 추가")
            
            # 시그널 연결
            self.save_button.clicked.connect(self.accept)
            self.cancel_button.clicked.connect(self.reject)
            self.fs_explorer.clicked.connect(self.browse_data_path)

            # 레이아웃 설정
            self.setLayout(self.ui.layout())
            
        except Exception as e:
            self.logger.error(f"데이터 소스 다이얼로그 UI 설정 중 오류 발생: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())

    def accept(self):
        """저장 버튼 클릭 시 처리"""
        try:
            # 입력값 검증
            name = self.name_input.text().strip()
            data_path = self.data_path_input.text().strip()
            
            if not name:
                QMessageBox.warning(self, "입력 오류", "데이터 소스 명을 입력하세요.")
                self.name_input.setFocus()
                return
                
            if not data_path:
                QMessageBox.warning(self, "입력 오류", "원본 데이터를 선택택하세요.")
                self.data_path_input.setFocus()
                return
                
            if not os.path.exists(data_path):
                QMessageBox.warning(self, "입력 오류", "입력한 데이터 경로가 존재하지 않습니다.")
                self.data_path_input.setFocus()
                return
            
            # 모든 검증을 통과하면 부모 클래스의 accept() 호출
            super().accept()
            
        except Exception as e:
            self.logger.error(f"데이터 소스 저장 중 오류 발생: {str(e)}")
            QMessageBox.critical(self, "오류", f"데이터 소스 저장 중 오류가 발생했습니다.\n{str(e)}")

    def get_data(self):
        data_path = self.data_path_input.text()
        if data_path == '' or not os.path.exists(data_path):
            self.logger.error(f"데이터 소스 경로가 존재하지 않습니다. : {data_path}")
            return None
        
        data_type = get_file_extension(data_path.lower())

        if os.path.isdir(data_path):
            type = 'dir'
        else:
            type = 'file'


        return {
            'uuid': self.uuid,
            'name': self.name_input.text(),
            'type': type,
            'data_type': data_type,
            'data_path': self.data_path_input.text(),
            'charset': self.charset_input.currentText(),
            'separator': self.separator_input.currentText(),
            'has_header': self.has_header_input.currentText()
        }

            
    def validate_and_accept(self):
        """필수 입력 항목 검증"""
        data_path = self.data_path_input.text()
        if data_path == '':
            QMessageBox.warning(self, "입력 오류", f"원본 데이터를 선택택하세요.")
            self.ui.data_path_input.setFocus()
            return None        
        if not os.path.exists(data_path):
            QMessageBox.warning(self, "입력 오류", f"원본 데이터가 존재하지 않습니다.")
            self.ui.data_path_input.setFocus()
            return None


        if not self.ui.name_input.text().strip():
            QMessageBox.warning(self, "입력 오류", "데이터 소스 명을 입력하세요.")
            self.ui.name_input.setFocus()
            return
            
        data_dir = self.ui.data_input.text().strip()
        if not data_dir:
            QMessageBox.warning(self, "입력 오류", "데이터 디렉토리를 선택하세요.")
            self.ui.data_input.setFocus()
            return
            
        # 디렉토리 권한 확인
        if not self.check_directory_permissions(data_dir):
            self.ui.data_input.setFocus()
            return
            
        # 프로젝트 데이터 저장
        project_data = self.get_project_data()
        if self.save_project(project_data):
            self.accept()

    def browse_data_path(self):
        """데이터 파일/폴더 선택 (QMenu 방식)"""
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
        file_action = QAction("파일 선택", self)
        dir_action = QAction("폴더 선택", self)
        menu.addAction(file_action)
        menu.addAction(dir_action)

        def select_file():
            start_path = self.data_path_input.text().strip()
            if not start_path or not os.path.exists(start_path):
                start_path = os.path.expanduser('~')
            file_path, _ = QFileDialog.getOpenFileName(
                self, "원본 데이터 파일 선택", start_path,
                "CSV 파일 (*.csv);;.parquet 파일 (*.parquet);;모든 파일 (*.*)"
            )
            if file_path:
                if platform.system() == 'Windows':
                    file_path = file_path.replace('/', '\\')
                self.data_path_input.setText(file_path)

        def select_dir():
            start_path = self.data_path_input.text().strip()
            if not start_path or not os.path.exists(start_path):
                start_path = os.path.expanduser('~')
            dir_path = QFileDialog.getExistingDirectory(
                self, "원본 데이터 폴더 선택", start_path
            )
            if dir_path:
                if platform.system() == 'Windows':
                    dir_path = dir_path.replace('/', '\\')
                self.data_path_input.setText(dir_path)

        file_action.triggered.connect(select_file)
        dir_action.triggered.connect(select_dir)
        menu.exec_(self.fs_explorer.mapToGlobal(self.fs_explorer.rect().bottomLeft()))

class ProjectPanel(QWidget):
    def __init__(self, project_data, parent=None):
        super().__init__(parent)
        self.project_data = project_data
        self.parent = parent
        self.logger = logging.getLogger(__name__)        
        self.setup_ui()
        
    def setup_ui(self):
        try:
            # UI 파일 로드
            loader = QUiLoader()
            self.ui = loader.load("src/ui/project_panel.ui")
            if not self.ui:
                self.logger.error("프로젝트 메뉴 패널 UI 파일을 로드할 수 없습니다.")
                return
            
            # 위젯 참조
            self.project_name = self.ui.findChild(QLabel, "project_name")
            self.project_name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            self.project_name.setMinimumWidth(0)
            self.update_project_name_elision()  # 초기 이름 줄임 처리
            
            self.desc_text = self.ui.findChild(QTextEdit, "desc_text")
            self.data_list = self.ui.findChild(QListWidget, "data_list")
            self.flow_list = self.ui.findChild(QListWidget, "flow_list")
            self.data_add_btn = self.ui.findChild(QPushButton, "data_add_btn")
            self.flow_add_btn = self.ui.findChild(QPushButton, "flow_add_btn")
            self.close_btn = self.ui.findChild(QPushButton, "close_btn")
            
            # 프로젝트 정보 설정
            self.desc_text.setPlainText(self.project_data.get('description', ''))
            
            # 데이터 소스 목록 로드
            self.load_data_sources()
            
            # 이미지 경로 설정
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            
            add_icon_path = os.path.join(base_path, 'ui', 'resources', 'images', 'add.png')
            add_hover_icon_path = os.path.join(base_path, 'ui', 'resources', 'images', 'add-hover.png')
            
            # 버튼 스타일 설정
            self.data_add_btn.setStyleSheet(f"""
                QPushButton {{
                    image: url({add_icon_path.replace('\\', '/')});
                    border: none;
                    background: transparent;
                }}
                QPushButton:hover {{
                    image: url({add_hover_icon_path.replace('\\', '/')});
                }}
            """)
            
            self.flow_add_btn.setStyleSheet(f"""
                QPushButton {{
                    image: url({add_icon_path.replace('\\', '/')});
                    border: none;
                    background: transparent;
                }}
                QPushButton:hover {{
                    image: url({add_hover_icon_path.replace('\\', '/')});
                }}
            """)
            
            # 시그널 연결
            self.data_add_btn.clicked.connect(self.add_data_source)
            self.flow_add_btn.clicked.connect(self._on_add_flow)
            self.close_btn.clicked.connect(self._on_close)
            
            self.data_list.setContextMenuPolicy(Qt.CustomContextMenu)
            self.data_list.customContextMenuRequested.connect(self.show_data_source_menu)
            
            # 레이아웃 설정
            self.setLayout(self.ui.layout())
            
        except Exception as e:
            self.logger.error(f"프로젝트 패널 UI 설정 중 오류 발생: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            
    def load_data_sources(self):
        """데이터 소스 목록을 로드하고 표시합니다."""
        try:
            # 프로젝트 디렉토리 경로 설정
            if os.name == 'nt':  # Windows
                data_dir = os.path.join(os.getenv('LOCALAPPDATA', ''), 'UPSDATA', 'S-DIA', 'projects')
            else:  # Linux/Mac
                data_dir = os.path.expanduser('~/.upsdata/s-dia/projects')
            
            # 프로젝트 UUID 디렉토리
            project_dir = os.path.join(data_dir, self.project_data.get('uuid', ''))
            datasource_path = os.path.join(project_dir, 'datasource.json')
            
            # 데이터 소스 목록 로드
            data_sources = []
            if os.path.exists(datasource_path):
                with open(datasource_path, 'r', encoding='utf-8') as f:
                    data_sources = json.load(f)
            
            # 리스트 위젯 초기화
            self.ui.data_list.clear()
            
            if not data_sources or len(data_sources) == 0:
                # 데이터 소스가 없는 경우 메시지 표시
                item = QListWidgetItem("등록된 데이터 소스가 없습니다.")
                item.setTextAlignment(Qt.AlignCenter)
                font = item.font()
                font.setItalic(True)
                item.setFont(font)
                item.setFlags(item.flags() & ~Qt.ItemIsSelectable & ~Qt.ItemIsEnabled)  # 선택과 활성화 비활성화
                self.ui.data_list.addItem(item)
            else:
                # 데이터 소스 목록 표시
                for source in data_sources:
                    name = source.get('name', '')
                    item = QListWidgetItem(name)
                    
                    # 리스트 위젯의 너비 계산
                    list_width = self.ui.data_list.viewport().width()
                    # 텍스트 너비 계산
                    font_metrics = self.ui.data_list.fontMetrics()
                    text_width = font_metrics.horizontalAdvance(name)
                    
                    # 텍스트가 리스트 너비보다 길 경우에만 툴팁 설정
                    if text_width > list_width - 20:  # 20은 여유 공간
                        item.setToolTip(name)
                    
                    self.ui.data_list.addItem(item)
                    
        except Exception as e:
            self.logger.error(f"데이터 소스 로드 중 오류 발생: {str(e)}")
            
    def add_data_source(self):
        """새 데이터 소스를 추가합니다."""
        try:
            dialog = DataSourceDialog(self, None)
            if dialog.exec() == QDialog.Accepted:
                data = dialog.get_data()
                if data == None:
                    return
                # 프로젝트 디렉토리 경로 설정
                if os.name == 'nt':  # Windows
                    data_dir = os.path.join(os.getenv('LOCALAPPDATA', ''), 'UPSDATA', 'S-DIA', 'projects')
                else:  # Linux/Mac
                    data_dir = os.path.expanduser('~/.upsdata/s-dia/projects')
                
                # 프로젝트 UUID 디렉토리
                project_dir = os.path.join(data_dir, self.project_data.get('uuid', ''))
                datasource_path = os.path.join(project_dir, 'datasource.json')
                
                # 기존 데이터 소스 목록 로드
                data_sources = []
                if os.path.exists(datasource_path):
                    with open(datasource_path, 'r', encoding='utf-8') as f:
                        data_sources = json.load(f)
                
                # 새 데이터 소스 추가
                data_sources.append(data)
                
                # 데이터 소스 목록 저장
                with open(datasource_path, 'w', encoding='utf-8') as f:
                    json.dump(data_sources, f, ensure_ascii=False, indent=2)
                
                # 데이터 소스 목록 새로고침
                self.load_data_sources()
                
        except Exception as e:
            self.logger.error(f"데이터 소스 추가 중 오류 발생: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            
    def _on_add_flow(self):
        """플로우 추가 버튼 클릭 처리"""
        if self.parent:
            self.parent._on_add_flow(self.project_data)
            
    def _on_close(self):
        """닫기 버튼 클릭 처리"""
        if self.parent:
            self.parent.close_project_panel()

    def show_data_source_menu(self, pos):
        item = self.data_list.itemAt(pos)
        if not item or not item.isSelected() or not (item.flags() & Qt.ItemIsEnabled):
            return
        # 데이터 소스 이름으로 데이터 찾기
        name = item.text()
        # 데이터 소스 목록 로드
        data_sources = self._get_current_data_sources()
        data = next((d for d in data_sources if d.get('name') == name), None)
        if not data:
            return
        menu = QMenu(self)
        edit_action = menu.addAction('수정')
        dist_action = menu.addAction('분포')
        del_action = menu.addAction('삭제')
        action = menu.exec_(self.data_list.viewport().mapToGlobal(pos))
        if action == edit_action:
            self.edit_data_source(data)
        elif action == dist_action:
            # TODO: 분포 기능 구현 필요
            pass
        elif action == del_action:
            self.delete_data_source(data)

    def delete_data_source(self, data):
        name = data.get('name', '')
        reply = QMessageBox.question(
            self,
            '데이터 소스 삭제',
            f'"{name}" 를 정말 삭제하겠습니까?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # 데이터 소스 목록 불러오기
            data_sources = self._get_current_data_sources()
            # uuid로 삭제
            data_sources = [d for d in data_sources if d.get('uuid') != data.get('uuid')]
            # 저장
            if os.name == 'nt':
                data_dir = os.path.join(os.getenv('LOCALAPPDATA', ''), 'UPSDATA', 'S-DIA', 'projects')
            else:
                data_dir = os.path.expanduser('~/.upsdata/s-dia/projects')
            project_dir = os.path.join(data_dir, self.project_data.get('uuid', ''))
            datasource_path = os.path.join(project_dir, 'datasource.json')
            with open(datasource_path, 'w', encoding='utf-8') as f:
                json.dump(data_sources, f, ensure_ascii=False, indent=2)
            self.load_data_sources()

    def _get_current_data_sources(self):
        # 현재 프로젝트의 데이터 소스 목록을 반환
        if os.name == 'nt':
            data_dir = os.path.join(os.getenv('LOCALAPPDATA', ''), 'UPSDATA', 'S-DIA', 'projects')
        else:
            data_dir = os.path.expanduser('~/.upsdata/s-dia/projects')
        project_dir = os.path.join(data_dir, self.project_data.get('uuid', ''))
        datasource_path = os.path.join(project_dir, 'datasource.json')
        data_sources = []
        if os.path.exists(datasource_path):
            with open(datasource_path, 'r', encoding='utf-8') as f:
                data_sources = json.load(f)
        return data_sources

    def edit_data_source(self, data):
        dialog = DataSourceDialog(self, data)
        if dialog.exec() == QDialog.Accepted:
            new_data = dialog.get_data()
            if new_data is None:
                return
            # 기존 데이터 소스 목록 불러오기
            data_sources = self._get_current_data_sources()
            # 이름으로 기존 데이터 소스 찾기
            for idx, d in enumerate(data_sources):
                if d.get('uuid') == data.get('uuid'):
                    data_sources[idx] = new_data
                    break
            # 저장
            if os.name == 'nt':
                data_dir = os.path.join(os.getenv('LOCALAPPDATA', ''), 'UPSDATA', 'S-DIA', 'projects')
            else:
                data_dir = os.path.expanduser('~/.upsdata/s-dia/projects')
            project_dir = os.path.join(data_dir, self.project_data.get('uuid', ''))
            datasource_path = os.path.join(project_dir, 'datasource.json')
            with open(datasource_path, 'w', encoding='utf-8') as f:
                json.dump(data_sources, f, ensure_ascii=False, indent=2)
            self.load_data_sources() 

    def update_project_name_elision(self):
        """프로젝트 이름의 줄임 처리를 업데이트합니다."""
        metrics = self.project_name.fontMetrics()
        # 프로젝트명 표시 너비를 211px로 고정
        max_width = 211
        
        project_name = self.project_data.get('name', '')
        
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
            self.project_name.setText(display_name)
            self.project_name.setToolTip(project_name)  # 전체 이름을 툴팁으로 표시
        else:
            self.project_name.setText(project_name)
            self.project_name.setToolTip("")  # 툴팁 제거

    def resizeEvent(self, event):
        """창 크기가 변경될 때 호출됩니다."""
        super().resizeEvent(event)
        self.update_project_name_elision()  # 이름 줄임 처리 업데이트

    def showEvent(self, event):
        """패널이 처음 표시될 때 호출됩니다."""
        super().showEvent(event)
        # 이름 줄임 처리 업데이트
        QTimer.singleShot(0, self.update_project_name_elision) 