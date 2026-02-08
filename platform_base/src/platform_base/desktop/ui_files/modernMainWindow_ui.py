
################################################################################
## Form generated from reading UI file 'modernMainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QHBoxLayout, QWidget


class Ui_ModernMainWindow:
    def setupUi(self, ModernMainWindow):
        if not ModernMainWindow.objectName():
            ModernMainWindow.setObjectName("ModernMainWindow")
        ModernMainWindow.resize(1920, 1080)
        self.centralwidget = QWidget(ModernMainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralLayout = QHBoxLayout(self.centralwidget)
        self.centralLayout.setObjectName("centralLayout")
        ModernMainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(ModernMainWindow)

        QMetaObject.connectSlotsByName(ModernMainWindow)
    # setupUi

    def retranslateUi(self, ModernMainWindow):
        ModernMainWindow.setWindowTitle(QCoreApplication.translate("ModernMainWindow", "Platform Base v2.0 - An\u00e1lise de S\u00e9ries Temporais", None))
    # retranslateUi

