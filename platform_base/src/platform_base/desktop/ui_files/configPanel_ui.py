# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'configPanel.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFormLayout, QGroupBox,
    QHBoxLayout, QLabel, QPushButton, QSizePolicy,
    QTabWidget, QTextEdit, QVBoxLayout, QWidget)

class Ui_ConfigPanel(object):
    def setupUi(self, ConfigPanel):
        if not ConfigPanel.objectName():
            ConfigPanel.setObjectName(u"ConfigPanel")
        ConfigPanel.resize(350, 500)
        ConfigPanel.setMinimumSize(QSize(280, 400))
        self.mainLayout = QVBoxLayout(ConfigPanel)
        self.mainLayout.setObjectName(u"mainLayout")
        self.operationGroup = QGroupBox(ConfigPanel)
        self.operationGroup.setObjectName(u"operationGroup")
        self.operationFormLayout = QFormLayout(self.operationGroup)
        self.operationFormLayout.setObjectName(u"operationFormLayout")
        self.operationLabel = QLabel(self.operationGroup)
        self.operationLabel.setObjectName(u"operationLabel")

        self.operationFormLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.operationLabel)

        self.operationCombo = QComboBox(self.operationGroup)
        self.operationCombo.addItem("")
        self.operationCombo.addItem("")
        self.operationCombo.addItem("")
        self.operationCombo.addItem("")
        self.operationCombo.addItem("")
        self.operationCombo.setObjectName(u"operationCombo")

        self.operationFormLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.operationCombo)


        self.mainLayout.addWidget(self.operationGroup)

        self.configTabs = QTabWidget(ConfigPanel)
        self.configTabs.setObjectName(u"configTabs")
        self.interpTab = QWidget()
        self.interpTab.setObjectName(u"interpTab")
        self.interpTabLayout = QVBoxLayout(self.interpTab)
        self.interpTabLayout.setObjectName(u"interpTabLayout")
        self.interpWidget = QWidget(self.interpTab)
        self.interpWidget.setObjectName(u"interpWidget")

        self.interpTabLayout.addWidget(self.interpWidget)

        self.configTabs.addTab(self.interpTab, "")
        self.calculusTab = QWidget()
        self.calculusTab.setObjectName(u"calculusTab")
        self.calculusTabLayout = QVBoxLayout(self.calculusTab)
        self.calculusTabLayout.setObjectName(u"calculusTabLayout")
        self.calculusWidget = QWidget(self.calculusTab)
        self.calculusWidget.setObjectName(u"calculusWidget")

        self.calculusTabLayout.addWidget(self.calculusWidget)

        self.configTabs.addTab(self.calculusTab, "")
        self.syncTab = QWidget()
        self.syncTab.setObjectName(u"syncTab")
        self.syncTabLayout = QVBoxLayout(self.syncTab)
        self.syncTabLayout.setObjectName(u"syncTabLayout")
        self.syncWidget = QWidget(self.syncTab)
        self.syncWidget.setObjectName(u"syncWidget")

        self.syncTabLayout.addWidget(self.syncWidget)

        self.configTabs.addTab(self.syncTab, "")

        self.mainLayout.addWidget(self.configTabs)

        self.buttonsLayout = QHBoxLayout()
        self.buttonsLayout.setObjectName(u"buttonsLayout")
        self.executeBtn = QPushButton(ConfigPanel)
        self.executeBtn.setObjectName(u"executeBtn")
        self.executeBtn.setEnabled(False)

        self.buttonsLayout.addWidget(self.executeBtn)

        self.previewBtn = QPushButton(ConfigPanel)
        self.previewBtn.setObjectName(u"previewBtn")
        self.previewBtn.setEnabled(False)

        self.buttonsLayout.addWidget(self.previewBtn)


        self.mainLayout.addLayout(self.buttonsLayout)

        self.historyGroup = QGroupBox(ConfigPanel)
        self.historyGroup.setObjectName(u"historyGroup")
        self.historyLayout = QVBoxLayout(self.historyGroup)
        self.historyLayout.setObjectName(u"historyLayout")
        self.historyList = QTextEdit(self.historyGroup)
        self.historyList.setObjectName(u"historyList")
        self.historyList.setMaximumSize(QSize(16777215, 100))
        self.historyList.setReadOnly(True)

        self.historyLayout.addWidget(self.historyList)


        self.mainLayout.addWidget(self.historyGroup)

        self.statusLabel = QLabel(ConfigPanel)
        self.statusLabel.setObjectName(u"statusLabel")

        self.mainLayout.addWidget(self.statusLabel)


        self.retranslateUi(ConfigPanel)

        self.configTabs.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(ConfigPanel)
    # setupUi

    def retranslateUi(self, ConfigPanel):
        ConfigPanel.setWindowTitle(QCoreApplication.translate("ConfigPanel", u"Configuration Panel", None))
        self.operationGroup.setTitle(QCoreApplication.translate("ConfigPanel", u"Operation", None))
        self.operationLabel.setText(QCoreApplication.translate("ConfigPanel", u"Type:", None))
        self.operationCombo.setItemText(0, QCoreApplication.translate("ConfigPanel", u"Interpolation", None))
        self.operationCombo.setItemText(1, QCoreApplication.translate("ConfigPanel", u"Derivative", None))
        self.operationCombo.setItemText(2, QCoreApplication.translate("ConfigPanel", u"Integral", None))
        self.operationCombo.setItemText(3, QCoreApplication.translate("ConfigPanel", u"Smoothing", None))
        self.operationCombo.setItemText(4, QCoreApplication.translate("ConfigPanel", u"Filter", None))

        self.configTabs.setTabText(self.configTabs.indexOf(self.interpTab), QCoreApplication.translate("ConfigPanel", u"Interpolation", None))
        self.configTabs.setTabText(self.configTabs.indexOf(self.calculusTab), QCoreApplication.translate("ConfigPanel", u"Calculus", None))
        self.configTabs.setTabText(self.configTabs.indexOf(self.syncTab), QCoreApplication.translate("ConfigPanel", u"Synchronization", None))
        self.executeBtn.setText(QCoreApplication.translate("ConfigPanel", u"Execute", None))
        self.previewBtn.setText(QCoreApplication.translate("ConfigPanel", u"Preview", None))
        self.historyGroup.setTitle(QCoreApplication.translate("ConfigPanel", u"Operation History", None))
        self.statusLabel.setText(QCoreApplication.translate("ConfigPanel", u"Ready", None))
    # retranslateUi

