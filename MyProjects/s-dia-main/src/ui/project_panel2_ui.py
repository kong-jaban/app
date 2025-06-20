# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'project_panel2.ui'
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
    QScrollArea, QSizePolicy, QTextEdit, QWidget)

class Ui_ProjectMenuPanel(object):
    def setupUi(self, ProjectMenuPanel):
        if not ProjectMenuPanel.objectName():
            ProjectMenuPanel.setObjectName(u"ProjectMenuPanel")
        ProjectMenuPanel.resize(238, 698)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ProjectMenuPanel.sizePolicy().hasHeightForWidth())
        ProjectMenuPanel.setSizePolicy(sizePolicy)
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
"    min-height: 100px;\n"
"}\n"
"QTextEdit#desc_text {\n"
"    color: #e9ecef;\n"
"    background: transparent;\n"
"    border: none;\n"
"    padding: 0px;\n"
"    margin: 0px;\n"
"    min-height: 100px;\n"
"}\n"
"QFrame#data_section, QFrame#flow_section {\n"
"    background-color: #495057;\n"
"    border-radius: 6px;\n"
"    border: 1px solid #adb5bd;\n"
"    margin-top: 8px;\n"
"    min-height: 150px;\n"
"}\n"
"QLabel#data_label, QLabel#flow_label {\n"
"    font-size: 14px; \n"
"    font-weight: bold; \n"
"    color: white; \n"
"    padding: 0px;\n"
"    margin: 0px;\n"
"}\n"
"QPushButton#data_add_btn, QPushButton#flow_add_btn {\n"
"    border: none;\n"
"    background-color: "
                        "transparent;\n"
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
"QScrollArea QWidget#desc_container {\n"
"    background: transparent;\n"
""
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
"    background: transparent;\n"
"    width: 6px;\n"
"    margin: 1px 1px 1px 1px;\n"
"}\n"
"QScrollBar::handle:vertical {\n"
"    background: #6c757d;\n"
"    border-radius: 3px;\n"
"    min-height: 20px;\n"
"}\n"
"QScrollBar::handle:vertical:hover {\n"
"    background: #868e96;\n"
"}\n"
"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {\n"
"    height: 0px;\n"
"}\n"
"QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
"    background: transparent;\n"
"}\n"
"")
        self.project_section = QFrame(ProjectMenuPanel)
        self.project_section.setObjectName(u"project_section")
        self.project_section.setGeometry(QRect(8, 20, 222, 252))
        self.project_section.setFrameShape(QFrame.Shape.Panel)
        self.project_section.setFrameShadow(QFrame.Shadow.Plain)
        self.project_section.setLineWidth(0)
        self.horizontalLayoutWidget = QWidget(self.project_section)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(0, 0, 221, 31))
        self.project_name_header = QHBoxLayout(self.horizontalLayoutWidget)
        self.project_name_header.setSpacing(0)
        self.project_name_header.setObjectName(u"project_name_header")
        self.project_name_header.setContentsMargins(0, 0, 0, 4)
        self.project_name_label_layout = QHBoxLayout()
        self.project_name_label_layout.setSpacing(5)
        self.project_name_label_layout.setObjectName(u"project_name_label_layout")
        self.project_name_label_layout.setContentsMargins(4, -1, -1, 0)
        self.project_name = QLabel(self.horizontalLayoutWidget)
        self.project_name.setObjectName(u"project_name")
        self.project_name.setEnabled(True)
        font = QFont()
        font.setBold(True)
        self.project_name.setFont(font)

        self.project_name_label_layout.addWidget(self.project_name)


        self.project_name_header.addLayout(self.project_name_label_layout)

        self.project_box = QFrame(self.project_section)
        self.project_box.setObjectName(u"project_box")
        self.project_box.setGeometry(QRect(0, 30, 218, 216))
        self.project_box.setFrameShape(QFrame.Shape.Panel)
        self.project_box.setFrameShadow(QFrame.Shadow.Plain)
        self.desc_scroll = QScrollArea(self.project_box)
        self.desc_scroll.setObjectName(u"desc_scroll")
        self.desc_scroll.setGeometry(QRect(5, 5, 208, 198))
        self.desc_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.desc_scroll.setFrameShadow(QFrame.Shadow.Plain)
        self.desc_scroll.setWidgetResizable(True)
        self.desc_container = QWidget()
        self.desc_container.setObjectName(u"desc_container")
        self.desc_container.setGeometry(QRect(0, 0, 208, 198))
        self.desc_container.setStyleSheet(u"background: transparent;")
        self.desc_text = QTextEdit(self.desc_container)
        self.desc_text.setObjectName(u"desc_text")
        self.desc_text.setGeometry(QRect(4, 4, 200, 190))
        self.desc_text.setFrameShape(QFrame.Shape.NoFrame)
        self.desc_text.setFrameShadow(QFrame.Shadow.Plain)
        self.desc_text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.desc_text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.desc_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.desc_scroll.setWidget(self.desc_container)
        self.project_section_2 = QFrame(ProjectMenuPanel)
        self.project_section_2.setObjectName(u"project_section_2")
        self.project_section_2.setGeometry(QRect(10, 280, 222, 252))
        self.project_section_2.setFrameShape(QFrame.Shape.Panel)
        self.project_section_2.setFrameShadow(QFrame.Shadow.Plain)
        self.project_section_2.setLineWidth(0)
        self.horizontalLayoutWidget_2 = QWidget(self.project_section_2)
        self.horizontalLayoutWidget_2.setObjectName(u"horizontalLayoutWidget_2")
        self.horizontalLayoutWidget_2.setGeometry(QRect(0, 0, 221, 31))
        self.project_name_header_2 = QHBoxLayout(self.horizontalLayoutWidget_2)
        self.project_name_header_2.setSpacing(0)
        self.project_name_header_2.setObjectName(u"project_name_header_2")
        self.project_name_header_2.setContentsMargins(0, 0, 0, 4)
        self.project_name_label_layout_2 = QHBoxLayout()
        self.project_name_label_layout_2.setSpacing(5)
        self.project_name_label_layout_2.setObjectName(u"project_name_label_layout_2")
        self.project_name_label_layout_2.setContentsMargins(4, -1, -1, 0)
        self.project_name_2 = QLabel(self.horizontalLayoutWidget_2)
        self.project_name_2.setObjectName(u"project_name_2")
        self.project_name_2.setEnabled(True)
        self.project_name_2.setFont(font)

        self.project_name_label_layout_2.addWidget(self.project_name_2)


        self.project_name_header_2.addLayout(self.project_name_label_layout_2)

        self.project_box_2 = QFrame(self.project_section_2)
        self.project_box_2.setObjectName(u"project_box_2")
        self.project_box_2.setGeometry(QRect(0, 30, 218, 216))
        self.project_box_2.setFrameShape(QFrame.Shape.Panel)
        self.project_box_2.setFrameShadow(QFrame.Shadow.Plain)
        self.desc_scroll_2 = QScrollArea(self.project_box_2)
        self.desc_scroll_2.setObjectName(u"desc_scroll_2")
        self.desc_scroll_2.setGeometry(QRect(5, 5, 208, 198))
        self.desc_scroll_2.setFrameShape(QFrame.Shape.NoFrame)
        self.desc_scroll_2.setFrameShadow(QFrame.Shadow.Plain)
        self.desc_scroll_2.setWidgetResizable(True)
        self.desc_container_2 = QWidget()
        self.desc_container_2.setObjectName(u"desc_container_2")
        self.desc_container_2.setGeometry(QRect(0, 0, 208, 198))
        self.desc_container_2.setStyleSheet(u"background: transparent;")
        self.desc_text_2 = QTextEdit(self.desc_container_2)
        self.desc_text_2.setObjectName(u"desc_text_2")
        self.desc_text_2.setGeometry(QRect(4, 4, 200, 190))
        self.desc_text_2.setFrameShape(QFrame.Shape.NoFrame)
        self.desc_text_2.setFrameShadow(QFrame.Shadow.Plain)
        self.desc_text_2.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.desc_text_2.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.desc_text_2.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.desc_scroll_2.setWidget(self.desc_container_2)

        self.retranslateUi(ProjectMenuPanel)

        QMetaObject.connectSlotsByName(ProjectMenuPanel)
    # setupUi

    def retranslateUi(self, ProjectMenuPanel):
        ProjectMenuPanel.setWindowTitle("")
        self.project_name.setText(QCoreApplication.translate("ProjectMenuPanel", u"\ud504\ub85c\uc81d\ud2b8 \uc774\ub984", None))
        self.project_name_2.setText(QCoreApplication.translate("ProjectMenuPanel", u"\ud504\ub85c\uc81d\ud2b8 \uc774\ub984", None))
    # retranslateUi

