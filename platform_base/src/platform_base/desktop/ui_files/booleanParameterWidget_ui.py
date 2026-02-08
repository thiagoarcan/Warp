
################################################################################
## Form generated from reading UI file 'booleanParameterWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_BooleanParameterWidget:
    def setupUi(self, BooleanParameterWidget):
        if not BooleanParameterWidget.objectName():
            BooleanParameterWidget.setObjectName("BooleanParameterWidget")
        BooleanParameterWidget.resize(600, 400)
        self.mainLayout = QVBoxLayout(BooleanParameterWidget)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(BooleanParameterWidget)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(BooleanParameterWidget)

        QMetaObject.connectSlotsByName(BooleanParameterWidget)
    # setupUi

    def retranslateUi(self, BooleanParameterWidget):
        BooleanParameterWidget.setWindowTitle(QCoreApplication.translate("BooleanParameterWidget", "BooleanParameterWidget", None))
    # retranslateUi

