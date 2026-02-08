
################################################################################
## Form generated from reading UI file 'lowpassFilter.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_LowpassFilter:
    def setupUi(self, LowpassFilter):
        if not LowpassFilter.objectName():
            LowpassFilter.setObjectName("LowpassFilter")
        LowpassFilter.resize(600, 400)
        self.mainLayout = QVBoxLayout(LowpassFilter)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(LowpassFilter)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(LowpassFilter)

        QMetaObject.connectSlotsByName(LowpassFilter)
    # setupUi

    def retranslateUi(self, LowpassFilter):
        LowpassFilter.setWindowTitle(QCoreApplication.translate("LowpassFilter", "LowpassFilter", None))
    # retranslateUi

