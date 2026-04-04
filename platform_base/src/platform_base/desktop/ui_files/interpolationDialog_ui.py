# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'interpolationDialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_InterpolationDialog(object):
    def setupUi(self, InterpolationDialog):
        if not InterpolationDialog.objectName():
            InterpolationDialog.setObjectName(u"InterpolationDialog")
        InterpolationDialog.resize(600, 400)
        self.mainLayout = QVBoxLayout(InterpolationDialog)
        self.mainLayout.setObjectName(u"mainLayout")
        self.contentWidget = QWidget(InterpolationDialog)
        self.contentWidget.setObjectName(u"contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName(u"contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)

        self.buttonBox = QDialogButtonBox(InterpolationDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.mainLayout.addWidget(self.buttonBox)


        self.retranslateUi(InterpolationDialog)
        self.buttonBox.accepted.connect(InterpolationDialog.accept)
        self.buttonBox.rejected.connect(InterpolationDialog.reject)

        QMetaObject.connectSlotsByName(InterpolationDialog)
    # setupUi

    def retranslateUi(self, InterpolationDialog):
        InterpolationDialog.setWindowTitle(QCoreApplication.translate("InterpolationDialog", u"InterpolationDialog", None))
    # retranslateUi

