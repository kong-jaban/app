import copy
import os
import json
from PySide6.QtWidgets import QFrame, QWidget, QTableWidget, QTableWidgetItem, QCheckBox, QAbstractItemView, QHBoxLayout, QHeaderView, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QStyleOptionButton, QStyle, QApplication
from src.ui.database import get_flow_list, get_flow_by_uuid, update_flow, delete_process_from_flow
from src.ui.components.message_dialog import MessageDialog
from src.ui.components.confirm_dialog import ConfirmDialog
from ui.action.action_common import validate_schema, select_saved_process_card
from ui.components.custom_checkbox import CheckBoxHeader
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QLineEdit
from utils.enum_utils import sdataTypeToView

class RenameColumnsWidget(QWidget):
    def __init__(self, parent=None, flow_pos=None):
        super().__init__(parent)
        # UI 파일 로드
        loader = QUiLoader()
        ui_path = os.path.join(os.path.dirname(__file__), 'rename_columns.ui')
        self.ui = loader.load(ui_path, self)

        self.parent = parent
        self.data_source = parent.current_data_source if hasattr(parent, 'current_data_source') else None
        self.project_data = self.parent.parent.project_data if hasattr(self.parent, 'parent') else None
        
        self.flow_pos = flow_pos if flow_pos is not None else -1

        self.setLayout(self.ui.layout())
        
        # UI 요소 찾기
        self.title_label = self.ui.title_label
        self.rename_columns_table = self.ui.rename_columns_table
        self.save_button = self.ui.save_button
        self.delete_btn = self.ui.delete_btn

        self._init_table()
        self._init_events()
        self.set_schema()

    def _init_table(self):
        table = self.rename_columns_table
        table.setColumnCount(3)
        
        headers = ["기존 컬럼명", "새 컬럼명", "설명"]
        table.setHorizontalHeaderLabels(headers)

        width = self.parent.parent.parent.findChild(QFrame, "right_frame").width()

        table.setColumnWidth(0, int(width * 0.3)) 
        table.setColumnWidth(1, int(width * 0.3)) 
        table.setColumnWidth(2, int(width * 0.4))
        
        header = table.horizontalHeader()
        header.setStretchLastSection(True)

        table.verticalHeader().setVisible(False)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # 행 높이 설정 (필터와 동일하게)
        table.verticalHeader().setDefaultSectionSize(table.verticalHeader().defaultSectionSize() + 10)
        
        # 스크롤바 스타일 직접 적용
        table.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: #f1f3f5;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #adb5bd;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #868e96;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        table.horizontalScrollBar().setStyleSheet("""
            QScrollBar:horizontal {
                border: none;
                background: #f1f3f5;
                height: 8px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #adb5bd;
                min-width: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #868e96;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)
        
        # 스타일시트 설정 - 기존 컬럼명과 새 컬럼명을 구분하기 위한 스타일 개선
        table.setStyleSheet("""
            QTableWidget {
                background-color: #f8f9fa; 
                border: 1px solid #dee2e6; 
                border-radius: 4px; 
                gridline-color: #e9ecef; 
                color: #212529;
            }
            QTableWidget::item {
                padding: 4px; 
                border-bottom: 1px solid #e9ecef; 
                color: #212529; 
                background-color: white;
            }
            QTableWidget::item:selected { 
                background-color: #e7f5ff; 
                color: #212529; 
            }
            QTableWidget::item:focus { 
                outline: none; 
                border: 1px solid #339af0; 
                background: #e7f5ff; 
            }
            QHeaderView::section {
                background-color: #f8f9fa; 
                color: #212529; 
                padding: 8px; 
                border: none;
                border-right: 1px solid #dee2e6; 
                border-bottom: 1px solid #dee2e6; 
                font-weight: bold;
            }
            /* 기존 컬럼명 헤더 스타일 */
            QHeaderView::section:nth-child(1) {
                background-color: #e3f2fd;
                color: #1565c0;
                border-bottom: 2px solid #1565c0;
            }
            /* 새 컬럼명 헤더 스타일 */
            QHeaderView::section:nth-child(2) {
                background-color: #f3e5f5;
                color: #7b1fa2;
                border-bottom: 2px solid #7b1fa2;
            }
            /* 설명 헤더 스타일 */
            QHeaderView::section:nth-child(3) {
                background-color: #e8f5e8;
                color: #2e7d32;
                border-bottom: 2px solid #2e7d32;
            }
        """)

    def _init_events(self):
        if self.save_button:
            self.save_button.clicked.connect(self._on_save_clicked)
        if self.delete_btn:
            self.delete_btn.clicked.connect(self._on_delete_clicked)

    def set_schema(self):
        if not self.data_source:
            return
        
        # 신규일 때는 -1, 수정일 때는 실제 카드 위치 사용
        flow_pos = self.flow_pos if self.flow_pos > -1 else len(self.parent.flow_info.get('processes', []))
        schemas, transformed_dict = validate_schema(self.parent, self.data_source.get("schemas", []), self.parent.flow_info.get('processes', []), flow_pos)

        table = self.rename_columns_table
        table.setRowCount(len(schemas))
        pos = 0

        for i, column_name in enumerate(schemas):
            # print("3:"+column_name)
            schema = transformed_dict[column_name]

            # 기존 컬럼명 (편집 불가)
            original_name = QTableWidgetItem(schema.get('name', ''))
            original_name.setFlags(original_name.flags() & ~Qt.ItemIsEditable)
            original_name.setBackground(QColor("#f5f5f5"))  # 회색 배경으로 기존 컬럼명 구분
            
            # 새 컬럼명 (LineEdit 추가, 초기값은 빈 문자열)
            new_name_edit = QLineEdit()
            if self.flow_pos > -1:
                new_col = [col.get('new_column_name') for col in self.parent.flow_info.get('processes', [])[self.flow_pos].get('renames') if col.get("column_name") == column_name]
                if new_col:
                    new_name_edit.setText(new_col[0])
                
            # new_name_edit.setPlaceholderText("새 컬럼명을 입력하세요")
            new_name_edit.setStyleSheet("""
                QLineEdit {
                    padding: 1px;
                    border: 1px solid #ced4da;
                    border-radius: 4px;
                    background-color: #ffffff;
                    font-size: 14px;
                    color: #000;
                }
                QLineEdit:focus {
                    border: 1px solid #80bdff;
                    outline: 0;
                }
            """)
            
            # 설명 (편집 불가)
            comment = QTableWidgetItem(schema.get('comment', ''))
            comment.setFlags(comment.flags() & ~Qt.ItemIsEditable)
            comment.setBackground(QColor("#f9f9f9"))  # 연한 회색 배경으로 설명 구분

            table.setItem(pos, 0, original_name)
            table.setCellWidget(pos, 1, new_name_edit)
            table.setItem(pos, 2, comment)
            pos += 1

    def _on_save_clicked(self):
        # 1. 테이블에서 변경된 컬럼명 추출
        renames = []
        table = self.rename_columns_table
        for row in range(table.rowCount()):
            original_name_item = table.item(row, 0)
            new_name_widget = table.cellWidget(row, 1)
            
            if original_name_item and new_name_widget:
                original_name = original_name_item.text()
                new_name = new_name_widget.text().strip()
                
                # 새 컬럼명이 입력된 경우에만 저장
                if new_name:
                    renames.append({
                        "column_name": original_name,
                        "new_column_name": new_name
                    })

        # 2. flow.json 파일 경로 찾기
        project_uuid = self.parent.parent.project_data.get("uuid")
        flow_uuid = self.parent.parent.flow_info.get('uuid', None)
        if flow_uuid is None:
            MessageDialog.warning(self, "조회 실패", "현재 흐름 uuid를 찾을 수 없습니다.")
            return

        flow = get_flow_by_uuid(project_uuid, flow_uuid)
        if flow is None:
            MessageDialog.critical(self, "오류", "흐름 데이터를 찾을 수 없습니다.")
            return

        # 3. 프로세스 데이터 구성
        process_data = {
            "process_type": "rename_columns",
            "renames": renames
        }

        # 4. 흐름에 프로세스 추가/수정
        if self.flow_pos == -1:
            flow['processes'].append(process_data)
        else:
            flow['processes'][self.flow_pos] = process_data

        update_flow(project_uuid, flow)

        # 5. 성공 메시지 및 패널 새로고침
        MessageDialog.information(self, "저장 완료", "컬럼명 변경 설정이 저장되었습니다.")
        
        flow_panel = self.parent
        if flow_panel and hasattr(flow_panel, "set_flow_info"):
            updated_flow = get_flow_by_uuid(project_uuid, flow_uuid)
            flow_panel.set_flow_info(updated_flow)
            
            # 공통 함수를 사용하여 저장된 카드 선택 (original_flow_pos 전달)
            select_saved_process_card(flow_panel, process_data, updated_flow, self.flow_pos)

    def _on_delete_clicked(self):
        from src.ui.components.confirm_dialog import ConfirmDialog
        from src.ui.database import delete_process_from_flow

        confirmed = ConfirmDialog.confirm(self, '처리 삭제', '정말 삭제하겠습니까?')
        if not confirmed:
            return
        project_uuid = self.parent.parent.project_data.get('uuid', '')
        flow_uuid = self.parent.parent.flow_info.get('uuid', '')
        if not flow_uuid:
            return
        
        delete_process_from_flow(project_uuid, flow_uuid, self.flow_pos)
        
        flow_panel = self.parent
        if flow_panel and hasattr(flow_panel, "set_flow_info"):
            updated_flow = get_flow_by_uuid(project_uuid, flow_uuid)
            flow_panel.set_flow_info(updated_flow)

        right_frame = self.parent.parent.parent.ui.projects_container.findChild(QFrame, 'right_frame')
        if right_frame and right_frame.layout():
            while right_frame.layout().count():
                item = right_frame.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

    def set_process_data(self, process_data):
        """기존 프로세스 데이터로 위젯 설정"""
        if not process_data or 'renames' not in process_data:
            return
            
        # 먼저 set_schema를 호출하여 모든 스키마를 표시
        self.set_schema()
        
        # 저장된 컬럼명 변경 데이터 가져오기
        renames = process_data.get('renames', [])
        
        # 저장된 데이터를 테이블에 적용
        table = self.rename_columns_table
        for row in range(table.rowCount()):
            original_name_item = table.item(row, 0)
            if original_name_item:
                original_name = original_name_item.text()
                # 저장된 데이터에서 해당 컬럼의 새 이름 찾기
                for rename_item in renames:
                    if rename_item.get('column_name') == original_name:
                        new_name = rename_item.get('new_column_name', '')
                        new_name_widget = table.cellWidget(row, 1)
                        if new_name_widget:
                            new_name_widget.setText(new_name)
                        break 