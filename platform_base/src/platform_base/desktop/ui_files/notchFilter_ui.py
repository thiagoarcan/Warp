
################################################################################
## Form generated from reading UI file 'notchFilter.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_NotchFilter:
    def setupUi(self, NotchFilter):
        if not NotchFilter.objectName():
            NotchFilter.setObjectName("NotchFilter")
        NotchFilter.resize(600, 400)
        self.mainLayout = QVBoxLayout(NotchFilter)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(NotchFilter)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(NotchFilter)

        QMetaObject.connectSlotsByName(NotchFilter)
    # setupUi

    def retranslateUi(self, NotchFilter):
        NotchFilter.setWindowTitle(QCoreApplication.translate("NotchFilter", "NotchFilter", None))
    # retranslateUi

