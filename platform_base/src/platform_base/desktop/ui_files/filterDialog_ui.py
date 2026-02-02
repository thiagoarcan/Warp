# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'filterDialog.ui'
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

class Ui_FilterDialog(object):
    def setupUi(self, FilterDialog):
        if not FilterDialog.objectName():
            FilterDialog.setObjectName(u"FilterDialog")
        FilterDialog.resize(600, 400)
        self.mainLayout = QVBoxLayout(FilterDialog)
        self.mainLayout.setObjectName(u"mainLayout")
        self.contentWidget = QWidget(FilterDialog)
        self.contentWidget.setObjectName(u"contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName(u"contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)

        self.buttonBox = QDialogButtonBox(FilterDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.mainLayout.addWidget(self.buttonBox)


        self.retranslateUi(FilterDialog)
        self.buttonBox.accepted.connect(FilterDialog.accept)
        self.buttonBox.rejected.connect(FilterDialog.reject)

        QMetaObject.connectSlotsByName(FilterDialog)
    # setupUi

    def retranslateUi(self, FilterDialog):
        FilterDialog.setWindowTitle(QCoreApplication.translate("FilterDialog", u"FilterDialog", None))
    # retranslateUi

