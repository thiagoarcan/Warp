
################################################################################
## Form generated from reading UI file 'numericParameterWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_NumericParameterWidget:
    def setupUi(self, NumericParameterWidget):
        if not NumericParameterWidget.objectName():
            NumericParameterWidget.setObjectName("NumericParameterWidget")
        NumericParameterWidget.resize(600, 400)
        self.mainLayout = QVBoxLayout(NumericParameterWidget)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(NumericParameterWidget)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(NumericParameterWidget)

        QMetaObject.connectSlotsByName(NumericParameterWidget)
    # setupUi

    def retranslateUi(self, NumericParameterWidget):
        NumericParameterWidget.setWindowTitle(QCoreApplication.translate("NumericParameterWidget", "NumericParameterWidget", None))
    # retranslateUi

