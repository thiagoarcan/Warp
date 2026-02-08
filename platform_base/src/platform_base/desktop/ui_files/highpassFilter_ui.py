
################################################################################
## Form generated from reading UI file 'highpassFilter.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_HighpassFilter:
    def setupUi(self, HighpassFilter):
        if not HighpassFilter.objectName():
            HighpassFilter.setObjectName("HighpassFilter")
        HighpassFilter.resize(600, 400)
        self.mainLayout = QVBoxLayout(HighpassFilter)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(HighpassFilter)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(HighpassFilter)

        QMetaObject.connectSlotsByName(HighpassFilter)
    # setupUi

    def retranslateUi(self, HighpassFilter):
        HighpassFilter.setWindowTitle(QCoreApplication.translate("HighpassFilter", "HighpassFilter", None))
    # retranslateUi

