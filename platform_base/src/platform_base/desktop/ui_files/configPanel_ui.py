
################################################################################
## Form generated from reading UI file 'configPanel.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class Ui_ConfigPanel:
    def setupUi(self, ConfigPanel):
        if not ConfigPanel.objectName():
            ConfigPanel.setObjectName("ConfigPanel")
        ConfigPanel.resize(350, 500)
        ConfigPanel.setMinimumSize(QSize(280, 400))
        self.mainLayout = QVBoxLayout(ConfigPanel)
        self.mainLayout.setObjectName("mainLayout")
        self.operationGroup = QGroupBox(ConfigPanel)
        self.operationGroup.setObjectName("operationGroup")
        self.operationFormLayout = QFormLayout(self.operationGroup)
        self.operationFormLayout.setObjectName("operationFormLayout")
        self.operationLabel = QLabel(self.operationGroup)
        self.operationLabel.setObjectName("operationLabel")

        self.operationFormLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.operationLabel)

        self.operationCombo = QComboBox(self.operationGroup)
        self.operationCombo.addItem("")
        self.operationCombo.addItem("")
        self.operationCombo.addItem("")
        self.operationCombo.addItem("")
        self.operationCombo.addItem("")
        self.operationCombo.setObjectName("operationCombo")

        self.operationFormLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.operationCombo)


        self.mainLayout.addWidget(self.operationGroup)

        self.configTabs = QTabWidget(ConfigPanel)
        self.configTabs.setObjectName("configTabs")
        self.interpTab = QWidget()
        self.interpTab.setObjectName("interpTab")
        self.interpTabLayout = QVBoxLayout(self.interpTab)
        self.interpTabLayout.setObjectName("interpTabLayout")
        self.interpWidget = QWidget(self.interpTab)
        self.interpWidget.setObjectName("interpWidget")

        self.interpTabLayout.addWidget(self.interpWidget)

        self.configTabs.addTab(self.interpTab, "")
        self.calculusTab = QWidget()
        self.calculusTab.setObjectName("calculusTab")
        self.calculusTabLayout = QVBoxLayout(self.calculusTab)
        self.calculusTabLayout.setObjectName("calculusTabLayout")
        self.calculusWidget = QWidget(self.calculusTab)
        self.calculusWidget.setObjectName("calculusWidget")

        self.calculusTabLayout.addWidget(self.calculusWidget)

        self.configTabs.addTab(self.calculusTab, "")
        self.syncTab = QWidget()
        self.syncTab.setObjectName("syncTab")
        self.syncTabLayout = QVBoxLayout(self.syncTab)
        self.syncTabLayout.setObjectName("syncTabLayout")
        self.syncWidget = QWidget(self.syncTab)
        self.syncWidget.setObjectName("syncWidget")

        self.syncTabLayout.addWidget(self.syncWidget)

        self.configTabs.addTab(self.syncTab, "")

        self.mainLayout.addWidget(self.configTabs)

        self.buttonsLayout = QHBoxLayout()
        self.buttonsLayout.setObjectName("buttonsLayout")
        self.executeBtn = QPushButton(ConfigPanel)
        self.executeBtn.setObjectName("executeBtn")
        self.executeBtn.setEnabled(False)

        self.buttonsLayout.addWidget(self.executeBtn)

        self.previewBtn = QPushButton(ConfigPanel)
        self.previewBtn.setObjectName("previewBtn")
        self.previewBtn.setEnabled(False)

        self.buttonsLayout.addWidget(self.previewBtn)


        self.mainLayout.addLayout(self.buttonsLayout)

        self.historyGroup = QGroupBox(ConfigPanel)
        self.historyGroup.setObjectName("historyGroup")
        self.historyLayout = QVBoxLayout(self.historyGroup)
        self.historyLayout.setObjectName("historyLayout")
        self.historyList = QTextEdit(self.historyGroup)
        self.historyList.setObjectName("historyList")
        self.historyList.setMaximumSize(QSize(16777215, 100))
        self.historyList.setReadOnly(True)

        self.historyLayout.addWidget(self.historyList)


        self.mainLayout.addWidget(self.historyGroup)

        self.statusLabel = QLabel(ConfigPanel)
        self.statusLabel.setObjectName("statusLabel")

        self.mainLayout.addWidget(self.statusLabel)


        self.retranslateUi(ConfigPanel)

        self.configTabs.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(ConfigPanel)
    # setupUi

    def retranslateUi(self, ConfigPanel):
        ConfigPanel.setWindowTitle(QCoreApplication.translate("ConfigPanel", "Configuration Panel", None))
        self.operationGroup.setTitle(QCoreApplication.translate("ConfigPanel", "Operation", None))
        self.operationLabel.setText(QCoreApplication.translate("ConfigPanel", "Type:", None))
        self.operationCombo.setItemText(0, QCoreApplication.translate("ConfigPanel", "Interpolation", None))
        self.operationCombo.setItemText(1, QCoreApplication.translate("ConfigPanel", "Derivative", None))
        self.operationCombo.setItemText(2, QCoreApplication.translate("ConfigPanel", "Integral", None))
        self.operationCombo.setItemText(3, QCoreApplication.translate("ConfigPanel", "Smoothing", None))
        self.operationCombo.setItemText(4, QCoreApplication.translate("ConfigPanel", "Filter", None))

        self.configTabs.setTabText(self.configTabs.indexOf(self.interpTab), QCoreApplication.translate("ConfigPanel", "Interpolation", None))
        self.configTabs.setTabText(self.configTabs.indexOf(self.calculusTab), QCoreApplication.translate("ConfigPanel", "Calculus", None))
        self.configTabs.setTabText(self.configTabs.indexOf(self.syncTab), QCoreApplication.translate("ConfigPanel", "Synchronization", None))
        self.executeBtn.setText(QCoreApplication.translate("ConfigPanel", "Execute", None))
        self.previewBtn.setText(QCoreApplication.translate("ConfigPanel", "Preview", None))
        self.historyGroup.setTitle(QCoreApplication.translate("ConfigPanel", "Operation History", None))
        self.statusLabel.setText(QCoreApplication.translate("ConfigPanel", "Ready", None))
    # retranslateUi

