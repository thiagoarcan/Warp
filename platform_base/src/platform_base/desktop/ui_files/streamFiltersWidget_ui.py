# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'streamFiltersWidget.ui'
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

class Ui_StreamFiltersWidget(object):
    def setupUi(self, StreamFiltersWidget):
        if not StreamFiltersWidget.objectName():
            StreamFiltersWidget.setObjectName(u"StreamFiltersWidget")
        StreamFiltersWidget.resize(600, 400)
        self.mainLayout = QVBoxLayout(StreamFiltersWidget)
        self.mainLayout.setObjectName(u"mainLayout")
        self.contentWidget = QWidget(StreamFiltersWidget)
        self.contentWidget.setObjectName(u"contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName(u"contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(StreamFiltersWidget)

        QMetaObject.connectSlotsByName(StreamFiltersWidget)
    # setupUi

    def retranslateUi(self, StreamFiltersWidget):
        StreamFiltersWidget.setWindowTitle(QCoreApplication.translate("StreamFiltersWidget", u"StreamFiltersWidget", None))
    # retranslateUi

