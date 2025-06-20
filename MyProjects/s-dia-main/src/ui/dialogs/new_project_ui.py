# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'new_project.ui'
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
    QLineEdit, QMainWindow, QPushButton, QSizePolicy,
    QSpacerItem, QTextEdit, QVBoxLayout, QWidget)

class Ui_NewProjectDialog(object):
    def setupUi(self, NewProjectDialog):
        if not NewProjectDialog.objectName():
            NewProjectDialog.setObjectName(u"NewProjectDialog")
        NewProjectDialog.resize(600, 600)
        NewProjectDialog.setMinimumSize(QSize(600, 600))
        NewProjectDialog.setMaximumSize(QSize(600, 600))
        self.centralwidget = QWidget(NewProjectDialog)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"QWidget#centralwidget {\n"
"    background-color: #e9ecef;\n"
"}\n"
"QLabel {\n"
"    color: #000000;\n"
"    font-size: 14px;\n"
"    background-color: transparent;\n"
"}\n"
"QLineEdit, QTextEdit {\n"
"    padding: 8px 12px;\n"
"    border: 1px solid #ced4da;\n"
"    border-radius: 4px;\n"
"    background-color: #ffffff;\n"
"    font-size: 14px;\n"
"    min-height: 20px;\n"
"    color: #495057;\n"
"}\n"
"QLineEdit:focus, QTextEdit:focus {\n"
"    border: 1px solid #80bdff;\n"
"    border-color: #80bdff;\n"
"    outline: 0;\n"
"}\n"
"QPushButton {\n"
"    color: #495057;\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #ced4da;\n"
"    padding: 8px;\n"
"    border-radius: 4px;\n"
"    font-size: 14px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #f8f9fa;\n"
"}\n"
"QPushButton#create_button {\n"
"    color: #fff;\n"
"    background-color: #007bff;\n"
"    border-color: #007bff;\n"
"    /* box-shadow: none; */\n"
"    font-weight: bold;\n"
"}\n"
"QPushButton#create_button:hover {\n"
"    c"
                        "olor: #fff;\n"
"    background-color: #0069d9;\n"
"    border-color: #0062cc;\n"
"}\n"
"QPushButton#create_button:pressed {\n"
"    background-color: #0062cc;\n"
"    border-color: #005cbf;\n"
"}\n"
"QFrame#form_container {\n"
"    background-color: white;\n"
"    border-radius: 8px;\n"
"    border: 1px solid #dee2e6;\n"
"}")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.title_container = QWidget(self.centralwidget)
        self.title_container.setObjectName(u"title_container")
        self.title_container.setStyleSheet(u"background-color: transparent;")
        self.horizontalLayout = QHBoxLayout(self.title_container)
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.title_label = QLabel(self.title_container)
        self.title_label.setObjectName(u"title_label")
        self.title_label.setStyleSheet(u"font-size: 20px;\n"
"font-weight: bold;\n"
"color: #000000;\n"
"background-color: transparent;")

        self.horizontalLayout.addWidget(self.title_label)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_3)


        self.verticalLayout.addWidget(self.title_container)

        self.form_container = QFrame(self.centralwidget)
        self.form_container.setObjectName(u"form_container")
        self.form_container.setFrameShape(QFrame.Shape.StyledPanel)
        self.form_container.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.form_container)
        self.verticalLayout_2.setSpacing(4)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(24, 24, 24, 24)
        self.name_container = QWidget(self.form_container)
        self.name_container.setObjectName(u"name_container")
        self.name_layout = QHBoxLayout(self.name_container)
        self.name_layout.setSpacing(2)
        self.name_layout.setObjectName(u"name_layout")
        self.name_layout.setContentsMargins(0, 0, 0, 4)
        self.name_text = QLabel(self.name_container)
        self.name_text.setObjectName(u"name_text")
        self.name_text.setStyleSheet(u"font-size: 16px;\n"
"font-weight: bold;")

        self.name_layout.addWidget(self.name_text)

        self.name_required = QLabel(self.name_container)
        self.name_required.setObjectName(u"name_required")
        self.name_required.setStyleSheet(u"color: #dc3545;\n"
"font-size: 16px;\n"
"font-weight: bold;")

        self.name_layout.addWidget(self.name_required)

        self.name_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.name_layout.addItem(self.name_spacer)


        self.verticalLayout_2.addWidget(self.name_container)

        self.name_input = QLineEdit(self.form_container)
        self.name_input.setObjectName(u"name_input")

        self.verticalLayout_2.addWidget(self.name_input)

        self.spacer1 = QSpacerItem(20, 12, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_2.addItem(self.spacer1)

        self.data_container = QWidget(self.form_container)
        self.data_container.setObjectName(u"data_container")
        self.data_title_layout = QHBoxLayout(self.data_container)
        self.data_title_layout.setSpacing(2)
        self.data_title_layout.setObjectName(u"data_title_layout")
        self.data_title_layout.setContentsMargins(0, 0, 0, 4)
        self.data_text = QLabel(self.data_container)
        self.data_text.setObjectName(u"data_text")
        self.data_text.setStyleSheet(u"font-size: 16px;\n"
"font-weight: bold;")

        self.data_title_layout.addWidget(self.data_text)

        self.data_required = QLabel(self.data_container)
        self.data_required.setObjectName(u"data_required")
        self.data_required.setStyleSheet(u"color: #dc3545;\n"
"font-size: 16px;\n"
"font-weight: bold;")

        self.data_title_layout.addWidget(self.data_required)

        self.data_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.data_title_layout.addItem(self.data_spacer)


        self.verticalLayout_2.addWidget(self.data_container)

        self.data_layout = QHBoxLayout()
        self.data_layout.setObjectName(u"data_layout")
        self.data_input = QLineEdit(self.form_container)
        self.data_input.setObjectName(u"data_input")

        self.data_layout.addWidget(self.data_input)

        self.browse_button = QPushButton(self.form_container)
        self.browse_button.setObjectName(u"browse_button")
        self.browse_button.setMinimumSize(QSize(80, 0))
        self.browse_button.setMaximumSize(QSize(80, 16777215))

        self.data_layout.addWidget(self.browse_button)


        self.verticalLayout_2.addLayout(self.data_layout)

        self.spacer2 = QSpacerItem(20, 12, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_2.addItem(self.spacer2)

        self.description_label = QLabel(self.form_container)
        self.description_label.setObjectName(u"description_label")
        self.description_label.setStyleSheet(u"font-size: 16px;\n"
"font-weight: bold;\n"
"margin-bottom: 4px;")

        self.verticalLayout_2.addWidget(self.description_label)

        self.description_input = QTextEdit(self.form_container)
        self.description_input.setObjectName(u"description_input")
        self.description_input.setMinimumSize(QSize(0, 38))
        self.description_input.setMaximumSize(QSize(16777215, 400))
        self.description_input.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.verticalLayout_2.addWidget(self.description_input)


        self.verticalLayout.addWidget(self.form_container)

        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(10)
        self.button_layout.setObjectName(u"button_layout")
        self.button_layout.setContentsMargins(-1, 10, -1, -1)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.button_layout.addItem(self.horizontalSpacer)

        self.create_button = QPushButton(self.centralwidget)
        self.create_button.setObjectName(u"create_button")
        self.create_button.setMinimumSize(QSize(80, 0))

        self.button_layout.addWidget(self.create_button)

        self.cancel_button = QPushButton(self.centralwidget)
        self.cancel_button.setObjectName(u"cancel_button")
        self.cancel_button.setMinimumSize(QSize(80, 0))

        self.button_layout.addWidget(self.cancel_button)


        self.verticalLayout.addLayout(self.button_layout)

        NewProjectDialog.setCentralWidget(self.centralwidget)

        self.retranslateUi(NewProjectDialog)
        self.create_button.clicked.connect(NewProjectDialog.accept)
        self.cancel_button.clicked.connect(NewProjectDialog.reject)

        QMetaObject.connectSlotsByName(NewProjectDialog)
    # setupUi

    def retranslateUi(self, NewProjectDialog):
        NewProjectDialog.setWindowTitle(QCoreApplication.translate("NewProjectDialog", u"S-DIA - \uc0c8 \ud504\ub85c\uc81d\ud2b8", None))
        self.title_label.setText(QCoreApplication.translate("NewProjectDialog", u"\uc0c8 \ud504\ub85c\uc81d\ud2b8", None))
        self.name_text.setText(QCoreApplication.translate("NewProjectDialog", u"\ud504\ub85c\uc81d\ud2b8 \uba85", None))
        self.name_required.setText(QCoreApplication.translate("NewProjectDialog", u"*", None))
        self.name_input.setPlaceholderText(QCoreApplication.translate("NewProjectDialog", u"\ud504\ub85c\uc81d\ud2b8 \uba85\uc744 \uc785\ub825\ud558\uc138\uc694", None))
        self.data_text.setText(QCoreApplication.translate("NewProjectDialog", u"\ub370\uc774\ud130 \ud3f4\ub354", None))
        self.data_required.setText(QCoreApplication.translate("NewProjectDialog", u"*", None))
        self.data_input.setPlaceholderText(QCoreApplication.translate("NewProjectDialog", u"\ub370\uc774\ud130 \ud3f4\ub354\ub97c \uc9c0\uc815\ud558\uc138\uc694", None))
        self.browse_button.setText(QCoreApplication.translate("NewProjectDialog", u"\ucc3e\uc544\ubcf4\uae30", None))
        self.description_label.setText(QCoreApplication.translate("NewProjectDialog", u"\ud504\ub85c\uc81d\ud2b8 \uc124\uba85", None))
        self.description_input.setPlaceholderText(QCoreApplication.translate("NewProjectDialog", u"\ud504\ub85c\uc81d\ud2b8 \uc124\uba85\uc744 \uc785\ub825\ud558\uc138\uc694", None))
        self.create_button.setText(QCoreApplication.translate("NewProjectDialog", u"\uc0dd\uc131", None))
        self.cancel_button.setText(QCoreApplication.translate("NewProjectDialog", u"\ucde8\uc18c", None))
    # retranslateUi

