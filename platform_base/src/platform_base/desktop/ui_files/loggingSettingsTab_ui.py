
################################################################################
## Form generated from reading UI file 'loggingSettingsTab.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_LoggingSettingsTab:
    def setupUi(self, LoggingSettingsTab):
        if not LoggingSettingsTab.objectName():
            LoggingSettingsTab.setObjectName("LoggingSettingsTab")
        LoggingSettingsTab.resize(600, 400)
        self.mainLayout = QVBoxLayout(LoggingSettingsTab)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(LoggingSettingsTab)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(LoggingSettingsTab)

        QMetaObject.connectSlotsByName(LoggingSettingsTab)
    # setupUi

    def retranslateUi(self, LoggingSettingsTab):
        LoggingSettingsTab.setWindowTitle(QCoreApplication.translate("LoggingSettingsTab", "LoggingSettingsTab", None))
    # retranslateUi

