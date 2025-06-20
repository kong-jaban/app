# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'project_panel.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QTextEdit, QVBoxLayout,
    QWidget)
import s-dia_rc

class Ui_ProjectMenuPanel(object):
    def setupUi(self, ProjectMenuPanel):
        if not ProjectMenuPanel.objectName():
            ProjectMenuPanel.setObjectName(u"ProjectMenuPanel")
        ProjectMenuPanel.resize(238, 698)
        ProjectMenuPanel.setAutoFillBackground(False)
        ProjectMenuPanel.setStyleSheet(u"QWidget {\n"
"    background-color: #212529;\n"
"}\n"
"QLabel#project_name {\n"
"    font-size: 14px; \n"
"    font-weight: bold; \n"
"    color: white; \n"
"    padding-bottom: 0px;\n"
"}\n"
"QFrame#desc_box {\n"
"    background-color: #495057;\n"
"    border-radius: 6px;\n"
"    border: 1px solid #adb5bd;\n"
"    margin-top: 8px;\n"
"    min-height: 90px;\n"
"    max-height: 150px;\n"
"}\n"
"QTextEdit#desc_text {\n"
"    color: #e9ecef;\n"
"    background: transparent;\n"
"    border: none;\n"
"    padding: 0px;\n"
"    margin: 0px;\n"
"    min-height: 90px;\n"
"    max-height: 150px;\n"
"}\n"
"QFrame#data_section, QFrame#flow_section {\n"
"    background-color: #495057;\n"
"    border-radius: 6px;\n"
"    border: 1px solid #adb5bd;\n"
"    margin-top: 8px;\n"
"    height: 100px;\n"
"}\n"
"QLabel#data_label, QLabel#flow_label {\n"
"    font-size: 14px; \n"
"    font-weight: bold; \n"
"    color: white; \n"
"    padding: 0px;\n"
"    margin: 0px;\n"
"}\n"
"QPushButton#data_add_btn, QPushButton#flow_add_btn {\n"
""
                        "    border: none;\n"
"    background-color: transparent;\n"
"    padding: 0px;\n"
"    margin: 0px;\n"
"    margin-top: 2px;\n"
"}\n"
"QFrame#data_list_container, QFrame#flow_list_container {\n"
"    background-color: #343a40;\n"
"    border: 1px solid #adb5bd;\n"
"    border-radius: 4px;\n"
"    min-height: 120px;\n"
"}\n"
"QLabel#no_data_label, QLabel#no_flow_label {\n"
"    color: #adb5bd;\n"
"    font-style: italic;\n"
"    font-size: 12px;\n"
"}\n"
"QPushButton#close_btn {\n"
"    background-color: #6c757d;\n"
"    padding: 8px;\n"
"    border-radius: 6px;\n"
"    text-align: center;\n"
"    font-size: 16px;\n"
"    font-weight: bold;\n"
"    border: 1px solid #adb5bd;\n"
"    color: white;\n"
"    min-height: 32px;\n"
"}\n"
"QPushButton#close_btn:hover {\n"
"    background-color: #868e96;\n"
"    border-color: #ced4da;\n"
"}\n"
"QScrollArea {\n"
"    border: none;\n"
"    background: transparent;\n"
"    border-radius: 6px;\n"
"    padding: 0px;\n"
"    margin: 0px;\n"
"}\n"
"QScrollArea QWidget#desc_con"
                        "tainer {\n"
"    background: transparent;\n"
"    border-radius: 6px;\n"
"    padding: 0px;\n"
"    margin: 0px;\n"
"}\n"
"QScrollArea QFrame {\n"
"    border: 1px solid #adb5bd;\n"
"    border-radius: 6px;\n"
"    background-color: #495057;\n"
"    padding: 0px;\n"
"    margin: 0px;\n"
"}\n"
"QScrollBar:vertical {\n"
"    border: none;\n"
"    background: #495057;\n"
"    width: 8px;\n"
"    margin: 0px;\n"
"    position: absolute;\n"
"    right: 0px;\n"
"}\n"
"QScrollBar::handle:vertical {\n"
"    background: #adb5bd;\n"
"    border-radius: 4px;\n"
"    min-height: 20px;\n"
"}\n"
"QScrollBar::handle:vertical:hover {\n"
"    background: #ced4da;\n"
"}\n"
"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {\n"
"    height: 0px;\n"
"}\n"
"QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
"    background: transparent;\n"
"}\n"
"")
        self.menu_layout = QVBoxLayout(ProjectMenuPanel)
        self.menu_layout.setSpacing(8)
        self.menu_layout.setObjectName(u"menu_layout")
        self.menu_layout.setContentsMargins(8, 20, 8, 16)
        self.project_section = QFrame(ProjectMenuPanel)
        self.project_section.setObjectName(u"project_section")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.project_section.sizePolicy().hasHeightForWidth())
        self.project_section.setSizePolicy(sizePolicy)
        self.project_section.setFrameShape(QFrame.Shape.Panel)
        self.project_section.setFrameShadow(QFrame.Shadow.Plain)
        self.project_section.setLineWidth(0)
        self.project_name_layout = QVBoxLayout(self.project_section)
        self.project_name_layout.setSpacing(0)
        self.project_name_layout.setObjectName(u"project_name_layout")
        self.project_name_layout.setContentsMargins(0, 4, 4, 4)
        self.project_name_header = QHBoxLayout()
        self.project_name_header.setSpacing(0)
        self.project_name_header.setObjectName(u"project_name_header")
        self.project_name_header.setContentsMargins(-1, -1, -1, 4)
        self.project_name_label_layout = QHBoxLayout()
        self.project_name_label_layout.setSpacing(5)
        self.project_name_label_layout.setObjectName(u"project_name_label_layout")
        self.project_name_label_layout.setContentsMargins(4, -1, -1, -1)
        self.project_name = QLabel(self.project_section)
        self.project_name.setObjectName(u"project_name")
        font = QFont()
        font.setBold(True)
        self.project_name.setFont(font)

        self.project_name_label_layout.addWidget(self.project_name)


        self.project_name_header.addLayout(self.project_name_label_layout)


        self.project_name_layout.addLayout(self.project_name_header)

        self.project_box = QFrame(self.project_section)
        self.project_box.setObjectName(u"project_box")
        self.project_box.setMinimumSize(QSize(0, 90))
        self.project_box.setMaximumSize(QSize(16777215, 150))
        self.project_box.setStyleSheet(u"")
        self.project_box.setFrameShape(QFrame.Shape.Panel)
        self.project_box.setFrameShadow(QFrame.Shadow.Plain)
        self.desc_layout = QVBoxLayout(self.project_box)
        self.desc_layout.setSpacing(0)
        self.desc_layout.setObjectName(u"desc_layout")
        self.desc_layout.setContentsMargins(4, 4, 4, 12)
        self.desc_scroll = QScrollArea(self.project_box)
        self.desc_scroll.setObjectName(u"desc_scroll")
        self.desc_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.desc_scroll.setFrameShadow(QFrame.Shadow.Plain)
        self.desc_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.desc_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.desc_scroll.setWidgetResizable(True)
        self.desc_container = QWidget()
        self.desc_container.setObjectName(u"desc_container")
        self.desc_container.setGeometry(QRect(0, 0, 208, 132))
        self.desc_container.setStyleSheet(u"background: transparent;")
        self.desc_container_layout = QVBoxLayout(self.desc_container)
        self.desc_container_layout.setSpacing(0)
        self.desc_container_layout.setObjectName(u"desc_container_layout")
        self.desc_container_layout.setContentsMargins(4, 4, 4, 4)
        self.desc_text = QTextEdit(self.desc_container)
        self.desc_text.setObjectName(u"desc_text")
        self.desc_text.setMinimumSize(QSize(0, 90))
        self.desc_text.setMaximumSize(QSize(16777215, 150))
        self.desc_text.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.desc_text.setStyleSheet(u"\n"
"                 QTextEdit {\n"
"                     color: #e9ecef;\n"
"                     background: transparent;\n"
"                     border: none;\n"
"                     padding: 0px;\n"
"                     margin: 0px;\n"
"                 }\n"
"                 QScrollBar:vertical {\n"
"                     border: none;\n"
"                     background: #495057;\n"
"                     width: 8px;\n"
"                     margin: 0px;\n"
"                     position: absolute;\n"
"                     right: 0px;\n"
"                 }\n"
"                 QScrollBar::handle:vertical {\n"
"                     background: #adb5bd;\n"
"                     border-radius: 4px;\n"
"                     min-height: 20px;\n"
"                 }\n"
"                 QScrollBar::handle:vertical:hover {\n"
"                     background: #ced4da;\n"
"                 }\n"
"                 QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {\n"
"                     height: 0p"
                        "x;\n"
"                 }\n"
"                 QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
"                     background: transparent;\n"
"                 }\n"
"                ")
        self.desc_text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.desc_text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.desc_container_layout.addWidget(self.desc_text)

        self.desc_scroll.setWidget(self.desc_container)

        self.desc_layout.addWidget(self.desc_scroll)


        self.project_name_layout.addWidget(self.project_box)


        self.menu_layout.addWidget(self.project_section)

        self.data_section = QFrame(ProjectMenuPanel)
        self.data_section.setObjectName(u"data_section")
        sizePolicy.setHeightForWidth(self.data_section.sizePolicy().hasHeightForWidth())
        self.data_section.setSizePolicy(sizePolicy)
        self.data_section.setFrameShape(QFrame.Shape.Panel)
        self.data_section.setFrameShadow(QFrame.Shadow.Plain)
        self.data_section.setLineWidth(0)
        self.data_layout = QVBoxLayout(self.data_section)
        self.data_layout.setSpacing(0)
        self.data_layout.setObjectName(u"data_layout")
        self.data_layout.setContentsMargins(0, 4, 4, 4)
        self.data_header = QHBoxLayout()
        self.data_header.setSpacing(0)
        self.data_header.setObjectName(u"data_header")
        self.data_header.setContentsMargins(-1, -1, -1, 4)
        self.label_layout = QHBoxLayout()
        self.label_layout.setSpacing(5)
        self.label_layout.setObjectName(u"label_layout")
        self.label_layout.setContentsMargins(4, -1, -1, -1)
        self.data_label = QLabel(self.data_section)
        self.data_label.setObjectName(u"data_label")
        self.data_label.setFont(font)

        self.label_layout.addWidget(self.data_label)

        self.data_add_btn = QPushButton(self.data_section)
        self.data_add_btn.setObjectName(u"data_add_btn")
        self.data_add_btn.setIconSize(QSize(14, 14))
        self.data_add_btn.setProperty(u"fixedSize", QSize(18, 18))

        self.label_layout.addWidget(self.data_add_btn)


        self.data_header.addLayout(self.label_layout)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.data_header.addItem(self.horizontalSpacer)


        self.data_layout.addLayout(self.data_header)

        self.data_scroll = QScrollArea(self.data_section)
        self.data_scroll.setObjectName(u"data_scroll")
        self.data_scroll.setMinimumSize(QSize(0, 100))
        self.data_scroll.setMaximumSize(QSize(16777215, 100))
        self.data_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.data_scroll.setFrameShadow(QFrame.Shadow.Plain)
        self.data_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.data_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.data_scroll.setWidgetResizable(True)
        self.data_list_container = QFrame()
        self.data_list_container.setObjectName(u"data_list_container")
        self.data_list_container.setGeometry(QRect(0, 0, 208, 122))
        self.data_list_container.setFrameShape(QFrame.Shape.Panel)
        self.data_list_container.setFrameShadow(QFrame.Shadow.Plain)
        self.data_list_layout = QVBoxLayout(self.data_list_container)
        self.data_list_layout.setSpacing(6)
        self.data_list_layout.setObjectName(u"data_list_layout")
        self.data_list_layout.setContentsMargins(8, 8, 8, 8)
        self.data_list = QListWidget(self.data_list_container)
        self.data_list.setObjectName(u"data_list")
        self.data_list.setStyleSheet(u"\n"
"              QListWidget {\n"
"                  background: transparent;\n"
"                  border: none;\n"
"                  color: #e9ecef;\n"
"              }\n"
"              QListWidget::item {\n"
"                  padding: 4px;\n"
"                  border-radius: 4px;\n"
"              }\n"
"              QListWidget::item:selected, QListWidget::item:hover {\n"
"                  background: #6c757d;\n"
"              }\n"
"             ")
        self.data_list.setFrameShape(QFrame.Shape.NoFrame)
        self.data_list.setFrameShadow(QFrame.Shadow.Plain)
        self.data_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.data_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.data_list_layout.addWidget(self.data_list)

        self.data_scroll.setWidget(self.data_list_container)

        self.data_layout.addWidget(self.data_scroll)


        self.menu_layout.addWidget(self.data_section)

        self.flow_section = QFrame(ProjectMenuPanel)
        self.flow_section.setObjectName(u"flow_section")
        sizePolicy.setHeightForWidth(self.flow_section.sizePolicy().hasHeightForWidth())
        self.flow_section.setSizePolicy(sizePolicy)
        self.flow_section.setFrameShape(QFrame.Shape.Panel)
        self.flow_section.setFrameShadow(QFrame.Shadow.Plain)
        self.flow_section.setLineWidth(0)
        self.flow_layout = QVBoxLayout(self.flow_section)
        self.flow_layout.setSpacing(0)
        self.flow_layout.setObjectName(u"flow_layout")
        self.flow_layout.setContentsMargins(0, 4, 4, 4)
        self.flow_header = QHBoxLayout()
        self.flow_header.setSpacing(0)
        self.flow_header.setObjectName(u"flow_header")
        self.flow_header.setContentsMargins(-1, -1, -1, 4)
        self.flow_label_layout = QHBoxLayout()
        self.flow_label_layout.setSpacing(5)
        self.flow_label_layout.setObjectName(u"flow_label_layout")
        self.flow_label_layout.setContentsMargins(4, -1, -1, -1)
        self.flow_label = QLabel(self.flow_section)
        self.flow_label.setObjectName(u"flow_label")
        self.flow_label.setFont(font)

        self.flow_label_layout.addWidget(self.flow_label)

        self.flow_add_btn = QPushButton(self.flow_section)
        self.flow_add_btn.setObjectName(u"flow_add_btn")
        self.flow_add_btn.setProperty(u"fixedSize", QSize(18, 18))

        self.flow_label_layout.addWidget(self.flow_add_btn)


        self.flow_header.addLayout(self.flow_label_layout)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.flow_header.addItem(self.horizontalSpacer_2)


        self.flow_layout.addLayout(self.flow_header)

        self.flow_scroll = QScrollArea(self.flow_section)
        self.flow_scroll.setObjectName(u"flow_scroll")
        self.flow_scroll.setMinimumSize(QSize(0, 100))
        self.flow_scroll.setMaximumSize(QSize(16777215, 100))
        self.flow_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.flow_scroll.setFrameShadow(QFrame.Shadow.Plain)
        self.flow_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.flow_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.flow_scroll.setWidgetResizable(True)
        self.flow_list_container = QFrame()
        self.flow_list_container.setObjectName(u"flow_list_container")
        self.flow_list_container.setGeometry(QRect(0, 0, 208, 122))
        self.flow_list_container.setFrameShape(QFrame.Shape.Panel)
        self.flow_list_container.setFrameShadow(QFrame.Shadow.Plain)
        self.flow_list_layout = QVBoxLayout(self.flow_list_container)
        self.flow_list_layout.setSpacing(6)
        self.flow_list_layout.setObjectName(u"flow_list_layout")
        self.flow_list_layout.setContentsMargins(8, 8, 8, 8)
        self.no_flow_label = QLabel(self.flow_list_container)
        self.no_flow_label.setObjectName(u"no_flow_label")
        self.no_flow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.flow_list_layout.addWidget(self.no_flow_label)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.flow_list_layout.addItem(self.verticalSpacer_2)

        self.flow_scroll.setWidget(self.flow_list_container)

        self.flow_layout.addWidget(self.flow_scroll)


        self.menu_layout.addWidget(self.flow_section)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.menu_layout.addItem(self.verticalSpacer)

        self.close_btn = QPushButton(ProjectMenuPanel)
        self.close_btn.setObjectName(u"close_btn")
        self.close_btn.setMinimumSize(QSize(0, 50))
        self.close_btn.setIconSize(QSize(16, 16))

        self.menu_layout.addWidget(self.close_btn)


        self.retranslateUi(ProjectMenuPanel)

        QMetaObject.connectSlotsByName(ProjectMenuPanel)
    # setupUi

    def retranslateUi(self, ProjectMenuPanel):
        self.project_name.setText(QCoreApplication.translate("ProjectMenuPanel", u"\ud504\ub85c\uc81d\ud2b8 \uc774\ub984", None))
        self.desc_text.setPlaceholderText("")
        self.data_label.setText(QCoreApplication.translate("ProjectMenuPanel", u"\ub370\uc774\ud130 \uc18c\uc2a4", None))
        self.flow_label.setText(QCoreApplication.translate("ProjectMenuPanel", u"\ud750\ub984", None))
        self.no_flow_label.setText(QCoreApplication.translate("ProjectMenuPanel", u"\ub4f1\ub85d\ub41c \ud750\ub984\uc774 \uc5c6\uc2b5\ub2c8\ub2e4.", None))
        self.close_btn.setText(QCoreApplication.translate("ProjectMenuPanel", u"\ud504\ub85c\uc81d\ud2b8 \ub2eb\uae30", None))
        pass
    # retranslateUi

