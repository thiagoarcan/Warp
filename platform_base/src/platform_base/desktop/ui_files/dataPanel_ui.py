
################################################################################
## Form generated from reading UI file 'dataPanel.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize
from PySide6.QtWidgets import (
    QAbstractItemView,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTabWidget,
    QTextEdit,
    QTreeView,
    QVBoxLayout,
    QWidget,
)


class Ui_DataPanel:
    def setupUi(self, DataPanel):
        if not DataPanel.objectName():
            DataPanel.setObjectName("DataPanel")
        DataPanel.resize(350, 600)
        DataPanel.setMinimumSize(QSize(250, 400))
        self.mainLayout = QVBoxLayout(DataPanel)
        self.mainLayout.setSpacing(6)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(6, 6, 6, 6)
        self.treeGroup = QGroupBox(DataPanel)
        self.treeGroup.setObjectName("treeGroup")
        self.treeLayout = QVBoxLayout(self.treeGroup)
        self.treeLayout.setObjectName("treeLayout")
        self.dataTree = QTreeView(self.treeGroup)
        self.dataTree.setObjectName("dataTree")
        self.dataTree.setAlternatingRowColors(True)
        self.dataTree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.dataTree.setRootIsDecorated(True)
        self.dataTree.setUniformRowHeights(True)
        self.dataTree.setAnimated(True)
        self.dataTree.header().setStretchLastSection(False)

        self.treeLayout.addWidget(self.dataTree)

        self.treeButtons = QHBoxLayout()
        self.treeButtons.setObjectName("treeButtons")
        self.loadBtn = QPushButton(self.treeGroup)
        self.loadBtn.setObjectName("loadBtn")

        self.treeButtons.addWidget(self.loadBtn)

        self.removeBtn = QPushButton(self.treeGroup)
        self.removeBtn.setObjectName("removeBtn")
        self.removeBtn.setEnabled(False)

        self.treeButtons.addWidget(self.removeBtn)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.treeButtons.addItem(self.horizontalSpacer)

        self.refreshBtn = QPushButton(self.treeGroup)
        self.refreshBtn.setObjectName("refreshBtn")

        self.treeButtons.addWidget(self.refreshBtn)


        self.treeLayout.addLayout(self.treeButtons)


        self.mainLayout.addWidget(self.treeGroup)

        self.infoGroup = QGroupBox(DataPanel)
        self.infoGroup.setObjectName("infoGroup")
        self.infoLayout = QVBoxLayout(self.infoGroup)
        self.infoLayout.setObjectName("infoLayout")
        self.infoTabs = QTabWidget(self.infoGroup)
        self.infoTabs.setObjectName("infoTabs")
        self.summaryTab = QWidget()
        self.summaryTab.setObjectName("summaryTab")
        self.summaryLayout = QVBoxLayout(self.summaryTab)
        self.summaryLayout.setObjectName("summaryLayout")
        self.summaryText = QTextEdit(self.summaryTab)
        self.summaryText.setObjectName("summaryText")
        self.summaryText.setMaximumSize(QSize(16777215, 150))
        self.summaryText.setReadOnly(True)

        self.summaryLayout.addWidget(self.summaryText)

        self.infoTabs.addTab(self.summaryTab, "")
        self.metadataTab = QWidget()
        self.metadataTab.setObjectName("metadataTab")
        self.metadataLayout = QVBoxLayout(self.metadataTab)
        self.metadataLayout.setObjectName("metadataLayout")
        self.metadataText = QTextEdit(self.metadataTab)
        self.metadataText.setObjectName("metadataText")
        self.metadataText.setMaximumSize(QSize(16777215, 150))
        self.metadataText.setReadOnly(True)

        self.metadataLayout.addWidget(self.metadataText)

        self.infoTabs.addTab(self.metadataTab, "")
        self.qualityTab = QWidget()
        self.qualityTab.setObjectName("qualityTab")
        self.qualityLayout = QVBoxLayout(self.qualityTab)
        self.qualityLayout.setObjectName("qualityLayout")
        self.qualityText = QTextEdit(self.qualityTab)
        self.qualityText.setObjectName("qualityText")
        self.qualityText.setMaximumSize(QSize(16777215, 150))
        self.qualityText.setReadOnly(True)

        self.qualityLayout.addWidget(self.qualityText)

        self.infoTabs.addTab(self.qualityTab, "")

        self.infoLayout.addWidget(self.infoTabs)


        self.mainLayout.addWidget(self.infoGroup)


        self.retranslateUi(DataPanel)

        self.infoTabs.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(DataPanel)
    # setupUi

    def retranslateUi(self, DataPanel):
        DataPanel.setWindowTitle(QCoreApplication.translate("DataPanel", "Data Panel", None))
        self.treeGroup.setTitle(QCoreApplication.translate("DataPanel", "Datasets & Series", None))
        self.loadBtn.setText(QCoreApplication.translate("DataPanel", "Load Data", None))
        self.removeBtn.setText(QCoreApplication.translate("DataPanel", "Remove", None))
        self.refreshBtn.setText(QCoreApplication.translate("DataPanel", "Refresh", None))
        self.infoGroup.setTitle(QCoreApplication.translate("DataPanel", "Data Information", None))
        self.infoTabs.setTabText(self.infoTabs.indexOf(self.summaryTab), QCoreApplication.translate("DataPanel", "Summary", None))
        self.infoTabs.setTabText(self.infoTabs.indexOf(self.metadataTab), QCoreApplication.translate("DataPanel", "Metadata", None))
        self.infoTabs.setTabText(self.infoTabs.indexOf(self.qualityTab), QCoreApplication.translate("DataPanel", "Quality", None))
    # retranslateUi

