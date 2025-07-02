import copy
import logging
import os
import json
from PySide6.QtWidgets import (QFrame, QWidget, QTableWidget, QTableWidgetItem, QCheckBox, 
                               QAbstractItemView, QHBoxLayout, QHeaderView, QMessageBox, 
                               QComboBox, QPushButton, QVBoxLayout, QLabel, QLineEdit,
                               QAbstractScrollArea)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt, QRect, QSize, Signal
from PySide6.QtGui import QPainter, QColor, QIcon
from PySide6.QtWidgets import QStyleOptionButton, QStyle, QApplication
from src.ui.database import get_flow_list, get_flow_by_uuid, update_flow, delete_process_from_flow
from src.ui.components.message_dialog import MessageDialog
from src.ui.components.confirm_dialog import ConfirmDialog
from ui.action.action_common import validate_schema, select_saved_process_card
from PySide6.QtGui import QIntValidator, QDoubleValidator

logger = logging.getLogger(__name__)

class FilterWidget(QWidget):
    
    def __init__(self, parent=None, flow_pos=None):
        super().__init__(parent)
        loader = QUiLoader()
        ui_path = os.path.join(os.path.dirname(__file__), 'filter.ui')
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
        self.connect_conditions_combobox = self.findChild(QComboBox, 'connect_conditions_combobox')
        self.add_condition_button = self.findChild(QPushButton, 'add_condition_button')
        self.conditions_table = self.findChild(QTableWidget, 'conditions_table')
        self.save_button = self.findChild(QWidget, 'save_button')
        self.delete_btn = self.findChild(QWidget, 'delete_btn')

        # 필터 조건을 저장할 리스트
        self.filter_conditions = []

        self._init_table()
        self._init_events()
        self.set_schema()  # FilterWidget 생성 시 자동으로 schema를 테이블에 채움

    def _init_table(self):
        table = self.conditions_table
        table.setColumnCount(5)
        
        # 헤더 설정
        headers = ["컬럼명", "데이터타입", "연산자", "값", ""]
        table.setHorizontalHeaderLabels(headers)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Interactive)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setStretchLastSection(False)

        # 초기 컬럼 크기 설정
        self._adjust_table_columns()

        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.horizontalHeader().setVisible(True)
        
        # 행 높이 설정 (기본 높이 + 6px)
        table.verticalHeader().setDefaultSectionSize(table.verticalHeader().defaultSectionSize() + 10)
        
        # 스크롤바 정책 설정 - 항상 숨김으로 설정
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 테이블 크기 정책 설정
        table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        
        # 테이블 최소 높이 설정 (헤더 + 기본 행 높이)
        min_height = table.horizontalHeader().height() + (table.verticalHeader().defaultSectionSize() * 3)
        table.setMinimumHeight(min_height)
        
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
        if self.add_condition_button:
            self.add_condition_button.clicked.connect(self._add_condition_row)

    def resizeEvent(self, event):
        """윈도우 크기 변경 시 테이블 컬럼 크기 조정"""
        super().resizeEvent(event)
        self._adjust_table_columns()

    def _adjust_table_columns(self):
        """테이블 컬럼 크기 조정"""
        if not self.conditions_table:
            return
        
        # 현재 윈도우 너비 가져오기
        current_width = self.width()
        
        # 고정 컬럼들의 총 너비 (1, 2, 4번째 컬럼)
        fixed_width = 100 + 120 + 50  # 데이터타입 + 연산자 + 삭제버튼
        
        # 남은 공간을 0번과 3번 컬럼이 2:1 비율로 나누어 가짐
        remaining_width = max(200, current_width - fixed_width - 50)  # 최소 200px 보장
        column_name_width = int(remaining_width * 0.4)  # 0번 컬럼 (40%)
        value_width = int(remaining_width * 0.6)        # 3번 컬럼 (60%)
        
        # 컬럼 너비 설정
        self.conditions_table.setColumnWidth(0, column_name_width)  # 컬럼명 (동적)
        self.conditions_table.setColumnWidth(1, 100)                # 데이터타입 (고정, 100px)
        self.conditions_table.setColumnWidth(2, 120)                # 연산자 (고정, 120px)
        self.conditions_table.setColumnWidth(3, value_width)        # 값 (동적)
        self.conditions_table.setColumnWidth(4, 50)                 # 삭제 버튼 (고정)

    def _get_available_columns(self):
        """사용 가능한 컬럼 목록 가져오기"""
        try:
            if not self.parent or not hasattr(self.parent, 'flow_info'):
                return []
            
            flow_info = self.parent.flow_info
            if not flow_info:
                return []
            
            datasource = self.data_source
            if not datasource:
                return []
            
            # validate_schema를 사용하여 컬럼 목록 가져오기
            schemas = datasource.get('schemas', [])
            processes = flow_info.get('processes', [])
            flow_pos = self.flow_pos if hasattr(self, 'flow_pos') else -1
            
            available_columns, self.transformed_dict = validate_schema(self.parent, schemas, processes, flow_pos)
            
            return available_columns if available_columns else []
            
        except Exception as e:
            logger.error(f"컬럼 목록 가져오기 실패: {e}")
            return []
    
    def _get_data_type_label(self, data_type):
        """데이터 타입을 한글 라벨로 변환"""
        if data_type in ['FLOAT', 'DECIMAL', 'DOUBLE']:
            return "실수"
        elif data_type in ['INTEGER', 'LONG', 'INT', 'BIGINT']:
            return "정수"
        elif data_type in ['DATETIME', 'TIMESTAMP']:
            return "일시"
        elif data_type in ['DATE']:
            return "날짜"
        else:
            return "문자"

    def _reset_value_edit_style(self, value_edit):
        """값 입력 필드의 스타일을 원래대로 되돌림"""
        value_edit.setStyleSheet('''
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
                color: #000;
            }
        ''')

    def _on_column_changed(self, row, column_combo, value_edit, is_loading=False):
        """컬럼 선택 변경 시 호출되는 메서드"""
        try:
            column_name = column_combo.currentText()
            if not column_name or column_name not in self.transformed_dict:
                return
            
            # 컬럼의 스키마 정보 가져오기
            column_info = self.transformed_dict[column_name]
            data_type = column_info.get('data_type', '').upper()
            
            # 데이터 타입 라벨 업데이트
            data_type_item = self.conditions_table.item(row, 1)
            if data_type_item:
                type_label = self._get_data_type_label(data_type)
                data_type_item.setText(type_label)
            
            # 연산자 콤보박스 업데이트
            condition_combo = self.conditions_table.cellWidget(row, 2)
            if condition_combo:
                current_operator = condition_combo.currentText()
                condition_combo.clear()
                
                # data_type에 따른 연산자 설정
                if data_type in ['LONG', 'INT', 'INTEGER', 'BIGINT', 'DOUBLE', 'FLOAT', 'DECIMAL', 'NUMERIC']:
                    # 숫자형: ==, !=, >, >=, <=, <
                    operators = ["==", "!=", ">", ">=", "<=", "<"]
                elif data_type in ['DATE', 'DATETIME', 'TIMESTAMP']:
                    # 날짜형: ==, !=, >, >=, <=, <
                    operators = ["==", "!=", ">", ">=", "<=", "<"]
                else:
                    # 문자열형: ==, !=, >, >=, <=, <, in, not in, contains, startswith, endswith
                    operators = ["==", "!=", ">", ">=", "<=", "<", "in", "not in", "contains", "startswith", "endswith"]
                
                condition_combo.addItems(operators)
                
                # 기존 연산자가 새 목록에 있으면 유지, 없으면 첫 번째로 설정
                index = condition_combo.findText(current_operator)
                if index >= 0:
                    condition_combo.setCurrentIndex(index)
                else:
                    condition_combo.setCurrentIndex(0)
            
            # 기존 데이터 로드 시에는 값 초기화하지 않음
            if not is_loading:
                # 값 입력 필드 초기화
                value_edit.clear()
                value_edit.setValidator(None)
            
            # data_type에 따른 입력 제한 설정
            if data_type in ['LONG', 'INT', 'INTEGER', 'BIGINT']:
                # 정수형: 숫자만 입력 가능
                value_edit.setPlaceholderText("숫자만 입력 가능")
                value_edit.setValidator(QIntValidator())
            elif data_type in ['DOUBLE', 'FLOAT', 'DECIMAL', 'NUMERIC']:
                # 실수형: 숫자와 소수점만 입력 가능
                value_edit.setPlaceholderText("숫자와 소수점만 입력 가능")
                value_edit.setValidator(QDoubleValidator())
            elif data_type in ['DATE', 'DATETIME', 'TIMESTAMP']:
                # 날짜형: 날짜 형식만 입력 가능
                value_edit.setPlaceholderText("YYYY-MM-DD 형식으로 입력")
                # 날짜 형식 검증을 위한 정규식 설정
                import re
                date_regex = re.compile(r'^\d{4}-\d{2}-\d{2}$')
                value_edit.textChanged.connect(lambda text, edit=value_edit, regex=date_regex: self._validate_date_format(edit, text, regex))
            elif data_type in ['BOOLEAN', 'BOOL']:
                # 불린형: true/false만 입력 가능
                value_edit.setPlaceholderText("true 또는 false 입력")
                value_edit.textChanged.connect(lambda text, edit=value_edit: self._validate_boolean_format(edit, text))
            else:
                # 문자열형: 제한 없음
                value_edit.setPlaceholderText("값을 입력하세요")
                value_edit.setValidator(None)
                
        except Exception as e:
            logger.error(f"컬럼 변경 처리 실패: {e}")
    
    def _validate_date_format(self, value_edit, text, regex):
        """날짜 형식 검증"""
        if text and not regex.match(text):
            value_edit.setStyleSheet("""
                QLineEdit {
                    padding: 1px;
                    border: 1px solid #dc3545;
                    border-radius: 4px;
                    background-color: #fff5f5;
                    font-size: 14px;
                    color: #000;
                }
                QLineEdit:focus {
                    border: 1px solid #dc3545;
                    outline: 0;
                    color: #000;
                }
            """)
        else:
            self._reset_value_edit_style(value_edit)
    
    def _validate_boolean_format(self, value_edit, text):
        """불린 형식 검증"""
        if text and text.lower() not in ['true', 'false']:
            value_edit.setStyleSheet("""
                QLineEdit {
                    padding: 1px;
                    border: 1px solid #dc3545;
                    border-radius: 4px;
                    background-color: #fff5f5;
                    font-size: 14px;
                    color: #000;
                }
                QLineEdit:focus {
                    border: 1px solid #dc3545;
                    outline: 0;
                    color: #000;
                }
            """)
        else:
            self._reset_value_edit_style(value_edit)

    def _add_condition_row(self):
        """조건 행 추가"""
        row = self.conditions_table.rowCount()
        self.conditions_table.insertRow(row)
        
        # 컬럼명 선택 콤보박스
        column_combo = QComboBox()
        column_combo.addItems(self.available_columns)
        column_combo.setStyleSheet('''
            QComboBox {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 1px;
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
            QComboBox QAbstractItemView QScrollBar:vertical {
                border: none;
                background: #f8f9fa;
                width: 10px;
                margin: 0px;
            }
            QComboBox QAbstractItemView QScrollBar::handle:vertical {
                background: #dee2e6;
                min-height: 20px;
                border-radius: 5px;
            }
            QComboBox QAbstractItemView QScrollBar::handle:vertical:hover {
                background: #adb5bd;
            }
            QComboBox QAbstractItemView QScrollBar::add-line:vertical, QComboBox QAbstractItemView QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QComboBox QAbstractItemView QScrollBar::add-page:vertical, QComboBox QAbstractItemView QScrollBar::sub-page:vertical {
                background: none;
            }
        ''')
        # 첫 번째 컬럼 자동 선택
        if self.available_columns:
            column_combo.setCurrentIndex(0)
        self.conditions_table.setCellWidget(row, 0, column_combo)
        
        # 데이터 타입 셀 (빈 값으로 초기화)
        self.conditions_table.setItem(row, 1, QTableWidgetItem(""))
        
        # 연산자 선택 콤보박스
        condition_combo = QComboBox()
        # 초기 연산자는 기본값으로 설정 (나중에 컬럼 선택 시 업데이트됨)
        condition_combo.addItems(["==", "!=", ">", ">=", "<=", "<"])
        condition_combo.setStyleSheet(column_combo.styleSheet())
        self.conditions_table.setCellWidget(row, 2, condition_combo)
        
        # 값 입력 필드
        value_edit = QLineEdit()
        value_edit.textChanged.connect(lambda text, edit=value_edit: self._reset_value_edit_style(edit))
        value_edit.setStyleSheet('''
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
                color: #000;
            }
        ''')
        self.conditions_table.setCellWidget(row, 3, value_edit)
        
        # 컬럼 변경 이벤트 연결 (모든 위젯 설정 후)
        column_combo.currentTextChanged.connect(lambda text, r=row, combo=column_combo, edit=value_edit: self._on_column_changed(r, combo, edit, False))
        
        # 첫 번째 컬럼에 대한 데이터 타입 적용
        if self.available_columns:
            self._on_column_changed(row, column_combo, value_edit, is_loading=True)
        
        # 삭제 버튼
        delete_btn = QPushButton("삭제")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        delete_btn.clicked.connect(lambda: self._delete_condition_row(row))
        self.conditions_table.setCellWidget(row, 4, delete_btn)
        
        # 스크롤바 필요성 확인 및 조정
        self._adjust_scrollbar_visibility()

    def _adjust_scrollbar_visibility(self):
        """스크롤바 가시성 조정"""
        table = self.conditions_table
        if not table:
            return
        
        # 테이블의 전체 높이 계산
        header_height = table.horizontalHeader().height()
        row_height = table.verticalHeader().defaultSectionSize()
        total_rows = table.rowCount()
        content_height = header_height + (row_height * total_rows)
        
        # 테이블의 가시 영역 높이
        visible_height = table.viewport().height()
        
        # 스크롤바 필요성에 따라 정책 설정
        if content_height > visible_height:
            table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        else:
            table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def _delete_condition_row(self, row):
        """조건 행 삭제"""
        self.conditions_table.removeRow(row)
        
        # 삭제 버튼의 row 인덱스 업데이트
        for i in range(row, self.conditions_table.rowCount()):
            delete_btn = self.conditions_table.cellWidget(i, 4)
            if delete_btn:
                delete_btn.clicked.disconnect()
                delete_btn.clicked.connect(lambda checked, r=i: self._delete_condition_row(r))
        
        # 스크롤바 필요성 확인 및 조정
        self._adjust_scrollbar_visibility()

    def set_schema(self):
        """스키마 정보를 테이블에 설정"""
        try:
            if not self.parent or not hasattr(self.parent, 'flow_info'):
                return
            
            flow_info = self.parent.flow_info
            if not flow_info:
                return

            datasource = self.parent.current_data_source
            
            self.available_columns, self.transformed_dict = validate_schema(self.parent, datasource.get('schemas', []), flow_info.get('processes', []), self.flow_pos)


            self.conditions_table.setRowCount(0)
            # 기본 조건 추가 제거 - 사용자가 직접 추가하도록 함
                
        except Exception as e:
            import logging
            logging.error(f"스키마 설정 실패: {e}")

    def _load_process_data(self):
        """기존 프로세스 데이터 로드"""
        try:
            if not hasattr(self, 'process_data') or not self.process_data:
                return
            
            # filter_data에서 데이터 추출
            filter_data = self.process_data.get('filter_data', {})
            if not filter_data:
                return
                
            # 연결 방법 설정
            connect_method = filter_data.get("connect_method", "and")
            if self.connect_conditions_combobox:
                index = self.connect_conditions_combobox.findText(connect_method)
                if index >= 0:
                    self.connect_conditions_combobox.setCurrentIndex(index)
            
            # 조건들 로드
            conditions = filter_data.get("conditions", [])
            for condition in conditions:
                row = self.conditions_table.rowCount()
                self.conditions_table.insertRow(row)
                
                # 컬럼명 선택 콤보박스
                column_combo = QComboBox()
                column_combo.addItems(self.available_columns)
                column_combo.setStyleSheet('''
                    QComboBox {
                        background-color: white;
                        border: 1px solid #dee2e6;
                        border-radius: 4px;
                        padding: 1px;
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
                    QComboBox QAbstractItemView QScrollBar:vertical {
                        border: none;
                        background: #f8f9fa;
                        width: 10px;
                        margin: 0px;
                    }
                    QComboBox QAbstractItemView QScrollBar::handle:vertical {
                        background: #dee2e6;
                        min-height: 20px;
                        border-radius: 5px;
                    }
                    QComboBox QAbstractItemView QScrollBar::handle:vertical:hover {
                        background: #adb5bd;
                    }
                    QComboBox QAbstractItemView QScrollBar::add-line:vertical, QComboBox QAbstractItemView QScrollBar::sub-line:vertical {
                        height: 0px;
                    }
                    QComboBox QAbstractItemView QScrollBar::add-page:vertical, QComboBox QAbstractItemView QScrollBar::sub-page:vertical {
                        background: none;
                    }
                ''')
                column_name = condition.get("column", "")

                index = column_combo.findText(column_name)
                if index >= 0:
                    column_combo.setCurrentIndex(index)
                self.conditions_table.setCellWidget(row, 0, column_combo)
                
                # 데이터 타입 셀 (빈 값으로 초기화)
                self.conditions_table.setItem(row, 1, QTableWidgetItem(""))
                
                # 연산자 선택 콤보박스
                condition_combo = QComboBox()
                # 초기 연산자는 기본값으로 설정 (나중에 컬럼 선택 시 업데이트됨)
                condition_combo.addItems(["==", "!=", ">", ">=", "<=", "<"])
                condition_combo.setStyleSheet(column_combo.styleSheet())
                operator = condition.get("operator", "")
                index = condition_combo.findText(operator)
                if index >= 0:
                    condition_combo.setCurrentIndex(index)
                self.conditions_table.setCellWidget(row, 2, condition_combo)
                
                # 값 입력 필드
                value_edit = QLineEdit()
                value_edit.setText(condition.get("value", ""))
                value_edit.textChanged.connect(lambda text, edit=value_edit: self._reset_value_edit_style(edit))
                value_edit.setStyleSheet('''
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
                        color: #000;
                    }
                ''')
                self.conditions_table.setCellWidget(row, 3, value_edit)
                
                # 삭제 버튼
                delete_btn = QPushButton("삭제")
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #dc3545;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 5px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #c82333;
                    }
                """)
                delete_btn.clicked.connect(lambda checked, r=row: self._delete_condition_row(r))
                self.conditions_table.setCellWidget(row, 4, delete_btn)
                
                # 컬럼 변경 이벤트 연결 (모든 위젯 설정 후)
                column_combo.currentTextChanged.connect(lambda text, r=row, combo=column_combo, edit=value_edit: self._on_column_changed(r, combo, edit, False))
                
                # 기존 컬럼에 대한 데이터 타입 적용 (이벤트 연결 후)
                if column_name:
                    self._on_column_changed(row, column_combo, value_edit, is_loading=True)
            
            # 스크롤바 가시성 조정
            self._adjust_scrollbar_visibility()
            
            logger.info(f"필터 데이터 로드 완료: {len(conditions)}개 조건, 연결방법: {connect_method}")
                    
        except Exception as e:
            logger.error(f"프로세스 데이터 로드 실패: {e}")
            MessageDialog.critical(self, "오류", f"기존 필터 데이터 로드 중 오류가 발생했습니다: {str(e)}")

    def _on_save_clicked(self):
        """저장 버튼 클릭 시 처리"""
        try:
            # 입력값 검증
            if not self.connect_conditions_combobox:
                MessageDialog.warning(self, "입력 오류", "연결 방법을 선택할 수 없습니다.")
                return
            
            # 테이블에서 필터 조건 추출
            filter_data = {
                "connect_method": self.connect_conditions_combobox.currentText(),
                "conditions": []
            }
            
            # 조건이 하나도 없는 경우 경고
            if self.conditions_table.rowCount() == 0:
                MessageDialog.warning(self, "입력 오류", "최소 하나의 조건을 추가해주세요.")
                return
            
            # 각 행의 조건 데이터 추출
            for row in range(self.conditions_table.rowCount()):
                column_combo = self.conditions_table.cellWidget(row, 0)
                condition_combo = self.conditions_table.cellWidget(row, 2)
                value_edit = self.conditions_table.cellWidget(row, 3)
                
                if column_combo and condition_combo and value_edit:
                    column_name = column_combo.currentText()
                    operator = condition_combo.currentText()
                    value = value_edit.text().strip()
                    
                    # 필수 값 검증
                    if not column_name:
                        MessageDialog.warning(self, "입력 오류", f"{row + 1}번째 행의 컬럼명을 선택해주세요.")
                        column_combo.setFocus()
                        return
                    
                    if not operator:
                        MessageDialog.warning(self, "입력 오류", f"{row + 1}번째 행의 연산자를 선택해주세요.")
                        condition_combo.setFocus()
                        return
                    
                    if not value:
                        MessageDialog.warning(self, "입력 오류", f"{row + 1}번째 행의 값을 입력해주세요.")
                        value_edit.setFocus()
                        return
                    
                    condition = {
                        "column": column_name,
                        "operator": operator,
                        "value": value
                    }
                    filter_data["conditions"].append(condition)
                else:
                    MessageDialog.warning(self, "입력 오류", f"{row + 1}번째 행의 데이터가 올바르지 않습니다.")
                    return

            # flow.json 파일 경로 찾기
            project_uuid = self.parent.parent.project_data.get("uuid")
            flow_uuid = self.parent.parent.flow_info.get('uuid', None)
            if flow_uuid is None:
                MessageDialog.warning(self, "조회 실패", "현재 흐름 uuid를 찾을 수 없습니다.")
                return

            flow = get_flow_by_uuid(project_uuid, flow_uuid)
            if flow is None:
                MessageDialog.critical(self, "오류", "흐름 데이터를 찾을 수 없습니다.")
                return

            # 프로세스 데이터 구성
            process_data = {
                "process_type": "filter",
                "content": "필터",
                "filter_data": filter_data
            }

            # 흐름에 프로세스 추가/수정
            if self.flow_pos == -1:
                # 신규 저장
                flow['processes'].append(process_data)
                logger.info(f"필터 신규 저장: {len(filter_data['conditions'])}개 조건, 연결방법: {filter_data['connect_method']}")
            else:
                # 수정 저장
                flow['processes'][self.flow_pos] = process_data
                logger.info(f"필터 수정 저장: {len(filter_data['conditions'])}개 조건, 연결방법: {filter_data['connect_method']}")

            update_flow(project_uuid, flow)

            # 성공 메시지 및 패널 새로고침
            MessageDialog.information(self, "저장 완료", f"필터 설정이 저장되었습니다.")
            
            flow_panel = self.parent
            if flow_panel and hasattr(flow_panel, "set_flow_info"):
                updated_flow = get_flow_by_uuid(project_uuid, flow_uuid)
                flow_panel.set_flow_info(updated_flow)
                
                # 공통 함수를 사용하여 저장된 카드 선택 (original_flow_pos 전달)
                select_saved_process_card(flow_panel, process_data, updated_flow, self.flow_pos)

        except Exception as e:
            logger.error(f"필터 저장 실패: {e}")
            MessageDialog.critical(self, "오류", f"필터 저장 중 오류가 발생했습니다: {str(e)}")

    def _on_delete_clicked(self):
        """삭제 버튼 클릭 시 처리"""
        confirmed = ConfirmDialog.confirm(self, '처리 삭제', '정말 삭제하겠습니까?')
        if not confirmed:
            return
        
        try:
            project_uuid = self.parent.parent.project_data.get('uuid', '')
            flow_uuid = self.parent.parent.flow_info.get('uuid', '')
            if not flow_uuid:
                MessageDialog.warning(self, "조회 실패", "현재 흐름 uuid를 찾을 수 없습니다.")
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
                        
        except Exception as e:
            logger.error(f"필터 삭제 실패: {e}")
            MessageDialog.critical(self, "오류", f"필터 삭제 중 오류가 발생했습니다: {str(e)}")

    def set_process_data(self, process_data):
        """프로세스 데이터 설정 (편집용)"""
        self.process_data = process_data
        if hasattr(self, 'conditions_table'):
            self.set_schema()
            self._load_process_data() 