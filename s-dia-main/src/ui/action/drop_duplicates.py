import copy
import os
import json
from PySide6.QtWidgets import (QFrame, QWidget, QTableWidget, QTableWidgetItem, QCheckBox, 
                               QAbstractItemView, QHBoxLayout, QHeaderView, QMessageBox, 
                               QComboBox, QPushButton, QVBoxLayout, QLabel, QScrollArea)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QPainter, QColor, QIcon
from PySide6.QtWidgets import QStyleOptionButton, QStyle, QApplication
from src.ui.database import get_flow_list, get_flow_by_uuid, update_flow, delete_process_from_flow
from src.ui.components.message_dialog import MessageDialog
from src.ui.components.confirm_dialog import ConfirmDialog
from src.ui.components.custom_checkbox import CheckBoxHeader
from ui.action.action_common import validate_schema, select_saved_process_card
from utils.enum_utils import sdataTypeToView

class DropDuplicatesWidget(QWidget):
    def __init__(self, parent=None, flow_pos=None):
        super().__init__(parent)
        loader = QUiLoader()
        ui_path = os.path.join(os.path.dirname(__file__), 'drop_duplicates.ui')
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

        self.setLayout(loaded.layout())
        
        # UI 요소 찾기
        self.title_label = self.findChild(QWidget, 'title_label')
        self.scroll_area = self.findChild(QScrollArea, 'scrollArea')
        self.column_table = self.findChild(QTableWidget, 'column_table')
        self.save_button = self.findChild(QWidget, 'save_button')
        self.delete_btn = self.findChild(QWidget, 'delete_btn')
        self.comboBox = self.findChild(QComboBox, 'comboBox')
        self.sortby_button = self.findChild(QPushButton, 'sortby_button')
        self.sort_layout = self.findChild(QVBoxLayout, 'sort_layout')

        # 정렬 조건을 저장할 리스트
        self.sort_conditions = []

        self._init_table()
        self._init_events()
        self._init_sort_button()
        self.set_schema()  # DropDuplicatesWidget 생성 시 자동으로 schema를 테이블에 채움

    def on_header_checkbox_toggled(self, checked):
        self._toggle_all_checkboxes(checked)

    def _init_table(self):
        table = self.column_table
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
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setStretchLastSection(True)

        # row 체크박스: QCheckBox 위젯을 QHBoxLayout에 담아 setCellWidget으로 구현
        self.row_checkboxes = []
        
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(True)
        
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

    def _init_sort_button(self):
        """정렬 기준 버튼 초기화"""
        # 정렬 기준 버튼에 아이콘 설정
        sort_icon_path = "src/ui/resources/images/add2.png"
        if os.path.exists(sort_icon_path):
            self.sortby_button.setIcon(QIcon(sort_icon_path))
            self.sortby_button.setIconSize(QSize(16, 16))
        
        self.sortby_button.clicked.connect(self._on_sort_button_clicked)

    def _on_sort_button_clicked(self):
        """정렬 기준 버튼 클릭 시 처리"""
        self.add_sort_condition()

    def add_sort_condition(self):
        """정렬 조건 추가"""
        # 정렬 조건 번호
        condition_number = len(self.sort_conditions) + 1
        
        # 정렬 조건 위젯 생성
        sort_widget = QWidget()
        sort_layout = QHBoxLayout(sort_widget)
        sort_layout.setContentsMargins(0, 5, 0, 5)
        sort_layout.setSpacing(10)
        
        # "컬럼기준 #N" 라벨
        label = QLabel(f"컬럼기준 #{condition_number}")
        label.setStyleSheet("""
            QLabel {
                color: #495057;
                font-size: 14px;
                min-width: 80px;
            }
        """)
        sort_layout.addWidget(label)
        
        # 컬럼 선택 콤보박스
        column_combo = QComboBox()
        column_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 5px 10px;
                min-height: 30px;
                color: #495057;
                min-width: 150px;
            }
            QComboBox:focus {
                border: 1px solid #339af0;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 30px;
                border: none;
            }
            QComboBox::down-arrow {
                image: url(src/ui/resources/images/down-arrow-svgrepo-com.svg);
                width: 10px;
                height: 10px;
                margin-right: 1px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                outline: none;
                selection-background-color: #e9ecef;
                selection-color: #000;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px 20px;
                color: #495057;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #e9ecef;
                color: #000;
            }
            QComboBox QAbstractScrollArea QScrollBar:vertical {
                border: none;
                background: #f8f9fa;
                width: 10px;
                margin: 0px;
            }
            QComboBox QAbstractScrollArea QScrollBar::handle:vertical {
                background: #dee2e6;
                min-height: 20px;
                border-radius: 5px;
            }
            QComboBox QAbstractScrollArea QScrollBar::handle:vertical:hover {
                background: #adb5bd;
            }
            QComboBox QAbstractScrollArea QScrollBar::add-line:vertical, QComboBox QAbstractScrollArea QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QComboBox QAbstractScrollArea QScrollBar::add-page:vertical, QComboBox QAbstractScrollArea QScrollBar::sub-page:vertical {
                background: none;
            }
            QComboBox QAbstractScrollArea QScrollBar:horizontal {
                border: none;
                background: #f8f9fa;
                height: 10px;
                margin: 0px;
            }
            QComboBox QAbstractScrollArea QScrollBar::handle:horizontal {
                background: #dee2e6;
                min-width: 20px;
                border-radius: 5px;
            }
            QComboBox QAbstractScrollArea QScrollBar::handle:horizontal:hover {
                background: #adb5bd;
            }
            QComboBox QAbstractScrollArea QScrollBar::add-line:horizontal, QComboBox QAbstractScrollArea QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            QComboBox QAbstractScrollArea QScrollBar::add-page:horizontal, QComboBox QAbstractScrollArea QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)
        
        # 컬럼 목록 추가
        if self.data_source and self.data_source.get("schemas"):
            for schema in self.current_coulumns: 
                column_combo.addItem(schema.get('name', ''))
        
        sort_layout.addWidget(column_combo)
        
        # 오름차순/내림차순 콤보박스
        order_combo = QComboBox()
        order_combo.setStyleSheet(column_combo.styleSheet())
        order_combo.addItem("오름차순")
        order_combo.addItem("내림차순")
        sort_layout.addWidget(order_combo)
        
        # 삭제 버튼
        delete_btn = QPushButton()
        delete_btn.setFixedSize(16, 16)
        delete_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                image: url(src/ui/resources/images/cancel.png);
            }
            QPushButton:hover {
                background-color: #f8f9fa;
                border-radius: 4px;
            }
        """)
        delete_btn.clicked.connect(lambda: self.remove_sort_condition(sort_widget))
        sort_layout.addWidget(delete_btn)
        
        # 여백 추가
        sort_layout.addStretch()
        
        # 정렬 조건을 sort_layout에 직접 추가 (QVBoxLayout이므로)
        self.sort_layout.addWidget(sort_widget)
        
        # 정렬 조건 정보를 리스트에 저장
        self.sort_conditions.append({
            'widget': sort_widget,
            'column_combo': column_combo,
            'order_combo': order_combo,
            'number': condition_number
        })

    def _toggle_all_checkboxes(self, checked):
        for chk in self.row_checkboxes:
            chk.setChecked(checked)

    def _init_events(self):
        if self.save_button:
            self.save_button.clicked.connect(self._on_save_clicked)
        if self.delete_btn:
            self.delete_btn.clicked.connect(self._on_delete_clicked)

    def _on_save_clicked(self):
        # 1. column_table에서 컬럼명/체크박스 추출
        selected_columns = []
        table = self.column_table
        for row in range(table.rowCount()):
            column_name_item = table.item(row, 1)
            if column_name_item is None:
                continue
            column_name = column_name_item.text()
            chk_widget = table.cellWidget(row, 0)
            if chk_widget is not None:
                checkbox = chk_widget.findChild(QCheckBox)
                is_checked = checkbox.isChecked() if checkbox else False
                if is_checked:
                    selected_columns.append(column_name)

        if not selected_columns:
            MessageDialog.warning(self, "경고", "중복 제거 기준 컬럼을 선택해주세요.")
            return

        # 2. 중복 시 남길 행 설정 가져오기
        keep_option = self.comboBox.currentText()
        keep_mapping = {
            "첫째 행": "first",
            "마지막 행": "last", 
            "남기지 않음": "none"
        }
        keep_value = keep_mapping.get(keep_option, "first")

        # 3. 정렬 조건 정보 가져오기
        sort_conditions = []
        for condition in self.sort_conditions:
            column_name = condition['column_combo'].currentText()
            order = condition['order_combo'].currentText()
            sort_conditions.append({
                'column': column_name,
                'order': 'asc' if order == "오름차순" else 'desc'
            })

        # 4. flow.json 파일 경로 찾기 (parent에서 프로젝트 정보 등 활용)
        project_uuid = self.parent.parent.project_data.get("uuid")
        flow_uuid = self.parent.parent.flow_info.get('uuid', None)
        if flow_uuid is None:
            MessageDialog.warning(self, "조회 실패", "현재 흐름 uuid를 찾을 수 없습니다.")
            return

        flow = get_flow_by_uuid(project_uuid, flow_uuid)
        if flow is None:
            print("현재 흐름 uuid를 찾을 수 없습니다.")
            return

        # 5. 프로세스 데이터 구성
        process_data = {
            "process_type": "drop_duplicates",
            "columns": selected_columns,
            "keep": keep_value,
            "sort_conditions": sort_conditions
        }

        # 6. 흐름에 프로세스 추가/수정
        if self.flow_pos == -1:
            flow['processes'].append(process_data)
        else:
            flow['processes'][self.flow_pos] = process_data

        update_flow(project_uuid, flow)

        # 성공 메시지
        MessageDialog.information(self, "성공", "중복 제거 설정이 저장되었습니다.")
        
        # 흐름 패널 새로고침
        flow_panel = self.parent
        # parent chain을 따라 올라가서 FlowPanel 찾기
        while flow_panel is not None and flow_panel.__class__.__name__ != "FlowPanel":
            flow_panel = flow_panel.parent()
        if flow_panel and hasattr(flow_panel, "set_flow_info"):
            updated_flow = get_flow_by_uuid(project_uuid, flow_uuid)
            flow_panel.set_flow_info(updated_flow)
            
            # 공통 함수를 사용하여 저장된 카드 선택 (original_flow_pos 전달)
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
        """데이터 소스 스키마를 테이블에 설정"""
        try:
            flow_pos = self.flow_pos if self.flow_pos > -1 else len(self.parent.flow_info.get('processes', []))
            schemas, transformed_dict = validate_schema(self.parent, self.data_source.get("schemas", []), self.parent.flow_info.get('processes', []), flow_pos)

            if schemas is not None:
                table = self.column_table
                self.row_checkboxes = []
                table.setRowCount(len(schemas))
                pos = 0
                self.current_coulumns = []
                for i, column_name in enumerate(schemas):
                    schema = transformed_dict[column_name]
                    self.current_coulumns.append(schema)        
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
                    layout.addWidget(checkbox)
                    self.row_checkboxes.append(checkbox)
                    table.setCellWidget(pos, 0, widget)
                    table.setItem(pos, 1, QTableWidgetItem(schema.get('name', '')))
                    table.setItem(pos, 2, QTableWidgetItem(schema.get('comment', ''))) 

                    pos += 1
                
        except Exception as e:
            print(f"스키마 설정 중 오류: {str(e)}")

    def set_process_data(self, process_data):
        """기존 프로세스 데이터로 위젯 설정"""
        try:
            if not process_data:
                return
                
            # 중복 제거 기준 컬럼들 체크
            columns = process_data.get('columns', [])
            table = self.column_table
            # 컬럼명-체크박스 매핑
            colname_to_is_checked = {col: True for col in columns}
            for row in range(table.rowCount()):
                column_name_item = table.item(row, 1)
                if column_name_item is None:
                    continue
                column_name = column_name_item.text()
                chk_widget = table.cellWidget(row, 0)
                if chk_widget is not None:
                    checkbox = chk_widget.findChild(QCheckBox)
                    if checkbox is not None:
                        checkbox.setChecked(colname_to_is_checked.get(column_name, False))
            
            # 중복 시 남길 행 설정
            keep_value = process_data.get('keep', 'first')
            keep_mapping = {
                "first": "첫째 행",
                "last": "마지막 행",
                "none": "남기지 않음"
            }
            keep_text = keep_mapping.get(keep_value, "첫째 행")
            
            index = self.comboBox.findText(keep_text)
            if index >= 0:
                self.comboBox.setCurrentIndex(index)
            
            # 정렬 조건 복원
            sort_conditions = process_data.get('sort_conditions', [])
            for sort_condition in sort_conditions:
                self.add_sort_condition()
                # 마지막에 추가된 정렬 조건 설정
                if self.sort_conditions:
                    last_condition = self.sort_conditions[-1]
                    column_name = sort_condition.get('column', '')
                    order = sort_condition.get('order', 'asc')
                    
                    # 컬럼 선택
                    column_index = last_condition['column_combo'].findText(column_name)
                    if column_index >= 0:
                        last_condition['column_combo'].setCurrentIndex(column_index)
                    
                    # 정렬 순서 선택
                    order_index = 0 if order == 'asc' else 1
                    last_condition['order_combo'].setCurrentIndex(order_index)
                
        except Exception as e:
            print(f"프로세스 데이터 설정 중 오류: {str(e)}")

    def remove_sort_condition(self, widget):
        """정렬 조건 삭제"""
        # 위젯 제거 (QVBoxLayout이므로 직접 removeWidget 사용)
        self.sort_layout.removeWidget(widget)
        widget.deleteLater()
        
        # 리스트에서 제거
        for i, condition in enumerate(self.sort_conditions):
            if condition['widget'] == widget:
                self.sort_conditions.pop(i)
                break
        
        # 번호 재정렬
        self.reorder_sort_conditions()

    def reorder_sort_conditions(self):
        """정렬 조건 번호 재정렬"""
        for i, condition in enumerate(self.sort_conditions):
            condition['number'] = i + 1
            # 라벨 업데이트
            label = condition['widget'].layout().itemAt(0).widget()
            if isinstance(label, QLabel):
                label.setText(f"컬럼기준 #{i + 1}") 

    def _setup_scroll_area(self):
        """스크롤 영역 설정 - 간단한 방식으로 구현"""
        # 기존 레이아웃을 그대로 유지
        # 정렬 조건이 많을 때는 sort_layout 내부에서 자동으로 스크롤이 나타남
        pass 