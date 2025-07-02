from PySide6.QtWidgets import (QDialog, QMessageBox, QLineEdit, QComboBox, QPushButton, 
                              QTableWidget, QTableWidgetItem, QCheckBox, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QMenu, QFileDialog, QHeaderView, QStyledItemDelegate, QApplication)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QAction, QIcon, QMovie, QColor
from PySide6.QtCore import Qt, QEvent, QTimer, QSize
from PySide6.QtUiTools import QUiLoader
import os
import sys
import logging
import platform
import uuid
import json

from ui.database import add_flow, get_flow_list, update_flow

from ..common.context_menu import CustomContextMenuFilter
from src.ui.components.message_dialog import MessageDialog

class FlowDialog(QDialog):
    def __init__(self, parent=None, flow=None):
        super().__init__(parent)

        self.parent = parent
        self.flow = flow  # 수정할 흐름 데이터 저장
        self.logger = logging.getLogger(__name__)
        self.context_menu_filter = CustomContextMenuFilter()
        
        # 다이얼로그 크기 고정
        self.setFixedSize(420, 278)  # 너비 420px, 높이 278px로 고정
        
        # 다이얼로그 제목 설정
        self.setWindowTitle("흐름 수정" if flow else "흐름 추가")
        
        self.loading_overlay = None  # 오버레이 위젯 참조용
        
        self.setup_ui()
        
        # 크기 변경 이벤트 처리
        self.installEventFilter(self)

    def setup_ui(self):
        try:
            # UI 파일 로드
            loader = QUiLoader()
            self.ui = loader.load("src/ui/dialogs/flow_dialog.ui")
            if not self.ui:
                self.logger.error("흐름 다이얼로그 UI 파일을 로드할 수 없습니다.")
                return

            # 위젯 참조
            self.title_label = self.ui.findChild(QLabel, "title_label")
            self.name_input = self.ui.findChild(QLineEdit, "name_input")
            self.data_input = self.ui.findChild(QComboBox, "data_input")
            self.output_input = self.ui.findChild(QLineEdit, "output_input")
            self.save_button = self.ui.findChild(QPushButton, "save_button")
            self.cancel_button = self.ui.findChild(QPushButton, "cancel_button")

            self.title_label.setText("흐름 수정" if self.flow else "흐름 추가")

            # 데이터 소스 목록 로드
            if os.name == 'nt':  # Windows
                data_dir = os.path.join(os.getenv('LOCALAPPDATA', ''), 'UPSDATA', 'S-DIA', 'projects')
            else:  # Linux/Mac
                data_dir = os.path.expanduser('~/.upsdata/s-dia/projects')
            
            # 프로젝트 UUID 디렉토리
            project_dir = os.path.join(data_dir, self.parent.project_data.get('uuid', ''))
            datasource_path = os.path.join(project_dir, 'datasource.json')
            
            # 데이터 소스 목록 로드
            data_sources = []
            if os.path.exists(datasource_path):
                with open(datasource_path, 'r', encoding='utf-8') as f:
                    try:
                        data_sources = json.load(f)
                    except json.JSONDecodeError:
                        data_sources = []

            # 데이터 소스 목록을 콤보박스에 추가
            self.data_input.clear()
            self.data_sources = {}  # 데이터 소스 정보 저장용 딕셔너리
            for source in data_sources:
                name = source.get('name', '')
                uuid = source.get('uuid', '')
                self.data_input.addItem(name)
                self.data_sources[name] = source

            # 컨텍스트 메뉴 필터 적용
            self.name_input.installEventFilter(self.context_menu_filter)
            self.output_input.installEventFilter(self.context_menu_filter)

            # 시그널 연결
            self.save_button.clicked.connect(self.accept)
            self.cancel_button.clicked.connect(self.reject)
            self.name_input.textChanged.connect(self.update_output_path)  # 흐름명 변경 시 출력 경로 업데이트

            # 레이아웃 설정
            self.setLayout(self.ui.layout())
            
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
                QLineEdit {
                    padding: 8px 12px;
                    border: 1px solid #ced4da;
                    border-radius: 4px;
                    background-color: #ffffff;
                    font-size: 14px;
                    min-height: 20px;
                    color: #495057;
                }
                QLineEdit:focus {
                    border: 1px solid #80bdff;
                    outline: 0;
                }
                QPushButton {
                    color: #495057;
                    background-color: #e9ecef;
                    border: 1px solid #ced4da;
                    padding: 8px;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #dee2e6;
                }
                QPushButton#save_button {
                    color: #fff;
                    background-color: #007bff;
                    border-color: #007bff;
                    font-weight: bold;
                }
                QPushButton#save_button:hover {
                    color: #fff;
                    background-color: #0069d9;
                    border-color: #0062cc;
                }
                QPushButton#save_button:pressed {
                    background-color: #0062cc;
                    border-color: #005cbf;
                }
            """)

            # 초기 출력 경로 설정
            self.update_output_path()
            
        except Exception as e:
            self.logger.error(f"흐름 다이얼로그 UI 설정 중 오류 발생: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())

    def update_output_path(self):
        """흐름명에 따라 출력 경로를 업데이트합니다."""
        try:
            name = self.name_input.text().strip()
            if not name:
                self.output_input.setText("")
                return

            # 프로젝트의 data_directory 사용
            project_dir = self.parent.project_data.get('data_directory', '')
            if not project_dir or not os.path.exists(project_dir):
                self.logger.error("프로젝트 디렉토리를 찾을 수 없습니다.")
                self.output_input.setText("")
                return
            
            # 출력 경로 설정
            output_path = os.path.join(project_dir, f"{name}.parquet")

            self.output_input.setText(output_path)
            
        except Exception as e:
            self.logger.error(f"출력 경로 업데이트 중 오류 발생: {str(e)}")
            self.output_input.setText("")

    def accept(self):
        """저장 버튼 클릭 시 처리"""
        try:
            # 입력값 검증
            name = self.name_input.text().strip()  # trim 처리
            selected_data_source = self.data_input.currentText()
            if not name:
                MessageDialog.warning(self, "입력 오류", "흐름 명을 입력하세요.")
                self.name_input.setFocus()
                return
            if not selected_data_source:
                MessageDialog.warning(self, "입력 오류", "입력 데이터를 선택하세요.")
                self.data_input.setFocus()
                return
            # 플로우명 중복 체크
            flows = get_flow_list(self.parent.project_data.get('uuid', ''))
            # 중복 체크 (수정 시 자신의 이름은 제외)
            for flow in flows:
                if flow.get('name', '').strip() == name:
                    # 수정 중인 흐름이면 중복 체크에서 제외
                    if self.flow and flow.get('uuid') == self.flow.get('uuid'):
                        continue
                    MessageDialog.warning(self, "입력 오류", f"'{name}' 흐름명이 이미 존재합니다.")
                    self.name_input.setFocus()
                    return
            # 선택된 데이터 소스의 UUID 가져오기
            data_source = self.data_sources.get(selected_data_source)
            if not data_source:
                MessageDialog.warning(self, "입력 오류", "선택한 데이터 소스를 찾을 수 없습니다.")
                return
            # 플로우 데이터 생성
            flow_data = {
                'uuid': self.flow.get('uuid') if self.flow else str(uuid.uuid4()),  # 수정 시 기존 UUID 유지
                'name': name,
                'data_source_uuid': data_source.get('uuid'),
                'processes': self.flow.get('processes', []) if self.flow else [],  # 수정 시 기존 노드 유지
            }
            # 플로우 목록에 추가 또는 업데이트
            if self.flow:  # 수정인 경우
                update_flow(self.parent.project_data.get('uuid', ''), flow_data)
            else:  # 새로 추가하는 경우
                add_flow(self.parent.project_data.get('uuid', ''), flow_data)
            # 부모 위젯의 플로우 목록 새로고침
            if hasattr(self.parent, 'load_flows'):
                self.parent.load_flows()
            # 모든 검증을 통과하면 부모 클래스의 accept() 호출
            super().accept()
        except Exception as e:
            self.logger.error(f"흐름 저장 중 오류 발생: {str(e)}")
            MessageDialog.critical(self, "오류", f"흐름 저장 중 오류가 발생했습니다.\n{str(e)}")

    def eventFilter(self, obj, event):
        """이벤트 필터"""
        if obj == self and event.type() == QEvent.Type.Resize:
            # 다이얼로그 크기가 변경될 때 내부 위젯 크기 조절
            self.adjust_widget_sizes()
        return super().eventFilter(obj, event)

    def adjust_widget_sizes(self):
        """내부 위젯들의 크기를 조절합니다."""
        try:
            # 다이얼로그의 현재 크기
            dialog_width = self.width()
            dialog_height = self.height()
            
            # TODO: 필요한 위젯 크기 조절 로직 구현
            
        except Exception as e:
            self.logger.error(f"위젯 크기 조절 중 오류 발생: {str(e)}") 