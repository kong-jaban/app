from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QApplication, QStyle, QSizePolicy
from PySide6.QtCore import Qt

class ConfirmDialog(QDialog):
    ICONS = {
        'question': QStyle.SP_MessageBoxQuestion,
        'warning': QStyle.SP_MessageBoxWarning,
        'critical': QStyle.SP_MessageBoxCritical,
        'information': QStyle.SP_MessageBoxInformation,
    }

    def __init__(self, parent=None, title="확인", message="", icon_type="question", buttons=("예", "아니오")):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setStyleSheet("""
        QDialog {
            background: #232323;
            color: #fff;
            border-radius: 8px;
        }
        QLabel {
            color: #fff;
            font-size: 12px;
            background-color: #232323;
        }
        QPushButton {
            min-width: 50px;
            min-height: 16px;
            border-radius: 6px;
            background: #2d2d2d;
            color: #fff;
            font-size: 12px;
            border: none;
            margin: 0 8px;
        }
        QPushButton:focus {
            border: 1px solid orange;
        }
        QPushButton:hover {
            background: #444;
        }
        QPushButton:disabled {
            background: #444;
            color: #888;
        }
        """)
        layout = QVBoxLayout(self)
        msg_layout = QHBoxLayout()
        # 아이콘
        icon_enum = self.ICONS.get(icon_type, QStyle.SP_MessageBoxQuestion)
        icon = QApplication.style().standardIcon(icon_enum)
        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(32, 32))
        msg_layout.addWidget(icon_label, alignment=Qt.AlignTop)
        # 메시지
        label = QLabel(message)
        label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        label.setWordWrap(True)
        label.setMinimumWidth(300)
        label.setMaximumWidth(500)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        msg_layout.addWidget(label)
        layout.addLayout(msg_layout)
        # 버튼
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignRight)
        self._btns = []
        for btn_text in buttons:
            btn = QPushButton(btn_text)
            btn.clicked.connect(self.accept if btn_text == "예" else self.reject)
            btn_layout.addWidget(btn)
            self._btns.append(btn)
        layout.addLayout(btn_layout)
        self.adjustSize()
        self.setFixedSize(self.size())  # 크기 고정

    @classmethod
    def confirm(cls, parent, title, message):
        dlg = cls(parent, title, message, icon_type="question", buttons=("예", "아니오"))
        result = dlg.exec_()
        return result == QDialog.Accepted 