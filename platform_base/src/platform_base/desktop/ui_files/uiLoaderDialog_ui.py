
################################################################################
## Form generated from reading UI file 'uiLoaderDialog.ui'
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


class Ui_UiLoaderDialog:
    def setupUi(self, UiLoaderDialog):
        if not UiLoaderDialog.objectName():
            UiLoaderDialog.setObjectName("UiLoaderDialog")
        UiLoaderDialog.resize(600, 400)
        self.mainLayout = QVBoxLayout(UiLoaderDialog)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(UiLoaderDialog)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)

        self.buttonBox = QDialogButtonBox(UiLoaderDialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.mainLayout.addWidget(self.buttonBox)


        self.retranslateUi(UiLoaderDialog)
        self.buttonBox.accepted.connect(UiLoaderDialog.accept)
        self.buttonBox.rejected.connect(UiLoaderDialog.reject)

        QMetaObject.connectSlotsByName(UiLoaderDialog)
    # setupUi

    def retranslateUi(self, UiLoaderDialog):
        UiLoaderDialog.setWindowTitle(QCoreApplication.translate("UiLoaderDialog", "UiLoaderDialog", None))
    # retranslateUi

