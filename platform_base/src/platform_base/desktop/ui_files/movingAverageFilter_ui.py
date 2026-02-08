
################################################################################
## Form generated from reading UI file 'movingAverageFilter.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_MovingAverageFilter:
    def setupUi(self, MovingAverageFilter):
        if not MovingAverageFilter.objectName():
            MovingAverageFilter.setObjectName("MovingAverageFilter")
        MovingAverageFilter.resize(600, 400)
        self.mainLayout = QVBoxLayout(MovingAverageFilter)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(MovingAverageFilter)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(MovingAverageFilter)

        QMetaObject.connectSlotsByName(MovingAverageFilter)
    # setupUi

    def retranslateUi(self, MovingAverageFilter):
        MovingAverageFilter.setWindowTitle(QCoreApplication.translate("MovingAverageFilter", "MovingAverageFilter", None))
    # retranslateUi

