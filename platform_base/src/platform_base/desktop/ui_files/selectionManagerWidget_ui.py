# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'selectionManagerWidget.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton, QSizePolicy,
    QSpacerItem, QTabWidget, QVBoxLayout, QWidget)

class Ui_SelectionManagerWidget(object):
    def setupUi(self, SelectionManagerWidget):
        if not SelectionManagerWidget.objectName():
            SelectionManagerWidget.setObjectName(u"SelectionManagerWidget")
        SelectionManagerWidget.resize(400, 300)
        self.mainLayout = QVBoxLayout(SelectionManagerWidget)
        self.mainLayout.setSpacing(8)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.datasetLayout = QHBoxLayout()
        self.datasetLayout.setObjectName(u"datasetLayout")
        self.datasetLabel = QLabel(SelectionManagerWidget)
        self.datasetLabel.setObjectName(u"datasetLabel")

        self.datasetLayout.addWidget(self.datasetLabel)

        self.datasetCombo = QComboBox(SelectionManagerWidget)
        self.datasetCombo.setObjectName(u"datasetCombo")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.datasetCombo.sizePolicy().hasHeightForWidth())
        self.datasetCombo.setSizePolicy(sizePolicy)

        self.datasetLayout.addWidget(self.datasetCombo)


        self.mainLayout.addLayout(self.datasetLayout)

        self.selectionTabs = QTabWidget(SelectionManagerWidget)
        self.selectionTabs.setObjectName(u"selectionTabs")
        self.activeTab = QWidget()
        self.activeTab.setObjectName(u"activeTab")
        self.activeLayout = QVBoxLayout(self.activeTab)
        self.activeLayout.setObjectName(u"activeLayout")
        self.activeList = QListWidget(self.activeTab)
        self.activeList.setObjectName(u"activeList")

        self.activeLayout.addWidget(self.activeList)

        self.selectionTabs.addTab(self.activeTab, "")
        self.savedTab = QWidget()
        self.savedTab.setObjectName(u"savedTab")
        self.savedLayout = QVBoxLayout(self.savedTab)
        self.savedLayout.setObjectName(u"savedLayout")
        self.savedList = QListWidget(self.savedTab)
        self.savedList.setObjectName(u"savedList")

        self.savedLayout.addWidget(self.savedList)

        self.selectionTabs.addTab(self.savedTab, "")

        self.mainLayout.addWidget(self.selectionTabs)

        self.actionLayout = QHBoxLayout()
        self.actionLayout.setObjectName(u"actionLayout")
        self.saveBtn = QPushButton(SelectionManagerWidget)
        self.saveBtn.setObjectName(u"saveBtn")

        self.actionLayout.addWidget(self.saveBtn)

        self.loadBtn = QPushButton(SelectionManagerWidget)
        self.loadBtn.setObjectName(u"loadBtn")

        self.actionLayout.addWidget(self.loadBtn)

        self.deleteBtn = QPushButton(SelectionManagerWidget)
        self.deleteBtn.setObjectName(u"deleteBtn")

        self.actionLayout.addWidget(self.deleteBtn)

        self.actionSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.actionLayout.addItem(self.actionSpacer)


        self.mainLayout.addLayout(self.actionLayout)


        self.retranslateUi(SelectionManagerWidget)

        QMetaObject.connectSlotsByName(SelectionManagerWidget)
    # setupUi

    def retranslateUi(self, SelectionManagerWidget):
        self.datasetLabel.setText(QCoreApplication.translate("SelectionManagerWidget", u"Dataset:", None))
        self.selectionTabs.setTabText(self.selectionTabs.indexOf(self.activeTab), QCoreApplication.translate("SelectionManagerWidget", u"Active", None))
        self.selectionTabs.setTabText(self.selectionTabs.indexOf(self.savedTab), QCoreApplication.translate("SelectionManagerWidget", u"Saved", None))
        self.saveBtn.setText(QCoreApplication.translate("SelectionManagerWidget", u"Save", None))
        self.loadBtn.setText(QCoreApplication.translate("SelectionManagerWidget", u"Load", None))
        self.deleteBtn.setText(QCoreApplication.translate("SelectionManagerWidget", u"Delete", None))
        pass
    # retranslateUi

