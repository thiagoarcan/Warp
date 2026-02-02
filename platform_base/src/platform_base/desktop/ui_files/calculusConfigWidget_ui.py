# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'calculusConfigWidget.ui'
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

class Ui_CalculusConfigWidget(object):
    def setupUi(self, CalculusConfigWidget):
        if not CalculusConfigWidget.objectName():
            CalculusConfigWidget.setObjectName(u"CalculusConfigWidget")
        CalculusConfigWidget.resize(600, 400)
        self.mainLayout = QVBoxLayout(CalculusConfigWidget)
        self.mainLayout.setObjectName(u"mainLayout")
        self.contentWidget = QWidget(CalculusConfigWidget)
        self.contentWidget.setObjectName(u"contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName(u"contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(CalculusConfigWidget)

        QMetaObject.connectSlotsByName(CalculusConfigWidget)
    # setupUi

    def retranslateUi(self, CalculusConfigWidget):
        CalculusConfigWidget.setWindowTitle(QCoreApplication.translate("CalculusConfigWidget", u"CalculusConfigWidget", None))
    # retranslateUi

