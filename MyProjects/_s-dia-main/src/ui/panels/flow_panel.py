import os
import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QMenu, QListWidgetItem, 
                              QLabel, QFrame, QHBoxLayout, QApplication, QPushButton, QDialog, QMessageBox, QAbstractItemView, QListWidget)
from PySide6.QtCore import Qt, QSize, Signal, QMimeData, QTimer
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QIcon, QPixmap, QDrag
import logging
import json

from ..database import get_datasources_list, get_datasource, delete_process_from_flow, get_flow_by_uuid, update_flow
from src.ui.action.export import ExportWidget
from src.ui.action.drop_duplicates import DropDuplicatesWidget
from src.ui.action.filter import FilterWidget
from src.ui.action.orderby import OrderByWidget
from src.ui.action.union import UnionWidget
from src.ui.action.join import JoinWidget
from src.ui.action.rounding import RoundingWidget
from src.ui.components.confirm_dialog import ConfirmDialog

class CustomQListWidget(QListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.NoDragDrop)  # 커스텀 드래그만 사용
        self._placeholder_item = None
        self._last_drop_row = None
        self._dragged_card_data = None  # 카드 데이터 저장용
        self._original_size = None
        self._dragged_row = None
        self._scroll_pos = None
        self._is_dragging = False  # 드래그 상태 추적
        self._is_valid_drop_area = True  # 드롭 가능 영역 여부
        self._original_item = None  # 원본 아이템 저장

    def dragStartEvent(self, event):
        # 드래그 시작할 때의 처리
        self._is_dragging = True
        self._is_valid_drop_area = True
        self._dragged_row = self.currentRow()
        self._scroll_pos = self.verticalScrollBar().value()
        
        # 현재 선택된 아이템의 데이터 저장
        current_item = self.currentItem()
        if current_item:
            current_widget = self.itemWidget(current_item)
            if isinstance(current_widget, ProcessCard):
                self._dragged_card_data = (
                    current_widget.process_type,
                    current_widget.content,
                    current_widget.flow_info,
                    current_widget.process_index
                )
                self._original_size = current_item.sizeHint()
                self._original_item = current_item
                
                # 실제 프로세스 인덱스 저장 (placeholder 추가 전)
                self._original_process_index = current_widget.process_index
                
                logging.debug(f'드래그 시작 - UI 인덱스: {self._dragged_row}, 프로세스 인덱스: {self._original_process_index}')
                
                # 드래그 시작 시 원본 카드 제거
                self.takeItem(self._dragged_row)
                
                # placeholder 추가 (원본 카드가 제거된 후의 위치에)
                self._placeholder_item = QListWidgetItem()
                self._placeholder_item.setSizeHint(self._original_size)
                self._placeholder_item.setBackground(Qt.lightGray)
                self.insertItem(self._dragged_row, self._placeholder_item)
                
                # 드래그 시작
                event.accept()
                return
        
        # 드래그할 수 없는 경우
        self._is_dragging = False
        self._dragged_card_data = None
        self._original_size = None
        self._dragged_row = None
        self._scroll_pos = None
        self._original_item = None
        self._original_process_index = None
        event.ignore()

    def dragEnterEvent(self, event):
        if self._is_dragging:
            self._is_valid_drop_area = True
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if not self._is_dragging:
            event.ignore()
            return

        # 드래그 중인 위치가 리스트 위젯 영역 내에 있는지 확인
        pos = event.position().toPoint()
        if not self.rect().contains(pos):
            self._is_valid_drop_area = False
            event.ignore()
            return

        # 드래그 가능 영역으로 돌아왔을 때
        self._is_valid_drop_area = True
        
        # 드롭 위치 계산 - 더 간단하고 정확한 방법
        drop_row = self._calculate_drop_row(pos)
        
        # placeholder 관리
        if self._placeholder_item:
            try:
                old_row = self.row(self._placeholder_item)
                if old_row != -1 and old_row != drop_row:
                    self.takeItem(old_row)
                    self.insertItem(drop_row, self._placeholder_item)
            except RuntimeError:
                # placeholder가 이미 삭제된 경우 새로 생성
                self._placeholder_item = QListWidgetItem()
                self._placeholder_item.setSizeHint(QSize(247, 78))
                self._placeholder_item.setBackground(Qt.lightGray)
                self.insertItem(drop_row, self._placeholder_item)
        else:
            self._placeholder_item = QListWidgetItem()
            self._placeholder_item.setSizeHint(QSize(247, 78))
            self._placeholder_item.setBackground(Qt.lightGray)
            self.insertItem(drop_row, self._placeholder_item)
        
        self._last_drop_row = drop_row
        
        # 스크롤 처리
        self._handle_scroll_during_drag(drop_row)
        
        event.accept()
    
    def _calculate_drop_row(self, pos):
        """드롭 위치를 계산하는 함수"""
        # 먼저 indexAt으로 기본 위치 확인
        index = self.indexAt(pos)
        if index.isValid():
            return index.row()
        
        # indexAt이 실패한 경우 (아이템 사이 또는 끝에 드롭)
        viewport_pos = self.viewport().mapFrom(self, pos)
        
        # 리스트가 비어있는 경우
        if self.count() == 0:
            return 0
        
        # placeholder를 제외한 실제 아이템들만 고려
        actual_items = []
        for i in range(self.count()):
            item = self.item(i)
            if item and item != self._placeholder_item:
                actual_items.append((i, item))
        
        # 실제 아이템이 없는 경우
        if not actual_items:
            return 0
        
        # 각 실제 아이템의 위치를 확인하여 드롭 위치 결정
        for i, item in actual_items:
            item_rect = self.visualItemRect(item)
            # 아이템의 상단 절반에 드롭하면 해당 위치에 삽입
            if viewport_pos.y() < item_rect.center().y():
                return i
        
        # 마지막 실제 아이템보다 아래에 드롭하면 끝에 추가
        # placeholder가 제거된 후의 실제 아이템 개수를 기준으로 계산
        actual_count = len(actual_items)
        if actual_count > 0:
            # 마지막 실제 아이템의 인덱스를 찾아서 그 다음 위치 반환
            last_actual_index = actual_items[-1][0]
            return last_actual_index + 1
        else:
            return 0
    
    def _handle_scroll_during_drag(self, drop_row):
        """드래그 중 스크롤 처리"""
        if drop_row < self.count():
            item = self.item(drop_row)
            if item:
                rect = self.visualItemRect(item)
                viewport_height = self.viewport().height()
                
                # 위쪽으로 스크롤
                if rect.top() < 0:
                    scroll_amount = min(rect.top(), -20)  # 최소 20픽셀씩 스크롤
                    self.verticalScrollBar().setValue(self.verticalScrollBar().value() + scroll_amount)
                # 아래쪽으로 스크롤
                elif rect.bottom() > viewport_height:
                    scroll_amount = min(rect.bottom() - viewport_height, 20)  # 최소 20픽셀씩 스크롤
                    self.verticalScrollBar().setValue(self.verticalScrollBar().value() + scroll_amount)

    def dragLeaveEvent(self, event):
        # 드래그가 리스트 위젯 영역을 벗어났을 때
        self._is_valid_drop_area = False
        # placeholder 제거
        try:
            if self._placeholder_item:
                row = self.row(self._placeholder_item)
                if row != -1:
                    self.takeItem(row)
        except RuntimeError:
            pass
        self._placeholder_item = None
        event.accept()

    def dropEvent(self, event):
        # 드래그 중이 아니면 무시
        if not self._is_dragging:
            event.ignore()
            return

        # placeholder 제거
        try:
            if self._placeholder_item:
                row = self.row(self._placeholder_item)
                if row != -1:
                    self.takeItem(row)
        except RuntimeError:
            pass
        self._placeholder_item = None

        # 실제 드롭 위치 계산 (placeholder가 제거된 후)
        drop_pos = event.position().toPoint()
        actual_drop_row = self._calculate_drop_row(drop_pos)
        
        # 드롭 위치가 리스트 범위를 벗어나지 않도록 조정
        actual_drop_row = max(0, min(actual_drop_row, self.count()))

        # 드롭 위치에 새로운 카드 생성
        if self._dragged_card_data is not None:
            process_type, content, flow_info, process_index = self._dragged_card_data
            original_process_index = getattr(self, '_original_process_index', self._dragged_row)
            logging.debug(f'드롭 - UI 인덱스: {self._dragged_row}, 프로세스 인덱스: {process_index}, 원본 프로세스 인덱스: {original_process_index}, 드롭 위치: {actual_drop_row}')
            
            # 새로운 카드 생성 (process_index는 나중에 업데이트)
            new_card = ProcessCard(process_type, content, flow_info, process_index, 3, ", ", self)
            new_item = QListWidgetItem()
            new_item.setSizeHint(QSize(247, 78))
            self.insertItem(actual_drop_row, new_item)
            self.setItemWidget(new_item, new_card)
            self.setCurrentItem(new_item)

            # FlowPanel 찾아서 프로세스 순서 변경 알림
            flow_panel = self.parent()
            while flow_panel is not None and flow_panel.__class__.__name__ != "FlowPanel":
                flow_panel = flow_panel.parent()
            if flow_panel and hasattr(flow_panel, '_on_process_order_changed'):
                # 실제 프로세스 인덱스 사용
                flow_panel._on_process_order_changed(None, original_process_index, original_process_index + 1, None, actual_drop_row)

        # 스크롤 위치 복원
        if self._scroll_pos is not None:
            self.verticalScrollBar().setValue(self._scroll_pos)
            self._scroll_pos = None

        # 상태 초기화
        self._dragged_card_data = None
        self._original_size = None
        self._dragged_row = None
        self._last_drop_row = None
        self._is_dragging = False
        self._original_item = None
        self._original_process_index = None
        event.accept()

    def _remove_placeholder(self):
        if self._placeholder_item:
            try:
                row = self.row(self._placeholder_item)
                if row != -1:
                    self.takeItem(row)
            except Exception:
                pass
            self._placeholder_item = None

    def _cancel_drag(self):
        """드래그 취소 시 원래 상태로 복원"""
        # placeholder 제거
        self._remove_placeholder()
        
        # 드래그 중인 카드가 있으면 원래 위치로 복원
        if self._is_dragging and self._dragged_card_data is not None:
            process_type, content, flow_info, process_index = self._dragged_card_data
            new_card = ProcessCard(process_type, content, flow_info, process_index, 3, ", ", self)
            new_item = QListWidgetItem()
            new_item.setSizeHint(QSize(247, 78))  # 고정된 크기 사용
            self.insertItem(self._dragged_row, new_item)
            self.setItemWidget(new_item, new_card)
            self.setCurrentItem(new_item)
        
        # 스크롤 위치 복원
        if self._scroll_pos is not None:
            self.verticalScrollBar().setValue(self._scroll_pos)
            self._scroll_pos = None
        
        # 모든 상태 초기화
        self._dragged_card_data = None
        self._original_size = None
        self._dragged_row = None
        self._last_drop_row = None
        self._is_dragging = False
        self._is_valid_drop_area = True
        self._original_item = None
        self._original_process_index = None

    def startDrag(self, supportedActions):
        item = self.currentItem()
        widget = self.itemWidget(item)
        if widget and isinstance(widget, ProcessCard):
            # 드래그 시작 시 원래 위치 저장
            self._scroll_pos = self.verticalScrollBar().value()
            self._dragged_card_data = (widget.process_type, widget.content, widget.flow_info, widget.process_index)
            self._original_size = item.sizeHint()
            self._dragged_row = self.row(item)
            self._is_dragging = True
            self._original_item = item
            self._original_process_index = widget.process_index
            
            # 원래 아이템 제거
            self.takeItem(self._dragged_row)
            
            # placeholder 추가
            self._placeholder_item = QListWidgetItem()
            self._placeholder_item.setSizeHint(QSize(247, 78))
            self._placeholder_item.setBackground(Qt.lightGray)
            self.insertItem(self._dragged_row, self._placeholder_item)
            
            # 드래그 이미지 생성
            pixmap = QPixmap(widget.size())
            widget.render(pixmap)
            drag = QDrag(self)
            drag.setPixmap(pixmap)
            drag.setHotSpot(widget.rect().center())
            mime = QMimeData()
            drag.setMimeData(mime)
            
            # 드래그 실행 및 결과 처리
            result = drag.exec(Qt.MoveAction)
            if result == Qt.IgnoreAction:  # 드롭 실패 또는 취소
                self._restore_dragged_card()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self._is_dragging:
            # ESC 키로 드래그 취소 시 원래 위치로 복원
            self._restore_dragged_card()
            event.accept()
        else:
            super().keyPressEvent(event)

    def _restore_dragged_card(self):
        """드래그된 카드를 원래 위치로 복원하는 함수"""
        # placeholder 제거
        try:
            if self._placeholder_item:
                row = self.row(self._placeholder_item)
                if row != -1:
                    self.takeItem(row)
        except RuntimeError:
            pass
        self._placeholder_item = None

        # 원래 위치로 복원
        if self._dragged_card_data is not None:
            process_type, content, flow_info, process_index = self._dragged_card_data
            new_card = ProcessCard(process_type, content, flow_info, process_index, 3, ", ", self)
            new_item = QListWidgetItem()
            new_item.setSizeHint(QSize(247, 78))
            self.insertItem(self._dragged_row, new_item)
            self.setItemWidget(new_item, new_card)
            self.setCurrentItem(new_item)
            self.repaint()

        # 스크롤 위치 복원
        if self._scroll_pos is not None:
            self.verticalScrollBar().setValue(self._scroll_pos)
            self._scroll_pos = None

        # 상태 초기화
        self._dragged_card_data = None
        self._original_size = None
        self._dragged_row = None
        self._last_drop_row = None
        self._is_dragging = False
        self._original_item = None
        self._original_process_index = None

class ProcessCard(QFrame):
    """프로세스 정보를 카드 형태로 표시하는 위젯"""
    
    # 수정, 삭제 시그널(외부에서 연결 가능)
    edit_requested = Signal()
    delete_requested = Signal()

    def __init__(self, process_type, content, flow_info, process_index=None, view_count=3, delimiter=", ",  parent=None):
        super().__init__(parent)
        self.setObjectName("processCard")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.process_type = process_type
        self.flow_info = flow_info
        self.process_index = process_index
        self.content = content
        self.setFixedHeight(68)  # 카드 높이 약간 줄임
        
        # 임시 카드인지 확인
        self.is_temp_card = False
        if process_type in ['컬럼 선택', '중복 제거', '컬럼명 변경', '필터', '정렬', '합치기(union)', '결합하기(join)', '라운딩'] and parent and hasattr(parent, 'temp_process_index') and parent.temp_process_index == process_index:
            self.is_temp_card = True
            logging.debug(f'임시 카드로 설정됨 - process_type: {process_type}, process_index: {process_index}, parent.temp_process_index: {parent.temp_process_index}')
        else:
           print(f'일반 카드로 설정됨 - process_type: {process_type}, process_index: {process_index}, parent.temp_process_index: {getattr(parent, "temp_process_index", None) if parent else None}')
        
        # 카드 스타일 설정
        if self.is_temp_card:
            # 임시 카드 스타일 (붉은 계열, 흐린 효과)
            self.setStyleSheet("""
                QToolTip {
                    background-color: #495057;
                    color: white;
                    border: 1px solid #343a40;
                    padding: 2px, 2px, 2px, 2px;
                    font-size: 12px;
                }
                QFrame#processCard {
                    background: rgba(255, 235, 235, 0.7);
                    border: 1px solid #ffcdd2;
                    border-radius: 4px;
                    padding: 2px;
                    max-width: 247px;
                    min-height: 68px;
                    max-height: 68px;
                    margin-left: 0px;
                    margin-right: 0px;
                }
                QFrame#processCard:hover {
                    background: rgba(255, 235, 235, 0.8);
                    color: #d32f2f;
                }                           
                QLabel#processType {
                    font-weight: bold;
                    font-size: 14px;
                    background: transparent;
                    color: #d32f2f;
                    border: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    padding: 2px 2px 2px 2px;
                }
                QLabel#content {
                    font-size: 12px;
                    background: transparent;
                    color: #666666;
                    border: none;
                    border-bottom-left-radius: 4px;
                    border-bottom-right-radius: 4px;
                    padding: 2px 2px 2px 2px;
                }
            """)
        else:
            # 일반 카드 스타일
            self.setStyleSheet("""
                QToolTip {
                    background-color: #495057;
                    color: white;
                    border: 1px solid #343a40;
                    padding: 2px, 2px, 2px, 2px;
                    font-size: 12px;
                }
                QFrame#processCard {
                    background: transparent;
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    padding: 2px;
                    max-width: 247px;
                    min-height: 68px;
                    max-height: 68px;
                    margin-left: 0px;
                    margin-right: 0px;
                }
                QFrame#processCard:hover {
                    background: #e9ecef;
                    color: #1864ab;
                }                           
                QLabel#processType {
                    font-weight: bold;
                    font-size: 14px;
                    background: transparent;
                    color: #1864ab;
                    border: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    padding: 2px 2px 2px 2px;
                }
                QLabel#content {
                    font-size: 12px;
                    background: transparent;
                    color: #333333;
                    border: none;
                    border-bottom-left-radius: 4px;
                    border-bottom-right-radius: 4px;
                    padding: 2px 2px 2px 2px;
                }
                QPushButton#menu_button {
                    background: transparent;
                    border: none;
                    font-size: 18px;
                    color: #868e96;
                    padding: 0 3px;
                }
                QPushButton#menu_button:hover {
                    background: #e9ecef;
                    color: #1864ab;
                }
            """)
        
        # 전체 레이아웃: 가로 배치
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 왼쪽: 기존 내용(세로)
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # 프로세스 타입 레이블
        type_label = QLabel(process_type)
        type_label.setObjectName("processType")
        content_layout.addWidget(type_label)
        
        # 컬럼 목록 레이블 (3개까지만, 나머지는 외 n개)
        if isinstance(content, str):
            all_columns = [col.strip() for col in content.split(",") if col.strip()]
            display_columns = all_columns[:view_count]
            extra_count = len(all_columns) - view_count
            if extra_count > 0:
                display_text = delimiter.join(display_columns) + f" 외 {extra_count}개"
            else:
                display_text = delimiter.join(display_columns)
        elif isinstance(content, list) and content and isinstance(content[0], dict):
            # 딕셔너리 리스트인 경우 column_name 추출
            all_columns = [col.get('column_name', '') for col in content if col.get('column_name')]
            display_columns = all_columns[:view_count]
            extra_count = len(all_columns) - view_count
            if extra_count > 0:
                display_text = delimiter.join(display_columns) + f" 외 {extra_count}개"
            else:
                display_text = delimiter.join(display_columns)
        else:
            all_columns = content if isinstance(content, list) else []
            display_columns = all_columns[:view_count]
            extra_count = len(all_columns) - view_count
            if extra_count > 0:
                display_text = delimiter.join(display_columns) + f" 외 {extra_count}개"
            else:
                display_text = delimiter.join(display_columns)
        
        if self.process_type == "정렬" and not self.is_temp_card:
            na_position = self.flow_info.get("processes")[self.process_index].get("na_position", "first")
            display_text += f'\nNA 위치: {"처음" if na_position == "first" else "마지막"}'

        columns_label = QLabel(display_text)
        columns_label.setObjectName("content")
        columns_label.setWordWrap(True)
        columns_label.setToolTip(delimiter.join(all_columns))
        content_layout.addWidget(columns_label)

        # 왼쪽(내용) 추가
        main_layout.addLayout(content_layout)

        # 오른쪽: 햄버거 메뉴 버튼(⋮) - 임시 카드가 아닌 경우에만 표시
        if not self.is_temp_card:
            menu_layout = QVBoxLayout()
            menu_layout.setContentsMargins(0, 0, 0, 0)
            menu_layout.addStretch(1)
            self.menu_button = QPushButton("⋮")
            self.menu_button.setObjectName("menu_button")
            self.menu_button.setFixedWidth(24)
            self.menu_button.setCursor(Qt.PointingHandCursor)
            menu_layout.addWidget(self.menu_button, alignment=Qt.AlignVCenter)
            menu_layout.addStretch(1)
            main_layout.addLayout(menu_layout)

            # 메뉴 연결
            self.menu_button.clicked.connect(self.show_menu)
        else:
            self.menu_button = None

    def show_menu(self):
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
            QMenu::separator {
                height: 1px;
                background: #dee2e6;
                margin: 5px 0px;
            }
        """)
        edit_action = menu.addAction("수정")
        delete_action = menu.addAction("삭제")
        action = menu.exec_(self.menu_button.mapToGlobal(self.menu_button.rect().bottomRight()))
        if action == edit_action:
            self.edit_requested.emit()
        elif action == delete_action:
            self.delete_requested.emit()

    def get_flow_panel(self):
        parent = self.parent()
        while parent is not None:
            if parent.__class__.__name__ == "FlowPanel":
                return parent
            parent = parent.parent()
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 임시 카드인 경우 드래그 시작 위치를 저장하지 않음
            if not self.is_temp_card:
                self._drag_start_pos = event.pos()
            
            if self.menu_button and self.menu_button.underMouse():
                event.accept()
                return
            # FlowPanel을 위로 타고 찾아서 호출
            flow_panel = self.get_flow_panel()
            if flow_panel and hasattr(flow_panel, 'on_process_card_clicked'):
                flow_panel.on_process_card_clicked(self.process_index, self.process_type, self.content, self.flow_info)
                # 해당 카드의 QListWidgetItem을 찾아 선택
                list_widget = flow_panel.ui.process_list
                for i in range(list_widget.count()):
                    item = list_widget.item(i)
                    if list_widget.itemWidget(item) == self:
                        list_widget.setCurrentItem(item)
                        break
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # 임시 카드인 경우 드래그를 허용하지 않음
        if self.is_temp_card:
            super().mouseMoveEvent(event)
            return
            
        if hasattr(self, '_drag_start_pos') and (event.buttons() & Qt.LeftButton):
            if (event.pos() - self._drag_start_pos).manhattanLength() > QApplication.startDragDistance():
                flow_panel = self.get_flow_panel()
                if flow_panel:
                    list_widget = flow_panel.ui.process_list
                    # 해당 카드의 QListWidgetItem을 찾아 선택 후 드래그 시작
                    for i in range(list_widget.count()):
                        item = list_widget.item(i)
                        if list_widget.itemWidget(item) == self:
                            list_widget.setCurrentItem(item)
                            list_widget.startDrag(Qt.MoveAction)
                            break
                return
        super().mouseMoveEvent(event)

class FlowPanel(QWidget):
    """흐름 상세 정보를 표시하는 패널"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        
        # 임시 처리 카드 추적용 변수 추가
        self.temp_process_index = None
        self.temp_process_type = None
        self.temp_process_data = None
        
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
                
            # process_list 스타일 설정
            if hasattr(self.ui, 'process_list'):
                # 기존 QListWidget을 CustomQListWidget으로 교체
                old_list = self.ui.process_list
                parent = old_list.parent()
                layout = old_list.parentWidget().layout()
                idx = layout.indexOf(old_list)
                layout.removeWidget(old_list)
                old_list.deleteLater()
                self.ui.process_list = CustomQListWidget(parent)
                layout.insertWidget(idx, self.ui.process_list)
                self.ui.process_list.setStyleSheet("""
                    QListWidget {
                        background-color: transparent;
                        border: none;
                    }
                    QListWidget::item {
                        padding: 4px;
                    }
                """)
                
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
                    padding: 2px 2px 2px 2px;
                    margin: 0px;
                }
                QListWidget::item {
                    margin: 2px 4px 2px 4px;
                    border: none;
                    min-height: 64px;
                    max-height: 64px;
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
                QToolTip {
                    background-color: #495057;
                    color: white;
                    border: 1px solid #343a40;
                    padding: 2px, 2px, 2px, 2px;
                    font-size: 12px;
                }
                QLabel {
                    color: #000000;
                    font-size: 16px;
                    font-weight: bold;
                }
                QLabel::hover {
                    color: #1864ab;
                }
            """)
            
            # 처리 추가 버튼 클릭 시 팝업 메뉴 연결
            self.ui.add_process_btn.clicked.connect(self.show_add_process_menu)
            self.ui.run_button.clicked.connect(self.run_flow_button)
            
            # 드래그 앤 드롭 설정
            self.ui.process_list.setDragEnabled(True)
            self.ui.process_list.setAcceptDrops(True)
            self.ui.process_list.setDropIndicatorShown(True)
            self.ui.process_list.setDragDropMode(QAbstractItemView.InternalMove)
            self.ui.process_list.model().rowsMoved.connect(self._on_process_order_changed)
            
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
                - processes (list): 프로세스 목록
        """
        try:
            if not flow_info:
                return
                
            # 흐름명 설정
            name = flow_info.get('name', '')
            self.ui.flow_name.setText(name)
            self.flow_info = flow_info
            
            # 임시 카드 정보 초기화 (저장 후 정식 카드로 변환)
            self.temp_process_index = None
            self.temp_process_type = None
            self.temp_process_data = None
            
            # data_source_uuid로 data_path 찾기
            data_source_uuid = flow_info.get('data_source_uuid', '')
            self.current_data_source = get_datasource(self.parent.project_data.get('uuid', ''), data_source_uuid)
            data_path = self.current_data_source.get('name', '') if self.current_data_source else ''

            # 입력란에 data_path 넣기
            if hasattr(self.ui, 'data_source_input'):
                self.ui.data_source_input.setText(data_path)
            
            # 결과 설정
            self.ui.result_text.setText(os.path.join(self.parent.project_data.get('data_directory'), name, f"{name}.parquet"))   
            
            # 프로세스 목록 설정
            if hasattr(self.ui, 'process_list'):
                self.ui.process_list.clear()
                processes = flow_info.get('processes', [])
                for idx, process in enumerate(processes):
                    process_type = process.get('process_type', '')
                    card = None

                    # 프로세스 타입에 따른 처리
                    if process_type == 'export':
                        # 컬럼 선택 프로세스인 경우
                        columns = process.get('columns', [])
                        export_columns = [col.get('column_name') for col in columns if col.get('is_export', False)]
                        
                        # if export_columns:
                        # 프로세스 타입과 컬럼 목록을 카드로 표시
                        columns_text = ", ".join(export_columns)
                        card = ProcessCard("컬럼 선택", columns_text, flow_info, process_index=idx, view_count=3, delimiter=", ", parent=self)
                    elif process_type == 'drop_duplicates':
                        # 중복 제거 프로세스인 경우
                        columns = process.get('columns', [])
                        columns_text = ", ".join(columns)
                        card = ProcessCard("중복 제거", columns_text, flow_info, process_index=idx, view_count=3, delimiter=", ", parent=self)
                    elif process_type == 'rename_columns':
                        # 컬럼명 변경 프로세스인 경우
                        renames = process.get('renames', [])
                        # "old → new" 형식의 문자열 생성, 변경된 것만 표시
                        rename_texts = [f"{r.get('column_name')}→{r.get('new_column_name')}" for r in renames if r.get('column_name') != r.get('new_column_name')]
                        content_text = ", ".join(rename_texts)
                        card = ProcessCard("컬럼명 변경", content_text, flow_info, process_index=idx, view_count=3, delimiter=", ", parent=self)
                    elif process_type == 'filter':
                        # 필터 프로세스인 경우
                        filter_data = process.get('filter_data', {})
                        content_texts = [f"{r.get('column')} {r.get('operator')} {r.get('value')}" for r in filter_data.get("conditions", [])]

                        card = ProcessCard("필터", content_texts, flow_info, process_index=idx, view_count=2, delimiter="\n", parent=self)
                    elif process_type == 'orderby':
                        # 정렬 프로세스인 경우
                        sort_conditions = process.get('sort_conditions', [])
                        # "컬럼명(오름차순/내림차순)" 형식의 문자열 생성
                        sort_texts = []
                        for condition in sort_conditions:
                            column = condition.get('column', '')
                            order = condition.get('order', 'asc')
                            order_text = "오름차순" if order == 'asc' else "내림차순"
                            sort_texts.append(f"{column}({order_text})")
                        content_text = ", ".join(sort_texts)
                        card = ProcessCard("정렬", content_text, flow_info, process_index=idx, view_count=3, delimiter=", ", parent=self)
                    elif process_type == 'union':
                        # 합치기(union) 프로세스인 경우
                        target_datasource_name = process.get('target_datasource_name', '')
                        content_text = f"결합할 데이터 소스: {target_datasource_name}"
                        card = ProcessCard("합치기(union)", content_text, flow_info, process_index=idx, view_count=3, delimiter=", ", parent=self)
                    elif process_type == 'join':
                        # 결합하기(join) 프로세스인 경우
                        target_datasource_name = process.get('target_datasource_name', '')
                        join_type = process.get('join_type', 'inner')
                        content_text = f"결합할 데이터 소스: {target_datasource_name} ({join_type})"
                        card = ProcessCard("결합하기(join)", content_text, flow_info, process_index=idx, view_count=3, delimiter=", ", parent=self)
                    elif process_type == 'rounding':
                        # 라운딩 프로세스인 경우
                        rounding_method = process.get('rounding_method', 'round')
                        decimal_places = process.get('decimal_places', 0)
                        columns = process.get('columns', [])
                        method_mapping = {
                            "round": "반올림",
                            "ceil": "올림",
                            "floor": "내림"
                        }
                        method_text = method_mapping.get(rounding_method, "반올림")
                        content_text = f"{method_text} ({decimal_places}자리) - {len(columns)}개 컬럼"
                        card = ProcessCard("라운딩", content_text, flow_info, process_index=idx, view_count=3, delimiter=", ", parent=self)

                    if card:
                        card.edit_requested.connect(lambda process_type=process_type, idx=idx, proc=process: self.open_edit_dialog(process_type, idx, proc))
                        card.delete_requested.connect(lambda idx=idx: self.delete_process(idx))
                    
                        # 카드를 리스트 아이템으로 추가
                        item = QListWidgetItem()
                        item.setSizeHint(QSize(247, 78))

                        self.ui.process_list.addItem(item)
                        self.ui.process_list.setItemWidget(item, card)
        
            # 지오메트리 강제 업데이트
            QTimer.singleShot(0, self._update_geometries)
            
        except Exception as e:
            self.logger.error(f"흐름 정보 설정 중 오류 발생: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            
    def _update_geometries(self):
        """위젯의 지오메트리를 강제로 업데이트하여 레이아웃 문제를 해결"""
        if hasattr(self.ui, 'process_list'):
            self.ui.process_list.updateGeometries()
            
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

    def run_flow_button(self):
        # 임시 카드가 있으면 삭제
        if self.temp_process_index is not None:
            self._remove_temp_process_card()
            
        self.parent.run_flow(self.flow_info)

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
        export_action = ds_menu.addAction("컬럼 선택")
        remove_duplicates_action = ds_menu.addAction("중복 제거")
        rename_columns_action = ds_menu.addAction("컬럼명 변경")
        filter_action = ds_menu.addAction("필터")
        orderby_action = ds_menu.addAction("정렬")
        union_action = ds_menu.addAction("합치기(union)")
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
        # 컬럼 선택 클릭 시 동작 연결
        export_action.triggered.connect(self.show_export_ui)
        # 중복 제거 클릭 시 동작 연결
        remove_duplicates_action.triggered.connect(self.show_drop_duplicates_ui)
        # 컬럼명 변경 클릭 시 동작 연결
        rename_columns_action.triggered.connect(self.show_rename_columns_ui)
        # 필터 클릭 시 동작 연결
        filter_action.triggered.connect(self.show_filter_ui)
        # 정렬 클릭 시 동작 연결
        orderby_action.triggered.connect(self.show_orderby_ui)
        # 합치기 클릭 시 동작 연결
        union_action.triggered.connect(self.show_union_ui)
        # 결합하기 클릭 시 동작 연결
        join_action = ds_menu.actions()[6]  # "결합하기(join)" 액션
        join_action.triggered.connect(self.show_join_ui)
        # 라운딩 클릭 시 동작 연결
        rounding_action = num_menu.actions()[0]  # "라운딩" 액션
        rounding_action.triggered.connect(self.show_rounding_ui)
        menu.exec_(self.ui.add_process_btn.mapToGlobal(self.ui.add_process_btn.rect().bottomLeft()))

    def show_export_ui(self):
        """right_frame에 export.ui 기반 ExportWidget을 표시"""
        # 기존 임시 카드가 있으면 삭제
        if self.temp_process_index is not None:
            self._remove_temp_process_card()
            
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
        export_widget = ExportWidget(parent=self)
        layout.addWidget(export_widget)
        
        # 임시 처리 카드 생성 및 추가
        self._create_temp_process_card('컬럼 선택', '')

    def show_drop_duplicates_ui(self):
        """right_frame에 drop_duplicates.ui 기반 DropDuplicatesWidget을 표시"""
        # 기존 임시 카드가 있으면 삭제
        if self.temp_process_index is not None:
            self._remove_temp_process_card()
            
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
        # DropDuplicatesWidget을 import해서 추가
        drop_duplicates_widget = DropDuplicatesWidget(self)
        layout.addWidget(drop_duplicates_widget)
        
        # 임시 처리 카드 생성 및 추가
        self._create_temp_process_card('중복 제거', '')

    def show_rename_columns_ui(self):
        """right_frame에 rename_columns.ui 기반 RenameColumnsWidget을 표시 (편집용)"""
        # 기존 임시 카드가 있으면 삭제
        if self.temp_process_index is not None:
            self._remove_temp_process_card()
            
        # 임시 처리 카드 생성 및 추가 (먼저 생성)
        self._create_temp_process_card('컬럼명 변경', '')
        
        main_window = self.parent
        if not main_window:
            return

        right_frame = None
        for child in main_window.parent.ui.projects_container.children():
            if hasattr(child, "objectName") and child.objectName() == "right_frame":
                right_frame = child
                break
        
        if not right_frame: return
        
        if right_frame.layout():
            while right_frame.layout().count():
                item = right_frame.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        else:
            right_frame.setLayout(QVBoxLayout())
        layout = right_frame.layout()

        from src.ui.action.rename_columns import RenameColumnsWidget
        # 신규 등록이므로 flow_pos를 -1로 설정
        rename_columns_widget = RenameColumnsWidget(self, flow_pos=-1)
        if hasattr(rename_columns_widget, 'set_process_data'):
            rename_columns_widget.set_process_data(self.temp_process_data)
        layout.addWidget(rename_columns_widget)

    def show_filter_ui(self):
        """right_frame에 filter.ui 기반 FilterWidget을 표시 (새 필터 추가용)"""
        # 기존 임시 카드가 있으면 삭제
        if self.temp_process_index is not None:
            self._remove_temp_process_card()
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
        if not right_frame or not right_frame.layout():
            return
        # 기존 위젯 제거
        layout = right_frame.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        # FilterWidget 추가 (빈 상태)
        filter_widget = FilterWidget(self)
        layout.addWidget(filter_widget)
        # 임시 처리 카드 생성
        self._create_temp_process_card('필터', '')

    def show_orderby_ui(self):
        """right_frame에 orderby.ui 기반 OrderByWidget을 표시"""
        # 기존 임시 카드가 있으면 삭제
        if self.temp_process_index is not None:
            self._remove_temp_process_card()
            
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

        if not right_frame or not right_frame.layout():
            return

        # 기존 위젯 제거
        layout = right_frame.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # OrderByWidget 추가 (새 정렬 추가용)
        orderby_widget = OrderByWidget(parent=self)
        layout.addWidget(orderby_widget)
        
        # 임시 처리 카드 생성 및 추가
        self._create_temp_process_card('정렬', '')

    def show_union_ui(self):
        """right_frame에 union.ui 기반 UnionWidget을 표시"""
        # 기존 임시 카드가 있으면 삭제
        if self.temp_process_index is not None:
            self._remove_temp_process_card()
            
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

        if not right_frame or not right_frame.layout():
            return

        # 기존 위젯 제거
        layout = right_frame.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # UnionWidget 추가 (새 합치기 추가용)
        union_widget = UnionWidget(parent=self)
        layout.addWidget(union_widget)
        
        # 임시 처리 카드 생성 및 추가
        self._create_temp_process_card('합치기(union)', '')

    def show_join_ui(self):
        """right_frame에 join.ui 기반 JoinWidget을 표시"""
        # 기존 임시 카드가 있으면 삭제
        if self.temp_process_index is not None:
            self._remove_temp_process_card()
            
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

        if not right_frame or not right_frame.layout():
            return

        # 기존 위젯 제거
        layout = right_frame.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # JoinWidget 추가 (새 결합 추가용)
        join_widget = JoinWidget(parent=self)
        layout.addWidget(join_widget)
        
        # 임시 처리 카드 생성 및 추가
        self._create_temp_process_card('결합하기(join)', '')

    def show_rounding_ui(self):
        """right_frame에 rounding.ui 기반 RoundingWidget을 표시"""
        # 기존 임시 카드가 있으면 삭제
        if self.temp_process_index is not None:
            self._remove_temp_process_card()
            
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

        if not right_frame or not right_frame.layout():
            return

        # 기존 위젯 제거
        layout = right_frame.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # RoundingWidget 추가 (새 라운딩 추가용)
        rounding_widget = RoundingWidget(parent=self)
        layout.addWidget(rounding_widget)
        
        # 임시 처리 카드 생성 및 추가
        self._create_temp_process_card('라운딩', '')

    def _on_process_order_changed(self, parent, start, end, destination, row):
        """프로세스 순서가 변경되었을 때 호출되는 함수"""
        if not self.flow_info:
            return
        
        logging.debug(f'프로세스 순서 변경 - 시작: {start}, 끝: {end}, 목적지: {destination}, 행: {row}')
        
        # 프로세스 리스트 재정렬
        processes = self.flow_info.get('processes', [])
        if start < len(processes):
            moved_process = processes.pop(start)
            processes.insert(row, moved_process)
            
            logging.debug(f'프로세스 이동 - {start}번째에서 {row}번째로 이동')
            
            # flow_info에 반영
            self.flow_info['processes'] = processes
            
            # flow.json에 반영 (update_flow 사용)
            try:
                project_uuid = self.parent.project_data.get('uuid', '')
                flow_uuid = self.flow_info.get('uuid', '')
                flow = get_flow_by_uuid(project_uuid, flow_uuid)
                if flow:
                    flow['processes'] = processes
                    update_flow(project_uuid, flow)
            except Exception as e:
                from src.ui.components.message_dialog import MessageDialog
                MessageDialog.critical(self, "오류", f"프로세스 순서 변경 중 오류가 발생했습니다: {str(e)}")
            
            # UI 업데이트 - 전체 리스트를 다시 생성하여 process_index를 올바르게 설정
            self._update_process_list_with_correct_indices()
    
    def _update_process_list_with_correct_indices(self):
        """프로세스 리스트를 올바른 인덱스로 업데이트"""
        if not hasattr(self, 'flow_info') or not self.flow_info:
            return
            
        # 현재 스크롤 위치 저장
        scroll_pos = self.ui.process_list.verticalScrollBar().value()
        
        # 프로세스 목록 설정
        if hasattr(self.ui, 'process_list'):
            self.ui.process_list.clear()
            processes = self.flow_info.get('processes', [])
            for idx, process in enumerate(processes):
                process_type = process.get('process_type', '')
                card = None

                # 프로세스 타입에 따른 처리
                if process_type == 'export':
                    # 컬럼 선택 프로세스인 경우
                    columns = process.get('columns', [])
                    export_columns = [col.get('column_name') for col in columns if col.get('is_export', False)]
                    
                    columns_text = ", ".join(export_columns)
                    card = ProcessCard("컬럼 선택", columns_text, self.flow_info, process_index=idx, view_count=3, delimiter=", ", parent=self)
                elif process_type == 'drop_duplicates':
                    # 중복 제거 프로세스인 경우
                    columns = process.get('columns', [])
                    columns_text = ", ".join(columns)
                    card = ProcessCard("중복 제거", columns_text, self.flow_info, process_index=idx, view_count=3, delimiter=", ", parent=self)
                elif process_type == 'rename_columns':
                    # 컬럼명 변경 프로세스인 경우
                    renames = process.get('renames', [])
                    # "old → new" 형식의 문자열 생성, 변경된 것만 표시
                    rename_texts = [f"{r.get('column_name')}→{r.get('new_column_name')}" for r in renames if r.get('column_name') != r.get('new_column_name')]
                    content_text = ", ".join(rename_texts)
                    card = ProcessCard("컬럼명 변경", content_text, self.flow_info, process_index=idx, view_count=3, delimiter=", ", parent=self)
                elif process_type == 'filter':
                    # 필터 프로세스인 경우
                    filter_data = process.get('filter_data', {})
                    content_texts = [f"{r.get('column')} {r.get('operator')} {r.get('value')}" for r in filter_data.get("conditions", [])]

                    card = ProcessCard("필터", content_texts, self.flow_info, process_index=idx, view_count=2, delimiter="\n", parent=self)
                elif process_type == 'orderby':
                    # 정렬 프로세스인 경우
                    sort_conditions = process.get('sort_conditions', [])
                    # "컬럼명(오름차순/내림차순)" 형식의 문자열 생성
                    sort_texts = []
                    for condition in sort_conditions:
                        column = condition.get('column', '')
                        order = condition.get('order', 'asc')
                        order_text = "오름차순" if order == 'asc' else "내림차순"
                        sort_texts.append(f"{column}({order_text})")
                    content_text = ", ".join(sort_texts)
                    card = ProcessCard("정렬", content_text, self.flow_info, process_index=idx, view_count=3, delimiter=", ", parent=self)
                elif process_type == 'union':
                    # 합치기(union) 프로세스인 경우
                    target_datasource_name = process.get('target_datasource_name', '')
                    content_text = f"결합할 데이터 소스: {target_datasource_name}"
                    card = ProcessCard("합치기(union)", content_text, self.flow_info, process_index=idx, view_count=3, delimiter=", ", parent=self)
                elif process_type == 'join':
                    # 결합하기(join) 프로세스인 경우
                    target_datasource_name = process.get('target_datasource_name', '')
                    join_type = process.get('join_type', 'inner')
                    content_text = f"결합할 데이터 소스: {target_datasource_name} ({join_type})"
                    card = ProcessCard("결합하기(join)", content_text, self.flow_info, process_index=idx, view_count=3, delimiter=", ", parent=self)
                elif process_type == 'rounding':
                    # 라운딩 프로세스인 경우
                    rounding_method = process.get('rounding_method', 'round')
                    decimal_places = process.get('decimal_places', 0)
                    columns = process.get('columns', [])
                    method_mapping = {
                        "round": "반올림",
                        "ceil": "올림",
                        "floor": "내림"
                    }
                    method_text = method_mapping.get(rounding_method, "반올림")
                    content_text = f"{method_text} ({decimal_places}자리) - {len(columns)}개 컬럼"
                    card = ProcessCard("라운딩", content_text, self.flow_info, process_index=idx, view_count=3, delimiter=", ", parent=self)

                if card:
                    card.edit_requested.connect(lambda process_type=process_type, idx=idx, proc=process: self.open_edit_dialog(process_type, idx, proc))
                    card.delete_requested.connect(lambda idx=idx: self.delete_process(idx))
                
                    # 카드를 리스트 아이템으로 추가
                    item = QListWidgetItem()
                    item.setSizeHint(QSize(247, 78))

                    self.ui.process_list.addItem(item)
                    self.ui.process_list.setItemWidget(item, card)
        
        # 스크롤 위치 복원
        self.ui.process_list.verticalScrollBar().setValue(scroll_pos)

    def _create_temp_process_card(self, process_type, content):
        """임시 처리 카드 생성 및 추가"""
        if not hasattr(self, 'flow_info') or not self.flow_info:
            return
            
        # 임시 처리 인덱스 설정 (실제 프로세스 개수 기준)
        processes = self.flow_info.get('processes', [])
        self.temp_process_index = len(processes)
        self.temp_process_type = process_type
        self.temp_process_data = {
            'process_type': process_type,
            'content': content,
            'is_temp': True
        }
        
        # 임시 처리 카드 생성
        card = ProcessCard(process_type, content, self.flow_info, self.temp_process_index, 3, ", ", self)
        item = QListWidgetItem()
        item.setSizeHint(QSize(247, 78))
        self.ui.process_list.addItem(item)
        self.ui.process_list.setItemWidget(item, card)
        
        # 생성된 카드 선택
        self.ui.process_list.setCurrentItem(item)
        
        # 임시 처리 정보를 flow_info에 추가
        processes.append(self.temp_process_data)
        self.flow_info['processes'] = processes

    def _remove_temp_process_card(self):
        """임시 처리 카드 삭제"""
        if self.temp_process_index is None:
            return
            
        logging.debug(f'임시 카드 삭제 시작 - temp_process_index: {self.temp_process_index}, temp_process_type: {self.temp_process_type}')
        
        # UI 리스트에서 임시 카드 찾아서 제거
        temp_card_found = False
        for i in range(self.ui.process_list.count()):
            item = self.ui.process_list.item(i)
            if item:
                widget = self.ui.process_list.itemWidget(item)
                if isinstance(widget, ProcessCard) and widget.is_temp_card:
                    logging.debug(f'임시 카드 발견 - UI 인덱스: {i}, process_type: {widget.process_type}')
                    self.ui.process_list.takeItem(i)
                    temp_card_found = True
                    break
        
        if not temp_card_found:
            logging.warning('UI에서 임시 카드를 찾을 수 없음')
        
        # flow_info에서 임시 처리 제거
        processes = self.flow_info.get('processes', [])
        if self.temp_process_index < len(processes):
            removed_process = processes.pop(self.temp_process_index)
            logging.debug(f'flow_info에서 임시 프로세스 제거 - 인덱스: {self.temp_process_index}, 타입: {removed_process.get("process_type")}')
            self.flow_info['processes'] = processes
        else:
            logging.warning(f'flow_info에서 임시 프로세스를 찾을 수 없음 - 인덱스: {self.temp_process_index}, 총 개수: {len(processes)}')
        
        # right_frame 비우기
        main_window = self.parent.parent if self.parent else None
        if main_window:
            right_frame = None
            for child in main_window.ui.projects_container.children():
                if isinstance(child, QWidget) and child.objectName() == "right_frame":
                    right_frame = child
                    break
            if right_frame and right_frame.layout():
                while right_frame.layout().count():
                    item = right_frame.layout().takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
        
        # 임시 처리 정보 초기화
        self.temp_process_index = None
        self.temp_process_type = None
        self.temp_process_data = None
        
        logging.debug('임시 카드 삭제 완료')

    def open_edit_dialog(self, process_type, process_index, process_data):
        if process_type == 'export':
            self.open_export_edit_dialog(process_index, process_data)
        elif process_type == 'drop_duplicates':
            self.open_drop_duplicates_edit_dialog(process_index, process_data)
        elif process_type == 'rename_columns':
            self.open_rename_columns_edit_dialog(process_index, process_data)
        elif process_type == 'filter':
            self.open_filter_edit_dialog(process_index, process_data)
        elif process_type == 'orderby':
            self.open_orderby_edit_dialog(process_index, process_data)
        elif process_type == 'union':
            self.open_union_edit_dialog(process_index, process_data)
        elif process_type == 'join':
            self.open_join_edit_dialog(process_index, process_data)
        elif process_type == 'rounding':
            self.open_rounding_edit_dialog(process_index, process_data)

    def open_export_edit_dialog(self, process_index, process_data):
        # right_frame 찾기
        main_window = self.parent
        if not main_window:
            return

        right_frame = None
        for child in main_window.parent.ui.projects_container.children():
            if hasattr(child, "objectName") and child.objectName() == "right_frame":
                right_frame = child
                break

        if not right_frame or not right_frame.layout():
            return

        # 기존 위젯 제거
        layout = right_frame.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # ExportWidget 추가
        export_widget = ExportWidget(parent=self, flow_pos=process_index)
        if hasattr(export_widget, 'set_process_data'):
            export_widget.set_process_data(process_data)
        layout.addWidget(export_widget)

    def open_drop_duplicates_edit_dialog(self, process_index, process_data):
        # right_frame 찾기
        main_window = self.parent
        if not main_window:
            return

        right_frame = None
        for child in main_window.parent.ui.projects_container.children():
            if hasattr(child, "objectName") and child.objectName() == "right_frame":
                right_frame = child
                break

        if not right_frame or not right_frame.layout():
            return

        # 기존 위젯 제거
        layout = right_frame.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # DropDuplicatesWidget 추가
        drop_duplicates_widget = DropDuplicatesWidget(parent=self, flow_pos=process_index)
        if hasattr(drop_duplicates_widget, 'set_process_data'):
            drop_duplicates_widget.set_process_data(process_data)
        layout.addWidget(drop_duplicates_widget)

    def open_rename_columns_edit_dialog(self, process_index, process_data):
        """right_frame에 rename_columns.ui 기반 RenameColumnsWidget을 표시 (편집용)"""
        main_window = self.parent
        if not main_window:
            return

        right_frame = None
        for child in main_window.parent.ui.projects_container.children():
            if hasattr(child, "objectName") and child.objectName() == "right_frame":
                right_frame = child
                break
        
        if not right_frame: 
            return
        
        if right_frame.layout():
            while right_frame.layout().count():
                item = right_frame.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        else:
            right_frame.setLayout(QVBoxLayout())
        layout = right_frame.layout()

        from src.ui.action.rename_columns import RenameColumnsWidget
        rename_columns_widget = RenameColumnsWidget(self, flow_pos=process_index)
        if hasattr(rename_columns_widget, 'set_process_data'):
            rename_columns_widget.set_process_data(process_data)
        layout.addWidget(rename_columns_widget)

    def open_filter_edit_dialog(self, process_index, process_data):
        """right_frame에 filter.ui 기반 FilterWidget을 표시 (편집용)"""
        main_window = self.parent
        if not main_window:
            return

        right_frame = None
        for child in main_window.parent.ui.projects_container.children():
            if hasattr(child, "objectName") and child.objectName() == "right_frame":
                right_frame = child
                break

        if not right_frame or not right_frame.layout():
            return

        # 기존 위젯 제거
        layout = right_frame.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # FilterWidget 추가
        filter_widget = FilterWidget(self, flow_pos=process_index)
        if hasattr(filter_widget, 'set_process_data'):
            filter_widget.set_process_data(process_data)
        layout.addWidget(filter_widget)

    def open_orderby_edit_dialog(self, process_index, process_data):
        """right_frame에 orderby.ui 기반 OrderByWidget을 표시"""
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

        if not right_frame or not right_frame.layout():
            return

        # 기존 위젯 제거
        layout = right_frame.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # OrderByWidget 추가
        orderby_widget = OrderByWidget(parent=self, flow_pos=process_index)
        if hasattr(orderby_widget, 'set_process_data'):
            orderby_widget.set_process_data(process_data)
        layout.addWidget(orderby_widget)

    def open_union_edit_dialog(self, process_index, process_data):
        """right_frame에 union.ui 기반 UnionWidget을 표시"""
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

        if not right_frame or not right_frame.layout():
            return

        # 기존 위젯 제거
        layout = right_frame.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # UnionWidget 추가
        union_widget = UnionWidget(parent=self, flow_pos=process_index)
        if hasattr(union_widget, 'set_process_data'):
            union_widget.set_process_data(process_data)
        layout.addWidget(union_widget)

    def open_join_edit_dialog(self, process_index, process_data):
        """right_frame에 join.ui 기반 JoinWidget을 표시"""
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

        if not right_frame or not right_frame.layout():
            return

        # 기존 위젯 제거
        layout = right_frame.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # JoinWidget 추가
        join_widget = JoinWidget(parent=self, flow_pos=process_index)
        if hasattr(join_widget, 'set_process_data'):
            join_widget.set_process_data(process_data)
        layout.addWidget(join_widget)

    def open_rounding_edit_dialog(self, process_index, process_data):
        """right_frame에 rounding.ui 기반 RoundingWidget을 표시"""
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

        if not right_frame or not right_frame.layout():
            return

        # 기존 위젯 제거
        layout = right_frame.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # RoundingWidget 추가
        rounding_widget = RoundingWidget(parent=self, flow_pos=process_index)
        if hasattr(rounding_widget, 'set_process_data'):
            rounding_widget.set_process_data(process_data)
        layout.addWidget(rounding_widget)

    def on_process_card_clicked(self, process_index, process_type, content, flow_info):
        """프로세스 카드 클릭 시 호출되는 메서드"""
        # 임시 카드 클릭인지 확인
        if self.temp_process_index is not None and process_index == self.temp_process_index:
            # 임시 카드 클릭 시 아무것도 하지 않음
            return
        
        # 임시 카드가 있으면 무조건 삭제 (다른 카드를 클릭했든 아니든)
        original_temp_index = None
        if self.temp_process_index is not None:
            original_temp_index = self.temp_process_index
            self._remove_temp_process_card()
        
        # 프로세스 타입에 따라 편집 다이얼로그 열기
        processes = self.flow_info.get('processes', [])
        
        # 임시 카드가 삭제된 경우 process_index 조정
        if original_temp_index is not None and process_index > original_temp_index:
            # 임시 카드 위치보다 뒤에 있던 카드들은 인덱스가 하나 줄어듦
            adjusted_process_index = process_index - 1
        else:
            adjusted_process_index = process_index
            
        if adjusted_process_index < len(processes):
            process = processes[adjusted_process_index]
            self.current_process = process
            
            # 프로세스 타입 결정 (process_type 또는 type 필드 사용)
            actual_process_type = process.get("process_type") or process.get("type")
            
            self.open_edit_dialog(actual_process_type, adjusted_process_index, process)

    def delete_process(self, process_index):
        """프로세스 삭제"""
        # ConfirmDialog의 confirm 메서드로 삭제 확인
        confirmed = ConfirmDialog.confirm(self, '처리 삭제', '정말 삭제하겠습니까?')
        if not confirmed:
            return
        if not hasattr(self, 'flow_info') or not self.flow_info:
            return
        # 스크롤 위치 저장
        scroll_pos = 0
        if hasattr(self.ui, 'process_list'):
            scroll_pos = self.ui.process_list.verticalScrollBar().value()
        # database.py의 delete_process_from_flow 함수 사용
        project_uuid = self.parent.project_data.get('uuid', '')
        flow_uuid = self.flow_info.get('uuid', '')
        self.flow_info = delete_process_from_flow(project_uuid, flow_uuid, process_index)
        self.set_flow_info(self.flow_info)
        # 스크롤 위치 복원
        if hasattr(self.ui, 'process_list'):
            self.ui.process_list.verticalScrollBar().setValue(scroll_pos)

        right_frame = self.parent.parent.ui.projects_container.findChild(QFrame, 'right_frame')
        if right_frame and right_frame.layout():
            while right_frame.layout().count():
                item = right_frame.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

    def set_process_data(self, process_data):
        """프로세스 데이터를 flow_info에 저장"""
        if not process_data or not hasattr(self, 'flow_info'):
            return
            
        try:
            # 임시 카드가 있으면 제거
            if self.temp_process_index is not None:
                self._remove_temp_process_card()
                
            # 프로세스 데이터를 flow_info에 추가
            processes = self.flow_info.get('processes', [])
            processes.append(process_data)
            self.flow_info['processes'] = processes
            
            # flow.json에 반영
            project_uuid = self.parent.project_data.get('uuid', '')
            flow_uuid = self.flow_info.get('uuid', '')
            flow = get_flow_by_uuid(project_uuid, flow_uuid)
            if flow:
                flow['processes'] = processes
                update_flow(project_uuid, flow)
                
            # UI 업데이트
            self.set_flow_info(self.flow_info)
            
        except Exception as e:
            from src.ui.components.message_dialog import MessageDialog
            MessageDialog.critical(self, "오류", f"프로세스 데이터 저장 중 오류가 발생했습니다: {str(e)}")
