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
from src.ui.database import get_flow_list, get_flow_by_uuid, update_flow, delete_process_from_flow, get_datasources_list, get_datasource
from src.ui.components.message_dialog import MessageDialog
from src.ui.components.confirm_dialog import ConfirmDialog
from src.ui.components.custom_checkbox import CheckBoxHeader
from ui.action.action_common import validate_schema, select_saved_process_card
from utils.enum_utils import sdataTypeToView

class UnionWidget(QWidget):
    def __init__(self, parent=None, flow_pos=None):
        super().__init__(parent)
        loader = QUiLoader()
        ui_path = os.path.join(os.path.dirname(__file__), 'union.ui')
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
        self.current_datasource_label = self.findChild(QLabel, 'current_datasource_label')
        self.current_datasource_table = self.findChild(QTableWidget, 'current_datasource_table')
        self.target_datasource_label = self.findChild(QLabel, 'target_datasource_label')
        self.datasource_list_combo = self.findChild(QComboBox, 'datasource_list_combo')
        self.target_datasource_table = self.findChild(QTableWidget, 'target_datasource_table')
        self.save_button = self.findChild(QWidget, 'save_button')
        self.delete_btn = self.findChild(QWidget, 'delete_btn')

        # 스크롤바 스타일 직접 적용
        self.current_datasource_table.verticalScrollBar().setStyleSheet("""
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
        
        self.current_datasource_table.horizontalScrollBar().setStyleSheet("""
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
        self.current_datasource_table.setStyleSheet("""
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

        self.target_datasource_table.verticalScrollBar().setStyleSheet(self.current_datasource_table.verticalScrollBar().styleSheet())
        self.target_datasource_table.horizontalScrollBar().setStyleSheet(self.current_datasource_table.horizontalScrollBar().styleSheet())
        self.target_datasource_table.setStyleSheet(self.current_datasource_table.styleSheet())

        self._init_events()
        self._init_tables()
        self._populate_datasource_combo()
        self._load_current_datasource_info()
        self.set_schema()  # UnionWidget 생성 시 자동으로 schema를 설정

    def _init_events(self):
        """이벤트 초기화"""
        self.save_button.clicked.connect(self._on_save_clicked)
        self.delete_btn.clicked.connect(self._on_delete_clicked)
        self.datasource_list_combo.currentIndexChanged.connect(self._on_datasource_combo_changed)

    def _init_tables(self):
        """테이블 초기화"""
        # 현재 데이터 소스 테이블 설정
        self.current_datasource_table.setColumnCount(3)
        self.current_datasource_table.setHorizontalHeaderLabels(["번호", "컬럼명", "타입"])
        
        header = self.current_datasource_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # 번호
        header.setSectionResizeMode(1, QHeaderView.Interactive)  # 컬럼명
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # 타입
        header.setStretchLastSection(True)
        
        # 타겟 데이터 소스 테이블 설정
        self.target_datasource_table.setColumnCount(3)
        self.target_datasource_table.setHorizontalHeaderLabels(["번호", "컬럼명", "타입"])
        
        header = self.target_datasource_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # 번호
        header.setSectionResizeMode(1, QHeaderView.Interactive)  # 컬럼명
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # 타입
        header.setStretchLastSection(True)
        
        # 타겟 데이터 소스 테이블의 기본 배경색을 백색으로 설정
        # self.target_datasource_table.setStyleSheet("""
        #     QTableWidget {
        #         background-color: white;
        #         border: 1px solid #dee2e6;
        #         border-radius: 4px;
        #         gridline-color: #e9ecef;
        #         color: #212529;
        #     }
        #     QTableWidget::item {
        #         padding: 4px;
        #         border-bottom: 1px solid #e9ecef;
        #         color: #212529;
        #         background-color: white;
        #     }
        #     QTableWidget::item:selected {
        #         background-color: #e7f5ff;
        #         color: #212529;
        #     }
        #     QTableWidget::item:focus {
        #         outline: none;
        #         border: none;
        #         background: #e7f5ff;
        #         color: #212529;
        #     }
        #     QHeaderView::section {
        #         background-color: #f8f9fa;
        #         color: #212529;
        #         padding: 8px;
        #         border: none;
        #         border-right: 1px solid #dee2e6;
        #         border-bottom: 1px solid #dee2e6;
        #         font-weight: bold;
        #     }
        # """)

    def _populate_datasource_combo(self):
        """데이터 소스 콤보박스에 목록 채우기 (현재 데이터 소스 제외)"""
        if not self.project_data:
            return
            
        project_uuid = self.project_data.get("uuid")
        if not project_uuid:
            return
            
        # 모든 데이터 소스 목록 가져오기
        datasources = get_datasources_list(project_uuid)
        if not datasources:
            return
            
        # 현재 데이터 소스 이름
        current_datasource_name = self.data_source.get("name", "") if self.data_source else ""
        
        # 콤보박스 초기화
        self.datasource_list_combo.clear()
        
        # 기본 선택 항목 추가
        self.datasource_list_combo.addItem("결합할 데이터 소스를 선택하세요.", None)
        
        # 현재 데이터 소스를 제외한 데이터 소스들만 추가
        for datasource in datasources:
            datasource_name = datasource.get("name", "")
            if datasource_name and datasource_name != current_datasource_name:
                self.datasource_list_combo.addItem(datasource_name, datasource.get("uuid"))

    def _load_current_datasource_info(self):
        """현재 데이터 소스 정보 로드"""
        if not self.data_source:
            return
            
        # 현재 데이터 소스 라벨 업데이트
        current_name = self.data_source.get("name", "현재 데이터 소스")
        self.current_datasource_label.setText(f"현재 데이터 소스: {current_name}")
        
        # 현재 데이터 소스 테이블에 컬럼 정보 표시
        # schemas = self.data_source.get("schemas", [])

        flow_pos = self.flow_pos if self.flow_pos > -1 else len(self.parent.flow_info.get('processes', []))
        columns, transformed_dict = validate_schema(self.parent, self.data_source.get("schemas", []), self.parent.flow_info.get('processes', []), flow_pos)

        self.current_datasource_table.setRowCount(len(columns))
        
        for i, column_name in enumerate(columns):
            schema = transformed_dict.get(column_name, {})
            # 번호
            number_item = QTableWidgetItem(str(i + 1))
            number_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.current_datasource_table.setItem(i, 0, number_item)
            
            # 컬럼명
            column_name_item = QTableWidgetItem(schema.get('name', ''))
            self.current_datasource_table.setItem(i, 1, column_name_item)
            
            # 타입
            type_item = QTableWidgetItem(sdataTypeToView(schema.get('data_type', '')))
            self.current_datasource_table.setItem(i, 2, type_item)

    def _on_datasource_combo_changed(self, index):
        """데이터 소스 콤보박스 변경 시 호출"""
        if index == 0:  # "결합할 데이터 소스를 선택하세요." 선택
            self.target_datasource_table.setRowCount(0)
            return
            
        selected_uuid = self.datasource_list_combo.currentData()
        if not selected_uuid:
            return
            
        # 선택된 데이터 소스 정보 가져오기
        project_uuid = self.project_data.get("uuid")
        selected_datasource = get_datasource(project_uuid, selected_uuid)
        
        if not selected_datasource:
            return
            
        # 타겟 데이터 소스 테이블에 컬럼 정보 표시
        schemas = selected_datasource.get("schemas", [])
        self.target_datasource_table.setRowCount(len(schemas))
        
        for i, schema in enumerate(schemas):
            # 번호
            number_item = QTableWidgetItem(str(i + 1))
            number_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.target_datasource_table.setItem(i, 0, number_item)
            
            # 컬럼명
            column_name_item = QTableWidgetItem(schema.get('name', ''))
            self.target_datasource_table.setItem(i, 1, column_name_item)
            
            # 타입
            type_item = QTableWidgetItem(sdataTypeToView(schema.get('data_type', '')))
            self.target_datasource_table.setItem(i, 2, type_item)

    def set_schema(self):
        """스키마 설정 (Union의 경우 특별한 스키마 설정이 필요하지 않음)"""
        pass

    def _on_save_clicked(self):
        """저장 버튼 클릭 시 처리"""
        # 선택된 데이터 소스 확인
        selected_datasource_name = self.datasource_list_combo.currentText()
        selected_datasource_uuid = self.datasource_list_combo.currentData()
        
        if not selected_datasource_name or selected_datasource_name == "결합할 데이터 소스를 선택하세요.":
            MessageDialog.warning(self, "경고", "결합할 데이터 소스를 선택해주세요.")
            return
            
        # 데이터 구조 검증
        try:
            self._validate_data_structure(selected_datasource_uuid)
        except Exception as e:
            MessageDialog.critical(self, "오류", str(e))
            return
            
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

        # 프로세스 데이터 구성
        process_data = {
            "process_type": "union",
            "target_datasource_name": selected_datasource_name,
            "target_datasource_uuid": selected_datasource_uuid,
            "content": f"테이블 행 결합: {selected_datasource_name}"
        }

        # 흐름에 프로세스 추가/수정
        if self.flow_pos == -1:
            flow['processes'].append(process_data)
        else:
            flow['processes'][self.flow_pos] = process_data

        update_flow(project_uuid, flow)

        # 성공 메시지 및 패널 새로고침
        MessageDialog.information(self, "저장 완료", "테이블 행 결합 설정이 저장되었습니다.")
        
        flow_panel = self.parent
        if flow_panel and hasattr(flow_panel, "set_flow_info"):
            updated_flow = get_flow_by_uuid(project_uuid, flow_uuid)
            flow_panel.set_flow_info(updated_flow)
            
            # 공통 함수를 사용하여 저장된 카드 선택 (original_flow_pos 전달)
            select_saved_process_card(flow_panel, process_data, updated_flow, self.flow_pos)

    def _validate_data_structure(self, target_datasource_uuid):
        """데이터 구조 검증 - 컬럼 수, 컬럼명, 순서, 타입이 동일한지 확인"""
        if not self.data_source or not target_datasource_uuid:
            return False
            
        # 현재 데이터 소스의 스키마
        current_schemas = self.data_source.get("schemas", [])
        
        # 타겟 데이터 소스의 스키마 가져오기
        project_uuid = self.project_data.get("uuid")
        target_datasource = get_datasource(project_uuid, target_datasource_uuid)
        if not target_datasource:
            raise ValueError("결합할 데이터 소스를 찾을 수 없습니다.")
            
        target_schemas = target_datasource.get("schemas", [])
        
        # 1. 컬럼 수 검증
        if len(current_schemas) < len(target_schemas):
            raise ValueError("결합할 데이터 소스의 컬럼 정보는 현재 데이터 소스의 컬럼 정보를 앞 부분에 포함 하고 있어야합니다.")
            
        # 2. 컬럼명, 순서, 타입 검증
        # for i, current_schema in enumerate(current_schemas):
        #     target_schema = target_schemas[i]

        #     current_name = current_schema.get('name', '')
        #     current_typ   e = current_schema.get('type', '')
        #     target_name = target_schema.get('name', '')
        #     target_type = target_schema.get('type', '')
            
        #     # 컬럼명과 타입이 동일한지 확인
        #     if current_name != target_name or current_type != target_type:
        #         raise ValueError("결합할 데이터 소스의 컬럼 정보는 현재 데이터 소스의 컬럼 정보를 앞 부분에 포함 하고 있어야합니다.")
               

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
        """기존 프로세스 데이터로 위젯 설정"""
        if not process_data:
            return
            
        # 저장된 데이터 소스 정보 가져오기
        target_datasource_name = process_data.get('target_datasource_name', '')
        target_datasource_uuid = process_data.get('target_datasource_uuid', '')
        
        if target_datasource_name:
            # 콤보박스에서 해당 데이터 소스 선택
            for i in range(self.datasource_list_combo.count()):
                if (self.datasource_list_combo.itemText(i) == target_datasource_name or 
                    self.datasource_list_combo.itemData(i) == target_datasource_uuid):
                    self.datasource_list_combo.setCurrentIndex(i)
                    # 선택된 데이터 소스의 테이블 정보도 업데이트
                    self._on_datasource_combo_changed(i)
                    break 