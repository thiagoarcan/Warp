
################################################################################
## Form generated from reading UI file 'integralDialog.ui'
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


class Ui_IntegralDialog:
    def setupUi(self, IntegralDialog):
        if not IntegralDialog.objectName():
            IntegralDialog.setObjectName("IntegralDialog")
        IntegralDialog.resize(600, 400)
        self.mainLayout = QVBoxLayout(IntegralDialog)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(IntegralDialog)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)

        self.buttonBox = QDialogButtonBox(IntegralDialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.mainLayout.addWidget(self.buttonBox)


        self.retranslateUi(IntegralDialog)
        self.buttonBox.accepted.connect(IntegralDialog.accept)
        self.buttonBox.rejected.connect(IntegralDialog.reject)

        QMetaObject.connectSlotsByName(IntegralDialog)
    # setupUi

    def retranslateUi(self, IntegralDialog):
        IntegralDialog.setWindowTitle(QCoreApplication.translate("IntegralDialog", "IntegralDialog", None))
    # retranslateUi

