# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'previewWidget.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_PreviewWidget(object):
    def setupUi(self, PreviewWidget):
        if not PreviewWidget.objectName():
            PreviewWidget.setObjectName(u"PreviewWidget")
        PreviewWidget.resize(600, 400)
        PreviewWidget.setMinimumSize(QSize(300, 200))
        self.mainLayout = QVBoxLayout(PreviewWidget)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.canvasFrame = QFrame(PreviewWidget)
        self.canvasFrame.setObjectName(u"canvasFrame")
        self.canvasFrame.setFrameShape(QFrame.StyledPanel)
        self.canvasFrame.setFrameShadow(QFrame.Sunken)
        self.canvasLayout = QVBoxLayout(self.canvasFrame)
        self.canvasLayout.setSpacing(0)
        self.canvasLayout.setContentsMargins(0, 0, 0, 0)
        self.canvasLayout.setObjectName(u"canvasLayout")

        self.mainLayout.addWidget(self.canvasFrame)


        self.retranslateUi(PreviewWidget)

        QMetaObject.connectSlotsByName(PreviewWidget)
    # setupUi

    def retranslateUi(self, PreviewWidget):
        PreviewWidget.setWindowTitle(QCoreApplication.translate("PreviewWidget", u"Preview", None))
    # retranslateUi

