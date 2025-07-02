from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QApplication, QStyle, QSizePolicy
from PySide6.QtCore import Qt

class MessageDialog(QDialog):
    ICONS = {
        'information': QStyle.SP_MessageBoxInformation,
        'warning': QStyle.SP_MessageBoxWarning,
        'critical': QStyle.SP_MessageBoxCritical,
        'question': QStyle.SP_MessageBoxQuestion,
    }

    def __init__(self, parent=None, title="알림", message="", icon_type="information", buttons=("확인",)):
        super().__init__(None)
        self.setWindowTitle(title)
        self.setObjectName("message_dialog")
        self.setModal(True)
        self.setStyleSheet("""
        QDialog {
            background: #232323;
            color: #fff;
            border-radius: 8px;
        }
        QLabel {
            color: #fff;
            background: #232323;
            font-size: 12px;
        }
        QPushButton {
            min-width: 60px;
            min-height: 24px;
            border-radius: 6px;
            background: #2d2d2d;
            color: #fff;
            font-size: 12px;
            border: none;
            margin: 0 8px;
        }
        QPushButton:focus {
            border: none;
            outline: none;
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
        # 아이콘 (QStyle에서 표준 아이콘 사용)
        icon_enum = self.ICONS.get(icon_type, QStyle.SP_MessageBoxInformation)
        icon = QApplication.style().standardIcon(icon_enum)
        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(32, 32))
        icon_label.setObjectName("message_dialog_icon")
        msg_layout.addWidget(icon_label, alignment=Qt.AlignTop)
        # 메시지
        label = QLabel(message)
        label.setText(message)
        label.setObjectName("message_dialog_label")
        label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        label.setWordWrap(True)
        label.setMinimumWidth(220)
        label.setMaximumWidth(450)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        msg_layout.addWidget(label)
        layout.addLayout(msg_layout)
        # 버튼
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignRight)  # 버튼을 오른쪽에 정렬
        self._btns = []
        for btn_text in buttons:
            btn = QPushButton(btn_text)
            btn.setObjectName("message_dialog_button")
            btn.setFixedHeight(20)
            btn.clicked.connect(self.accept)
            btn_layout.addWidget(btn)
            self._btns.append(btn)
        layout.addLayout(btn_layout)
        self.adjustSize()  # 메시지 길이에 따라 다이얼로그 크기 자동 조정
        self.setFixedSize(self.size())  # 크기 고정

    @classmethod
    def information(cls, parent, title, message):
        dlg = cls(parent, title, message, icon_type="information", buttons=("확인",))
        dlg.exec_()
        return True

    @classmethod
    def warning(cls, parent, title, message):
        dlg = cls(parent, title, message, icon_type="warning", buttons=("확인",))
        dlg.exec_()
        return True

    @classmethod
    def critical(cls, parent, title, message):
        dlg = cls(parent, title, message, icon_type="critical", buttons=("확인",))
        dlg.exec_()
        return True

    @classmethod
    def question(cls, parent, title, message):
        dlg = cls(parent, title, message, icon_type="question", buttons=("예", "아니오"))
        result = dlg.exec_()
        return dlg._btns[0].hasFocus()  # 예(True) or 아니오(False) 