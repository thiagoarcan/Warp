
################################################################################
## Form generated from reading UI file 'logWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_LogWidget:
    def setupUi(self, LogWidget):
        if not LogWidget.objectName():
            LogWidget.setObjectName("LogWidget")
        LogWidget.resize(600, 400)
        self.mainLayout = QVBoxLayout(LogWidget)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(LogWidget)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(LogWidget)

        QMetaObject.connectSlotsByName(LogWidget)
    # setupUi

    def retranslateUi(self, LogWidget):
        LogWidget.setWindowTitle(QCoreApplication.translate("LogWidget", "LogWidget", None))
    # retranslateUi

