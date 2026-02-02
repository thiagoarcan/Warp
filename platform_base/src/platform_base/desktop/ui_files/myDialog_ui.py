# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'myDialog.ui'
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

class Ui_MyDialog(object):
    def setupUi(self, MyDialog):
        if not MyDialog.objectName():
            MyDialog.setObjectName(u"MyDialog")
        MyDialog.resize(600, 400)
        self.mainLayout = QVBoxLayout(MyDialog)
        self.mainLayout.setObjectName(u"mainLayout")
        self.contentWidget = QWidget(MyDialog)
        self.contentWidget.setObjectName(u"contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName(u"contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)

        self.buttonBox = QDialogButtonBox(MyDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.mainLayout.addWidget(self.buttonBox)


        self.retranslateUi(MyDialog)
        self.buttonBox.accepted.connect(MyDialog.accept)
        self.buttonBox.rejected.connect(MyDialog.reject)

        QMetaObject.connectSlotsByName(MyDialog)
    # setupUi

    def retranslateUi(self, MyDialog):
        MyDialog.setWindowTitle(QCoreApplication.translate("MyDialog", u"MyDialog", None))
    # retranslateUi

