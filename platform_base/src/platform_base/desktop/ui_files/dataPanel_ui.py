# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dataPanel.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QGroupBox, QHBoxLayout,
    QHeaderView, QPushButton, QSizePolicy, QSpacerItem,
    QTabWidget, QTextEdit, QTreeView, QVBoxLayout,
    QWidget)

class Ui_DataPanel(object):
    def setupUi(self, DataPanel):
        if not DataPanel.objectName():
            DataPanel.setObjectName(u"DataPanel")
        DataPanel.resize(350, 600)
        DataPanel.setMinimumSize(QSize(250, 400))
        self.mainLayout = QVBoxLayout(DataPanel)
        self.mainLayout.setSpacing(6)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(6, 6, 6, 6)
        self.treeGroup = QGroupBox(DataPanel)
        self.treeGroup.setObjectName(u"treeGroup")
        self.treeLayout = QVBoxLayout(self.treeGroup)
        self.treeLayout.setObjectName(u"treeLayout")
        self.dataTree = QTreeView(self.treeGroup)
        self.dataTree.setObjectName(u"dataTree")
        self.dataTree.setAlternatingRowColors(True)
        self.dataTree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.dataTree.setRootIsDecorated(True)
        self.dataTree.setUniformRowHeights(True)
        self.dataTree.setAnimated(True)
        self.dataTree.header().setStretchLastSection(False)

        self.treeLayout.addWidget(self.dataTree)

        self.treeButtons = QHBoxLayout()
        self.treeButtons.setObjectName(u"treeButtons")
        self.loadBtn = QPushButton(self.treeGroup)
        self.loadBtn.setObjectName(u"loadBtn")

        self.treeButtons.addWidget(self.loadBtn)

        self.removeBtn = QPushButton(self.treeGroup)
        self.removeBtn.setObjectName(u"removeBtn")
        self.removeBtn.setEnabled(False)

        self.treeButtons.addWidget(self.removeBtn)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.treeButtons.addItem(self.horizontalSpacer)

        self.refreshBtn = QPushButton(self.treeGroup)
        self.refreshBtn.setObjectName(u"refreshBtn")

        self.treeButtons.addWidget(self.refreshBtn)


        self.treeLayout.addLayout(self.treeButtons)


        self.mainLayout.addWidget(self.treeGroup)

        self.infoGroup = QGroupBox(DataPanel)
        self.infoGroup.setObjectName(u"infoGroup")
        self.infoLayout = QVBoxLayout(self.infoGroup)
        self.infoLayout.setObjectName(u"infoLayout")
        self.infoTabs = QTabWidget(self.infoGroup)
        self.infoTabs.setObjectName(u"infoTabs")
        self.summaryTab = QWidget()
        self.summaryTab.setObjectName(u"summaryTab")
        self.summaryLayout = QVBoxLayout(self.summaryTab)
        self.summaryLayout.setObjectName(u"summaryLayout")
        self.summaryText = QTextEdit(self.summaryTab)
        self.summaryText.setObjectName(u"summaryText")
        self.summaryText.setMaximumSize(QSize(16777215, 150))
        self.summaryText.setReadOnly(True)

        self.summaryLayout.addWidget(self.summaryText)

        self.infoTabs.addTab(self.summaryTab, "")
        self.metadataTab = QWidget()
        self.metadataTab.setObjectName(u"metadataTab")
        self.metadataLayout = QVBoxLayout(self.metadataTab)
        self.metadataLayout.setObjectName(u"metadataLayout")
        self.metadataText = QTextEdit(self.metadataTab)
        self.metadataText.setObjectName(u"metadataText")
        self.metadataText.setMaximumSize(QSize(16777215, 150))
        self.metadataText.setReadOnly(True)

        self.metadataLayout.addWidget(self.metadataText)

        self.infoTabs.addTab(self.metadataTab, "")
        self.qualityTab = QWidget()
        self.qualityTab.setObjectName(u"qualityTab")
        self.qualityLayout = QVBoxLayout(self.qualityTab)
        self.qualityLayout.setObjectName(u"qualityLayout")
        self.qualityText = QTextEdit(self.qualityTab)
        self.qualityText.setObjectName(u"qualityText")
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
        DataPanel.setWindowTitle(QCoreApplication.translate("DataPanel", u"Data Panel", None))
        self.treeGroup.setTitle(QCoreApplication.translate("DataPanel", u"Datasets & Series", None))
        self.loadBtn.setText(QCoreApplication.translate("DataPanel", u"Load Data", None))
        self.removeBtn.setText(QCoreApplication.translate("DataPanel", u"Remove", None))
        self.refreshBtn.setText(QCoreApplication.translate("DataPanel", u"Refresh", None))
        self.infoGroup.setTitle(QCoreApplication.translate("DataPanel", u"Data Information", None))
        self.infoTabs.setTabText(self.infoTabs.indexOf(self.summaryTab), QCoreApplication.translate("DataPanel", u"Summary", None))
        self.infoTabs.setTabText(self.infoTabs.indexOf(self.metadataTab), QCoreApplication.translate("DataPanel", u"Metadata", None))
        self.infoTabs.setTabText(self.infoTabs.indexOf(self.qualityTab), QCoreApplication.translate("DataPanel", u"Quality", None))
    # retranslateUi

