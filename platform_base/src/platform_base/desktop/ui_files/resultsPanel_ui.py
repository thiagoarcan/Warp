# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'resultsPanel.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QTabWidget, QTableWidget, QTableWidgetItem, QTextEdit,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

class Ui_ResultsPanel(object):
    def setupUi(self, ResultsPanel):
        if not ResultsPanel.objectName():
            ResultsPanel.setObjectName(u"ResultsPanel")
        ResultsPanel.resize(500, 400)
        ResultsPanel.setMinimumSize(QSize(300, 250))
        self.mainLayout = QVBoxLayout(ResultsPanel)
        self.mainLayout.setObjectName(u"mainLayout")
        self.tabs = QTabWidget(ResultsPanel)
        self.tabs.setObjectName(u"tabs")
        self.resultsTab = QWidget()
        self.resultsTab.setObjectName(u"resultsTab")
        self.resultsTabLayout = QVBoxLayout(self.resultsTab)
        self.resultsTabLayout.setObjectName(u"resultsTabLayout")
        self.resultsTable = QTableWidget(self.resultsTab)
        if (self.resultsTable.columnCount() < 7):
            self.resultsTable.setColumnCount(7)
        __qtablewidgetitem = QTableWidgetItem()
        self.resultsTable.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.resultsTable.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.resultsTable.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.resultsTable.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.resultsTable.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.resultsTable.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.resultsTable.setHorizontalHeaderItem(6, __qtablewidgetitem6)
        self.resultsTable.setObjectName(u"resultsTable")
        self.resultsTable.setAlternatingRowColors(True)
        self.resultsTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.resultsTable.setSortingEnabled(True)

        self.resultsTabLayout.addWidget(self.resultsTable)

        self.detailsGroup = QGroupBox(self.resultsTab)
        self.detailsGroup.setObjectName(u"detailsGroup")
        self.detailsLayout = QVBoxLayout(self.detailsGroup)
        self.detailsLayout.setObjectName(u"detailsLayout")
        self.resultDetails = QTextEdit(self.detailsGroup)
        self.resultDetails.setObjectName(u"resultDetails")
        self.resultDetails.setMaximumSize(QSize(16777215, 150))
        self.resultDetails.setReadOnly(True)

        self.detailsLayout.addWidget(self.resultDetails)


        self.resultsTabLayout.addWidget(self.detailsGroup)

        self.tabs.addTab(self.resultsTab, "")
        self.logsTab = QWidget()
        self.logsTab.setObjectName(u"logsTab")
        self.logsTabLayout = QVBoxLayout(self.logsTab)
        self.logsTabLayout.setObjectName(u"logsTabLayout")
        self.logFilterLayout = QHBoxLayout()
        self.logFilterLayout.setObjectName(u"logFilterLayout")
        self.levelLabel = QLabel(self.logsTab)
        self.levelLabel.setObjectName(u"levelLabel")

        self.logFilterLayout.addWidget(self.levelLabel)

        self.levelFilter = QComboBox(self.logsTab)
        self.levelFilter.addItem("")
        self.levelFilter.addItem("")
        self.levelFilter.addItem("")
        self.levelFilter.addItem("")
        self.levelFilter.addItem("")
        self.levelFilter.setObjectName(u"levelFilter")

        self.logFilterLayout.addWidget(self.levelFilter)

        self.filterLabel = QLabel(self.logsTab)
        self.filterLabel.setObjectName(u"filterLabel")

        self.logFilterLayout.addWidget(self.filterLabel)

        self.textFilter = QLineEdit(self.logsTab)
        self.textFilter.setObjectName(u"textFilter")

        self.logFilterLayout.addWidget(self.textFilter)

        self.clearLogsBtn = QPushButton(self.logsTab)
        self.clearLogsBtn.setObjectName(u"clearLogsBtn")

        self.logFilterLayout.addWidget(self.clearLogsBtn)


        self.logsTabLayout.addLayout(self.logFilterLayout)

        self.logWidget = QTextEdit(self.logsTab)
        self.logWidget.setObjectName(u"logWidget")
        self.logWidget.setReadOnly(True)

        self.logsTabLayout.addWidget(self.logWidget)

        self.tabs.addTab(self.logsTab, "")
        self.qualityTab = QWidget()
        self.qualityTab.setObjectName(u"qualityTab")
        self.qualityTabLayout = QVBoxLayout(self.qualityTab)
        self.qualityTabLayout.setObjectName(u"qualityTabLayout")
        self.qualityTree = QTreeWidget(self.qualityTab)
        self.qualityTree.setObjectName(u"qualityTree")
        self.qualityTree.setAlternatingRowColors(True)

        self.qualityTabLayout.addWidget(self.qualityTree)

        self.tabs.addTab(self.qualityTab, "")

        self.mainLayout.addWidget(self.tabs)

        self.buttonsLayout = QHBoxLayout()
        self.buttonsLayout.setObjectName(u"buttonsLayout")
        self.clearResultsBtn = QPushButton(ResultsPanel)
        self.clearResultsBtn.setObjectName(u"clearResultsBtn")

        self.buttonsLayout.addWidget(self.clearResultsBtn)

        self.exportResultsBtn = QPushButton(ResultsPanel)
        self.exportResultsBtn.setObjectName(u"exportResultsBtn")

        self.buttonsLayout.addWidget(self.exportResultsBtn)

        self.buttonsSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonsLayout.addItem(self.buttonsSpacer)

        self.autoShowCheck = QCheckBox(ResultsPanel)
        self.autoShowCheck.setObjectName(u"autoShowCheck")
        self.autoShowCheck.setChecked(True)

        self.buttonsLayout.addWidget(self.autoShowCheck)


        self.mainLayout.addLayout(self.buttonsLayout)


        self.retranslateUi(ResultsPanel)

        self.tabs.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(ResultsPanel)
    # setupUi

    def retranslateUi(self, ResultsPanel):
        ResultsPanel.setWindowTitle(QCoreApplication.translate("ResultsPanel", u"Results Panel", None))
        ___qtablewidgetitem = self.resultsTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("ResultsPanel", u"Operation", None));
        ___qtablewidgetitem1 = self.resultsTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("ResultsPanel", u"Series", None));
        ___qtablewidgetitem2 = self.resultsTable.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("ResultsPanel", u"Status", None));
        ___qtablewidgetitem3 = self.resultsTable.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("ResultsPanel", u"Duration", None));
        ___qtablewidgetitem4 = self.resultsTable.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("ResultsPanel", u"Points", None));
        ___qtablewidgetitem5 = self.resultsTable.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("ResultsPanel", u"Quality", None));
        ___qtablewidgetitem6 = self.resultsTable.horizontalHeaderItem(6)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("ResultsPanel", u"Created", None));
        self.detailsGroup.setTitle(QCoreApplication.translate("ResultsPanel", u"Result Details", None))
        self.tabs.setTabText(self.tabs.indexOf(self.resultsTab), QCoreApplication.translate("ResultsPanel", u"Results", None))
        self.levelLabel.setText(QCoreApplication.translate("ResultsPanel", u"Level:", None))
        self.levelFilter.setItemText(0, QCoreApplication.translate("ResultsPanel", u"All", None))
        self.levelFilter.setItemText(1, QCoreApplication.translate("ResultsPanel", u"Error", None))
        self.levelFilter.setItemText(2, QCoreApplication.translate("ResultsPanel", u"Warning", None))
        self.levelFilter.setItemText(3, QCoreApplication.translate("ResultsPanel", u"Info", None))
        self.levelFilter.setItemText(4, QCoreApplication.translate("ResultsPanel", u"Debug", None))

        self.filterLabel.setText(QCoreApplication.translate("ResultsPanel", u"Filter:", None))
        self.textFilter.setPlaceholderText(QCoreApplication.translate("ResultsPanel", u"Search logs...", None))
        self.clearLogsBtn.setText(QCoreApplication.translate("ResultsPanel", u"Clear", None))
        self.logWidget.setFontFamily(QCoreApplication.translate("ResultsPanel", u"Consolas", None))
        self.tabs.setTabText(self.tabs.indexOf(self.logsTab), QCoreApplication.translate("ResultsPanel", u"Logs", None))
        ___qtreewidgetitem = self.qualityTree.headerItem()
        ___qtreewidgetitem.setText(2, QCoreApplication.translate("ResultsPanel", u"Status", None));
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("ResultsPanel", u"Value", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("ResultsPanel", u"Metric", None));
        self.tabs.setTabText(self.tabs.indexOf(self.qualityTab), QCoreApplication.translate("ResultsPanel", u"Quality", None))
        self.clearResultsBtn.setText(QCoreApplication.translate("ResultsPanel", u"Clear Results", None))
        self.exportResultsBtn.setText(QCoreApplication.translate("ResultsPanel", u"Export Results", None))
        self.autoShowCheck.setText(QCoreApplication.translate("ResultsPanel", u"Auto-show on results", None))
    # retranslateUi

