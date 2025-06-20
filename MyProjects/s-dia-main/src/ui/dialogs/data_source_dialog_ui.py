# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'data_source_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_DataSourceDialog(object):
    def setupUi(self, DataSourceDialog):
        if not DataSourceDialog.objectName():
            DataSourceDialog.setObjectName(u"DataSourceDialog")
        DataSourceDialog.resize(800, 600)
        DataSourceDialog.setMinimumSize(QSize(800, 600))
        DataSourceDialog.setMaximumSize(QSize(800, 600))
        self.centralwidget = QWidget(DataSourceDialog)
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
"QPushButton#save_button {\n"
"    color: #fff;\n"
"    background-color: #80bdff;\n"
"    border-color: #80bdff;\n"
"    font-weight: bold;\n"
"}\n"
"QPushButton#save_button:hover {\n"
"    color: #fff;\n"
"    background-color"
                        ": #80bdff;\n"
"    border-color: #80bdff;\n"
"}\n"
"QPushButton#save_button:pressed {\n"
"    background-color: #80bdff;\n"
"    border-color: #80bdff;\n"
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

        self.horizontalSpacer_4 = QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.name_layout.addItem(self.horizontalSpacer_4)

        self.name_input = QLineEdit(self.name_container)
        self.name_input.setObjectName(u"name_input")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.name_input.sizePolicy().hasHeightForWidth())
        self.name_input.setSizePolicy(sizePolicy)
        self.name_input.setMinimumSize(QSize(600, 38))
        self.name_input.setMaximumSize(QSize(600, 38))

        self.name_layout.addWidget(self.name_input)


        self.verticalLayout_2.addWidget(self.name_container)

        self.data_path_container = QWidget(self.form_container)
        self.data_path_container.setObjectName(u"data_path_container")
        self.desc_layout = QHBoxLayout(self.data_path_container)
        self.desc_layout.setSpacing(2)
        self.desc_layout.setObjectName(u"desc_layout")
        self.desc_layout.setContentsMargins(0, 0, 0, 4)
        self.desc_text = QLabel(self.data_path_container)
        self.desc_text.setObjectName(u"desc_text")
        self.desc_text.setStyleSheet(u"font-size: 16px;\n"
"font-weight: bold;")

        self.desc_layout.addWidget(self.desc_text)

        self.label = QLabel(self.data_path_container)
        self.label.setObjectName(u"label")
        self.label.setStyleSheet(u"color: #dc3545;\n"
"font-size: 16px;\n"
"font-weight: bold;")

        self.desc_layout.addWidget(self.label)

        self.horizontalSpacer_5 = QSpacerItem(32, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.desc_layout.addItem(self.horizontalSpacer_5)

        self.data_path_input = QLineEdit(self.data_path_container)
        self.data_path_input.setObjectName(u"data_path_input")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.data_path_input.sizePolicy().hasHeightForWidth())
        self.data_path_input.setSizePolicy(sizePolicy1)
        self.data_path_input.setMinimumSize(QSize(519, 38))
        self.data_path_input.setMaximumSize(QSize(557, 38))

        self.desc_layout.addWidget(self.data_path_input)

        self.fs_explorer = QPushButton(self.data_path_container)
        self.fs_explorer.setObjectName(u"fs_explorer")
        self.fs_explorer.setMinimumSize(QSize(79, 0))
        self.fs_explorer.setMaximumSize(QSize(79, 16777215))

        self.desc_layout.addWidget(self.fs_explorer)


        self.verticalLayout_2.addWidget(self.data_path_container)

        self.csv_1_container = QWidget(self.form_container)
        self.csv_1_container.setObjectName(u"csv_1_container")
        self.type_layout = QHBoxLayout(self.csv_1_container)
        self.type_layout.setSpacing(2)
        self.type_layout.setObjectName(u"type_layout")
        self.type_layout.setContentsMargins(0, 0, 0, 4)
        self.type_text = QLabel(self.csv_1_container)
        self.type_text.setObjectName(u"type_text")
        self.type_text.setStyleSheet(u"font-size: 16px;\n"
"font-weight: bold;")

        self.type_layout.addWidget(self.type_text)

        self.horizontalSpacer = QSpacerItem(58, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.type_layout.addItem(self.horizontalSpacer)

        self.label_2 = QLabel(self.csv_1_container)
        self.label_2.setObjectName(u"label_2")

        self.type_layout.addWidget(self.label_2)

        self.horizontalSpacer_6 = QSpacerItem(8, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.type_layout.addItem(self.horizontalSpacer_6)

        self.charset_input = QComboBox(self.csv_1_container)
        self.charset_input.addItem("")
        self.charset_input.addItem("")
        self.charset_input.setObjectName(u"charset_input")
        self.charset_input.setMinimumSize(QSize(100, 42))
        self.charset_input.setMaximumSize(QSize(70, 38))
        self.charset_input.setStyleSheet(u"                QComboBox {\n"
"                    background-color: white;\n"
"                    border: 1px solid #dee2e6;\n"
"                    border-radius: 4px;\n"
"                    padding: 5px 10px;\n"
"                    min-height: 30px;\n"
"                    color: #495057;\n"
"                }\n"
"                QComboBox:focus {\n"
"                    border: 1px solid #339af0;\n"
"                }\n"
"                QComboBox::drop-down {\n"
"                    subcontrol-origin: padding;\n"
"                    subcontrol-position: center right;\n"
"                    width: 30px;\n"
"                    border: none;\n"
"                }\n"
"                QComboBox::down-arrow {\n"
"                    image: url(src/ui/resources/images/down-arrow-svgrepo-com.svg);\n"
"                    width: 10px;\n"
"                    height: 10px;\n"
"                    margin-right: 1px;\n"
"                }\n"
"                QComboBox QAbstractItemView {\n"
"                  "
                        "  background-color: white;\n"
"                    border: 1px solid #dee2e6;\n"
"                    border-radius: 4px;\n"
"                    outline: none;\n"
"                    selection-background-color: #e9ecef;\n"
"                    selection-color: #000;\n"
"                }\n"
"                QComboBox QAbstractItemView::item {\n"
"                    padding: 8px 20px;\n"
"                    color: #495057;\n"
"                }\n"
"                QComboBox QAbstractItemView::item:selected {\n"
"                    background-color: #e9ecef;\n"
"                    color: #000;\n"
"                }")
        self.charset_input.setMaxVisibleItems(13)
        self.charset_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        self.type_layout.addWidget(self.charset_input)

        self.type_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.type_layout.addItem(self.type_spacer)


        self.verticalLayout_2.addWidget(self.csv_1_container)

        self.csv_2_container = QWidget(self.form_container)
        self.csv_2_container.setObjectName(u"csv_2_container")
        self.type_layout1 = QHBoxLayout(self.csv_2_container)
        self.type_layout1.setSpacing(2)
        self.type_layout1.setObjectName(u"type_layout1")
        self.type_layout1.setContentsMargins(0, 0, 0, 4)
        self.horizontalSpacer_7 = QSpacerItem(126, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.type_layout1.addItem(self.horizontalSpacer_7)

        self.label_3 = QLabel(self.csv_2_container)
        self.label_3.setObjectName(u"label_3")

        self.type_layout1.addWidget(self.label_3)

        self.horizontalSpacer_8 = QSpacerItem(38, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.type_layout1.addItem(self.horizontalSpacer_8)

        self.separator_input = QComboBox(self.csv_2_container)
        self.separator_input.addItem("")
        self.separator_input.addItem("")
        self.separator_input.addItem("")
        self.separator_input.setObjectName(u"separator_input")
        self.separator_input.setMinimumSize(QSize(100, 42))
        self.separator_input.setMaximumSize(QSize(70, 38))
        self.separator_input.setStyleSheet(u"                QComboBox {\n"
"                    background-color: white;\n"
"                    border: 1px solid #dee2e6;\n"
"                    border-radius: 4px;\n"
"                    padding: 5px 10px;\n"
"                    min-height: 30px;\n"
"                    color: #495057;\n"
"                }\n"
"                QComboBox:focus {\n"
"                    border: 1px solid #339af0;\n"
"                }\n"
"                QComboBox::drop-down {\n"
"                    subcontrol-origin: padding;\n"
"                    subcontrol-position: center right;\n"
"                    width: 30px;\n"
"                    border: none;\n"
"                }\n"
"                QComboBox::down-arrow {\n"
"                    image: url(src/ui/resources/images/down-arrow-svgrepo-com.svg);\n"
"                    width: 10px;\n"
"                    height: 10px;\n"
"                    margin-right: 1px;\n"
"                }\n"
"                QComboBox QAbstractItemView {\n"
"                  "
                        "  background-color: white;\n"
"                    border: 1px solid #dee2e6;\n"
"                    border-radius: 4px;\n"
"                    outline: none;\n"
"                    selection-background-color: #e9ecef;\n"
"                    selection-color: #000;\n"
"                }\n"
"                QComboBox QAbstractItemView::item {\n"
"                    padding: 8px 20px;\n"
"                    color: #495057;\n"
"                }\n"
"                QComboBox QAbstractItemView::item:selected {\n"
"                    background-color: #e9ecef;\n"
"                    color: #000;\n"
"                }")
        self.separator_input.setEditable(False)
        self.separator_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        self.type_layout1.addWidget(self.separator_input)

        self.type_spacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.type_layout1.addItem(self.type_spacer_2)


        self.verticalLayout_2.addWidget(self.csv_2_container)

        self.csv_3_container = QWidget(self.form_container)
        self.csv_3_container.setObjectName(u"csv_3_container")
        self.type_layout2 = QHBoxLayout(self.csv_3_container)
        self.type_layout2.setSpacing(2)
        self.type_layout2.setObjectName(u"type_layout2")
        self.type_layout2.setContentsMargins(0, 0, 0, 4)
        self.horizontalSpacer_10 = QSpacerItem(126, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.type_layout2.addItem(self.horizontalSpacer_10)

        self.label_4 = QLabel(self.csv_3_container)
        self.label_4.setObjectName(u"label_4")

        self.type_layout2.addWidget(self.label_4)

        self.horizontalSpacer_9 = QSpacerItem(24, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.type_layout2.addItem(self.horizontalSpacer_9)

        self.has_header_input = QComboBox(self.csv_3_container)
        self.has_header_input.addItem("")
        self.has_header_input.addItem("")
        self.has_header_input.setObjectName(u"has_header_input")
        self.has_header_input.setMinimumSize(QSize(100, 42))
        self.has_header_input.setMaximumSize(QSize(70, 38))
        self.has_header_input.setStyleSheet(u"                QComboBox {\n"
"                    background-color: white;\n"
"                    border: 1px solid #dee2e6;\n"
"                    border-radius: 4px;\n"
"                    padding: 5px 10px;\n"
"                    min-height: 30px;\n"
"                    color: #495057;\n"
"                }\n"
"                QComboBox:focus {\n"
"                    border: 1px solid #339af0;\n"
"                }\n"
"                QComboBox::drop-down {\n"
"                    subcontrol-origin: padding;\n"
"                    subcontrol-position: center right;\n"
"                    width: 30px;\n"
"                    border: none;\n"
"                }\n"
"                QComboBox::down-arrow {\n"
"                    image: url(src/ui/resources/images/down-arrow-svgrepo-com.svg);\n"
"                    width: 10px;\n"
"                    height: 10px;\n"
"                    margin-right: 1px;\n"
"                }\n"
"                QComboBox QAbstractItemView {\n"
"                  "
                        "  background-color: white;\n"
"                    border: 1px solid #dee2e6;\n"
"                    border-radius: 4px;\n"
"                    outline: none;\n"
"                    selection-background-color: #e9ecef;\n"
"                    selection-color: #000;\n"
"                }\n"
"                QComboBox QAbstractItemView::item {\n"
"                    padding: 8px 20px;\n"
"                    color: #495057;\n"
"                }\n"
"                QComboBox QAbstractItemView::item:selected {\n"
"                    background-color: #e9ecef;\n"
"                    color: #000;\n"
"                }")
        self.has_header_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        self.type_layout2.addWidget(self.has_header_input)

        self.type_spacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.type_layout2.addItem(self.type_spacer_3)


        self.verticalLayout_2.addWidget(self.csv_3_container)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.verticalLayout.addWidget(self.form_container)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_11 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_11)

        self.save_button = QPushButton(self.centralwidget)
        self.save_button.setObjectName(u"save_button")
        self.save_button.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_2.addWidget(self.save_button)

        self.cancel_button = QPushButton(self.centralwidget)
        self.cancel_button.setObjectName(u"cancel_button")
        self.cancel_button.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_2.addWidget(self.cancel_button)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        DataSourceDialog.setCentralWidget(self.centralwidget)

        self.retranslateUi(DataSourceDialog)

        self.charset_input.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(DataSourceDialog)
    # setupUi

    def retranslateUi(self, DataSourceDialog):
        DataSourceDialog.setWindowTitle(QCoreApplication.translate("DataSourceDialog", u"S-DIA - \ub370\uc774\ud130 \uc18c\uc2a4", None))
        self.title_label.setText(QCoreApplication.translate("DataSourceDialog", u"\ub370\uc774\ud130 \uc18c\uc2a4 \ucd94\uac00", None))
        self.name_text.setText(QCoreApplication.translate("DataSourceDialog", u"\ub370\uc774\ud130 \uc18c\uc2a4 \uba85", None))
        self.name_required.setText(QCoreApplication.translate("DataSourceDialog", u"*", None))
        self.name_input.setPlaceholderText(QCoreApplication.translate("DataSourceDialog", u"\ub370\uc774\ud130 \uc18c\uc2a4 \uba85\uc744 \uc785\ub825\ud558\uc138\uc694", None))
        self.desc_text.setText(QCoreApplication.translate("DataSourceDialog", u"\uc6d0\ubcf8 \ub370\uc774\ud0c0", None))
        self.label.setText(QCoreApplication.translate("DataSourceDialog", u"*", None))
        self.fs_explorer.setText(QCoreApplication.translate("DataSourceDialog", u"\ucc3e\uc544\ubcf4\uae30", None))
        self.type_text.setText(QCoreApplication.translate("DataSourceDialog", u"CSV \uc635\uc158", None))
        self.label_2.setText(QCoreApplication.translate("DataSourceDialog", u"\uc6d0\ubcf8\ub370\uc774\ud130", None))
        self.charset_input.setItemText(0, QCoreApplication.translate("DataSourceDialog", u"UTF-8", None))
        self.charset_input.setItemText(1, QCoreApplication.translate("DataSourceDialog", u"EUC-KR", None))

        self.label_3.setText(QCoreApplication.translate("DataSourceDialog", u"\uad6c\ubd84\uc790", None))
        self.separator_input.setItemText(0, QCoreApplication.translate("DataSourceDialog", u",", None))
        self.separator_input.setItemText(1, QCoreApplication.translate("DataSourceDialog", u"TAB", None))
        self.separator_input.setItemText(2, QCoreApplication.translate("DataSourceDialog", u"|", None))

        self.label_4.setText(QCoreApplication.translate("DataSourceDialog", u"\ud5e4\ub354\uc5ec\ubd80", None))
        self.has_header_input.setItemText(0, QCoreApplication.translate("DataSourceDialog", u"\uc788\uc74c", None))
        self.has_header_input.setItemText(1, QCoreApplication.translate("DataSourceDialog", u"\uc5c6\uc74c", None))

        self.save_button.setText(QCoreApplication.translate("DataSourceDialog", u"\uc800\uc7a5", None))
        self.cancel_button.setText(QCoreApplication.translate("DataSourceDialog", u"\ucde8\uc18c", None))
    # retranslateUi

