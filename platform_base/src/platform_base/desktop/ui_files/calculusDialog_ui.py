
################################################################################
## Form generated from reading UI file 'calculusDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, Qt
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QVBoxLayout,
    QWidget,
)


class Ui_CalculusDialog:
    def setupUi(self, CalculusDialog):
        if not CalculusDialog.objectName():
            CalculusDialog.setObjectName("CalculusDialog")
        CalculusDialog.resize(600, 400)
        self.mainLayout = QVBoxLayout(CalculusDialog)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(CalculusDialog)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)

        self.buttonBox = QDialogButtonBox(CalculusDialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.mainLayout.addWidget(self.buttonBox)


        self.retranslateUi(CalculusDialog)
        self.buttonBox.accepted.connect(CalculusDialog.accept)
        self.buttonBox.rejected.connect(CalculusDialog.reject)

        QMetaObject.connectSlotsByName(CalculusDialog)
    # setupUi

    def retranslateUi(self, CalculusDialog):
        CalculusDialog.setWindowTitle(QCoreApplication.translate("CalculusDialog", "CalculusDialog", None))
    # retranslateUi

