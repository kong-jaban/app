from PySide6.QtWidgets import (QWidget, QMessageBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDialogButtonBox,
                              QTextEdit, QPushButton, QFrame, QListWidget, QListWidgetItem, QDialog,
                              QMainWindow, QComboBox, QFileDialog, QButtonGroup, QRadioButton, QMenu, QSizePolicy,
                              QTableView, QHeaderView, QScrollArea)
from PySide6.QtGui import QAction, QStandardItemModel, QStandardItem, QDesktopServices
from PySide6.QtCore import Qt, QTimer, QUrl, Signal
from PySide6.QtUiTools import QUiLoader
import os
import sys
import logging
import json
import uuid
import platform
import pandas as pd

from ..components.distribution_viewer import DistributionViewer
from ui.flow_widget import Flow
from utils.string_utils import get_file_extension
from ..dialogs.data_source_dialog import DataSourceDialog
from ..dialogs.flow_dialog import FlowDialog
from ..common.context_menu import CustomContextMenuFilter
from .flow_panel import FlowPanel
from ..database import delete_flow, get_datasource, get_datasources_list, add_datasource, delete_datasource, get_flow_list, reload_flow_from_file, update_datasource, get_datasource_by_name, get_flow_by_name
from src.ui.components.confirm_dialog import ConfirmDialog
from ..dialogs.flow_progress_dialog import FlowProgressDialog

class ProjectPanel(QWidget):
    """프로젝트 패널"""
    flow_selected = Signal(dict)  # 흐름 선택 시그널
    process_selected = Signal(dict)  # 처리 선택 시그널
    process_deleted = Signal(str)  # 처리 삭제 시그널 (flow_uuid를 전달)
    
    def __init__(self, project_data, parent=None):
        super().__init__(parent)
        self.project_data = project_data
        self.parent = parent
        self.logger = logging.getLogger(__name__)        
        self.context_menu_filter = CustomContextMenuFilter()
        self.selected_flow = None
        self.selected_process = None
        self.setup_ui()

        get_datasources_list(self.project_data.get('uuid', ''), True)

        
    list_scroll_style = """
                QListWidget {
                    background: transparent;
                    border: none;
                    color: #e9ecef;
                }
                QListWidget::item {
                    padding: 4px;
                    border-radius: 4px;
                }
                QListWidget::item:selected, QListWidget::item:hover {
                    background: #6c757d;
                }
                QListWidget:focus {
                    border: none;
                    outline: none;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #495057;
                    width: 8px;
                    margin: 0px;
                    position: absolute;
                    right: 0px;
                }
                QScrollBar::handle:vertical {
                    background: #adb5bd;
                    border-radius: 4px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #ced4da;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: transparent;
                }
            """
    def setup_ui(self):
        try:
            # UI 파일 로드
            loader = QUiLoader()
            self.ui = loader.load("src/ui/panels/project_panel.ui")
            if not self.ui:
                self.logger.error("프로젝트 메뉴 패널 UI 파일을 로드할 수 없습니다.")
                return
            
            # 위젯 참조
            self.project_name = self.ui.findChild(QLabel, "project_name")
            self.project_name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            self.project_name.setMinimumWidth(0)
            # 프로젝트명 폰트 크기 증가
            font = self.project_name.font()
            font.setPointSize(font.pointSize() + 1)
            self.project_name.setFont(font)
            
            self.desc_text = self.ui.findChild(QTextEdit, "desc_text")
            self.desc_text.installEventFilter(self.context_menu_filter)
            self.data_list = self.ui.findChild(QListWidget, "data_list")
            self.data_list.setStyleSheet(self.list_scroll_style)
            self.flow_list = self.ui.findChild(QListWidget, "flow_list")
            self.flow_list.setStyleSheet(self.list_scroll_style)
            self.open_folder_btn = self.ui.findChild(QPushButton, "open_folder_btn")
            self.data_add_btn = self.ui.findChild(QPushButton, "data_add_btn")
            self.flow_add_btn = self.ui.findChild(QPushButton, "flow_add_btn")
            self.close_btn = self.ui.findChild(QPushButton, "close_btn")
            
            # 닫기 버튼 폰트 크기 증가 및 스타일 개선
            close_font = self.close_btn.font()
            close_font.setPointSize(close_font.pointSize() + 1)
            self.close_btn.setFont(close_font)
            self.close_btn.setStyleSheet("""
                QPushButton#close_btn {
                    background-color: #339af0;
                    padding: 8px;
                    border-radius: 6px;
                    text-align: center;
                    font-size: 15px;
                    font-weight: bold;
                    border: 1px solid #228be6;
                    color: white;
                    min-height: 32px;
                }
                QPushButton#close_btn:hover {
                    background-color: #228be6;
                    border-color: #339af0;
                }
            """)
            
            # 프로젝트 정보 설정
            self.desc_text.setPlainText(self.project_data.get('description', ''))
            
            # 데이터 소스 목록 로드
            self.load_data_sources()
            
            # 플로우 목록 로드
            self.load_flows()
            
            # 이미지 경로 설정
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            
            add_icon_path = os.path.join(base_path, 'ui', 'resources', 'images', 'add.png')
            add_hover_icon_path = os.path.join(base_path, 'ui', 'resources', 'images', 'add-hover.png')

            open_folder_icon_path = os.path.join(base_path, 'ui', 'resources', 'images', 'icons8-folder-80.png')
            open_folder_hover_icon_path = os.path.join(base_path, 'ui', 'resources', 'images', 'icons8-opened-folder-80.png')
            # 버튼 스타일 설정
            self.open_folder_btn.setStyleSheet(f"""
                QPushButton {{
                    image: url({open_folder_icon_path.replace('\\', '/')});
                    border: none;
                    background: transparent;
                }}
                QPushButton:hover {{
                    image: url({open_folder_hover_icon_path.replace('\\', '/')});
                }}
            """)

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
            self.data_list.itemDoubleClicked.connect(self.on_data_source_double_clicked)
            
            # 흐름 목록 컨텍스트 메뉴 및 더블클릭 설정
            self.flow_list.setContextMenuPolicy(Qt.CustomContextMenu)
            self.flow_list.customContextMenuRequested.connect(self.show_flow_menu)
            self.flow_list.itemDoubleClicked.connect(self.on_flow_double_clicked)
            
            # 흐름 목록 클릭 이벤트 연결
            self.ui.flow_list.itemClicked.connect(self.on_flow_clicked)
            
            # 레이아웃 설정
            self.setLayout(self.ui.layout())
            self.update_project_name_elision()  # 초기 이름 줄임 처리

            self.open_folder_btn.clicked.connect(self.open_project_folder)
            self.open_folder_btn.setToolTip(f'프로젝트 폴더 "{self.project_data.get('data_directory')}" 열기')

            
        except Exception as e:
            self.logger.error(f"프로젝트 패널 UI 설정 중 오류 발생: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            
    def load_data_sources(self):
        """데이터 소스 목록을 로드하고 표시합니다."""
        data_sourceses = get_datasources_list(self.project_data.get('uuid', ''), True)
            
        # 리스트 위젯 초기화
        self.ui.data_list.clear()
            
        if not data_sourceses or len(data_sourceses) == 0:
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
            for source in data_sourceses:
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
            
    def add_data_source(self):
        """새 데이터 소스를 추가합니다."""
        try:
            dialog = DataSourceDialog(self, None)
            if dialog.exec() == QDialog.Accepted:
                data = dialog.get_data()
                if data == None:
                    return

                add_datasource(self.project_data.get('uuid', ''), data)
                
                # 데이터 소스 목록 새로고침
                self.load_data_sources()
                
        except Exception as e:
            self.logger.error(f"데이터 소스 추가 중 오류 발생: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            
    def _on_add_flow(self):
        """플로우 추가 버튼 클릭 처리"""
        try:
            dialog = FlowDialog(self)
            if dialog.exec() == QDialog.Accepted:
                # TODO: 플로우 저장 로직 구현
                pass
        except Exception as e:
            self.logger.error(f"플로우 추가 중 오류 발생: {str(e)}")
            QMessageBox.critical(self, "오류", f"플로우 추가 중 오류가 발생했습니다.\n{str(e)}")
            
    def _on_close(self):
        """닫기 버튼 클릭 처리"""
        if self.parent:
            self.parent.close_project_panel()

    def open_project_folder(self):
        """프로젝트 폴더 열기"""
        if self.project_data.get('data_directory', '') and \
            os.path.exists(self.project_data.get('data_directory')) and \
            os.path.isdir(self.project_data.get('data_directory')):
            path = os.path.normpath(self.project_data.get('data_directory'))
            url = QUrl.fromLocalFile(path)
            QDesktopServices.openUrl(url)
        else:
            QMessageBox.warning(self, "프로젝트 폴더 열기 오류", "프로젝트 폴더가 존재하지 않습니다.")

    def show_data_source_menu(self, pos):
        item = self.data_list.itemAt(pos)
        if not item or not item.isSelected() or not (item.flags() & Qt.ItemIsEnabled):
            return
        # 데이터 소스 이름으로 데이터 찾기
        name = item.text()
        # 데이터 소스 목록 로드
        data_sources = get_datasources_list(self.project_data.get('uuid', ''))
        data = next((d for d in data_sources if d.get('name') == name), None)
        if not data:
            return
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
            QMenu::separator {
                height: 1px;
                background: #dee2e6;
                margin: 5px 0px;
            }
        """)
        edit_action = menu.addAction('수정')
        dist_action = menu.addAction('분포')
        del_action = menu.addAction('삭제')
        action = menu.exec_(self.data_list.viewport().mapToGlobal(pos))
        if action == edit_action:
            self.edit_data_source(data)
        elif action == dist_action:
            self.show_distribution(data)
        elif action == del_action:
            self.delete_data_source(data)
    def show_distribution(self, data_source):
        try:
            # CSV 파일 읽기
            df = pd.read_csv(data_source['data_path'], encoding=data_source.get('charset', 'utf-8'))
            
            # 분포 뷰어 생성
            viewer = DistributionViewer(df, project_name=self.project_data.get('name', '프로젝트'))
            
            # 메인 윈도우의 프레임들 가져오기
            main_window = self.window()  # 현재 위젯의 최상위 윈도우를 가져옴
            left_frame = main_window.findChild(QFrame, "left_frame")
            right_frame = main_window.findChild(QFrame, "right_frame")
            
            if not left_frame or not right_frame:
                raise Exception("프레임을 찾을 수 없습니다.")
            
            # 좌측 프레임 설정
            if left_frame.layout():
                old_layout = left_frame.layout()
                while old_layout.count():
                    item = old_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                QWidget().setLayout(old_layout)
            
            # 우측 프레임 설정
            if right_frame.layout():
                old_layout = right_frame.layout()
                while old_layout.count():
                    item = old_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                QWidget().setLayout(old_layout)
            
            # 좌측 프레임에 컬럼 리스트 추가
            left_layout = QVBoxLayout(left_frame)
            left_layout.setContentsMargins(16, 16, 16, 16)
            left_layout.setSpacing(16)
            
            # 컬럼 리스트
            left_layout.addWidget(QLabel("컬럼 선택"))
            column_list = QListWidget()
            column_list.addItems(df.columns)
            column_list.currentTextChanged.connect(viewer.display_distribution)
            left_layout.addWidget(column_list)
            
            # 차트 유형 선택
            left_layout.addWidget(QLabel("차트 유형"))
            chart_type_combo = QComboBox()
            chart_type_combo.addItems(["막대그래프",  "파이차트"])  #"히스토그램",
            chart_type_combo.currentTextChanged.connect(lambda chart_type: viewer.display_distribution(column_list.currentItem().text() if column_list.currentItem() else None, chart_type))
            left_layout.addWidget(chart_type_combo)
            left_layout.addStretch()
            
            # 우측 프레임에 차트 추가
            right_layout = QVBoxLayout(right_frame)
            right_layout.setContentsMargins(16, 16, 16, 16)
            right_layout.setSpacing(16)
            right_layout.addWidget(viewer)
            
        except Exception as e:
            QMessageBox.critical(self, "오류", f"분포 분석 중 오류가 발생했습니다: {str(e)}")

    def delete_data_source(self, data):
        name = data.get('name', '')
        confirmed = ConfirmDialog.confirm(
            self,
            '데이터 소스 삭제',
            f'"{name}" 를 정말 삭제하겠습니까?'
        )
        if confirmed:
            delete_datasource(self.project_data.get('uuid', ''), data.get('uuid', ''))
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
                try:
                    data_sources = json.load(f)
                except json.JSONDecodeError:
                    # 파일이 비어있거나 잘못된 형식이면 빈 리스트로 시작
                    data_sources = []
        return data_sources

    def edit_data_source(self, data):
        dialog = DataSourceDialog(self, data)
        if dialog.exec() == QDialog.Accepted:
            new_data = dialog.get_data()
            if new_data is None:
                return
            
            update_datasource(self.project_data.get('uuid', ''), new_data)
            
            # 데이터 소스 목록 새로고침 후 이전 선택 항목 다시 선택
            self.load_data_sources()

            data_sources = get_datasources_list(self.project_data.get('uuid', ''))
            # 수정된 데이터 소스의 UUID로 항목 찾기
            for i in range(self.data_list.count()):
                item = self.data_list.item(i)
                # 데이터 소스 목록에서 해당 이름의 데이터 소스 찾기
                for source in data_sources:
                    if source.get('name') == item.text() and source.get('uuid') == new_data.get('uuid'):
                        self.data_list.setCurrentItem(item)
                        return

    def update_project_name_elision(self):
        """프로젝트 이름의 줄임 처리를 업데이트합니다."""
        metrics = self.project_name.fontMetrics()
        # 프로젝트명 표시 너비를 211px로 고정
        max_width = 196 #211
        
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

    def on_data_source_double_clicked(self, item):
        # 데이터 소스 이름으로 데이터 찾기
        name = item.text()
        data = get_datasource_by_name(self.project_data.get('uuid', ''), name)
        if data:
            self.edit_data_source(data) 

    def load_flows(self):
        """플로우 목록을 로드하고 표시합니다."""
        try:
            flows = get_flow_list(self.project_data.get('uuid', ''))
            
            # 리스트 위젯 초기화
            self.flow_list.clear()
            
            if not flows or len(flows) == 0:
                # 플로우가 없는 경우 메시지 표시
                item = QListWidgetItem("등록된 플로우가 없습니다.")
                item.setTextAlignment(Qt.AlignCenter)
                font = item.font()
                font.setItalic(True)
                item.setFont(font)
                item.setFlags(item.flags() & ~Qt.ItemIsSelectable & ~Qt.ItemIsEnabled)  # 선택과 활성화 비활성화
                self.flow_list.addItem(item)
            else:
                # 플로우 목록 표시
                for flow in flows:
                    name = flow.get('name', '')
                    item = QListWidgetItem(name)
                    
                    # 리스트 위젯의 너비 계산
                    list_width = self.flow_list.viewport().width()
                    # 텍스트 너비 계산
                    font_metrics = self.flow_list.fontMetrics()
                    text_width = font_metrics.horizontalAdvance(name)
                    
                    # 텍스트가 리스트 너비보다 길 경우에만 툴팁 설정
                    if text_width > list_width - 20:  # 20은 여유 공간
                        item.setToolTip(name)
                    
                    self.flow_list.addItem(item)
                
        except Exception as e:
            self.logger.error(f"플로우 목록 로드 중 오류 발생: {str(e)}") 

    def show_flow_menu(self, pos):
        """흐름 목록의 컨텍스트 메뉴를 표시합니다."""
        item = self.flow_list.itemAt(pos)
        if not item or not item.isSelected() or not (item.flags() & Qt.ItemIsEnabled):
            return
            
        # 흐름 이름으로 흐름 찾기
        name = item.text()
        # 흐름 목록 로드
        flow = get_flow_by_name(self.project_data.get('uuid', ''), name)
        if not flow:
            return
            
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
            QMenu::separator {
                height: 1px;
                background: #dee2e6;
                margin: 5px 0px;
            }
        """)
        edit_action = menu.addAction('수정')
        del_action = menu.addAction('삭제')
        run_action = menu.addAction('실행')
        action = menu.exec_(self.flow_list.viewport().mapToGlobal(pos))
        
        if action == edit_action:
            self.edit_flow(flow)
        elif action == del_action:
            self.delete_flow(flow)
        elif action == run_action:
            self.run_flow(flow)

    def on_flow_double_clicked(self, item):
        """흐름 항목 더블클릭 처리"""
        # 흐름 이름으로 흐름 찾기
        name = item.text()
        flow = get_flow_by_name(self.project_data.get('uuid', ''), name)
        if flow:
            self.edit_flow(flow)

    def edit_flow(self, flow):
        """흐름 수정 다이얼로그를 표시합니다."""
        dialog = FlowDialog(self, flow)  # 수정할 흐름 데이터 전달
        dialog.name_input.setText(flow.get('name', ''))
        
        # 데이터 소스 UUID로 콤보박스 선택
        data_source_uuid = flow.get('data_source_uuid', '')
        if data_source_uuid:
            for i in range(dialog.data_input.count()):
                item_text = dialog.data_input.itemText(i)
                if dialog.data_sources.get(item_text, {}).get('uuid') == data_source_uuid:
                    dialog.data_input.setCurrentIndex(i)
                    break
        
        if dialog.exec() == QDialog.Accepted:
            # 수정된 데이터는 FlowDialog에서 직접 처리하므로 여기서는 아무것도 하지 않음
            # 흐름 목록 새로고침 후 이전 선택 항목 다시 선택
            self.load_flows()

            
            # 수정된 흐름의 UUID로 항목 찾기
            flows = get_flow_list(self.project_data.get('uuid', ''))
            for i in range(self.flow_list.count()):
                item = self.flow_list.item(i)
                # 흐름 목록에서 해당 이름의 흐름 찾기
                for f in flows:
                    if f.get('name') == item.text() and f.get('uuid') == flow.get('uuid'):
                        self.flow_list.setCurrentItem(item)
                        return

    def delete_flow(self, flow):
        """흐름을 삭제합니다."""
        name = flow.get('name', '')
        confirmed = ConfirmDialog.confirm(
            self,
            '흐름 삭제',
            f'"{name}" 를 정말 삭제하겠습니까?'
        )
        if confirmed:
            delete_flow(self.project_data.get('uuid', ''), flow.get('uuid', ''))
            self.load_flows()

    def run_flow(self, flow):
        """흐름 실행"""
        # 기존 데이터 소스 확인
        from ui.database import get_datasource_by_name
        from PySide6.QtWidgets import QMessageBox
        
        ds = get_datasource_by_name(self.project_data.get('uuid', ''), flow.get('name'))
        
        # 기존 데이터 소스가 존재하면 컨펌 다이얼로그 표시
        if ds:
            reply = QMessageBox.question(
                self,
                "데이터 소스 중복 확인",
                f"흐름이 실행되면 흐름명으로 데이터 소스가 생성됩니다.\n"
                f"흐름명과 같은 데이터 소스 명이 이미 존재하여 기존 데이터 소스가 변경됩니다.\n"
                f"계속 진행 하시겠습니까?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return

        # 진행률 다이얼로그 생성
        # self.flow = flow
        self.project = self.project_data
        self.datasource = get_datasource(self.project_data.get('uuid', ''), flow.get('data_source_uuid', ''))

        self.dialog = FlowProgressDialog(flow, self)
        
        # 취소 버튼 연결
        self.dialog.canceled.connect(lambda: print("흐름 실행 취소됨"))

        # 다이얼로그 표시
        self.dialog.show()

        # try:
        #     ymls = self.dialog.process_init(self)
        #     if ymls:
        #         self.dialog.process_run(ymls)
                
        #     self.dialog.process_finish()
        # except Exception as e:
        #     self.logger.error(f"흐름 실행 중 오류 발생: {str(e)}")
        #     self.dialog.process_finish()
        


    def on_flow_clicked(self, item):
        try:
            # 흐름 이름으로 흐름 찾기
            name = item.text()
            flow = get_flow_by_name(self.project_data.get('uuid', ''), name)
            if not flow:
                return

            # 부모 윈도우의 projects_container 찾기
            main_window = self.parent
            if not main_window:
                return

            # projects_container에서 left_frame 찾기
            left_frame = None
            for child in main_window.ui.projects_container.children():
                if isinstance(child, QFrame) and child.objectName() == "left_frame":
                    left_frame = child
                    break

            if not left_frame:
                self.logger.error("left_frame을 찾을 수 없습니다.")
                return

            # 기존 위젯 제거
            if left_frame.layout():
                while left_frame.layout().count():
                    item = left_frame.layout().takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()

            # FlowPanel 생성 및 추가
            self.flow_info = flow
            flow_panel = FlowPanel(self)
            left_frame.layout().addWidget(flow_panel)
            
            # 흐름 정보 설정
            flow_panel.set_flow_info(flow)

            # === right_frame 비우기 추가 ===
            right_frame = None
            for child in main_window.ui.projects_container.children():
                if isinstance(child, QFrame) and child.objectName() == "right_frame":
                    right_frame = child
                    break
            if right_frame and right_frame.layout():
                while right_frame.layout().count():
                    item = right_frame.layout().takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
        except Exception as e:
            self.logger.error(f"흐름 상세 정보 표시 중 오류 발생: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc()) 

    def _on_delete_clicked(self):
        """삭제 버튼 클릭 시 호출"""
        # 삭제 확인 다이얼로그
        reply = QMessageBox.question(
            self,
            "삭제 확인",
            "정말로 이 흐름을 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 데이터베이스에서 삭제
            delete_flow(self.parent.project_data.get('uuid'), self.flow_info.get('uuid'))
            # 캐시 강제 리로드
            reload_flow_from_file(self.parent.project_data.get('uuid'))
            # 삭제 완료 시그널 발생
            self.delete_requested.emit()
            # 처리 삭제 시그널 발생
            self.process_deleted.emit(self.flow_info.get('uuid'))
            # 패널 닫기
            self.close() 