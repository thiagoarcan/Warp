# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'accessibleWidget.ui'
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

class Ui_AccessibleWidget(object):
    def setupUi(self, AccessibleWidget):
        if not AccessibleWidget.objectName():
            AccessibleWidget.setObjectName(u"AccessibleWidget")
        AccessibleWidget.resize(600, 400)
        self.mainLayout = QVBoxLayout(AccessibleWidget)
        self.mainLayout.setObjectName(u"mainLayout")
        self.contentWidget = QWidget(AccessibleWidget)
        self.contentWidget.setObjectName(u"contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName(u"contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(AccessibleWidget)

        QMetaObject.connectSlotsByName(AccessibleWidget)
    # setupUi

    def retranslateUi(self, AccessibleWidget):
        AccessibleWidget.setWindowTitle(QCoreApplication.translate("AccessibleWidget", u"AccessibleWidget", None))
    # retranslateUi

