
################################################################################
## Form generated from reading UI file 'previewCanvas.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_PreviewCanvas:
    def setupUi(self, PreviewCanvas):
        if not PreviewCanvas.objectName():
            PreviewCanvas.setObjectName("PreviewCanvas")
        PreviewCanvas.resize(600, 400)
        self.mainLayout = QVBoxLayout(PreviewCanvas)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(PreviewCanvas)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(PreviewCanvas)

        QMetaObject.connectSlotsByName(PreviewCanvas)
    # setupUi

    def retranslateUi(self, PreviewCanvas):
        PreviewCanvas.setWindowTitle(QCoreApplication.translate("PreviewCanvas", "PreviewCanvas", None))
    # retranslateUi

