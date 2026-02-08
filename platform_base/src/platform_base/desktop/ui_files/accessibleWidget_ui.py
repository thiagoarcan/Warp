
################################################################################
## Form generated from reading UI file 'accessibleWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_AccessibleWidget:
    def setupUi(self, AccessibleWidget):
        if not AccessibleWidget.objectName():
            AccessibleWidget.setObjectName("AccessibleWidget")
        AccessibleWidget.resize(600, 400)
        self.mainLayout = QVBoxLayout(AccessibleWidget)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(AccessibleWidget)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(AccessibleWidget)

        QMetaObject.connectSlotsByName(AccessibleWidget)
    # setupUi

    def retranslateUi(self, AccessibleWidget):
        AccessibleWidget.setWindowTitle(QCoreApplication.translate("AccessibleWidget", "AccessibleWidget", None))
    # retranslateUi

