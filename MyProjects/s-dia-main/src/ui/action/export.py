import os
from PySide6.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QCheckBox, QAbstractItemView, QHBoxLayout, QHeaderView
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QStyleOptionButton, QStyle, QApplication

class CheckBoxHeader(QHeaderView):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.isChecked = False
        self.setSectionsClickable(True)
        self.setDefaultAlignment(Qt.AlignCenter)

    def paintSection(self, painter, rect, logicalIndex):
        # 배경 그리기
        painter.fillRect(rect, QColor("#f8f9fa"))
        
        # 테두리 그리기
        painter.setPen(QColor("#dee2e6"))
        painter.drawLine(rect.right(), rect.top(), rect.right(), rect.bottom())
        painter.drawLine(rect.left(), rect.bottom(), rect.right(), rect.bottom())
        
        if logicalIndex == 0:
            # 체크박스 그리기
            option = QStyleOptionButton()
            option.rect = self._checkboxRect(rect)
            option.state = QStyle.State_Enabled
            if self.isChecked:
                option.state |= QStyle.State_On
            else:
                option.state |= QStyle.State_Off
            self.style().drawControl(QStyle.CE_CheckBox, option, painter)
        else:
            # 다른 헤더 텍스트 그리기
            text = self.model().headerData(logicalIndex, Qt.Horizontal)
            if text:
                painter.setPen(QColor("#212529"))
                painter.drawText(rect, Qt.AlignCenter, text)

    def _checkboxRect(self, rect):
        size = 20
        # 정확한 중앙 정렬을 위해 rect의 중심점을 기준으로 계산
        center_x = rect.x() + rect.width() // 2
        center_y = rect.y() + rect.height() // 2
        x = center_x - size // 2 + 1
        y = center_y - size // 2 + 1
        return QRect(x, y, size, size)

    def mousePressEvent(self, event):
        if self.logicalIndexAt(event.pos()) == 0:
            rect = self.sectionViewportPosition(0)
            if self._checkboxRect(QRect(rect, 0, self.sectionSize(0), self.height())).contains(event.pos()):
                self.isChecked = not self.isChecked
                self.updateSection(0)
                widget = self.parent()
                if widget is not None:
                    widget = widget.parent()
                if widget is not None and hasattr(widget, 'on_header_checkbox_toggled'):
                    widget.on_header_checkbox_toggled(self.isChecked)
                return
        super().mousePressEvent(event)

class ExportWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        loader = QUiLoader()
        ui_path = os.path.join(os.path.dirname(__file__), 'export.ui')
        loaded = loader.load(ui_path, self)
        self.setLayout(loaded.layout())
        
        # UI 요소 찾기
        self.title_label = self.findChild(QWidget, 'title_label')
        self.export_table = self.findChild(QTableWidget, 'export_table')
        self.save_button = self.findChild(QWidget, 'save_button')
        self.cancel_btn = self.findChild(QWidget, 'cancel_btn')

        self._init_table()
        self._init_events()

    def on_header_checkbox_toggled(self, checked):
        self._toggle_all_checkboxes(checked)

    def _init_table(self):
        table = self.export_table
        table.setRowCount(50)
        table.setColumnCount(3)
        
        # 헤더 설정
        headers = ["", "컬럼명", "설명"]
        for i, header in enumerate(headers):
            table.setHorizontalHeaderItem(i, QTableWidgetItem(header))
        
        # 커스텀 헤더 적용
        self.checkbox_header = CheckBoxHeader(Qt.Horizontal, table)
        table.setHorizontalHeader(self.checkbox_header)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        table.horizontalHeader().setStretchLastSection(True)
        table.setColumnWidth(0, 28)
        
        # row 체크박스: QCheckBox 위젯을 QHBoxLayout에 담아 setCellWidget으로 구현
        self.row_checkboxes = []
        for i in range(50):
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
                    margin-left: 2px;
                }

            """)
            checkbox.stateChanged.connect(self._on_row_checkbox_changed)
            layout.addWidget(checkbox)
            self.row_checkboxes.append(checkbox)
            table.setCellWidget(i, 0, widget)
            table.setItem(i, 1, QTableWidgetItem(f"column_{i+1}"))
            table.setItem(i, 2, QTableWidgetItem(f"설명 {i+1}"))
        
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # 스타일시트 설정
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
                border: none;
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

    def _toggle_all_checkboxes(self, checked):
        for chk in self.row_checkboxes:
            chk.setChecked(checked)

    def _init_events(self):
        if self.save_button:
            self.save_button.clicked.connect(self._on_save_clicked)
        if self.cancel_btn:
            self.cancel_btn.clicked.connect(self._on_cancel_clicked)

    def _on_save_clicked(self):
        # 저장 버튼 클릭 시 처리
        pass

    def _on_cancel_clicked(self):
        # 취소 버튼 클릭 시 처리
        pass

    def _on_row_checkbox_changed(self):
        checked_count = sum(chk.isChecked() for chk in self.row_checkboxes)
        total = len(self.row_checkboxes)
        if checked_count == total:
            self.checkbox_header.isChecked = True
            self.checkbox_header.updateSection(0)
        else:
            self.checkbox_header.isChecked = False
            self.checkbox_header.updateSection(0) 