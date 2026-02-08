
################################################################################
## Form generated from reading UI file 'resultsTable.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_ResultsTable:
    def setupUi(self, ResultsTable):
        if not ResultsTable.objectName():
            ResultsTable.setObjectName("ResultsTable")
        ResultsTable.resize(600, 400)
        self.mainLayout = QVBoxLayout(ResultsTable)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(ResultsTable)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(ResultsTable)

        QMetaObject.connectSlotsByName(ResultsTable)
    # setupUi

    def retranslateUi(self, ResultsTable):
        ResultsTable.setWindowTitle(QCoreApplication.translate("ResultsTable", "ResultsTable", None))
    # retranslateUi

