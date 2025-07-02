from PySide6.QtWidgets import QHeaderView, QStyleOptionButton, QStyle
from PySide6.QtCore import Qt, QRect, Signal
from PySide6.QtGui import QColor

class CheckBoxHeader(QHeaderView):
    toggled = Signal(bool)

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
        y = center_y - size // 2 
        return QRect(x, y, size, size)

    def mousePressEvent(self, event):
        if self.logicalIndexAt(event.pos()) == 0:
            self.isChecked = not self.isChecked
            self.updateSection(0)
            self.toggled.emit(self.isChecked)
        super().mousePressEvent(event)