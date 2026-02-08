
################################################################################
## Form generated from reading UI file 'interpolationConfigWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_InterpolationConfigWidget:
    def setupUi(self, InterpolationConfigWidget):
        if not InterpolationConfigWidget.objectName():
            InterpolationConfigWidget.setObjectName("InterpolationConfigWidget")
        InterpolationConfigWidget.resize(600, 400)
        self.mainLayout = QVBoxLayout(InterpolationConfigWidget)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(InterpolationConfigWidget)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(InterpolationConfigWidget)

        QMetaObject.connectSlotsByName(InterpolationConfigWidget)
    # setupUi

    def retranslateUi(self, InterpolationConfigWidget):
        InterpolationConfigWidget.setWindowTitle(QCoreApplication.translate("InterpolationConfigWidget", "InterpolationConfigWidget", None))
    # retranslateUi

