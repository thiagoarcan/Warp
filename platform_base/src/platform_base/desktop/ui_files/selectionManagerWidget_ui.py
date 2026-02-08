
################################################################################
## Form generated from reading UI file 'selectionManagerWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class Ui_SelectionManagerWidget:
    def setupUi(self, SelectionManagerWidget):
        if not SelectionManagerWidget.objectName():
            SelectionManagerWidget.setObjectName("SelectionManagerWidget")
        SelectionManagerWidget.resize(400, 300)
        self.mainLayout = QVBoxLayout(SelectionManagerWidget)
        self.mainLayout.setSpacing(8)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.datasetLayout = QHBoxLayout()
        self.datasetLayout.setObjectName("datasetLayout")
        self.datasetLabel = QLabel(SelectionManagerWidget)
        self.datasetLabel.setObjectName("datasetLabel")

        self.datasetLayout.addWidget(self.datasetLabel)

        self.datasetCombo = QComboBox(SelectionManagerWidget)
        self.datasetCombo.setObjectName("datasetCombo")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.datasetCombo.sizePolicy().hasHeightForWidth())
        self.datasetCombo.setSizePolicy(sizePolicy)

        self.datasetLayout.addWidget(self.datasetCombo)


        self.mainLayout.addLayout(self.datasetLayout)

        self.selectionTabs = QTabWidget(SelectionManagerWidget)
        self.selectionTabs.setObjectName("selectionTabs")
        self.activeTab = QWidget()
        self.activeTab.setObjectName("activeTab")
        self.activeLayout = QVBoxLayout(self.activeTab)
        self.activeLayout.setObjectName("activeLayout")
        self.activeList = QListWidget(self.activeTab)
        self.activeList.setObjectName("activeList")

        self.activeLayout.addWidget(self.activeList)

        self.selectionTabs.addTab(self.activeTab, "")
        self.savedTab = QWidget()
        self.savedTab.setObjectName("savedTab")
        self.savedLayout = QVBoxLayout(self.savedTab)
        self.savedLayout.setObjectName("savedLayout")
        self.savedList = QListWidget(self.savedTab)
        self.savedList.setObjectName("savedList")

        self.savedLayout.addWidget(self.savedList)

        self.selectionTabs.addTab(self.savedTab, "")

        self.mainLayout.addWidget(self.selectionTabs)

        self.actionLayout = QHBoxLayout()
        self.actionLayout.setObjectName("actionLayout")
        self.saveBtn = QPushButton(SelectionManagerWidget)
        self.saveBtn.setObjectName("saveBtn")

        self.actionLayout.addWidget(self.saveBtn)

        self.loadBtn = QPushButton(SelectionManagerWidget)
        self.loadBtn.setObjectName("loadBtn")

        self.actionLayout.addWidget(self.loadBtn)

        self.deleteBtn = QPushButton(SelectionManagerWidget)
        self.deleteBtn.setObjectName("deleteBtn")

        self.actionLayout.addWidget(self.deleteBtn)

        self.actionSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.actionLayout.addItem(self.actionSpacer)


        self.mainLayout.addLayout(self.actionLayout)


        self.retranslateUi(SelectionManagerWidget)

        QMetaObject.connectSlotsByName(SelectionManagerWidget)
    # setupUi

    def retranslateUi(self, SelectionManagerWidget):
        self.datasetLabel.setText(QCoreApplication.translate("SelectionManagerWidget", "Dataset:", None))
        self.selectionTabs.setTabText(self.selectionTabs.indexOf(self.activeTab), QCoreApplication.translate("SelectionManagerWidget", "Active", None))
        self.selectionTabs.setTabText(self.selectionTabs.indexOf(self.savedTab), QCoreApplication.translate("SelectionManagerWidget", "Saved", None))
        self.saveBtn.setText(QCoreApplication.translate("SelectionManagerWidget", "Save", None))
        self.loadBtn.setText(QCoreApplication.translate("SelectionManagerWidget", "Load", None))
        self.deleteBtn.setText(QCoreApplication.translate("SelectionManagerWidget", "Delete", None))
    # retranslateUi

