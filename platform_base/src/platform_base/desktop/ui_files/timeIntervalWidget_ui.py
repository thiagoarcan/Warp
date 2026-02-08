
################################################################################
## Form generated from reading UI file 'timeIntervalWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_TimeIntervalWidget:
    def setupUi(self, TimeIntervalWidget):
        if not TimeIntervalWidget.objectName():
            TimeIntervalWidget.setObjectName("TimeIntervalWidget")
        TimeIntervalWidget.resize(600, 400)
        self.mainLayout = QVBoxLayout(TimeIntervalWidget)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(TimeIntervalWidget)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(TimeIntervalWidget)

        QMetaObject.connectSlotsByName(TimeIntervalWidget)
    # setupUi

    def retranslateUi(self, TimeIntervalWidget):
        TimeIntervalWidget.setWindowTitle(QCoreApplication.translate("TimeIntervalWidget", "TimeIntervalWidget", None))
    # retranslateUi

