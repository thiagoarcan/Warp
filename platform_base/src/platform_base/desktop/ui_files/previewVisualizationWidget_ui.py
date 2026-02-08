
################################################################################
## Form generated from reading UI file 'previewVisualizationWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_PreviewVisualizationWidget:
    def setupUi(self, PreviewVisualizationWidget):
        if not PreviewVisualizationWidget.objectName():
            PreviewVisualizationWidget.setObjectName("PreviewVisualizationWidget")
        PreviewVisualizationWidget.resize(600, 400)
        self.mainLayout = QVBoxLayout(PreviewVisualizationWidget)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(PreviewVisualizationWidget)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(PreviewVisualizationWidget)

        QMetaObject.connectSlotsByName(PreviewVisualizationWidget)
    # setupUi

    def retranslateUi(self, PreviewVisualizationWidget):
        PreviewVisualizationWidget.setWindowTitle(QCoreApplication.translate("PreviewVisualizationWidget", "PreviewVisualizationWidget", None))
    # retranslateUi

