import os
import sys
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMenu
from PySide6.QtCore import Qt, QSize
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QIcon
import logging

class FlowPanel(QWidget):
    """흐름 상세 정보를 표시하는 패널"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        
        # UI 로드
        self._load_ui()
        
        # 초기화
        self._init_ui()
        
    def _load_ui(self):
        """UI 파일 로드"""
        try:
            loader = QUiLoader()
            self.ui = loader.load("src/ui/panels/flow_left.ui")
            if not self.ui:
                self.logger.error("flow_left.ui 파일을 로드할 수 없습니다.")
                return
                
            # UI를 현재 위젯에 추가
            layout = self.layout()
            if layout:
                layout.addWidget(self.ui)
            else:
                self.setLayout(QVBoxLayout())
                self.layout().addWidget(self.ui)
                
        except Exception as e:
            self.logger.error(f"UI 로드 중 오류 발생: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            
    def _init_ui(self):
        """UI 초기화"""
        try:
            # 처리 목록 스타일 설정
            self.ui.process_list.setStyleSheet("""
                QListWidget {
                    background-color: #ffffff;
                    color: #495057;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                }
                QListWidget::item {
                    padding: 8px;
                }
                QListWidget::item:selected {
                    background-color: #e7f5ff;
                    color: #1864ab;
                }
                QListWidget::item:hover {
                    background-color: #d0ebff;
                    color: #1864ab;
                }
                QListWidget:focus {
                    border: none;
                    outline: none;
                }
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
            
            # 처리 목록 아이템 추가
            self.ui.process_list.addItems([
                "데이터 전처리",
                "이상치 제거",
                "결측치 처리",
                "특성 선택",
                "데이터 정규화",
                "모델 학습",
                "모델 평가",
                "하이퍼파라미터 튜닝",
                "교차 검증",
                "모델 저장",
                "예측 수행",
                "결과 시각화",
                "성능 지표 계산",
                "보고서 생성",
                "데이터 백업",
                "로그 기록",
                "알림 설정",
                "결과 저장",
                "작업 완료",
                "리소스 정리"
            ])
            
            # 처리 추가 버튼 아이콘 설정
            self.ui.add_process_btn.setIcon(QIcon("src/ui/resources/images/add2.png"))
            self.ui.add_process_btn.setIconSize(QSize(16, 16))
            self.ui.add_process_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    border-radius: 4px;
                    padding: 4px;
                }
            """)
            
            # 흐름명 스타일 설정
            self.ui.flow_name.setStyleSheet("""
                QLabel {
                    color: #000000;
                    font-size: 16px;
                    font-weight: bold;
                }
                QLabel::hover {
                    color: #1864ab;
                }
            """)
            
            # 데이터 소스 목록 추가
            if hasattr(self.parent, 'data_list'):
                data_sources = []
                for i in range(self.parent.data_list.count()):
                    item = self.parent.data_list.item(i)
                    if item:
                        data_sources.append(item.text())
                self.ui.data_source_input.addItems(data_sources)
            
            # 처리 추가 버튼 클릭 시 팝업 메뉴 연결
            self.ui.add_process_btn.clicked.connect(self.show_add_process_menu)
            
        except Exception as e:
            self.logger.error(f"UI 초기화 중 오류 발생: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            
    def set_flow_info(self, flow_info):
        """흐름 정보 설정
        
        Args:
            flow_info (dict): 흐름 정보
                - name (str): 흐름명
                - input (str): 입력
                - result (str): 결과
        """
        try:
            if not flow_info:
                return
                
            # 흐름명 설정
            name = flow_info.get('name', '')
            self.ui.flow_name.setText(name)
            
            # 흐름명이 길 경우 말줄임표로 표시
            metrics = self.ui.flow_name.fontMetrics()
            max_width = 243 # 256 #self.ui.flow_name.width() - 10  # 여유 공간
            
            if metrics.horizontalAdvance(name) > max_width:
                # 말줄임표를 포함한 최대 길이 계산
                ellipsis = "..."
                # ellipsis_width = metrics.horizontalAdvance(ellipsis)
                # max_text_width = max_width - ellipsis_width
                
                # 흐름명을 잘라내고 말줄임표 추가
                truncated_name = ""
                for i in range(len(name)):
                    test_text = name[:i+1]
                    if metrics.horizontalAdvance(test_text) > max_width:
                        break
                    truncated_name = test_text
                
                display_name = truncated_name + ellipsis
                self.ui.flow_name.setText(display_name)
                self.ui.flow_name.setToolTip(name)  # 전체 이름을 툴팁으로 표시
            else:
                self.ui.flow_name.setText(name)
                self.ui.flow_name.setToolTip("")  # 툴팁 제거
                
            # 툴팁 스타일 설정
            self.ui.flow_name.setStyleSheet("""
                QLabel {
                    color: #000000;
                    font-size: 16px;
                    font-weight: bold;
                }                
                QToolTip {
                    background-color: #212529;
                    color: white;
                    font-size: 12px;
                }
            """)                
            
            # 입력 설정
            input_data = flow_info.get('input', '')
            index = self.ui.data_source_input.findText(input_data)
            if index >= 0:
                self.ui.data_source_input.setCurrentIndex(index)
            
            # 결과 설정
            self.ui.result_text.setText(flow_info.get('result', ''))
            
        except Exception as e:
            self.logger.error(f"흐름 정보 설정 중 오류 발생: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            
    def resizeEvent(self, event):
        """창 크기가 변경될 때 호출됩니다."""
        super().resizeEvent(event)
        # 흐름명 말줄임표 업데이트
        if hasattr(self, 'ui') and hasattr(self.ui, 'flow_name'):
            name = self.ui.flow_name.toolTip() or self.ui.flow_name.text()
            if name:
                metrics = self.ui.flow_name.fontMetrics()
                max_width = 243 #self.ui.flow_name.width() - 10
                
                if metrics.horizontalAdvance(name) > max_width:
                    ellipsis = "..."
                    # ellipsis_width = metrics.horizontalAdvance(ellipsis)
                    # max_text_width = max_width - ellipsis_width
                    
                    truncated_name = ""
                    for i in range(len(name)):
                        test_text = name[:i+1]
                        if metrics.horizontalAdvance(test_text) > max_width:
                            break
                        truncated_name = test_text
                    
                    display_name = truncated_name + ellipsis
                    self.ui.flow_name.setText(display_name)
                    self.ui.flow_name.setToolTip(name)
                else:
                    self.ui.flow_name.setText(name)
                    self.ui.flow_name.setToolTip("") 

    def show_add_process_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #6c757d;
                color: #fff;
                border: 1px solid #adb5bd;
                border-radius: 4px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                color: #fff;
            }
            QMenu::item:selected {
                background-color: #495057;
                color: #fff;
            }
        """)
        # 데이터 소스 단위 처리 하위 메뉴
        ds_menu = QMenu("데이터 소스 단위 처리", self)
        ds_menu.setStyleSheet(menu.styleSheet())
        export_action = ds_menu.addAction("내보내기")
        ds_menu.addAction("중복 제거")
        ds_menu.addAction("컬럼명 변경")
        ds_menu.addAction("필터")
        ds_menu.addAction("정렬")
        ds_menu.addAction("합치기(union)")
        ds_menu.addAction("결합하기(join)")
        ds_menu.addAction("분포")
        ds_menu.addAction("그룹 집계")
        menu.addMenu(ds_menu)
        # 컬럼.숫자 하위 메뉴
        num_menu = QMenu("컬럼.숫자", self)
        num_menu.setStyleSheet(menu.styleSheet())
        num_menu.addAction("라운딩")
        num_menu.addAction("랜덤라운딩")
        num_menu.addAction("상/하단 코딩")
        num_menu.addAction("지정 단위 범주화")
        num_menu.addAction("동일 구간 범주화")
        num_menu.addAction("구간 분류")
        num_menu.addAction("일련번호 대체(연속)")
        num_menu.addAction("일련번호 대체(불연속)")
        menu.addMenu(num_menu)
        # 컬럼.문자열/매핑 하위 메뉴
        str_menu = QMenu("컬럼.문자열/매핑", self)
        str_menu.setStyleSheet(menu.styleSheet())
        str_menu.addAction("대문자로")
        str_menu.addAction("소문자로")
        str_menu.addAction("문자열 추출")
        str_menu.addAction("치환")
        str_menu.addAction("결합")
        str_menu.addAction("매핑")
        menu.addMenu(str_menu)
        # 컬럼.날짜/매핑 하위 메뉴
        date_menu = QMenu("컬럼.날짜/매핑", self)
        date_menu.setStyleSheet(menu.styleSheet())
        date_menu.addAction("경과일")
        date_menu.addAction("잡음 추가")
        menu.addMenu(date_menu)
        # 컬럼.암호화 하위 메뉴
        enc_menu = QMenu("컬럼.암호화", self)
        enc_menu.setStyleSheet(menu.styleSheet())
        enc_menu.addAction("해시")
        menu.addMenu(enc_menu)
        menu.addAction("조건")
        # 내보내기 클릭 시 동작 연결
        export_action.triggered.connect(self.show_export_ui)
        menu.exec_(self.ui.add_process_btn.mapToGlobal(self.ui.add_process_btn.rect().bottomLeft()))

    def show_export_ui(self):
        """right_frame에 export.ui 기반 ExportWidget을 표시"""
        # MainWindow 인스턴스 찾기
        main_window = self.parent.parent if self.parent else None
        if not main_window:
            return
        # projects_container에서 right_frame 찾기
        right_frame = None
        for child in main_window.ui.projects_container.children():
            if isinstance(child, QWidget) and child.objectName() == "right_frame":
                right_frame = child
                break
        if not right_frame:
            return
        # 기존 위젯 제거
        if right_frame.layout():
            while right_frame.layout().count():
                item = right_frame.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        else:
            right_frame.setLayout(QVBoxLayout())
        layout = right_frame.layout()
        # ExportWidget을 import해서 추가
        from src.ui.action.export import ExportWidget
        export_widget = ExportWidget(right_frame)
        layout.addWidget(export_widget) 