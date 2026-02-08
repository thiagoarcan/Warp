
################################################################################
## Form generated from reading UI file 'generalSettingsTab.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_GeneralSettingsTab:
    def setupUi(self, GeneralSettingsTab):
        if not GeneralSettingsTab.objectName():
            GeneralSettingsTab.setObjectName("GeneralSettingsTab")
        GeneralSettingsTab.resize(600, 400)
        self.mainLayout = QVBoxLayout(GeneralSettingsTab)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(GeneralSettingsTab)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(GeneralSettingsTab)

        QMetaObject.connectSlotsByName(GeneralSettingsTab)
    # setupUi

    def retranslateUi(self, GeneralSettingsTab):
        GeneralSettingsTab.setWindowTitle(QCoreApplication.translate("GeneralSettingsTab", "GeneralSettingsTab", None))
    # retranslateUi

