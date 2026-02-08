
################################################################################
## Form generated from reading UI file 'derivativeDialog.ui'
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


class Ui_DerivativeDialog:
    def setupUi(self, DerivativeDialog):
        if not DerivativeDialog.objectName():
            DerivativeDialog.setObjectName("DerivativeDialog")
        DerivativeDialog.resize(600, 400)
        self.mainLayout = QVBoxLayout(DerivativeDialog)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(DerivativeDialog)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)

        self.buttonBox = QDialogButtonBox(DerivativeDialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.mainLayout.addWidget(self.buttonBox)


        self.retranslateUi(DerivativeDialog)
        self.buttonBox.accepted.connect(DerivativeDialog.accept)
        self.buttonBox.rejected.connect(DerivativeDialog.reject)

        QMetaObject.connectSlotsByName(DerivativeDialog)
    # setupUi

    def retranslateUi(self, DerivativeDialog):
        DerivativeDialog.setWindowTitle(QCoreApplication.translate("DerivativeDialog", "DerivativeDialog", None))
    # retranslateUi

