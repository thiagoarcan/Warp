
################################################################################
## Form generated from reading UI file 'memoryIndicator.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_MemoryIndicator:
    def setupUi(self, MemoryIndicator):
        if not MemoryIndicator.objectName():
            MemoryIndicator.setObjectName("MemoryIndicator")
        MemoryIndicator.resize(600, 400)
        self.mainLayout = QVBoxLayout(MemoryIndicator)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(MemoryIndicator)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(MemoryIndicator)

        QMetaObject.connectSlotsByName(MemoryIndicator)
    # setupUi

    def retranslateUi(self, MemoryIndicator):
        MemoryIndicator.setWindowTitle(QCoreApplication.translate("MemoryIndicator", "MemoryIndicator", None))
    # retranslateUi

