import copy
import os
import json
from PySide6.QtWidgets import (QFrame, QWidget, QTableWidget, QTableWidgetItem, QCheckBox, 
                               QAbstractItemView, QHeaderView, QMessageBox, QAbstractScrollArea,
                               QComboBox, QPushButton, QVBoxLayout, QLabel, QSizePolicy, QLineEdit)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt, QRect, QSize, QTimer
from PySide6.QtGui import QPainter, QColor, QIcon
from PySide6.QtWidgets import QStyleOptionButton, QStyle, QApplication
from src.ui.database import get_flow_list, get_flow_by_uuid, update_flow, delete_process_from_flow, get_datasources_list, get_datasource
from src.ui.components.message_dialog import MessageDialog
from src.ui.components.confirm_dialog import ConfirmDialog
from src.ui.components.custom_checkbox import CheckBoxHeader
from ui.action.action_common import validate_schema, select_saved_process_card
from utils.enum_utils import sdataTypeToView

class JoinWidget(QWidget):
    def __init__(self, parent=None, flow_pos=None):
        super().__init__(parent)
        loader = QUiLoader()
        ui_path = os.path.join(os.path.dirname(__file__), 'join.ui')
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
        self.current_datasource_line = self.findChild(QLineEdit, 'current_datasource_line')
        self.join_datasource_combo = self.findChild(QComboBox, 'join_datasource_combo')
        self.join_type_combo = self.findChild(QComboBox, 'join_type_combo')
        self.join_columns_table = self.findChild(QTableWidget, 'join_columns_table')
        self.add_column_button = self.findChild(QPushButton, 'add_column_button')
        self.save_button = self.findChild(QPushButton, 'save_button')
        self.delete_btn = self.findChild(QPushButton, 'delete_btn')

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
            QLineEdit:disabled {
                background-color: #e9ecef;
                color: #6c757d;
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

        # 현재 데이터 소스 라인에디트 스타일
        if self.current_datasource_line:
            self.current_datasource_line.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    border: 1px solid #ced4da;
                    border-radius: 4px;
                    background-color: #e9ecef;
                    font-size: 14px;
                    color: #6c757d;
                }
                QLineEdit:focus {
                    border: 1px solid #80bdff;
                    outline: 0;
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
        '''

        if self.join_datasource_combo:
            self.join_datasource_combo.setStyleSheet(combo_style)
        
        if self.join_type_combo:
            self.join_type_combo.setStyleSheet(combo_style)

        # 스크롤바 스타일 직접 적용
        self.join_columns_table.verticalScrollBar().setStyleSheet("""
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
        
        self.join_columns_table.horizontalScrollBar().setStyleSheet("""
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
        self.join_columns_table.setStyleSheet("""
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

        self._init_events()
        self._init_tables()
        self._populate_datasource_combo()
        self._load_current_datasource_info()
        self.set_schema()  # JoinWidget 생성 시 자동으로 schema를 설정

    def _init_events(self):
        """이벤트 초기화"""
        self.save_button.clicked.connect(self._on_save_clicked)
        self.join_datasource_combo.currentIndexChanged.connect(self._on_datasource_combo_changed)
        self.add_column_button.clicked.connect(self._on_add_column_clicked)
        self.delete_btn.clicked.connect(self._on_delete_clicked)

    def _init_tables(self):
        """테이블 초기화"""
        # 결합 컬럼 테이블 설정 (삭제 버튼 컬럼 추가)
        self.join_columns_table.setColumnCount(4)
        self.join_columns_table.setHorizontalHeaderLabels(["순서", "컬럼명(left)", "대상 컬럼명(right)", ""])
        
        header = self.join_columns_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # 순서만 고정 크기
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 컬럼명(left) - 윈도우 크기에 맞춰 늘어남
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # 대상 컬럼명(right) - 윈도우 크기에 맞춰 늘어남
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # 삭제 버튼 컬럼 고정 크기
        header.setStretchLastSection(False)
        
        # 순서 컬럼과 삭제 버튼 컬럼만 고정 크기 설정
        self.join_columns_table.setColumnWidth(0, 60)  # 순서만 고정 크기
        self.join_columns_table.setColumnWidth(3, 60)  # 삭제 버튼 컬럼 고정 크기
        
        # 테이블 초기화 - 모든 행 제거
        self.join_columns_table.setRowCount(0)
        
        # 행 높이 설정 (필터와 동일하게)
        self.join_columns_table.verticalHeader().setDefaultSectionSize(self.join_columns_table.verticalHeader().defaultSectionSize() + 10)

    def _populate_datasource_combo(self):
        """데이터 소스 콤보박스에 목록 채우기 (현재 데이터 소스 제외)"""
        if not self.project_data:
            return
            
        project_uuid = self.project_data.get("uuid")
        if not project_uuid:
            return
            
        try:
            datasources = get_datasources_list(project_uuid)
            current_datasource_uuid = self.data_source.get("uuid") if self.data_source else None
            
            self.join_datasource_combo.clear()
            
            for datasource in datasources:
                datasource_uuid = datasource.get("uuid")
                datasource_name = datasource.get("name", "")
                
                # 현재 데이터 소스는 제외
                if datasource_uuid != current_datasource_uuid:
                    self.join_datasource_combo.addItem(datasource_name, datasource_uuid)
                    
        except Exception as e:
            MessageDialog.critical(self, "오류", f"데이터 소스 목록을 불러오는 중 오류가 발생했습니다: {str(e)}")

    def _load_current_datasource_info(self):
        """현재 데이터 소스 정보 로드"""
        if self.data_source:
            datasource_name = self.data_source.get("name", "")
            self.current_datasource_line.setText(datasource_name)

    def _on_datasource_combo_changed(self, index):
        """데이터 소스 콤보박스 변경 시 호출"""
        if index >= 0:
            # 대상 컬럼명(right) 콤보박스 초기화
            self._update_right_columns()

    def _update_right_columns(self):
        """대상 컬럼명(right) 콤보박스 업데이트"""
        selected_uuid = self.join_datasource_combo.currentData()
        
        # 모든 행의 대상 컬럼명(right) 콤보박스 업데이트
        for row in range(self.join_columns_table.rowCount()):
            right_combo = self.join_columns_table.cellWidget(row, 2)
            if right_combo:
                right_combo.clear()
                right_combo.addItem("")  # 빈 값 추가 (초기값)
                
                if selected_uuid:
                    try:
                        target_datasource = get_datasource(self.project_data.get("uuid"), selected_uuid)
                        import logging
                        logging.debug(f"대상 데이터 소스: {target_datasource}")
                        
                        if target_datasource and 'schemas' in target_datasource:
                            logging.debug(f"스키마 정보: {target_datasource['schemas']}")
                            # schemas에서 컬럼명 추출
                            for schema in target_datasource['schemas']:
                                logging.debug(f"개별 스키마: {schema}")
                                if 'name' in schema:
                                    right_combo.addItem(schema['name'])
                                elif 'column_name' in schema:
                                    right_combo.addItem(schema['column_name'])
                        else:
                            logging.debug(f"스키마 정보가 없습니다. target_datasource keys: {target_datasource.keys() if target_datasource else 'None'}")
                    except Exception as e:
                        import logging
                        logging.error(f"대상 데이터 소스 정보 로드 오류: {str(e)}")
                        MessageDialog.critical(self, "오류", f"대상 데이터 소스 정보를 불러오는 중 오류가 발생했습니다: {str(e)}")

    def _on_add_column_clicked(self):
        """결합 컬럼 추가 버튼 클릭 시 호출"""
        current_row_count = self.join_columns_table.rowCount()
        
        # 새 행 추가
        self.join_columns_table.insertRow(current_row_count)
        
        # 순서 설정 (1부터 시작)
        order_item = QTableWidgetItem(str(current_row_count + 1))
        order_item.setFlags(order_item.flags() & ~Qt.ItemIsEditable)  # 읽기 전용
        self.join_columns_table.setItem(current_row_count, 0, order_item)
        
        # 콤보박스 스타일 정의
        combo_style = '''
            QComboBox {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 4px;
                color: #495057;
                font-size: 13px;
            }
            QComboBox:focus {
                border: 1px solid #339af0;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 20px;
                border: none;
            }
            QComboBox::down-arrow {
                image: url(src/ui/resources/images/down-arrow-svgrepo-com.svg);
                width: 8px;
                height: 8px;
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
                padding: 6px 15px;
                color: #495057;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #e9ecef;
                color: #000;
            }
            QComboBox QAbstractItemView QScrollBar:vertical {
                border: none;
                background: #f8f9fa;
                width: 8px;
                margin: 0px;
            }
            QComboBox QAbstractItemView QScrollBar::handle:vertical {
                background: #dee2e6;
                min-height: 15px;
                border-radius: 4px;
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
        '''
        
        # 컬럼명(left) 콤보박스 추가 - validate_schema에서 받은 컬럼들 사용
        left_combo = QComboBox()
        left_combo.setStyleSheet(combo_style)
        left_combo.addItem("")  # 빈 값 추가 (초기값)
        
        # validate_schema에서 받은 컬럼들 추가
        if hasattr(self, 'available_columns') and self.available_columns:
            for column in self.available_columns:
                left_combo.addItem(column)
        
        self.join_columns_table.setCellWidget(current_row_count, 1, left_combo)
        
        # 대상 컬럼명(right) 콤보박스 추가
        right_combo = QComboBox()
        right_combo.setStyleSheet(combo_style)
        right_combo.addItem("")  # 빈 값 추가 (초기값)
        
        # 선택된 데이터 소스의 컬럼들 추가
        selected_uuid = self.join_datasource_combo.currentData()
        if selected_uuid:
            try:
                target_datasource = get_datasource(self.project_data.get("uuid"), selected_uuid)
                import logging
                logging.debug(f"대상 데이터 소스: {target_datasource}")
                
                if target_datasource and 'schemas' in target_datasource:
                    logging.debug(f"스키마 정보: {target_datasource['schemas']}")
                    # schemas에서 컬럼명 추출
                    for schema in target_datasource['schemas']:
                        logging.debug(f"개별 스키마: {schema}")
                        if 'name' in schema:
                            right_combo.addItem(schema['name'])
                        elif 'column_name' in schema:
                            right_combo.addItem(schema['column_name'])
                else:
                    logging.debug(f"스키마 정보가 없습니다. target_datasource keys: {target_datasource.keys() if target_datasource else 'None'}")
            except Exception as e:
                import logging
                logging.error(f"대상 데이터 소스 정보 로드 오류: {str(e)}")
                MessageDialog.critical(self, "오류", f"대상 데이터 소스 정보를 불러오는 중 오류가 발생했습니다: {str(e)}")
        
        self.join_columns_table.setCellWidget(current_row_count, 2, right_combo)
        
        # 삭제 버튼 추가
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
        delete_btn.clicked.connect(lambda: self._delete_join_column_row(current_row_count))
        self.join_columns_table.setCellWidget(current_row_count, 3, delete_btn)

    def _delete_join_column_row(self, row):
        """결합 컬럼 행 삭제"""
        self.join_columns_table.removeRow(row)
        
        # 삭제 버튼의 row 인덱스 업데이트
        for i in range(row, self.join_columns_table.rowCount()):
            delete_btn = self.join_columns_table.cellWidget(i, 3)
            if delete_btn:
                delete_btn.clicked.disconnect()
                delete_btn.clicked.connect(lambda checked, r=i: self._delete_join_column_row(r))
        
        # 순서 재정렬
        for i in range(self.join_columns_table.rowCount()):
            order_item = self.join_columns_table.item(i, 0)
            if order_item:
                order_item.setText(str(i + 1))

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
            
            # 테이블 초기화
            self.join_columns_table.setRowCount(0)
                
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
            MessageDialog.information(self, "저장 완료", "결합하기(join) 설정이 저장되었습니다.")
            
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
        # 결합할 데이터 소스 선택 확인
        if self.join_datasource_combo.currentIndex() < 0:
            MessageDialog.warning(self, "경고", "결합할 데이터 소스를 선택해주세요.")
            return False
            
        # 결합 타입 선택 확인
        if self.join_type_combo.currentIndex() < 0:
            MessageDialog.warning(self, "경고", "결합 타입을 선택해주세요.")
            return False
            
        # 결합 컬럼이 하나 이상 있는지 확인
        if self.join_columns_table.rowCount() == 0:
            MessageDialog.warning(self, "경고", "결합 컬럼을 하나 이상 추가해주세요.")
            return False
            
        # 각 행에서 컬럼명이 선택되었는지 확인
        for row in range(self.join_columns_table.rowCount()):
            left_combo = self.join_columns_table.cellWidget(row, 1)
            right_combo = self.join_columns_table.cellWidget(row, 2)
            
            if left_combo and right_combo:
                left_column = left_combo.currentText()
                right_column = right_combo.currentText()
                
                if not left_column or left_column == "":
                    MessageDialog.warning(self, "경고", f"{row + 1}번째 행의 컬럼명(left)을 선택해주세요.")
                    return False
                    
                if not right_column or right_column == "":
                    MessageDialog.warning(self, "경고", f"{row + 1}번째 행의 대상 컬럼명(right)을 선택해주세요.")
                    return False
            
        return True

    def _create_process_data(self):
        """프로세스 데이터 생성"""
        target_datasource_name = self.join_datasource_combo.currentText()
        join_type = self.join_type_combo.currentText()
        
        process_data = {
            "process_type": "join",
            "target_datasource_uuid": self.join_datasource_combo.currentData(),
            "target_datasource_name": target_datasource_name,
            "join_type": join_type,
            "content": f"테이블 결합: {target_datasource_name} ({join_type})",
            "join_columns": []
        }
        
        # 결합 컬럼 정보 수집 (빈 값이 아닌 경우만)
        for row in range(self.join_columns_table.rowCount()):
            left_combo = self.join_columns_table.cellWidget(row, 1)
            right_combo = self.join_columns_table.cellWidget(row, 2)
            
            if left_combo and right_combo:
                left_column = left_combo.currentText()
                right_column = right_combo.currentText()
                
                # 빈 값이 아닌 경우만 추가
                if left_column and left_column != "" and right_column and right_column != "":
                    process_data["join_columns"].append({
                        "order": row + 1,
                        "left_column": left_column,
                        "right_column": right_column
                    })
        
        return process_data

    def set_process_data(self, process_data):
        """기존 프로세스 데이터 설정 (편집용)"""
        if not process_data:
            return
            
        try:
            # 결합할 데이터 소스 설정
            target_uuid = process_data.get("target_datasource_uuid")
            if target_uuid:
                for i in range(self.join_datasource_combo.count()):
                    if self.join_datasource_combo.itemData(i) == target_uuid:
                        self.join_datasource_combo.setCurrentIndex(i)
                        break
                        
            # 결합 타입 설정
            join_type = process_data.get("join_type", "inner")
            for i in range(self.join_type_combo.count()):
                if self.join_type_combo.itemText(i) == join_type:
                    self.join_type_combo.setCurrentIndex(i)
                    break
                    
            # 결합 컬럼 설정
            join_columns = process_data.get("join_columns", [])
            self.join_columns_table.setRowCount(0)  # 기존 행 제거
            
            for column_info in join_columns:
                self._on_add_column_clicked()  # 새 행 추가
                row = self.join_columns_table.rowCount() - 1
                
                # 컬럼 정보 설정
                left_combo = self.join_columns_table.cellWidget(row, 1)
                right_combo = self.join_columns_table.cellWidget(row, 2)
                
                if left_combo:
                    left_column = column_info.get("left_column", "")
                    for i in range(left_combo.count()):
                        if left_combo.itemText(i) == left_column:
                            left_combo.setCurrentIndex(i)
                            break
                            
                if right_combo:
                    right_column = column_info.get("right_column", "")
                    for i in range(right_combo.count()):
                        if right_combo.itemText(i) == right_column:
                            right_combo.setCurrentIndex(i)
                            break
                            
        except Exception as e:
            MessageDialog.critical(self, "오류", f"프로세스 데이터 설정 중 오류가 발생했습니다: {str(e)}")

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