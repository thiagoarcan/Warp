
################################################################################
## Form generated from reading UI file 'bandpassFilter.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_BandpassFilter:
    def setupUi(self, BandpassFilter):
        if not BandpassFilter.objectName():
            BandpassFilter.setObjectName("BandpassFilter")
        BandpassFilter.resize(600, 400)
        self.mainLayout = QVBoxLayout(BandpassFilter)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(BandpassFilter)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(BandpassFilter)

        QMetaObject.connectSlotsByName(BandpassFilter)
    # setupUi

    def retranslateUi(self, BandpassFilter):
        BandpassFilter.setWindowTitle(QCoreApplication.translate("BandpassFilter", "BandpassFilter", None))
    # retranslateUi

