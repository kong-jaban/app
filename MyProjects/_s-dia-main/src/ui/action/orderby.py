import copy
import os
import json
from PySide6.QtWidgets import (QFrame, QWidget, QTableWidget, QTableWidgetItem, QCheckBox, 
                               QAbstractItemView, QHeaderView, QMessageBox, QAbstractScrollArea,
                               QComboBox, QPushButton, QVBoxLayout, QLabel, QSizePolicy)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QPainter, QColor, QIcon
from PySide6.QtWidgets import QStyleOptionButton, QStyle, QApplication
from src.ui.database import get_flow_list, get_flow_by_uuid, update_flow, delete_process_from_flow
from src.ui.components.message_dialog import MessageDialog
from src.ui.components.confirm_dialog import ConfirmDialog
from src.ui.components.custom_checkbox import CheckBoxHeader
from ui.action.action_common import validate_schema, select_saved_process_card

class OrderByWidget(QWidget):
    def __init__(self, parent=None, flow_pos=None):
        super().__init__(parent)
        loader = QUiLoader()
        ui_path = os.path.join(os.path.dirname(__file__), 'orderby.ui')
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
        self.conditions_table = self.findChild(QTableWidget, 'conditions_table')
        self.save_button = self.findChild(QWidget, 'save_button')
        self.delete_btn = self.findChild(QWidget, 'delete_btn')
        self.add_condition_button = self.findChild(QPushButton, 'add_condition_button')
        self.na_position_combo = self.findChild(QComboBox, 'na_position_combo')

        # 정렬 조건을 저장할 리스트
        self.sort_conditions = []
        
        # 컬럼 목록 초기화
        self.current_coulumns = []
        
        # 사용자가 조정한 컬럼 크기 추적
        self._user_adjusted_columns = set()
        self._is_programmatic_resize = False

        self._init_events()
        self._init_table()
        self.set_schema()  # OrderByWidget 생성 시 자동으로 schema를 설정

    def _init_table(self):
        """테이블 초기화"""
        # 컬럼 헤더 설정
        self.conditions_table.setColumnCount(4)
        self.conditions_table.setHorizontalHeaderLabels(["번호", "컬럼명", "정렬순서", ""])
        
        # 컬럼 너비 설정
        header = self.conditions_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # 번호
        header.setSectionResizeMode(1, QHeaderView.Interactive)  # 컬럼명
        header.setSectionResizeMode(2, QHeaderView.Interactive)  # 정렬순서
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # 삭제
        header.setStretchLastSection(False)  # 마지막 섹션 고정
        
        # 헤더 크기 변경 이벤트 연결
        # header.sectionResized.connect(self._on_header_section_resized)

        # 초기 컬럼 크기 설정
        self._adjust_table_columns()

        self.conditions_table.verticalHeader().setVisible(False)
        self.conditions_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.conditions_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.conditions_table.horizontalHeader().setVisible(True)
        
        # 행 높이 설정 (필터와 동일하게)
        self.conditions_table.verticalHeader().setDefaultSectionSize(self.conditions_table.verticalHeader().defaultSectionSize() + 10)
        
        # 스크롤바 정책 설정 - 필요시에만 표시
        self.conditions_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.conditions_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 테이블 크기 정책 설정 - 내용에 맞게 조정
        self.conditions_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        
        # 테이블 최소 높이 설정 (헤더 + 기본 행 높이)
        min_height = self.conditions_table.horizontalHeader().height() + (self.conditions_table.verticalHeader().defaultSectionSize() * 3)
        self.conditions_table.setMinimumHeight(min_height)
        
        # 스크롤바 스타일 직접 적용
        self.conditions_table.verticalScrollBar().setStyleSheet("""
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
        
        self.conditions_table.horizontalScrollBar().setStyleSheet("""
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
        self.conditions_table.setStyleSheet("""
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

    def _on_header_section_resized(self, logical_index, old_size, new_size):
        """헤더 섹션 크기 변경 시 호출되는 메서드"""
        # 프로그램에 의한 크기 조정이 아닌 경우에만 사용자 조정으로 기록
        if not self._is_programmatic_resize and logical_index in [1, 2]:
            self._user_adjusted_columns.add(logical_index)
        
        # 헤더 크기 변경 후 테이블이 전체 영역을 채우도록 조정
        QApplication.processEvents()
        self._adjust_table_for_full_width()

    def resizeEvent(self, event):
        """윈도우 크기 변경 시 테이블 컬럼 크기 조정"""
        super().resizeEvent(event)
        # 윈도우 크기 변경 시에는 사용자 조정 기록을 초기화
        self._user_adjusted_columns.clear()
        self._adjust_table_columns()

    def _adjust_table_columns(self):
        """테이블 컬럼 크기 조정 (초기 설정용)"""
        if not self.conditions_table:
            return
        
        self._is_programmatic_resize = True
        
        try:
            # 부모 컨테이너의 크기를 가져와서 테이블 크기 조정
            try:
                right_frame = self.parent.parent.parent.findChild(QFrame, "right_frame")
                if right_frame:
                    width = right_frame.width()
                else:
                    width = self.width()
            except:
                width = self.width()
            
            # 고정 컬럼들의 총 너비 (0, 3번째 컬럼)
            fixed_width = 60 + 60  # 번호 + 삭제버튼
            
            # 남은 공간을 1번과 2번 컬럼이 1:1 비율로 나누어 가짐
            remaining_width = max(200, width - fixed_width - 50)  # 최소 200px 보장
            column_name_width = int(remaining_width * 0.5)  # 1번 컬럼 (50%)
            order_width = int(remaining_width * 0.5)        # 2번 컬럼 (50%)
            
            # 컬럼 너비 설정 - 삭제 컬럼은 고정 크기 유지
            self.conditions_table.setColumnWidth(0, 60)                 # 번호 (고정)
            self.conditions_table.setColumnWidth(1, column_name_width)  # 컬럼명 (동적)
            self.conditions_table.setColumnWidth(2, order_width)        # 정렬순서 (동적)
            self.conditions_table.setColumnWidth(3, 60)                 # 삭제 (고정)
            
            # 테이블이 부모 컨테이너의 크기에 맞게 조정되도록 설정
            self.conditions_table.setMaximumWidth(16777215)  # 최대 제한 해제
        finally:
            self._is_programmatic_resize = False

    def _adjust_table_for_full_width(self):
        """테이블이 전체 너비를 채우도록 조정 (사용자 조정 후)"""
        if not self.conditions_table:
            return
        
        self._is_programmatic_resize = True
        
        try:
            # 부모 컨테이너의 크기를 가져오기
            try:
                right_frame = self.parent.parent.parent.findChild(QFrame, "right_frame")
                if right_frame:
                    available_width = right_frame.width()
                else:
                    available_width = self.width()
            except:
                available_width = self.width()
            
            # 현재 컬럼들의 총 너비 계산
            current_total_width = sum([
                self.conditions_table.columnWidth(0),  # 번호
                self.conditions_table.columnWidth(1),  # 컬럼명
                self.conditions_table.columnWidth(2),  # 정렬순서
                self.conditions_table.columnWidth(3)   # 삭제
            ])
            
            # 사용자가 조정하지 않은 컬럼들만 크기 조정
            if 1 not in self._user_adjusted_columns and 2 not in self._user_adjusted_columns:
                # 둘 다 조정하지 않은 경우: 1:1 비율로 조정
                fixed_width = 60 + 60  # 번호 + 삭제
                remaining_width = max(200, available_width - fixed_width - 50)
                column_name_width = int(remaining_width * 0.5)
                order_width = int(remaining_width * 0.5)
                
                self.conditions_table.setColumnWidth(1, column_name_width)
                self.conditions_table.setColumnWidth(2, order_width)
            elif 1 not in self._user_adjusted_columns:
                # 1번 컬럼만 조정하지 않은 경우: 남은 공간을 1번 컬럼에 할당
                fixed_width = 60 + 60 + self.conditions_table.columnWidth(2)  # 번호 + 삭제 + 정렬순서
                remaining_width = max(100, available_width - fixed_width - 50)
                self.conditions_table.setColumnWidth(1, remaining_width)
            elif 2 not in self._user_adjusted_columns:
                # 2번 컬럼만 조정하지 않은 경우: 남은 공간을 2번 컬럼에 할당
                fixed_width = 60 + 60 + self.conditions_table.columnWidth(1)  # 번호 + 삭제 + 컬럼명
                remaining_width = max(100, available_width - fixed_width - 50)
                self.conditions_table.setColumnWidth(2, remaining_width)
            
            # 테이블이 부모 컨테이너의 크기에 맞게 조정되도록 설정
            self.conditions_table.setMaximumWidth(16777215)  # 최대 제한 해제
        finally:
            self._is_programmatic_resize = False

    def _init_events(self):
        """이벤트 초기화"""
        self.save_button.clicked.connect(self._on_save_clicked)
        self.delete_btn.clicked.connect(self._on_delete_clicked)
        self.add_condition_button.clicked.connect(self.add_sort_condition)

    def add_sort_condition(self):
        """정렬 조건 추가"""
        row = self.conditions_table.rowCount()
        self.conditions_table.insertRow(row)
        
        # 번호
        number_item = QTableWidgetItem(str(row + 1))
        number_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.conditions_table.setItem(row, 0, number_item)
        
        # 컬럼명 콤보박스
        column_combo = QComboBox()
        column_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 5px 10px;
                color: #495057;
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
            QScrollBar:vertical {
                border: none;
                background: #f8f9fa;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #dee2e6;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #adb5bd;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # 컬럼 목록 추가
        self._populate_column_combo(column_combo)
        
        self.conditions_table.setCellWidget(row, 1, column_combo)
        
        # 정렬순서 콤보박스
        order_combo = QComboBox()
        order_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 5px 10px;
                color: #495057;
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
            QScrollBar:vertical {
                border: none;
                background: #f8f9fa;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #dee2e6;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #adb5bd;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QScrollBar:horizontal {
                border: none;
                background: #f8f9fa;
                height: 10px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #dee2e6;
                min-width: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #adb5bd;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)
        order_combo.addItems(["오름차순", "내림차순"])
        self.conditions_table.setCellWidget(row, 2, order_combo)
        
        # 삭제 버튼
        delete_button = QPushButton("삭제")
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        delete_button.clicked.connect(lambda: self.remove_sort_condition(row))
        self.conditions_table.setCellWidget(row, 3, delete_button)

    def _populate_column_combo(self, combo):
        """콤보박스에 컬럼 목록 추가"""
        combo.clear()
        
        # 여러 방법으로 컬럼 목록 가져오기 시도
        columns = []
        
        # 1. current_coulumns에서 가져오기
        if hasattr(self, 'current_coulumns') and self.current_coulumns:
            for schema in self.current_coulumns:
                if isinstance(schema, dict) and 'name' in schema:
                    columns.append(schema.get('name', ''))
                elif isinstance(schema, str):
                    columns.append(schema)
        
        # 2. data_source에서 직접 가져오기
        if not columns and self.data_source:
            if hasattr(self.data_source, 'schema'):
                for schema in self.data_source.schema:
                    if isinstance(schema, dict) and 'name' in schema:
                        columns.append(schema.get('name', ''))
                    elif isinstance(schema, str):
                        columns.append(schema)
            elif hasattr(self.data_source, 'get') and self.data_source.get("schemas"):
                for schema in self.data_source.get("schemas", []):
                    if isinstance(schema, dict) and 'name' in schema:
                        columns.append(schema.get('name', ''))
                    elif isinstance(schema, str):
                        columns.append(schema)
        
        # 3. 부모에서 스키마 정보 가져오기
        if not columns and self.parent:
            if hasattr(self.parent, 'current_data_source') and self.parent.current_data_source:
                if hasattr(self.parent.current_data_source, 'schema'):
                    for schema in self.parent.current_data_source.schema:
                        if isinstance(schema, dict) and 'name' in schema:
                            columns.append(schema.get('name', ''))
                        elif isinstance(schema, str):
                            columns.append(schema)
        
        # 컬럼 목록 추가
        for column in columns:
            if column and column not in [combo.itemText(i) for i in range(combo.count())]:
                combo.addItem(column)
        
        # 컬럼이 없으면 기본 메시지 추가
        if combo.count() == 0:
            combo.addItem("컬럼을 선택하세요")

    def remove_sort_condition(self, row):
        """정렬 조건 삭제"""
        self.conditions_table.removeRow(row)
        self.reorder_sort_conditions()

    def reorder_sort_conditions(self):
        """정렬 조건 번호 재정렬"""
        for row in range(self.conditions_table.rowCount()):
            number_item = QTableWidgetItem(str(row + 1))
            number_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.conditions_table.setItem(row, 0, number_item)

    def _on_save_clicked(self):
        """저장 버튼 클릭 시 처리"""
        # 정렬 조건 정보 가져오기
        sort_conditions = []
        
        for row in range(self.conditions_table.rowCount()):
            column_combo = self.conditions_table.cellWidget(row, 1)
            order_combo = self.conditions_table.cellWidget(row, 2)
            
            if column_combo and order_combo:
                column_name = column_combo.currentText()
                order_type = order_combo.currentText()
                
                if column_name:  # 컬럼명이 선택된 경우만 추가
                    sort_conditions.append({
                        'column': column_name,
                        'order': 'asc' if order_type == "오름차순" else 'desc'
                    })
        
        # 정렬 조건이 없는 경우 경고
        if not sort_conditions:
            msg = MessageDialog(self, "알림", "정렬 조건을 추가해주세요.")
            msg.exec()
            return

        # na_position_combo
        na_position_combo = self.na_position_combo.currentText()
        if na_position_combo == "마지막":
            na_position = "last"
        else:
            na_position = "first"

        # 플로우 데이터 업데이트
        try:
            # flow.json 파일 경로 찾기
            project_uuid = self.parent.parent.project_data.get("uuid")
            flow_uuid = self.parent.parent.flow_info.get('uuid', None)
            if flow_uuid is None:
                msg = MessageDialog(self, "오류", "현재 흐름 uuid를 찾을 수 없습니다.")
                msg.exec()
                return

            flow = get_flow_by_uuid(project_uuid, flow_uuid)
            if flow is None:
                msg = MessageDialog(self, "오류", "흐름 데이터를 찾을 수 없습니다.")
                msg.exec()
                return

            # 프로세스 데이터 구성
            process_data = {
                "process_type": "orderby",
                "na_position": na_position,
                "content": ', '.join([f"{cond['column']}({'오름차순' if cond['order'] == 'asc' else '내림차순'})" for cond in sort_conditions]),
                "sort_conditions": sort_conditions,
            }

            # 흐름에 프로세스 추가/수정
            if self.flow_pos == -1:
                # 신규 저장
                flow['processes'].append(process_data)
            else:
                # 수정 저장
                flow['processes'][self.flow_pos] = process_data

            update_flow(project_uuid, flow)

            # 성공 메시지 및 패널 새로고침
            msg = MessageDialog(self, "알림", "정렬 조건이 저장되었습니다.")
            msg.exec()
            
            # 부모 위젯에 변경사항 알림
            flow_panel = self.parent
            if flow_panel and hasattr(flow_panel, "set_flow_info"):
                updated_flow = get_flow_by_uuid(project_uuid, flow_uuid)
                flow_panel.set_flow_info(updated_flow)
                
                # 공통 함수를 사용하여 저장된 카드 선택 (original_flow_pos 전달)
                select_saved_process_card(flow_panel, process_data, updated_flow, self.flow_pos)
                
        except Exception as e:
            msg = MessageDialog(self, "오류", f"저장 중 오류가 발생했습니다: {str(e)}")
            msg.exec()

    def _on_delete_clicked(self):
        """삭제 버튼 클릭 시 처리"""
        confirmed = ConfirmDialog.confirm(self, '처리 삭제', '정말 삭제하겠습니까?')
        if not confirmed:
            return
        
        try:
            project_uuid = self.parent.parent.project_data.get('uuid', '')
            flow_uuid = self.parent.parent.flow_info.get('uuid', '')
            if not flow_uuid:
                msg = MessageDialog(self, "오류", "현재 흐름 uuid를 찾을 수 없습니다.")
                msg.exec()
                return
            
            delete_process_from_flow(project_uuid, flow_uuid, self.flow_pos)
            
            # 흐름 패널 새로고침
            flow_panel = self.parent
            if flow_panel and hasattr(flow_panel, "set_flow_info"):
                updated_flow = get_flow_by_uuid(project_uuid, flow_uuid)
                flow_panel.set_flow_info(updated_flow)

            # right_frame 비우기
            right_frame = self.parent.parent.parent.ui.projects_container.findChild(QFrame, 'right_frame')
            if right_frame and right_frame.layout():
                while right_frame.layout().count():
                    item = right_frame.layout().takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                        
            msg = MessageDialog(self, "알림", "정렬 프로세스가 삭제되었습니다.")
            msg.exec()
                        
        except Exception as e:
            msg = MessageDialog(self, "오류", f"삭제 중 오류가 발생했습니다: {str(e)}")
            msg.exec()

    def set_schema(self):
        """스키마 설정"""
        # 여러 방법으로 스키마 정보 가져오기
        if self.data_source and hasattr(self.data_source, 'schema'):
            self.current_coulumns = self.data_source.schema
        elif self.data_source and hasattr(self.data_source, 'get') and self.data_source.get("schemas"):
            self.current_coulumns = self.data_source.get("schemas", [])
        elif self.parent and hasattr(self.parent, 'current_data_source') and self.parent.current_data_source:
            if hasattr(self.parent.current_data_source, 'schema'):
                self.current_coulumns = self.parent.current_data_source.schema
        else:
            self.current_coulumns = []

    def set_process_data(self, process_data):
        """프로세스 데이터 설정"""
        if not process_data:
            return
        
        # 기존 테이블 내용 초기화
        self.conditions_table.setRowCount(0)
        
        # 정렬 조건 데이터 로드 (sort_conditions 필드 사용)
        sort_conditions = process_data.get('sort_conditions', [])
        na_position = process_data.get('na_position', 'last')

        if na_position == "last":
            self.na_position_combo.setCurrentText("마지막")
        else:
            self.na_position_combo.setCurrentText("처음")
        
        for i, condition in enumerate(sort_conditions):
            row = self.conditions_table.rowCount()
            self.conditions_table.insertRow(row)
            
            # 번호
            number_item = QTableWidgetItem(str(row + 1))
            number_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.conditions_table.setItem(row, 0, number_item)
            
            # 컬럼명 콤보박스
            column_combo = QComboBox()
            column_combo.setStyleSheet("""
                QComboBox {
                    background-color: white;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 5px 10px;
                    color: #495057;
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
                QScrollBar:vertical {
                    border: none;
                    background: #f8f9fa;
                    width: 10px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background: #dee2e6;
                    min-height: 20px;
                    border-radius: 5px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #adb5bd;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: none;
                }
                QScrollBar:horizontal {
                    border: none;
                    background: #f8f9fa;
                    height: 10px;
                    margin: 0px;
                }
                QScrollBar::handle:horizontal {
                    background: #dee2e6;
                    min-width: 20px;
                    border-radius: 5px;
                }
                QScrollBar::handle:horizontal:hover {
                    background: #adb5bd;
                }
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    width: 0px;
                }
                QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                    background: none;
                }
            """)
            
            # 컬럼 목록 추가
            self._populate_column_combo(column_combo)
            
            # 현재 컬럼명 설정
            current_column = condition.get('column', '')
            index = column_combo.findText(current_column)
            if index >= 0:
                column_combo.setCurrentIndex(index)
            
            self.conditions_table.setCellWidget(row, 1, column_combo)
            
            # 정렬순서 콤보박스
            order_combo = QComboBox()
            order_combo.setStyleSheet("""
                QComboBox {
                    background-color: white;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 5px 10px;
                    color: #495057;
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
                QScrollBar:vertical {
                    border: none;
                    background: #f8f9fa;
                    width: 10px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background: #dee2e6;
                    min-height: 20px;
                    border-radius: 5px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #adb5bd;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: none;
                }
                QScrollBar:horizontal {
                    border: none;
                    background: #f8f9fa;
                    height: 10px;
                    margin: 0px;
                }
                QScrollBar::handle:horizontal {
                    background: #dee2e6;
                    min-width: 20px;
                    border-radius: 5px;
                }
                QScrollBar::handle:horizontal:hover {
                    background: #adb5bd;
                }
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    width: 0px;
                }
                QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                    background: none;
                }
            """)
            order_combo.addItems(["오름차순", "내림차순"])
            
            # 현재 정렬순서 설정
            current_order = condition.get('order', 'asc')
            order_combo.setCurrentText("오름차순" if current_order == 'asc' else "내림차순")
            
            self.conditions_table.setCellWidget(row, 2, order_combo)
            
            # 삭제 버튼
            delete_button = QPushButton("삭제")
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
                QPushButton:pressed {
                    background-color: #bd2130;
                }
            """)
            delete_button.clicked.connect(lambda checked, r=row: self.remove_sort_condition(r))
            self.conditions_table.setCellWidget(row, 3, delete_button)
