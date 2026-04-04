# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'plot2DWidget.ui'
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

class Ui_Plot2DWidget(object):
    def setupUi(self, Plot2DWidget):
        if not Plot2DWidget.objectName():
            Plot2DWidget.setObjectName(u"Plot2DWidget")
        Plot2DWidget.resize(600, 400)
        self.mainLayout = QVBoxLayout(Plot2DWidget)
        self.mainLayout.setObjectName(u"mainLayout")
        self.contentWidget = QWidget(Plot2DWidget)
        self.contentWidget.setObjectName(u"contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName(u"contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(Plot2DWidget)

        QMetaObject.connectSlotsByName(Plot2DWidget)
    # setupUi

    def retranslateUi(self, Plot2DWidget):
        Plot2DWidget.setWindowTitle(QCoreApplication.translate("Plot2DWidget", u"Plot2DWidget", None))
    # retranslateUi

