
################################################################################
## Form generated from reading UI file 'richTooltip.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_RichTooltip:
    def setupUi(self, RichTooltip):
        if not RichTooltip.objectName():
            RichTooltip.setObjectName("RichTooltip")
        RichTooltip.resize(600, 400)
        self.mainLayout = QVBoxLayout(RichTooltip)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(RichTooltip)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(RichTooltip)

        QMetaObject.connectSlotsByName(RichTooltip)
    # setupUi

    def retranslateUi(self, RichTooltip):
        RichTooltip.setWindowTitle(QCoreApplication.translate("RichTooltip", "RichTooltip", None))
    # retranslateUi

