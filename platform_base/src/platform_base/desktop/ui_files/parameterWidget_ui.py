
################################################################################
## Form generated from reading UI file 'parameterWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_ParameterWidget:
    def setupUi(self, ParameterWidget):
        if not ParameterWidget.objectName():
            ParameterWidget.setObjectName("ParameterWidget")
        ParameterWidget.resize(600, 400)
        self.mainLayout = QVBoxLayout(ParameterWidget)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(ParameterWidget)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(ParameterWidget)

        QMetaObject.connectSlotsByName(ParameterWidget)
    # setupUi

    def retranslateUi(self, ParameterWidget):
        ParameterWidget.setWindowTitle(QCoreApplication.translate("ParameterWidget", "ParameterWidget", None))
    # retranslateUi

