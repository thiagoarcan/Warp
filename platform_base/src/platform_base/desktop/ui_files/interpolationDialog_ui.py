
################################################################################
## Form generated from reading UI file 'interpolationDialog.ui'
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


class Ui_InterpolationDialog:
    def setupUi(self, InterpolationDialog):
        if not InterpolationDialog.objectName():
            InterpolationDialog.setObjectName("InterpolationDialog")
        InterpolationDialog.resize(600, 400)
        self.mainLayout = QVBoxLayout(InterpolationDialog)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(InterpolationDialog)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)

        self.buttonBox = QDialogButtonBox(InterpolationDialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.mainLayout.addWidget(self.buttonBox)


        self.retranslateUi(InterpolationDialog)
        self.buttonBox.accepted.connect(InterpolationDialog.accept)
        self.buttonBox.rejected.connect(InterpolationDialog.reject)

        QMetaObject.connectSlotsByName(InterpolationDialog)
    # setupUi

    def retranslateUi(self, InterpolationDialog):
        InterpolationDialog.setWindowTitle(QCoreApplication.translate("InterpolationDialog", "InterpolationDialog", None))
    # retranslateUi

