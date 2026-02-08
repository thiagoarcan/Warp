
################################################################################
## Form generated from reading UI file 'performanceSettingsTab.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QVBoxLayout, QWidget


class Ui_PerformanceSettingsTab:
    def setupUi(self, PerformanceSettingsTab):
        if not PerformanceSettingsTab.objectName():
            PerformanceSettingsTab.setObjectName("PerformanceSettingsTab")
        PerformanceSettingsTab.resize(600, 400)
        self.mainLayout = QVBoxLayout(PerformanceSettingsTab)
        self.mainLayout.setObjectName("mainLayout")
        self.contentWidget = QWidget(PerformanceSettingsTab)
        self.contentWidget.setObjectName("contentWidget")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.contentWidget)


        self.retranslateUi(PerformanceSettingsTab)

        QMetaObject.connectSlotsByName(PerformanceSettingsTab)
    # setupUi

    def retranslateUi(self, PerformanceSettingsTab):
        PerformanceSettingsTab.setWindowTitle(QCoreApplication.translate("PerformanceSettingsTab", "PerformanceSettingsTab", None))
    # retranslateUi

