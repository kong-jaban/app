# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Distribution.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QFrame,
    QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_DistributionDialog(object):
    def setupUi(self, DistributionDialog):
        if not DistributionDialog.objectName():
            DistributionDialog.setObjectName(u"DistributionDialog")
        DistributionDialog.resize(800, 600)
        DistributionDialog.setStyleSheet(u"QDialog {\n"
"    background-color: #212529;\n"
"}\n"
"QLabel {\n"
"    color: white;\n"
"    font-size: 14px;\n"
"    font-weight: bold;\n"
"}\n"
"QListWidget {\n"
"    background-color: #adb5bd;\n"
"    border: 1px solid #adb5bd;\n"
"    border-radius: 4px;\n"
"    color: #e9ecef;\n"
"}\n"
"QListWidget::item {\n"
"    padding: 4px;\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: #495057;\n"
"}\n"
"QComboBox {\n"
"    background-color: #adb5bd;\n"
"    border: 1px solid #adb5bd;\n"
"    border-radius: 4px;\n"
"    color: #e9ecef;\n"
"    padding: 4px;\n"
"}\n"
"QComboBox::drop-down {\n"
"    border: none;\n"
"}\n"
"QComboBox::down-arrow {\n"
"    image: url(resources/down_arrow.png);\n"
"    width: 12px;\n"
"    height: 12px;\n"
"}\n"
"QFrame {\n"
"    background-color: #adb5bd;\n"
"    border-radius: 6px;\n"
"    border: 1px solid #adb5bd;\n"
"}\n"
"")
        self.horizontalLayout = QHBoxLayout(DistributionDialog)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.leftPanel = QFrame(DistributionDialog)
        self.leftPanel.setObjectName(u"leftPanel")
        self.leftPanel.setMinimumWidth(200)
        self.leftPanel.setMaximumWidth(300)
        self.leftLayout = QVBoxLayout(self.leftPanel)
        self.leftLayout.setObjectName(u"leftLayout")
        self.columnsLabel = QLabel(self.leftPanel)
        self.columnsLabel.setObjectName(u"columnsLabel")

        self.leftLayout.addWidget(self.columnsLabel)

        self.columnList = QListWidget(self.leftPanel)
        self.columnList.setObjectName(u"columnList")

        self.leftLayout.addWidget(self.columnList)


        self.horizontalLayout.addWidget(self.leftPanel)

        self.rightPanel = QFrame(DistributionDialog)
        self.rightPanel.setObjectName(u"rightPanel")
        self.rightLayout = QVBoxLayout(self.rightPanel)
        self.rightLayout.setObjectName(u"rightLayout")
        self.controlsLayout = QHBoxLayout()
        self.controlsLayout.setObjectName(u"controlsLayout")
        self.chartTypeLabel = QLabel(self.rightPanel)
        self.chartTypeLabel.setObjectName(u"chartTypeLabel")

        self.controlsLayout.addWidget(self.chartTypeLabel)

        self.chartTypeComboBox = QComboBox(self.rightPanel)
        self.chartTypeComboBox.addItem("")
        self.chartTypeComboBox.addItem("")
        self.chartTypeComboBox.addItem("")
        self.chartTypeComboBox.setObjectName(u"chartTypeComboBox")

        self.controlsLayout.addWidget(self.chartTypeComboBox)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.controlsLayout.addItem(self.horizontalSpacer)


        self.rightLayout.addLayout(self.controlsLayout)

        self.plotWidget = QWidget(self.rightPanel)
        self.plotWidget.setObjectName(u"plotWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plotWidget.sizePolicy().hasHeightForWidth())
        self.plotWidget.setSizePolicy(sizePolicy)

        self.rightLayout.addWidget(self.plotWidget)


        self.horizontalLayout.addWidget(self.rightPanel)


        self.retranslateUi(DistributionDialog)

        QMetaObject.connectSlotsByName(DistributionDialog)
    # setupUi

    def retranslateUi(self, DistributionDialog):
        DistributionDialog.setWindowTitle(QCoreApplication.translate("DistributionDialog", u"\uceec\ub7fc \ubd84\ud3ec \ubcf4\uae30", None))
        self.columnsLabel.setText(QCoreApplication.translate("DistributionDialog", u"\uceec\ub7fc \ubaa9\ub85d", None))
        self.chartTypeLabel.setText(QCoreApplication.translate("DistributionDialog", u"\ucc28\ud2b8 \uc720\ud615", None))
        self.chartTypeComboBox.setItemText(0, QCoreApplication.translate("DistributionDialog", u"\ud788\uc2a4\ud1a0\uadf8\ub7a8", None))
        self.chartTypeComboBox.setItemText(1, QCoreApplication.translate("DistributionDialog", u"\ubc15\uc2a4\ud50c\ub86f", None))
        self.chartTypeComboBox.setItemText(2, QCoreApplication.translate("DistributionDialog", u"\ubc14 \ucc28\ud2b8", None))

    # retranslateUi

