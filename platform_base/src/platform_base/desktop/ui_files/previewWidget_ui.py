
################################################################################
## Form generated from reading UI file 'previewWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize
from PySide6.QtWidgets import QFrame, QVBoxLayout


class Ui_PreviewWidget:
    def setupUi(self, PreviewWidget):
        if not PreviewWidget.objectName():
            PreviewWidget.setObjectName("PreviewWidget")
        PreviewWidget.resize(600, 400)
        PreviewWidget.setMinimumSize(QSize(300, 200))
        self.mainLayout = QVBoxLayout(PreviewWidget)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.canvasFrame = QFrame(PreviewWidget)
        self.canvasFrame.setObjectName("canvasFrame")
        self.canvasFrame.setFrameShape(QFrame.StyledPanel)
        self.canvasFrame.setFrameShadow(QFrame.Sunken)
        self.canvasLayout = QVBoxLayout(self.canvasFrame)
        self.canvasLayout.setSpacing(0)
        self.canvasLayout.setContentsMargins(0, 0, 0, 0)
        self.canvasLayout.setObjectName("canvasLayout")

        self.mainLayout.addWidget(self.canvasFrame)


        self.retranslateUi(PreviewWidget)

        QMetaObject.connectSlotsByName(PreviewWidget)
    # setupUi

    def retranslateUi(self, PreviewWidget):
        PreviewWidget.setWindowTitle(QCoreApplication.translate("PreviewWidget", "Preview", None))
    # retranslateUi

