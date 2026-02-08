
################################################################################
## Form generated from reading UI file 'plot3DWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_Plot3DWidget:
    def setupUi(self, Plot3DWidget):
        if not Plot3DWidget.objectName():
            Plot3DWidget.setObjectName("Plot3DWidget")
        Plot3DWidget.resize(600, 400)
        self.mainLayout = QVBoxLayout(Plot3DWidget)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(Plot3DWidget)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(Plot3DWidget)

        QMetaObject.connectSlotsByName(Plot3DWidget)
    # setupUi

    def retranslateUi(self, Plot3DWidget):
        Plot3DWidget.setWindowTitle(QCoreApplication.translate("Plot3DWidget", "Plot3DWidget", None))
    # retranslateUi

