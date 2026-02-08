
################################################################################
## Form generated from reading UI file 'autoSaveIndicator.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_AutoSaveIndicator:
    def setupUi(self, AutoSaveIndicator):
        if not AutoSaveIndicator.objectName():
            AutoSaveIndicator.setObjectName("AutoSaveIndicator")
        AutoSaveIndicator.resize(600, 400)
        self.mainLayout = QVBoxLayout(AutoSaveIndicator)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(AutoSaveIndicator)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(AutoSaveIndicator)

        QMetaObject.connectSlotsByName(AutoSaveIndicator)
    # setupUi

    def retranslateUi(self, AutoSaveIndicator):
        AutoSaveIndicator.setWindowTitle(QCoreApplication.translate("AutoSaveIndicator", "AutoSaveIndicator", None))
    # retranslateUi

