
################################################################################
## Form generated from reading UI file 'choiceParameterWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_ChoiceParameterWidget:
    def setupUi(self, ChoiceParameterWidget):
        if not ChoiceParameterWidget.objectName():
            ChoiceParameterWidget.setObjectName("ChoiceParameterWidget")
        ChoiceParameterWidget.resize(600, 400)
        self.mainLayout = QVBoxLayout(ChoiceParameterWidget)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(ChoiceParameterWidget)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(ChoiceParameterWidget)

        QMetaObject.connectSlotsByName(ChoiceParameterWidget)
    # setupUi

    def retranslateUi(self, ChoiceParameterWidget):
        ChoiceParameterWidget.setWindowTitle(QCoreApplication.translate("ChoiceParameterWidget", "ChoiceParameterWidget", None))
    # retranslateUi

