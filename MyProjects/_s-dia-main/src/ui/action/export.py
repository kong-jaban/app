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

class ExportWidget(QWidget):
    def __init__(self, parent=None, flow_pos=None):
        super().__init__(parent)
        loader = QUiLoader()
        ui_path = os.path.join(os.path.dirname(__file__), 'export.ui')
        loaded = loader.load(ui_path, self)

        self.parent = parent
        self.data_source = parent.current_data_source if hasattr(parent, 'current_data_source') else None
        self.project_data = self.parent.parent.project_data if hasattr(self.parent, 'parent') else None
        # flow_pos 안전하게 처리
        if flow_pos is not None:
            self.flow_pos = flow_pos
        elif hasattr(parent, 'flow_pos'):
            self.flow_pos = parent.flow_pos
        else:
            self.flow_pos = -1
        # self.flows_seze = parent.ui.process_list.count()

        self.setLayout(loaded.layout())
        
        # UI 요소 찾기
        self.title_label = self.findChild(QWidget, 'title_label')
        self.export_table = self.findChild(QTableWidget, 'export_table')
        self.save_button = self.findChild(QWidget, 'save_button')
        self.delete_btn = self.findChild(QWidget, 'delete_btn')

        self._init_table()
        self._init_events()
        self.set_schema()  # ExportWidget 생성 시 자동으로 schema를 테이블에 채움

    def on_header_checkbox_toggled(self, checked):
        self._toggle_all_checkboxes(checked)

    def _init_table(self):
        table = self.export_table
        # table.setRowCount(50)
        table.setColumnCount(3)
        
        # 헤더 설정
        headers = ["", "컬럼명", "설명"]
        table.setHorizontalHeaderLabels(headers)

        width = self.parent.parent.parent.findChild(QFrame, "right_frame").width()

        # 컬럼 너비 설정
        table.setColumnWidth(0, 28) 
        table.setColumnWidth(1, 200) 
        table.setColumnWidth(2, width - 200 - 28) 
        
        # 커스텀 헤더 적용
        self.checkbox_header = CheckBoxHeader(Qt.Horizontal, table)
        table.setHorizontalHeader(self.checkbox_header)
        self.checkbox_header.toggled.connect(self.on_header_checkbox_toggled)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setStretchLastSection(True)

        # row 체크박스: QCheckBox 위젯을 QHBoxLayout에 담아 setCellWidget으로 구현
        self.row_checkboxes = []
        
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        # table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(True)
        # table.setFixedSize(width - 35, self.parent.height() - 140)
        
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

    def _toggle_all_checkboxes(self, checked):
        for chk in self.row_checkboxes:
            chk.setChecked(checked)

    def _init_events(self):
        if self.save_button:
            self.save_button.clicked.connect(self._on_save_clicked)
        if self.delete_btn:
            self.delete_btn.clicked.connect(self._on_delete_clicked)

    def _on_save_clicked(self):
        # 1. export 테이블에서 컬럼명/체크박스 추출
        columns = []
        table = self.export_table
        for row in range(table.rowCount()):
            column_name_item = table.item(row, 1)
            if column_name_item is None:
                continue
            column_name = column_name_item.text()
            chk_widget = table.cellWidget(row, 0)
            if chk_widget is not None:
                checkbox = chk_widget.findChild(QCheckBox)
                is_export = checkbox.isChecked() if checkbox else False
            else:
                is_export = False
            columns.append({
                "column_name": column_name,
                "is_export": is_export
            })

        # 2. flow.json 파일 경로 찾기 (parent에서 프로젝트 정보 등 활용)
        project_uuid = self.parent.parent.project_data.get("uuid")
        flow_uuid = self.parent.parent.flow_info.get('uuid', None)
        if flow_uuid is None:
            MessageDialog.warning(self, "조회 실패", "현재 흐름 uuid를 찾을 수 없습니다.")
            return

        flow = get_flow_by_uuid(project_uuid, flow_uuid)
        if flow is None:
            # print("현재 흐름 uuid를 찾을 수 없습니다.")
            return
            
        # 임시 카드인지 확인하고 정식 카드로 변환
        if self.flow_pos == -1:
            # 새로 추가하는 경우
            flow['processes'].append({
                "process_type": "export",
                "columns": columns
            })
        else:
            # 기존 카드 수정하는 경우
            flow['processes'][self.flow_pos] = {
                "process_type": "export",
                "columns": columns
            }
        update_flow(project_uuid, flow)

        # 저장 성공 메시지
        MessageDialog.information(self, "저장 완료", "컬럼 선택 설정이 저장되었습니다.")

        # 흐름 패널 카드 갱신 (FlowPanel 찾기)
        flow_panel = self.parent
        # parent chain을 따라 올라가서 FlowPanel 찾기
        while flow_panel is not None and flow_panel.__class__.__name__ != "FlowPanel":
            flow_panel = flow_panel.parent()
        if flow_panel and hasattr(flow_panel, "set_flow_info"):
            updated_flow = get_flow_by_uuid(project_uuid, flow_uuid)
            flow_panel.set_flow_info(updated_flow)
            
            # 공통 함수를 사용하여 저장된 카드 선택 (original_flow_pos 전달)
            process_data = {
                "process_type": "export",
                "columns": columns
            }
            select_saved_process_card(flow_panel, process_data, updated_flow, self.flow_pos)

    def _on_delete_clicked(self):
        # 삭제 버튼 클릭 시 처리
        confirmed = ConfirmDialog.confirm(self, '처리 삭제', '정말 삭제하겠습니까?')
        if not confirmed:
            return
        project_uuid = self.parent.parent.project_data.get('uuid', '')
        flow_uuid = self.parent.parent.flow_info.get('uuid', '')
        if not flow_uuid:
            return
        # database.py의 delete_process_from_flow 함수 사용
        delete_process_from_flow(project_uuid, flow_uuid, self.flow_pos)
        # 흐름 패널 카드 갱신 (FlowPanel 찾기)
        flow_panel = self.parent
        # parent chain을 따라 올라가서 FlowPanel 찾기
        while flow_panel is not None and flow_panel.__class__.__name__ != "FlowPanel":
            flow_panel = flow_panel.parent()
        if flow_panel and hasattr(flow_panel, "set_flow_info"):
            updated_flow = get_flow_by_uuid(project_uuid, flow_uuid)
            flow_panel.set_flow_info(updated_flow)

        right_frame = self.parent.parent.parent.ui.projects_container.findChild(QFrame, 'right_frame')
        if right_frame and right_frame.layout():
            while right_frame.layout().count():
                item = right_frame.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

    def _on_row_checkbox_changed(self):
        checked_count = sum(chk.isChecked() for chk in self.row_checkboxes)
        total = len(self.row_checkboxes)
        if checked_count == total:
            self.checkbox_header.isChecked = True
            self.checkbox_header.updateSection(0)
        else:
            self.checkbox_header.isChecked = False
            self.checkbox_header.updateSection(0)

    def set_schema(self):
        flow_pos = self.flow_pos if self.flow_pos > -1 else len(self.parent.flow_info.get('processes', []))
        schemas, transformed_dict = validate_schema(self.parent, self.data_source.get("schemas", []), self.parent.flow_info.get('processes', []), flow_pos)

        # schema_list = copy.deepcopy(self.data_source.get("schemas", []))
        # transformed_dict = {item["name"]: item for item in schema_list}


        # schemas = [ item.get('name') for item in schema_list ]
        # current_proces = self.parent.flow_info.get('processes')[flow_pos]

        # for proc_idx, process in enumerate(self.parent.flow_info.get('processes', [])):
        #     if proc_idx >= flow_pos:
        #         break
        #     if process.get('process_type') == 'export':
        #         columns = [ col.get('column_name') for col in process.get('columns', []) if col.get('is_export') == True ]
        #         cols = []
        #         for idx, column in enumerate(schemas):
        #             if column in columns:
        #                 cols.append(column)
        #                 # schemas.pop(idx)
        #         schemas = cols
        #     elif process.get('process_type') == 'rename_columns':
        #         columns = [ col.get('column_name') for col in process.get('renames', []) ]
        #         cols = []
        #         for idx, column in enumerate(schemas):
        #             ren_cols = [col.get('new_column_name') for col in process.get('renames', []) if col.get("column_name") == column]
        #             if ren_cols:
        #                 cols.append(ren_cols[0])
        #                 transformed_dict[ren_cols[0]] = transformed_dict[column]
        #                 transformed_dict[ren_cols[0]]['name'] = ren_cols[0]
        #                 del transformed_dict[column]
        #             else:
        #                 cols.append(column)

        #         schemas = cols

        if schemas is not None:
            table = self.export_table
            self.row_checkboxes = []
            table.setRowCount(len(schemas))
            pos = 0
            for i, column_name in enumerate(schemas):
                # if schema.get('name') not in schemas:
                #     continue
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setAlignment(Qt.AlignCenter)
                checkbox = QCheckBox()
                checkbox.stateChanged.connect(self._on_row_checkbox_changed)
                checkbox.setStyleSheet("""
                    QCheckBox {
                        background: transparent;
                    }
                    QCheckBox::indicator:unchecked {
                        background-color: #000;
                        border-radius: 4px;
                        width: 15px;
                        height: 15px;

                    }
                """) 
                schema = transformed_dict[column_name]
                layout.addWidget(checkbox)
                self.row_checkboxes.append(checkbox)
                table.setCellWidget(pos, 0, widget)
                table.setItem(pos, 1, QTableWidgetItem(schema.get('name', '')))
                table.setItem(pos, 2, QTableWidgetItem(schema.get('comment', ''))) 

                pos += 1


    def set_process_data(self, process_data):
        """flow.json의 export 프로세스 데이터를 받아 체크박스 상태를 반영"""
        columns = process_data.get('columns', [])
        table = self.export_table
        # 컬럼명-체크박스 매핑
        colname_to_is_export = {col['column_name']: col.get('is_export', False) for col in columns}
        for row in range(table.rowCount()):
            column_name_item = table.item(row, 1)
            if column_name_item is None:
                continue
            column_name = column_name_item.text()
            chk_widget = table.cellWidget(row, 0)
            if chk_widget is not None:
                checkbox = chk_widget.findChild(QCheckBox)
                if checkbox is not None:
                    checkbox.setChecked(colname_to_is_export.get(column_name, False)) 