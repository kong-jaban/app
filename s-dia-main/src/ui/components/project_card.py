from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QWidget, QScrollArea, QMessageBox, QApplication,
                              QToolButton, QMenu, QSizePolicy, QTextEdit)
from PySide6.QtCore import Qt, QMimeData, QPoint, QEvent, QRect, QSize, QTimer
from PySide6.QtGui import QFont, QDrag, QPainter, QPen, QColor, QPixmap, QCursor
import os
import json
import logging
import platform
import sys

from ..common.context_menu import CustomContextMenuFilter

class MenuButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent  # 부모 위젯을 속성으로 저장
        self.setObjectName("menu_button")
        self.setFixedSize(30, 30)
        self.setFont(QFont("Arial", 20))
        self.setCursor(Qt.PointingHandCursor)
        self.setText("⋮")
        self.setStyleSheet("""
            QPushButton#menu_button {
                color: #495057;
                background-color: transparent;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton#menu_button:hover {
                background-color: #d0ebff;
            }
        """)

    def mousePressEvent(self, event):
        """마우스 클릭 이벤트 처리"""
        if event.button() == Qt.LeftButton:
            # 부모 위젯(ProjectCard)의 메뉴 표시 메서드 호출
            if self.parent and hasattr(self.parent, 'show_menu'):
                self.parent.show_menu()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """마우스 릴리즈 이벤트 처리"""
        if event.button() == Qt.LeftButton:
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def event(self, event):
        """모든 이벤트를 여기서 처리"""
        if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            # 부모 위젯(ProjectCard)의 메뉴 표시 메서드 호출
            if self.parent and hasattr(self.parent, 'show_menu'):
                self.parent.show_menu()
            event.accept()
            return True
        return super().event(event)

class ProjectCard(QFrame):
    def __init__(self, project_data, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.project_data = project_data
        self.parent = parent
        self.drag_start_position = None
        self.context_menu_filter = CustomContextMenuFilter()
        
        # 데이터 폴더 상태 검사
        self.check_data_folder_status()
        
        # 툴팁 지연시간 설정
        self.setToolTipDuration(0)
        
        self.setup_ui()
        
        # 드래그 활성화
        self.setAcceptDrops(True)
        
    def check_data_folder_status(self):
        """데이터 폴더 상태 검사"""
        data_dir = self.project_data.get('data_directory', '')
        self.folder_exists = os.path.exists(data_dir)
        self.has_write_permission = True  # 권한 체크 제거
        
    def setup_ui(self):
        """카드 UI 설정"""
        self.setObjectName("project_card")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(200)  # 높이 고정
        self.setMinimumWidth(300)  # 최소 너비 설정
        
        # 클릭 가능한 영역을 위한 투명 버튼
        self.clickable_area = QPushButton(self)
        self.clickable_area.setObjectName("clickable_area")
        self.clickable_area.setStyleSheet("""
            QPushButton#clickable_area {
                background: transparent;
                border: none;
            }
        """)
        self.clickable_area.clicked.connect(self.on_card_clicked)
        
        # 경고 상태에 따른 스타일 설정
        if not self.folder_exists:
            self.setStyleSheet("""
                QFrame#project_card {
                    background-color: #fff5f5;
                    border: 1px solid #ffc9c9;
                    border-radius: 8px;
                }
                QFrame#project_card:hover {
                    border-color: #ff8787;
                    background-color: #ffe3e3;
                }
                QLabel#warning_icon {
                    color: #e03131;
                    font-size: 18px;
                    background-color: #fff5f5;
                }
                QFrame#project_card:hover QLabel#warning_icon {
                    background-color: #ffe3e3;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #fff5f5;
                    width: 8px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background: #ffc9c9;
                    border-radius: 4px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #ff8787;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: transparent;
                }
            """)
            self.setToolTip("데이터 폴더가 존재하지 않습니다.")
        else:
            self.setStyleSheet("""
                QFrame#project_card {
                    background-color: #e7f5ff;
                    border: 1px solid #d0ebff;
                    border-radius: 8px;
                }
                QFrame#project_card:hover {
                    border-color: #339af0;
                    background-color: #dbeeff;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #e7f5ff;
                    width: 8px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background: #d0ebff;
                    border-radius: 4px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #339af0;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: transparent;
                }
            """)
        
        # 공통 스타일 추가
        self.setStyleSheet(self.styleSheet() + """
            QPushButton#menu_button {
                color: #495057;
                background-color: transparent;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton#menu_button:hover {
                background-color: #d0ebff;
            }
            QWidget#header_widget, QWidget#name_container, QWidget#desc_container {
                background-color: transparent;
            }
            QLabel#project_name {
                font-size: 18px;
                font-weight: bold;
                color: #1864ab;
                padding: 5px;
                background-color: transparent;
            }
            QLabel#project_description {
                font-size: 14px;
                color: #495057;
                background-color: transparent;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
                padding-top: 5px;
            }
            QToolTip {
                background-color: #495057;
                color: white;
                border: 1px solid #343a40;
                padding: 5px;
                font-size: 14px;
            }
        """)
        
        # 카드 레이아웃 설정
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        # 상단 영역 (제목 + 메뉴 버튼)
        header_widget = QWidget()
        header_widget.setObjectName("header_widget")
        header_widget.setFixedHeight(30)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(20)  # 프로젝트 이름과 메뉴 버튼 사이의 간격을 20px로 설정
        
        # 프로젝트 이름 컨테이너
        name_container = QWidget()
        name_container.setObjectName("name_container")
        name_layout = QHBoxLayout(name_container)
        name_layout.setContentsMargins(0, 0, 0, 0)
        
        # 경고 아이콘 (필요한 경우)
        if not self.folder_exists:
            warning_container = QWidget()
            warning_container.setFixedWidth(25)  # 아이콘 너비만큼만 설정
            warning_container.setStyleSheet("background: transparent;")
            
            warning_layout = QHBoxLayout(warning_container)
            warning_layout.setContentsMargins(0, 0, 0, 0)
            warning_layout.setSpacing(0)
            
            warning_label = QLabel("⚠")
            warning_label.setStyleSheet("""
                color: #e03131;
                font-size: 18px;
                background: transparent;
            """)
            warning_layout.addWidget(warning_label, 0, Qt.AlignCenter)
            name_layout.addWidget(warning_container)
        
        # 프로젝트 이름
        self.name_label = QLabel(self.project_data.get('name', ''))
        self.name_label.setObjectName("project_name")
        self.name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.name_label.setMinimumWidth(0)  # 최소 너비 제한 해제
        self.name_label.setFixedHeight(30)  # 높이 고정
        self.update_name_elision()  # 초기 이름 줄임 처리
        
        # 전체 제목을 툴팁으로 표시
        if self.name_label.text() != self.project_data.get('name', ''):
            self.name_label.setToolTip(self.project_data.get('name', ''))
        
        name_layout.addWidget(self.name_label)
        header_layout.addWidget(name_container, 1)
        
        # 메뉴 버튼 (점 3개)
        self.menu_button = MenuButton(self)
        header_layout.addWidget(self.menu_button, 0, Qt.AlignRight | Qt.AlignTop)
        
        layout.addWidget(header_widget)
        
        # 프로젝트 설명
        # 스크롤 영역 생성
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("background: transparent;")
        
        # 설명을 담을 컨테이너
        desc_container = QWidget()
        desc_container.setObjectName("desc_container")
        desc_container.setStyleSheet("""
            QWidget#desc_container {
                background: transparent;
                padding: 5px 0;
            }
        """)
        desc_layout = QVBoxLayout(desc_container)
        desc_layout.setContentsMargins(0, 0, 0, 0)
        desc_layout.setSpacing(0)
        desc_layout.setAlignment(Qt.AlignTop)
        
        # 설명 텍스트 에디트
        desc_edit = QTextEdit()
        desc_edit.setObjectName("project_description")
        desc_edit.setPlainText(self.project_data.get('description', ''))
        desc_edit.setReadOnly(True)
        desc_edit.setFrameShape(QFrame.NoFrame)
        desc_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        desc_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        desc_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        desc_edit.installEventFilter(self.context_menu_filter)
        
        # 경고 상태에 따른 스크롤바 스타일 설정
        if not self.folder_exists:
            desc_edit.setStyleSheet("""
                QTextEdit#project_description {
                    background: transparent;
                    padding: 0;
                    margin: 0;
                    font-size: 14px;
                    color: #666;
                    border: none;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #fff5f5;
                    width: 8px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background: #ffc9c9;
                    border-radius: 4px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #ff8787;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: transparent;
                }
            """)
        else:
            desc_edit.setStyleSheet("""
                QTextEdit#project_description {
                    background: transparent;
                    padding: 0;
                    margin: 0;
                    font-size: 14px;
                    color: #666;
                    border: none;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #e7f5ff;
                    width: 8px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background: #d0ebff;
                    border-radius: 4px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #339af0;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: transparent;
                }
            """)
        
        desc_layout.addWidget(desc_edit)
        
        # 스크롤 영역에 컨테이너 설정
        scroll_area.setWidget(desc_container)
        
        # 스크롤 영역의 높이를 고정 (헤더와 경로 라벨 높이를 고려)
        scroll_area.setFixedHeight(107)  # 카드 높이(200) - (헤더 높이 + 경로 라벨 높이 + 여백)
        
        layout.addWidget(scroll_area)
        
        # 데이터 디렉토리 경로
        path_label = QLabel(self.project_data.get('data_directory', ''))
        path_label.setObjectName("project_path")
        if not self.folder_exists:
            path_label.setStyleSheet("font-size: 12px; color: #1971c2; background: transparent; padding-top: 3px; text-decoration: line-through;")
        else:
            path_label.setStyleSheet("font-size: 12px; color: #1971c2; background: transparent; padding-top: 3px;")
        path_label.setWordWrap(True)
        path_label.setFixedHeight(20)  # 경로 라벨 높이 고정
        layout.addWidget(path_label)
        
    def update_name_elision(self):
        """프로젝트 이름의 줄임 처리를 업데이트합니다."""
        metrics = self.name_label.fontMetrics()
        # 카드의 전체 너비에서 메뉴 버튼, 경고 아이콘, 간격, 여백을 제외한 공간 계산
        max_width = self.width() - 100  # 메뉴 버튼(30px) + 간격(20px) + 여백(20px)
        if not self.folder_exists:
            max_width -= 25  # 경고 아이콘 너비(25px) 추가로 제외
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
            self.name_label.setText(display_name)
            self.name_label.setToolTip(project_name)  # 전체 제목을 툴팁으로 표시
        else:
            self.name_label.setText(project_name)
            self.name_label.setToolTip("")  # 툴팁 제거
            
    def resizeEvent(self, event):
        """창 크기가 변경될 때 호출됩니다."""
        super().resizeEvent(event)
        self.update_name_elision()  # 이름 줄임 처리 업데이트
        # 클릭 가능 영역을 카드 전체에 맞추되, 메뉴 버튼 영역은 제외
        self.clickable_area.setGeometry(0, 0, self.width() - 40, self.height())
        
    def showEvent(self, event):
        """카드가 처음 표시될 때 호출됩니다."""
        super().showEvent(event)
        # 이름 줄임 처리 업데이트
        QTimer.singleShot(0, self.update_name_elision)

    def on_card_clicked(self):
        """카드 클릭 처리"""
        if self.parent and hasattr(self.parent, 'on_project_click'):
            self.parent.on_project_click(self)

    def mousePressEvent(self, event):
        """마우스 클릭 이벤트 처리"""
        if event.button() == Qt.LeftButton:
            # 메뉴 버튼이 클릭된 경우는 이벤트를 여기서 처리하고 종료
            if self.menu_button.underMouse():
                event.accept()
                return
                
            self.drag_start_position = event.pos()
            
            # 카드 영역 클릭 시 메뉴 패널 표시
            if self.parent and hasattr(self.parent, 'on_project_click'):
                self.parent.on_project_click(self)
                event.accept()
                return
                
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """마우스 릴리즈 이벤트 처리"""
        if event.button() == Qt.LeftButton:
            # 메뉴 버튼이 클릭된 경우는 이벤트를 여기서 처리하고 종료
            if self.menu_button.underMouse():
                event.accept()
                return
        super().mouseReleaseEvent(event)
            
    def mouseMoveEvent(self, event):
        """마우스 이동 이벤트 처리"""
        if not (event.buttons() & Qt.LeftButton):
            return
        if not self.drag_start_position:
            return
            
        # 최소 드래그 거리 확인
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return
            
        # hover 상태 초기화를 위해 leave 이벤트 강제 발생
        leave_event = QEvent(QEvent.Leave)
        QApplication.sendEvent(self, leave_event)
            
        # 드래그 시작
        drag = QDrag(self)
        mime_data = QMimeData()
        
        # 프로젝트 데이터를 JSON으로 직렬화
        project_json = json.dumps(self.project_data)
        mime_data.setText(project_json)
        mime_data.setData("application/x-projectcard", str(id(self)).encode())
        drag.setMimeData(mime_data)
        
        # 드래그 중인 카드의 시각적 표현 생성
        pixmap = self.grab()
        # 반투명 효과 적용
        temp_pixmap = QPixmap(pixmap.size())
        temp_pixmap.fill(Qt.transparent)
        painter = QPainter(temp_pixmap)
        painter.setOpacity(0.7)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        
        drag.setPixmap(temp_pixmap)
        drag.setHotSpot(event.pos())
        
        # 드래그 시작 시 현재 카드를 반투명하게 만듦
        self.setStyleSheet(self.styleSheet() + "background-color: rgba(255, 255, 255, 0.5);")
        
        # 드래그 실행
        result = drag.exec_(Qt.MoveAction)
        
        # 드래그 종료 시 원래 스타일로 복원
        self.setStyleSheet(self.styleSheet().replace("background-color: rgba(255, 255, 255, 0.5);", ""))
        
        # 드래그 종료 후 다시 한번 hover 상태 초기화
        QApplication.sendEvent(self, leave_event)
        
    def dragEnterEvent(self, event):
        """드래그 진입 이벤트 처리"""
        if event.mimeData().hasFormat("application/x-projectcard"):
            source_id = int(event.mimeData().data("application/x-projectcard").data())
            if source_id != id(self):
                event.accept()
                # 드래그 진입 시 카드 사이에 공간을 시각적으로 표시
                self.setStyleSheet(self.styleSheet() + """
                    QFrame#project_card {
                        margin-left: 30px;
                    }
                """)
            else:
                event.ignore()
        
    def dragLeaveEvent(self, event):
        """드래그 떠남 이벤트 처리"""
        # 드래그가 떠날 때 원래 스타일로 복원
        self.setStyleSheet(self.styleSheet().replace("margin-left: 30px;", ""))
        event.accept()
        
    def dragMoveEvent(self, event):
        """드래그 이동 이벤트 처리"""
        if event.mimeData().hasFormat("application/x-projectcard"):
            source_id = int(event.mimeData().data("application/x-projectcard").data())
            if source_id != id(self):
                event.accept()
            else:
                event.ignore()
                
    def dropEvent(self, event):
        """드롭 이벤트 처리"""
        source_id = int(event.mimeData().data("application/x-projectcard").data())
        if source_id == id(self):
            return
            
        # 스타일 복원
        self.setStyleSheet(self.styleSheet().replace("margin-left: 30px;", ""))
            
        # 부모 위젯에 카드 순서 변경 요청
        if self.parent and hasattr(self.parent, 'reorder_cards'):
            source_card = self.find_card_by_id(source_id)
            if source_card:
                self.parent.reorder_cards(source_card, self)
                
        # hover 상태 초기화를 위해 leave 이벤트 강제 발생
        leave_event = QEvent(QEvent.Leave)
        QApplication.sendEvent(self, leave_event)
        
    def find_card_by_id(self, card_id):
        """ID로 카드 찾기"""
        if self.parent:
            for card in self.parent.findChildren(ProjectCard):
                if id(card) == card_id:
                    return card
        return None
        
    def paintEvent(self, event):
        """카드 그리기"""
        super().paintEvent(event)
        
        # 드래그 오버 상태일 때 삽입 위치 표시
        if self.underMouse() and self._is_drag_active():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # 삽입 위치를 나타내는 선 그리기
            pen = QPen(QColor("#339af0"))
            pen.setWidth(2)
            painter.setPen(pen)
            
            rect = self.rect()
            painter.drawLine(0, 0, 0, rect.height())
            
    def _is_drag_active(self):
        """현재 드래그가 활성화되어 있는지 확인"""
        drag_mime = QApplication.instance().clipboard().mimeData()
        return drag_mime.hasFormat("application/x-projectcard") 

    def show_menu(self):
        """프로젝트 메뉴 표시"""
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
        """)
        
        # 메뉴 항목 추가
        open_action = menu.addAction("열기")
        edit_action = menu.addAction("수정")
        menu.addSeparator()
        delete_action = menu.addAction("삭제")
        
        # 메뉴 버튼의 위치를 기준으로 메뉴 표시
        menu_pos = self.menu_button.mapToGlobal(QPoint(0, self.menu_button.height()))
        action = menu.exec_(menu_pos)
        
        # 선택된 메뉴 처리
        if action == open_action:
            if hasattr(self.parent, 'on_project_open'):
                self.parent.on_project_open(self)
        elif action == edit_action:
            if hasattr(self.parent, 'on_project_edit'):
                self.parent.on_project_edit(self)
        elif action == delete_action:
            if hasattr(self.parent, 'on_project_delete'):
                self.parent.on_project_delete(self)
                
    