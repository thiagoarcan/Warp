
################################################################################
## Form generated from reading UI file 'vizPanel.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)


class Ui_VizPanel:
    def setupUi(self, VizPanel):
        if not VizPanel.objectName():
            VizPanel.setObjectName("VizPanel")
        VizPanel.resize(900, 600)
        VizPanel.setMinimumSize(QSize(400, 300))
        self.mainLayout = QVBoxLayout(VizPanel)
        self.mainLayout.setSpacing(4)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(4, 4, 4, 4)
        self.toolbar = QToolBar(VizPanel)
        self.toolbar.setObjectName("toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)

        self.mainLayout.addWidget(self.toolbar)

        self.plotControlsLayout = QHBoxLayout()
        self.plotControlsLayout.setObjectName("plotControlsLayout")
        self.plotTypeLabel = QLabel(VizPanel)
        self.plotTypeLabel.setObjectName("plotTypeLabel")

        self.plotControlsLayout.addWidget(self.plotTypeLabel)

        self.plotTypeCombo = QComboBox(VizPanel)
        self.plotTypeCombo.addItem("")
        self.plotTypeCombo.addItem("")
        self.plotTypeCombo.addItem("")
        self.plotTypeCombo.addItem("")
        self.plotTypeCombo.setObjectName("plotTypeCombo")

        self.plotControlsLayout.addWidget(self.plotTypeCombo)

        self.newPlotButton = QPushButton(VizPanel)
        self.newPlotButton.setObjectName("newPlotButton")

        self.plotControlsLayout.addWidget(self.newPlotButton)

        self.plotControlsSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.plotControlsLayout.addItem(self.plotControlsSpacer)


        self.mainLayout.addLayout(self.plotControlsLayout)

        self.mainSplitter = QSplitter(VizPanel)
        self.mainSplitter.setObjectName("mainSplitter")
        self.mainSplitter.setOrientation(Qt.Horizontal)
        self.plotTabs = QTabWidget(self.mainSplitter)
        self.plotTabs.setObjectName("plotTabs")
        self.plotTabs.setTabsClosable(True)
        self.plotTabs.setMovable(True)
        self.mainSplitter.addWidget(self.plotTabs)
        self.controlsWidget = QWidget(self.mainSplitter)
        self.controlsWidget.setObjectName("controlsWidget")
        self.controlsWidget.setMinimumSize(QSize(180, 0))
        self.controlsWidget.setMaximumSize(QSize(300, 16777215))
        self.controlsLayout = QVBoxLayout(self.controlsWidget)
        self.controlsLayout.setObjectName("controlsLayout")
        self.controlsLayout.setContentsMargins(0, 0, 0, 0)
        self.settingsGroup = QGroupBox(self.controlsWidget)
        self.settingsGroup.setObjectName("settingsGroup")
        self.settingsLayout = QVBoxLayout(self.settingsGroup)
        self.settingsLayout.setObjectName("settingsLayout")
        self.widthLayout = QHBoxLayout()
        self.widthLayout.setObjectName("widthLayout")
        self.widthLabel = QLabel(self.settingsGroup)
        self.widthLabel.setObjectName("widthLabel")

        self.widthLayout.addWidget(self.widthLabel)

        self.lineWidthSpin = QSpinBox(self.settingsGroup)
        self.lineWidthSpin.setObjectName("lineWidthSpin")
        self.lineWidthSpin.setMinimum(1)
        self.lineWidthSpin.setMaximum(10)
        self.lineWidthSpin.setValue(2)

        self.widthLayout.addWidget(self.lineWidthSpin)


        self.settingsLayout.addLayout(self.widthLayout)

        self.gridCheck = QCheckBox(self.settingsGroup)
        self.gridCheck.setObjectName("gridCheck")
        self.gridCheck.setChecked(True)

        self.settingsLayout.addWidget(self.gridCheck)

        self.legendCheck = QCheckBox(self.settingsGroup)
        self.legendCheck.setObjectName("legendCheck")
        self.legendCheck.setChecked(True)

        self.settingsLayout.addWidget(self.legendCheck)


        self.controlsLayout.addWidget(self.settingsGroup)

        self.seriesGroup = QGroupBox(self.controlsWidget)
        self.seriesGroup.setObjectName("seriesGroup")
        self.seriesGroupLayout = QVBoxLayout(self.seriesGroup)
        self.seriesGroupLayout.setObjectName("seriesGroupLayout")
        self.seriesList = QWidget(self.seriesGroup)
        self.seriesList.setObjectName("seriesList")
        self.seriesListLayout = QVBoxLayout(self.seriesList)
        self.seriesListLayout.setObjectName("seriesListLayout")
        self.seriesListLayout.setContentsMargins(0, 0, 0, 0)

        self.seriesGroupLayout.addWidget(self.seriesList)


        self.controlsLayout.addWidget(self.seriesGroup)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.controlsLayout.addItem(self.verticalSpacer)

        self.mainSplitter.addWidget(self.controlsWidget)

        self.mainLayout.addWidget(self.mainSplitter)


        self.retranslateUi(VizPanel)

        QMetaObject.connectSlotsByName(VizPanel)
    # setupUi

    def retranslateUi(self, VizPanel):
        VizPanel.setWindowTitle(QCoreApplication.translate("VizPanel", "Visualization Panel", None))
        self.plotTypeLabel.setText(QCoreApplication.translate("VizPanel", "Plot Type:", None))
        self.plotTypeCombo.setItemText(0, QCoreApplication.translate("VizPanel", "2D Line", None))
        self.plotTypeCombo.setItemText(1, QCoreApplication.translate("VizPanel", "2D Scatter", None))
        self.plotTypeCombo.setItemText(2, QCoreApplication.translate("VizPanel", "3D Surface", None))
        self.plotTypeCombo.setItemText(3, QCoreApplication.translate("VizPanel", "Heatmap", None))

        self.newPlotButton.setText(QCoreApplication.translate("VizPanel", "New Plot", None))
        self.settingsGroup.setTitle(QCoreApplication.translate("VizPanel", "Plot Settings", None))
        self.widthLabel.setText(QCoreApplication.translate("VizPanel", "Line Width:", None))
        self.gridCheck.setText(QCoreApplication.translate("VizPanel", "Show Grid", None))
        self.legendCheck.setText(QCoreApplication.translate("VizPanel", "Show Legend", None))
        self.seriesGroup.setTitle(QCoreApplication.translate("VizPanel", "Active Series", None))
    # retranslateUi

