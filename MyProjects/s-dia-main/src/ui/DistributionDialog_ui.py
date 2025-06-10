# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DistributionDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QSizePolicy,
    QVBoxLayout, QWidget)
class Ui_DistributionDialog(object):
    def setupUi(self, DistributionDialog):
        if not DistributionDialog.objectName():
            DistributionDialog.setObjectName(u"DistributionDialog")
        DistributionDialog.setStyleSheet(u"\n"
"QDialog#DistributionDialog {\n"
"    background: white;\n"
"}\n"
"QLabel#title_label {\n"
"    color: #1864ab;\n"
"    font-size: 18px;\n"
"    font-weight: bold;\n"
"}\n"
"   ")
        self.verticalLayout = QVBoxLayout(DistributionDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.title_label = QLabel(DistributionDialog)
        self.title_label.setObjectName(u"title_label")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.title_label)

        self.plot_area = QWidget(DistributionDialog)
        self.plot_area.setObjectName(u"plot_area")

        self.verticalLayout.addWidget(self.plot_area)


        self.retranslateUi(DistributionDialog)

        QMetaObject.connectSlotsByName(DistributionDialog)
    # setupUi

    def retranslateUi(self, DistributionDialog):
        DistributionDialog.setWindowTitle(QCoreApplication.translate("DistributionDialog", u"\ub370\uc774\ud130 \ubd84\ud3ec \uc2dc\uac01\ud654", None))
        self.title_label.setText(QCoreApplication.translate("DistributionDialog", u"\uceec\ub7fc \ub370\uc774\ud130 \ubd84\ud3ec", None))
    # retranslateUi

