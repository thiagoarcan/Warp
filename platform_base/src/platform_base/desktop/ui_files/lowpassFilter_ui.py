# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'lowpassFilter.ui'
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
from PySide6.QtWidgets import (QApplication, QSizePolicy, QVBoxLayout, QWidget)

class Ui_LowpassFilter(object):
    def setupUi(self, LowpassFilter):
        if not LowpassFilter.objectName():
            LowpassFilter.setObjectName(u"LowpassFilter")
        LowpassFilter.resize(600, 400)
        self.mainLayout = QVBoxLayout(LowpassFilter)
        self.mainLayout.setObjectName(u"mainLayout")
        self.contentWidget = QWidget(LowpassFilter)
        self.contentWidget.setObjectName(u"contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName(u"contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(LowpassFilter)

        QMetaObject.connectSlotsByName(LowpassFilter)
    # setupUi

    def retranslateUi(self, LowpassFilter):
        LowpassFilter.setWindowTitle(QCoreApplication.translate("LowpassFilter", u"LowpassFilter", None))
    # retranslateUi

