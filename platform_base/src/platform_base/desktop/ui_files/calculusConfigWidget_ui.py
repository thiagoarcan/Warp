
################################################################################
## Form generated from reading UI file 'calculusConfigWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_CalculusConfigWidget:
    def setupUi(self, CalculusConfigWidget):
        if not CalculusConfigWidget.objectName():
            CalculusConfigWidget.setObjectName("CalculusConfigWidget")
        CalculusConfigWidget.resize(600, 400)
        self.mainLayout = QVBoxLayout(CalculusConfigWidget)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(CalculusConfigWidget)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(CalculusConfigWidget)

        QMetaObject.connectSlotsByName(CalculusConfigWidget)
    # setupUi

    def retranslateUi(self, CalculusConfigWidget):
        CalculusConfigWidget.setWindowTitle(QCoreApplication.translate("CalculusConfigWidget", "CalculusConfigWidget", None))
    # retranslateUi

