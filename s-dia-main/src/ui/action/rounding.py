import copy
import os
import json
from PySide6.QtWidgets import (QFrame, QWidget, QTableWidget, QTableWidgetItem, QCheckBox, 
                               QAbstractItemView, QHeaderView, QMessageBox, QAbstractScrollArea,
                               QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QLineEdit)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt, QRect, QSize, QTimer
from PySide6.QtGui import QPainter, QColor, QIcon
from PySide6.QtWidgets import QStyleOptionButton, QStyle, QApplication
from src.ui.database import get_flow_list, get_flow_by_uuid, update_flow, delete_process_from_flow
from src.ui.components.message_dialog import MessageDialog
from src.ui.components.confirm_dialog import ConfirmDialog
from src.ui.components.custom_checkbox import CheckBoxHeader
from ui.action.action_common import validate_schema, select_saved_process_card
from utils.enum_utils import sdataTypeToView

class RoundingWidget(QWidget):
    def __init__(self, parent=None, flow_pos=None):
        super().__init__(parent)
        loader = QUiLoader()
        ui_path = os.path.join(os.path.dirname(__file__), 'rounding.ui')
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
        self.title_label = self.findChild(QLabel, 'title_label')
        self.rounding_method_combo = self.findChild(QComboBox, 'rounding_method_combo')
        self.decimal_places_edit = self.findChild(QLineEdit, 'decimal_places_edit')
        self.example_label = self.findChild(QLabel, 'example_label')
        self.columns_table = self.findChild(QTableWidget, 'columns_table')
        self.save_button = self.findChild(QPushButton, 'save_button')
        self.delete_btn = self.findChild(QPushButton, 'delete_btn')

        # 라운딩 자리 입력 필드에 입력 검증 추가
        if self.decimal_places_edit:
            self.decimal_places_edit.textChanged.connect(self._validate_decimal_input)

        # 체크박스 리스트
        self.row_checkboxes = []

        # 전체 위젯 스타일시트 적용
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                color: #212529;
            }
            QLabel {
                color: #212529;
                font-size: 14px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: #ffffff;
                font-size: 14px;
                color: #495057;
            }
            QLineEdit:focus {
                border: 1px solid #80bdff;
                outline: 0;
                color: #495057;
            }
            QPushButton {
                padding: 8px 16px;
                border: 1px solid #007bff;
                border-radius: 4px;
                background-color: #007bff;
                color: white;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #0056b3;
                border-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
                border-color: #004085;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                border-color: #6c757d;
                color: #adb5bd;
            }
        """)

        # 타이틀 라벨 스타일
        if self.title_label:
            self.title_label.setStyleSheet("""
                QLabel {
                    color: #212529;
                    font-size: 18px;
                    font-weight: bold;
                    padding: 10px 0px;
                    background-color: white;
                }
            """)

        # 콤보박스 스타일
        combo_style = '''
            QComboBox {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
                color: #495057;
                font-size: 14px;
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
        '''

        if self.rounding_method_combo:
            self.rounding_method_combo.setStyleSheet(combo_style)

        # 예시 라벨 스타일 (빨간색)
        if self.example_label:
            self.example_label.setStyleSheet("""
                QLabel {
                    background: white;
                    color: #dc3545;
                    font-size: 12px;
                    font-style: italic;
                }
            """)

        # 삭제 버튼 스타일
        if self.delete_btn:
            self.delete_btn.setStyleSheet("""
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
            """)

        self._init_table()
        self._init_events()
        self.set_schema()
        
        # 초기 예시 설정
        self._update_example()

    def on_header_checkbox_toggled(self, checked):
        """헤더 체크박스 토글 시 호출"""
        self._toggle_all_checkboxes(checked)

    def _init_table(self):
        """테이블 초기화"""
        table = self.columns_table
        table.setColumnCount(4)
        
        # 헤더 설정
        headers = ["", "순서", "컬럼명", "설명"]
        table.setHorizontalHeaderLabels(headers)

        # 커스텀 헤더 적용
        self.checkbox_header = CheckBoxHeader(Qt.Horizontal, table)
        table.setHorizontalHeader(self.checkbox_header)
        self.checkbox_header.toggled.connect(self.on_header_checkbox_toggled)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # 체크박스
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # 순서
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # 컬럼명
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # 설명
        header.setStretchLastSection(False)

        # 컬럼 너비 설정
        table.setColumnWidth(0, 50)  # 체크박스
        table.setColumnWidth(1, 60)  # 순서

        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.horizontalHeader().setVisible(True)
        
        # 행 높이 설정
        table.verticalHeader().setDefaultSectionSize(table.verticalHeader().defaultSectionSize() + 10)
        
        # 스크롤바 스타일
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
        
        # 테이블 스타일시트
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
        """)

    def _toggle_all_checkboxes(self, checked):
        """모든 체크박스 토글"""
        for chk in self.row_checkboxes:
            chk.setChecked(checked)

    def _init_events(self):
        """이벤트 초기화"""
        if self.save_button:
            self.save_button.clicked.connect(self._on_save_clicked)
        if self.delete_btn:
            self.delete_btn.clicked.connect(self._on_delete_clicked)
        
        # 라운딩 방식과 자리 변경 시 예시 업데이트
        if self.rounding_method_combo:
            self.rounding_method_combo.currentTextChanged.connect(self._update_example)
        if self.decimal_places_edit:
            self.decimal_places_edit.textChanged.connect(self._update_example)

    def _update_example(self):
        """라운딩 예시 업데이트"""
        try:
            # 라운딩 방식 가져오기
            rounding_method = self.rounding_method_combo.currentText()
            
            # 라운딩 자리 가져오기
            decimal_places_text = self.decimal_places_edit.text().strip()
            if not decimal_places_text:
                self.example_label.setText("123456.7890 → 123456.7890")
                return
                
            try:
                decimal_places = int(decimal_places_text)
            except ValueError:
                self.example_label.setText("123456.7890 → 123456.7890")
                return
            
            # 원본 숫자
            original_number = 123456.7890
            
            # 라운딩 적용
            result = self._apply_rounding(original_number, decimal_places, rounding_method)
            
            # 예시 업데이트
            self.example_label.setText(f"123456.7890 → {result}")
            
        except Exception as e:
            # 오류 발생 시 기본값 표시
            self.example_label.setText("123456.7890 → 123456.7890")

    def _apply_rounding(self, number, decimal_places, method):
        """라운딩 적용"""
        import math
        
        # 소수점 기준으로 라운딩 위치 계산
        # decimal_places가 양수면 소수점 오른쪽, 음수면 소수점 왼쪽
        multiplier = 10 ** decimal_places
        
        if method == "반올림":
            result = round(number * multiplier) / multiplier
        elif method == "올림":
            result = math.ceil(number * multiplier) / multiplier
        elif method == "내림":
            result = math.floor(number * multiplier) / multiplier
        else:
            result = number
        
        # 결과 포맷팅
        if decimal_places >= 0:
            # 소수점 이하 자리수 지정
            return f"{result:.{decimal_places}f}"
        else:
            # 정수로 표시
            return f"{int(result)}"

    def set_schema(self):
        """스키마 설정"""
        try:
            if not self.parent or not hasattr(self.parent, 'flow_info'):
                return
            
            flow_info = self.parent.flow_info
            if not flow_info:
                return

            datasource = self.parent.current_data_source
            
            # validate_schema를 사용하여 사용 가능한 컬럼들 가져오기
            self.available_columns, self.transformed_dict = validate_schema(self.parent, datasource.get('schemas', []), flow_info.get('processes', []), self.flow_pos)
            
            # 숫자형 컬럼만 필터링
            numeric_columns = []
            numeric_transformed_dict = {}
            
            for column_name in self.available_columns:
                schema = self.transformed_dict.get(column_name, {})
                data_type = schema.get('data_type', '').lower()
                
                # 숫자형 데이터 타입 확인
                if any(numeric_type in data_type for numeric_type in ['long', 'int', 'float', 'double', 'decimal', 'number', 'numeric']):
                    numeric_columns.append(column_name)
                    numeric_transformed_dict[column_name] = schema
            
            # 숫자형 컬럼만 사용
            self.available_columns = numeric_columns
            self.transformed_dict = numeric_transformed_dict
            
            # 테이블 초기화
            self.columns_table.setRowCount(0)
            self.row_checkboxes = []
            
            if self.available_columns:
                table = self.columns_table
                table.setRowCount(len(self.available_columns))
                
                for i, column_name in enumerate(self.available_columns):
                    schema = self.transformed_dict.get(column_name, {})
                    
                    # 체크박스 위젯 생성
                    widget = QWidget()
                    layout = QHBoxLayout(widget)
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.setAlignment(Qt.AlignCenter)
                    checkbox = QCheckBox()
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
                    table.setCellWidget(i, 0, widget)
                    
                    # 순서
                    order_item = QTableWidgetItem(str(i + 1))
                    order_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    table.setItem(i, 1, order_item)
                    
                    # 컬럼명
                    column_name_item = QTableWidgetItem(schema.get('name', ''))
                    table.setItem(i, 2, column_name_item)
                    
                    # 설명
                    comment_item = QTableWidgetItem(schema.get('comment', ''))
                    table.setItem(i, 3, comment_item)
                
        except Exception as e:
            import logging
            logging.error(f"스키마 설정 실패: {e}")
            MessageDialog.critical(self, "오류", f"스키마 설정 중 오류가 발생했습니다: {str(e)}")

    def _on_save_clicked(self):
        """저장 버튼 클릭 시 호출"""
        try:
            # 입력 데이터 검증
            if not self._validate_input():
                return
                
            # 프로세스 데이터 생성
            process_data = self._create_process_data()
            
            # flow.json 파일 경로 찾기
            project_uuid = self.parent.parent.project_data.get("uuid")
            flow_uuid = self.parent.parent.flow_info.get('uuid', None)
            if flow_uuid is None:
                MessageDialog.critical(self, "조회 실패", "현재 흐름 uuid를 찾을 수 없습니다.")
                return

            flow = get_flow_by_uuid(project_uuid, flow_uuid)
            if flow is None:
                MessageDialog.critical(self, "오류", "흐름 데이터를 찾을 수 없습니다.")
                return

            # 흐름에 프로세스 추가/수정
            if self.flow_pos == -1:
                flow['processes'].append(process_data)
            else:
                flow['processes'][self.flow_pos] = process_data

            update_flow(project_uuid, flow)
            
            # 성공 메시지 및 패널 새로고침
            MessageDialog.information(self, "저장 완료", "라운딩 설정이 저장되었습니다.")
            
            flow_panel = self.parent
            if flow_panel and hasattr(flow_panel, "set_flow_info"):
                updated_flow = get_flow_by_uuid(project_uuid, flow_uuid)
                flow_panel.set_flow_info(updated_flow)
                
                # 공통 함수를 사용하여 저장된 카드 선택 (original_flow_pos 전달)
                select_saved_process_card(flow_panel, process_data, updated_flow, self.flow_pos)
                
            # 임시 카드 제거
            if hasattr(self.parent, '_remove_temp_process_card'):
                self.parent._remove_temp_process_card()
            
        except Exception as e:
            MessageDialog.critical(self, "오류", f"저장 중 오류가 발생했습니다: {str(e)}")

    def _validate_input(self):
        """입력 데이터 검증"""
        # 라운딩 방식 선택 확인
        if self.rounding_method_combo.currentIndex() < 0:
            MessageDialog.warning(self, "경고", "라운딩 방식을 선택해주세요.")
            return False
            
        # 라운딩 자리 입력 확인
        decimal_places_text = self.decimal_places_edit.text().strip()
        if not decimal_places_text:
            MessageDialog.warning(self, "경고", "라운딩 자리를 입력해주세요.")
            return False
            
        try:
            decimal_places = int(decimal_places_text)
        except ValueError:
            MessageDialog.warning(self, "경고", "라운딩 자리는 정수로 입력해주세요.")
            return False
            
        # 선택된 컬럼 확인
        selected_columns = []
        for i, checkbox in enumerate(self.row_checkboxes):
            if checkbox.isChecked():
                selected_columns.append(self.available_columns[i])
                
        if not selected_columns:
            MessageDialog.warning(self, "경고", "라운딩할 컬럼을 하나 이상 선택해주세요.")
            return False
            
        return True

    def _create_process_data(self):
        """프로세스 데이터 생성"""
        rounding_method = self.rounding_method_combo.currentText()
        decimal_places = int(self.decimal_places_edit.text().strip())
        
        # 선택된 컬럼들
        selected_columns = []
        for i, checkbox in enumerate(self.row_checkboxes):
            if checkbox.isChecked():
                selected_columns.append(self.available_columns[i])
        
        # 라운딩 방식 매핑
        method_mapping = {
            "반올림": "round",
            "올림": "ceil", 
            "내림": "floor"
        }
        
        process_data = {
            "process_type": "rounding",
            "rounding_method": method_mapping.get(rounding_method, "round"),
            "decimal_places": decimal_places,
            "columns": selected_columns,
            "content": f"라운딩: {rounding_method} ({decimal_places}자리) - {len(selected_columns)}개 컬럼"
        }
        
        return process_data

    def _on_delete_clicked(self):
        """삭제 버튼 클릭 시 처리"""
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
        """기존 프로세스 데이터 설정 (편집용)"""
        if not process_data:
            return
            
        try:
            # 라운딩 방식 설정
            method_mapping = {
                "round": "반올림",
                "ceil": "올림",
                "floor": "내림"
            }
            rounding_method = method_mapping.get(process_data.get("rounding_method", "round"), "반올림")
            for i in range(self.rounding_method_combo.count()):
                if self.rounding_method_combo.itemText(i) == rounding_method:
                    self.rounding_method_combo.setCurrentIndex(i)
                    break
                    
            # 라운딩 자리 설정
            decimal_places = process_data.get("decimal_places", 0)
            self.decimal_places_edit.setText(str(decimal_places))
                    
            # 선택된 컬럼들 체크
            selected_columns = process_data.get("columns", [])
            for i, checkbox in enumerate(self.row_checkboxes):
                if i < len(self.available_columns):
                    column_name = self.available_columns[i]
                    checkbox.setChecked(column_name in selected_columns)
                            
        except Exception as e:
            MessageDialog.critical(self, "오류", f"프로세스 데이터 설정 중 오류가 발생했습니다: {str(e)}")

    def _validate_decimal_input(self, text):
        """라운딩 자리 입력 검증"""
        import re
        
        # 빈 문자열이면 허용 (사용자가 지우는 중일 수 있음)
        if not text:
            return
            
        # 숫자, 음수, 소수점만 허용하는 정규식
        pattern = r'^-?\d*\.?\d*$'
        
        if not re.match(pattern, text):
            # 잘못된 문자가 입력된 경우 이전 텍스트로 되돌리기
            cursor_pos = self.decimal_places_edit.cursorPosition()
            current_text = self.decimal_places_edit.text()
            
            # 마지막 입력된 문자 제거
            if len(current_text) > 0:
                new_text = current_text[:-1]
                self.decimal_places_edit.setText(new_text)
                # 커서 위치 조정
                self.decimal_places_edit.setCursorPosition(min(cursor_pos - 1, len(new_text)))
            
            # 경고 메시지 표시
            # MessageDialog.warning(self, "경고", "라운딩 자리는 숫자, 음수, 소수점만 입력 가능합니다.") 