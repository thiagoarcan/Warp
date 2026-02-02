# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'previewMode.ui'
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

class Ui_PreviewMode(object):
    def setupUi(self, PreviewMode):
        if not PreviewMode.objectName():
            PreviewMode.setObjectName(u"PreviewMode")
        PreviewMode.resize(600, 400)
        self.mainLayout = QVBoxLayout(PreviewMode)
        self.mainLayout.setObjectName(u"mainLayout")
        self.contentWidget = QWidget(PreviewMode)
        self.contentWidget.setObjectName(u"contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName(u"contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(PreviewMode)

        QMetaObject.connectSlotsByName(PreviewMode)
    # setupUi

    def retranslateUi(self, PreviewMode):
        PreviewMode.setWindowTitle(QCoreApplication.translate("PreviewMode", u"PreviewMode", None))
    # retranslateUi

