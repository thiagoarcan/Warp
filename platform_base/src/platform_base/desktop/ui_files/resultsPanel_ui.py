
################################################################################
## Form generated from reading UI file 'resultsPanel.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QVBoxLayout,
    QWidget,
)


class Ui_ResultsPanel:
    def setupUi(self, ResultsPanel):
        if not ResultsPanel.objectName():
            ResultsPanel.setObjectName("ResultsPanel")
        ResultsPanel.resize(500, 400)
        ResultsPanel.setMinimumSize(QSize(300, 250))
        self.mainLayout = QVBoxLayout(ResultsPanel)
        self.mainLayout.setObjectName("mainLayout")
        self.tabs = QTabWidget(ResultsPanel)
        self.tabs.setObjectName("tabs")
        self.resultsTab = QWidget()
        self.resultsTab.setObjectName("resultsTab")
        self.resultsTabLayout = QVBoxLayout(self.resultsTab)
        self.resultsTabLayout.setObjectName("resultsTabLayout")
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
        self.resultsTable.setObjectName("resultsTable")
        self.resultsTable.setAlternatingRowColors(True)
        self.resultsTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.resultsTable.setSortingEnabled(True)

        self.resultsTabLayout.addWidget(self.resultsTable)

        self.detailsGroup = QGroupBox(self.resultsTab)
        self.detailsGroup.setObjectName("detailsGroup")
        self.detailsLayout = QVBoxLayout(self.detailsGroup)
        self.detailsLayout.setObjectName("detailsLayout")
        self.resultDetails = QTextEdit(self.detailsGroup)
        self.resultDetails.setObjectName("resultDetails")
        self.resultDetails.setMaximumSize(QSize(16777215, 150))
        self.resultDetails.setReadOnly(True)

        self.detailsLayout.addWidget(self.resultDetails)


        self.resultsTabLayout.addWidget(self.detailsGroup)

        self.tabs.addTab(self.resultsTab, "")
        self.logsTab = QWidget()
        self.logsTab.setObjectName("logsTab")
        self.logsTabLayout = QVBoxLayout(self.logsTab)
        self.logsTabLayout.setObjectName("logsTabLayout")
        self.logFilterLayout = QHBoxLayout()
        self.logFilterLayout.setObjectName("logFilterLayout")
        self.levelLabel = QLabel(self.logsTab)
        self.levelLabel.setObjectName("levelLabel")

        self.logFilterLayout.addWidget(self.levelLabel)

        self.levelFilter = QComboBox(self.logsTab)
        self.levelFilter.addItem("")
        self.levelFilter.addItem("")
        self.levelFilter.addItem("")
        self.levelFilter.addItem("")
        self.levelFilter.addItem("")
        self.levelFilter.setObjectName("levelFilter")

        self.logFilterLayout.addWidget(self.levelFilter)

        self.filterLabel = QLabel(self.logsTab)
        self.filterLabel.setObjectName("filterLabel")

        self.logFilterLayout.addWidget(self.filterLabel)

        self.textFilter = QLineEdit(self.logsTab)
        self.textFilter.setObjectName("textFilter")

        self.logFilterLayout.addWidget(self.textFilter)

        self.clearLogsBtn = QPushButton(self.logsTab)
        self.clearLogsBtn.setObjectName("clearLogsBtn")

        self.logFilterLayout.addWidget(self.clearLogsBtn)


        self.logsTabLayout.addLayout(self.logFilterLayout)

        self.logWidget = QTextEdit(self.logsTab)
        self.logWidget.setObjectName("logWidget")
        self.logWidget.setReadOnly(True)

        self.logsTabLayout.addWidget(self.logWidget)

        self.tabs.addTab(self.logsTab, "")
        self.qualityTab = QWidget()
        self.qualityTab.setObjectName("qualityTab")
        self.qualityTabLayout = QVBoxLayout(self.qualityTab)
        self.qualityTabLayout.setObjectName("qualityTabLayout")
        self.qualityTree = QTreeWidget(self.qualityTab)
        self.qualityTree.setObjectName("qualityTree")
        self.qualityTree.setAlternatingRowColors(True)

        self.qualityTabLayout.addWidget(self.qualityTree)

        self.tabs.addTab(self.qualityTab, "")

        self.mainLayout.addWidget(self.tabs)

        self.buttonsLayout = QHBoxLayout()
        self.buttonsLayout.setObjectName("buttonsLayout")
        self.clearResultsBtn = QPushButton(ResultsPanel)
        self.clearResultsBtn.setObjectName("clearResultsBtn")

        self.buttonsLayout.addWidget(self.clearResultsBtn)

        self.exportResultsBtn = QPushButton(ResultsPanel)
        self.exportResultsBtn.setObjectName("exportResultsBtn")

        self.buttonsLayout.addWidget(self.exportResultsBtn)

        self.buttonsSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonsLayout.addItem(self.buttonsSpacer)

        self.autoShowCheck = QCheckBox(ResultsPanel)
        self.autoShowCheck.setObjectName("autoShowCheck")
        self.autoShowCheck.setChecked(True)

        self.buttonsLayout.addWidget(self.autoShowCheck)


        self.mainLayout.addLayout(self.buttonsLayout)


        self.retranslateUi(ResultsPanel)

        self.tabs.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(ResultsPanel)
    # setupUi

    def retranslateUi(self, ResultsPanel):
        ResultsPanel.setWindowTitle(QCoreApplication.translate("ResultsPanel", "Results Panel", None))
        ___qtablewidgetitem = self.resultsTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("ResultsPanel", "Operation", None))
        ___qtablewidgetitem1 = self.resultsTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("ResultsPanel", "Series", None))
        ___qtablewidgetitem2 = self.resultsTable.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("ResultsPanel", "Status", None))
        ___qtablewidgetitem3 = self.resultsTable.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("ResultsPanel", "Duration", None))
        ___qtablewidgetitem4 = self.resultsTable.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("ResultsPanel", "Points", None))
        ___qtablewidgetitem5 = self.resultsTable.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("ResultsPanel", "Quality", None))
        ___qtablewidgetitem6 = self.resultsTable.horizontalHeaderItem(6)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("ResultsPanel", "Created", None))
        self.detailsGroup.setTitle(QCoreApplication.translate("ResultsPanel", "Result Details", None))
        self.tabs.setTabText(self.tabs.indexOf(self.resultsTab), QCoreApplication.translate("ResultsPanel", "Results", None))
        self.levelLabel.setText(QCoreApplication.translate("ResultsPanel", "Level:", None))
        self.levelFilter.setItemText(0, QCoreApplication.translate("ResultsPanel", "All", None))
        self.levelFilter.setItemText(1, QCoreApplication.translate("ResultsPanel", "Error", None))
        self.levelFilter.setItemText(2, QCoreApplication.translate("ResultsPanel", "Warning", None))
        self.levelFilter.setItemText(3, QCoreApplication.translate("ResultsPanel", "Info", None))
        self.levelFilter.setItemText(4, QCoreApplication.translate("ResultsPanel", "Debug", None))

        self.filterLabel.setText(QCoreApplication.translate("ResultsPanel", "Filter:", None))
        self.textFilter.setPlaceholderText(QCoreApplication.translate("ResultsPanel", "Search logs...", None))
        self.clearLogsBtn.setText(QCoreApplication.translate("ResultsPanel", "Clear", None))
        self.logWidget.setFontFamily(QCoreApplication.translate("ResultsPanel", "Consolas", None))
        self.tabs.setTabText(self.tabs.indexOf(self.logsTab), QCoreApplication.translate("ResultsPanel", "Logs", None))
        ___qtreewidgetitem = self.qualityTree.headerItem()
        ___qtreewidgetitem.setText(2, QCoreApplication.translate("ResultsPanel", "Status", None))
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("ResultsPanel", "Value", None))
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("ResultsPanel", "Metric", None))
        self.tabs.setTabText(self.tabs.indexOf(self.qualityTab), QCoreApplication.translate("ResultsPanel", "Quality", None))
        self.clearResultsBtn.setText(QCoreApplication.translate("ResultsPanel", "Clear Results", None))
        self.exportResultsBtn.setText(QCoreApplication.translate("ResultsPanel", "Export Results", None))
        self.autoShowCheck.setText(QCoreApplication.translate("ResultsPanel", "Auto-show on results", None))
    # retranslateUi

