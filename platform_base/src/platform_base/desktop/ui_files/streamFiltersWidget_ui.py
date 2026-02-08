
################################################################################
## Form generated from reading UI file 'streamFiltersWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_StreamFiltersWidget:
    def setupUi(self, StreamFiltersWidget):
        if not StreamFiltersWidget.objectName():
            StreamFiltersWidget.setObjectName("StreamFiltersWidget")
        StreamFiltersWidget.resize(600, 400)
        self.mainLayout = QVBoxLayout(StreamFiltersWidget)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(StreamFiltersWidget)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(StreamFiltersWidget)

        QMetaObject.connectSlotsByName(StreamFiltersWidget)
    # setupUi

    def retranslateUi(self, StreamFiltersWidget):
        StreamFiltersWidget.setWindowTitle(QCoreApplication.translate("StreamFiltersWidget", "StreamFiltersWidget", None))
    # retranslateUi

