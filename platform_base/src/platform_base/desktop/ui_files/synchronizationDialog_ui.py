
################################################################################
## Form generated from reading UI file 'synchronizationDialog.ui'
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


class Ui_SynchronizationDialog:
    def setupUi(self, SynchronizationDialog):
        if not SynchronizationDialog.objectName():
            SynchronizationDialog.setObjectName("SynchronizationDialog")
        SynchronizationDialog.resize(600, 400)
        self.mainLayout = QVBoxLayout(SynchronizationDialog)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(SynchronizationDialog)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)

        self.buttonBox = QDialogButtonBox(SynchronizationDialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.mainLayout.addWidget(self.buttonBox)


        self.retranslateUi(SynchronizationDialog)
        self.buttonBox.accepted.connect(SynchronizationDialog.accept)
        self.buttonBox.rejected.connect(SynchronizationDialog.reject)

        QMetaObject.connectSlotsByName(SynchronizationDialog)
    # setupUi

    def retranslateUi(self, SynchronizationDialog):
        SynchronizationDialog.setWindowTitle(QCoreApplication.translate("SynchronizationDialog", "SynchronizationDialog", None))
    # retranslateUi

