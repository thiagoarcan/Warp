# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'shortcutsDialog.ui'
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

class Ui_ShortcutsDialog(object):
    def setupUi(self, ShortcutsDialog):
        if not ShortcutsDialog.objectName():
            ShortcutsDialog.setObjectName(u"ShortcutsDialog")
        ShortcutsDialog.resize(600, 400)
        self.mainLayout = QVBoxLayout(ShortcutsDialog)
        self.mainLayout.setObjectName(u"mainLayout")
        self.contentWidget = QWidget(ShortcutsDialog)
        self.contentWidget.setObjectName(u"contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName(u"contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)

        self.buttonBox = QDialogButtonBox(ShortcutsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.mainLayout.addWidget(self.buttonBox)


        self.retranslateUi(ShortcutsDialog)
        self.buttonBox.accepted.connect(ShortcutsDialog.accept)
        self.buttonBox.rejected.connect(ShortcutsDialog.reject)

        QMetaObject.connectSlotsByName(ShortcutsDialog)
    # setupUi

    def retranslateUi(self, ShortcutsDialog):
        ShortcutsDialog.setWindowTitle(QCoreApplication.translate("ShortcutsDialog", u"ShortcutsDialog", None))
    # retranslateUi

