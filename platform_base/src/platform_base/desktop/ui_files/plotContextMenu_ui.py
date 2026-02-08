
################################################################################
## Form generated from reading UI file 'plotContextMenu.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_PlotContextMenu:
    def setupUi(self, PlotContextMenu):
        if not PlotContextMenu.objectName():
            PlotContextMenu.setObjectName("PlotContextMenu")
        PlotContextMenu.resize(600, 400)
        self.mainLayout = QVBoxLayout(PlotContextMenu)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(PlotContextMenu)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(PlotContextMenu)

        QMetaObject.connectSlotsByName(PlotContextMenu)
    # setupUi

    def retranslateUi(self, PlotContextMenu):
        PlotContextMenu.setWindowTitle(QCoreApplication.translate("PlotContextMenu", "PlotContextMenu", None))
    # retranslateUi

