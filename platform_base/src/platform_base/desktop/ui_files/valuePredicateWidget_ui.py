
################################################################################
## Form generated from reading UI file 'valuePredicateWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_ValuePredicateWidget:
    def setupUi(self, ValuePredicateWidget):
        if not ValuePredicateWidget.objectName():
            ValuePredicateWidget.setObjectName("ValuePredicateWidget")
        ValuePredicateWidget.resize(600, 400)
        self.mainLayout = QVBoxLayout(ValuePredicateWidget)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(ValuePredicateWidget)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(ValuePredicateWidget)

        QMetaObject.connectSlotsByName(ValuePredicateWidget)
    # setupUi

    def retranslateUi(self, ValuePredicateWidget):
        ValuePredicateWidget.setWindowTitle(QCoreApplication.translate("ValuePredicateWidget", "ValuePredicateWidget", None))
    # retranslateUi

