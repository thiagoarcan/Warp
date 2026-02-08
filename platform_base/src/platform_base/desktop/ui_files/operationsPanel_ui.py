
################################################################################
## Form generated from reading UI file 'operationsPanel.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class Ui_OperationsPanel:
    def setupUi(self, OperationsPanel):
        if not OperationsPanel.objectName():
            OperationsPanel.setObjectName("OperationsPanel")
        OperationsPanel.resize(350, 700)
        OperationsPanel.setMinimumSize(QSize(150, 400))
        OperationsPanel.setStyleSheet("\n"
"QWidget {\n"
"    background-color: #ffffff;\n"
"}\n"
"QGroupBox {\n"
"    font-weight: bold;\n"
"    border: 1px solid #e9ecef;\n"
"    border-radius: 6px;\n"
"    margin-top: 8px;\n"
"    padding-top: 8px;\n"
"    background-color: #f8f9fa;\n"
"}\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 8px;\n"
"    padding: 2px 6px;\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #e9ecef;\n"
"    border-radius: 3px;\n"
"}\n"
"QPushButton {\n"
"    background-color: #0d6efd;\n"
"    color: white;\n"
"    border: none;\n"
"    padding: 6px 12px;\n"
"    border-radius: 4px;\n"
"    font-weight: bold;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #0b5ed7;\n"
"}\n"
"QPushButton:disabled {\n"
"    background-color: #6c757d;\n"
"}\n"
'QPushButton[objectName="secondary"] {\n'
"    background-color: #6c757d;\n"
"}\n"
'QPushButton[objectName="success"] {\n'
"    background-color: #198754;\n"
"}\n"
"QSpinBox, QDoubleSpinBox {\n"
"    border: 1px solid #ced4da;\n"
"    bord"
                        "er-radius: 4px;\n"
"    padding: 4px 8px;\n"
"    background-color: white;\n"
"    min-height: 24px;\n"
"}\n"
"QComboBox {\n"
"    border: 1px solid #ced4da;\n"
"    border-radius: 4px;\n"
"    padding: 4px 8px;\n"
"    background-color: white;\n"
"    min-height: 24px;\n"
"}\n"
"QTabWidget::pane {\n"
"    border: 1px solid #e9ecef;\n"
"    border-radius: 4px;\n"
"    background-color: white;\n"
"}\n"
"QTabBar::tab {\n"
"    background-color: #f8f9fa;\n"
"    border: 1px solid #e9ecef;\n"
"    padding: 6px 10px;\n"
"    margin-right: 2px;\n"
"    border-top-left-radius: 4px;\n"
"    border-top-right-radius: 4px;\n"
"    font-size: 11px;\n"
"}\n"
"QTabBar::tab:selected {\n"
"    background-color: white;\n"
"    border-bottom-color: white;\n"
"}\n"
"   ")
        self.mainLayout = QVBoxLayout(OperationsPanel)
        self.mainLayout.setSpacing(4)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(4, 4, 4, 4)
        self.headerLabel = QLabel(OperationsPanel)
        self.headerLabel.setObjectName("headerLabel")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.headerLabel.setFont(font)

        self.mainLayout.addWidget(self.headerLabel)

        self.seriesGroup = QGroupBox(OperationsPanel)
        self.seriesGroup.setObjectName("seriesGroup")
        self.seriesLayout = QFormLayout(self.seriesGroup)
        self.seriesLayout.setObjectName("seriesLayout")
        self.seriesLayout.setContentsMargins(6, 10, 6, 6)
        self.seriesLabel = QLabel(self.seriesGroup)
        self.seriesLabel.setObjectName("seriesLabel")

        self.seriesLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.seriesLabel)

        self.seriesCombo = QComboBox(self.seriesGroup)
        self.seriesCombo.addItem("")
        self.seriesCombo.setObjectName("seriesCombo")
        self.seriesCombo.setEnabled(False)
        self.seriesCombo.setMinimumSize(QSize(150, 0))

        self.seriesLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.seriesCombo)


        self.mainLayout.addWidget(self.seriesGroup)

        self.tabWidget = QTabWidget(OperationsPanel)
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setTabPosition(QTabWidget.North)
        self.tabWidget.setUsesScrollButtons(True)
        self.interpTab = QWidget()
        self.interpTab.setObjectName("interpTab")
        self.interpTabLayout = QVBoxLayout(self.interpTab)
        self.interpTabLayout.setObjectName("interpTabLayout")
        self.interpScrollArea = QScrollArea(self.interpTab)
        self.interpScrollArea.setObjectName("interpScrollArea")
        self.interpScrollArea.setWidgetResizable(True)
        self.interpScrollContent = QWidget()
        self.interpScrollContent.setObjectName("interpScrollContent")
        self.interpContentLayout = QVBoxLayout(self.interpScrollContent)
        self.interpContentLayout.setSpacing(8)
        self.interpContentLayout.setObjectName("interpContentLayout")
        self.interpMethodGroup = QGroupBox(self.interpScrollContent)
        self.interpMethodGroup.setObjectName("interpMethodGroup")
        self.interpMethodLayout = QFormLayout(self.interpMethodGroup)
        self.interpMethodLayout.setObjectName("interpMethodLayout")
        self.interpMethodLabel = QLabel(self.interpMethodGroup)
        self.interpMethodLabel.setObjectName("interpMethodLabel")

        self.interpMethodLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.interpMethodLabel)

        self.interpMethodCombo = QComboBox(self.interpMethodGroup)
        self.interpMethodCombo.addItem("")
        self.interpMethodCombo.addItem("")
        self.interpMethodCombo.addItem("")
        self.interpMethodCombo.addItem("")
        self.interpMethodCombo.addItem("")
        self.interpMethodCombo.addItem("")
        self.interpMethodCombo.addItem("")
        self.interpMethodCombo.addItem("")
        self.interpMethodCombo.addItem("")
        self.interpMethodCombo.addItem("")
        self.interpMethodCombo.setObjectName("interpMethodCombo")

        self.interpMethodLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.interpMethodCombo)


        self.interpContentLayout.addWidget(self.interpMethodGroup)

        self.interpParamsGroup = QGroupBox(self.interpScrollContent)
        self.interpParamsGroup.setObjectName("interpParamsGroup")
        self.interpParamsLayout = QFormLayout(self.interpParamsGroup)
        self.interpParamsLayout.setObjectName("interpParamsLayout")
        self.interpPointsLabel = QLabel(self.interpParamsGroup)
        self.interpPointsLabel.setObjectName("interpPointsLabel")

        self.interpParamsLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.interpPointsLabel)

        self.interpPointsSpin = QSpinBox(self.interpParamsGroup)
        self.interpPointsSpin.setObjectName("interpPointsSpin")
        self.interpPointsSpin.setMinimum(10)
        self.interpPointsSpin.setMaximum(100000)
        self.interpPointsSpin.setValue(1000)

        self.interpParamsLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.interpPointsSpin)

        self.interpSmoothLabel = QLabel(self.interpParamsGroup)
        self.interpSmoothLabel.setObjectName("interpSmoothLabel")

        self.interpParamsLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.interpSmoothLabel)

        self.interpSmoothSpin = QDoubleSpinBox(self.interpParamsGroup)
        self.interpSmoothSpin.setObjectName("interpSmoothSpin")
        self.interpSmoothSpin.setDecimals(2)
        self.interpSmoothSpin.setMaximum(1.000000000000000)
        self.interpSmoothSpin.setSingleStep(0.010000000000000)

        self.interpParamsLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.interpSmoothSpin)

        self.interpDegreeLabel = QLabel(self.interpParamsGroup)
        self.interpDegreeLabel.setObjectName("interpDegreeLabel")

        self.interpParamsLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.interpDegreeLabel)

        self.interpDegreeSpin = QSpinBox(self.interpParamsGroup)
        self.interpDegreeSpin.setObjectName("interpDegreeSpin")
        self.interpDegreeSpin.setMinimum(1)
        self.interpDegreeSpin.setMaximum(10)
        self.interpDegreeSpin.setValue(3)

        self.interpParamsLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.interpDegreeSpin)

        self.interpExtrapolateCheck = QCheckBox(self.interpParamsGroup)
        self.interpExtrapolateCheck.setObjectName("interpExtrapolateCheck")

        self.interpParamsLayout.setWidget(3, QFormLayout.ItemRole.SpanningRole, self.interpExtrapolateCheck)


        self.interpContentLayout.addWidget(self.interpParamsGroup)

        self.interpButtonsLayout = QHBoxLayout()
        self.interpButtonsLayout.setObjectName("interpButtonsLayout")
        self.interpPreviewBtn = QPushButton(self.interpScrollContent)
        self.interpPreviewBtn.setObjectName("interpPreviewBtn")

        self.interpButtonsLayout.addWidget(self.interpPreviewBtn)

        self.interpApplyBtn = QPushButton(self.interpScrollContent)
        self.interpApplyBtn.setObjectName("interpApplyBtn")

        self.interpButtonsLayout.addWidget(self.interpApplyBtn)


        self.interpContentLayout.addLayout(self.interpButtonsLayout)

        self.interpSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.interpContentLayout.addItem(self.interpSpacer)

        self.interpScrollArea.setWidget(self.interpScrollContent)

        self.interpTabLayout.addWidget(self.interpScrollArea)

        self.tabWidget.addTab(self.interpTab, "")
        self.calculusTab = QWidget()
        self.calculusTab.setObjectName("calculusTab")
        self.calculusTabLayout = QVBoxLayout(self.calculusTab)
        self.calculusTabLayout.setObjectName("calculusTabLayout")
        self.calculusScrollArea = QScrollArea(self.calculusTab)
        self.calculusScrollArea.setObjectName("calculusScrollArea")
        self.calculusScrollArea.setWidgetResizable(True)
        self.calculusScrollContent = QWidget()
        self.calculusScrollContent.setObjectName("calculusScrollContent")
        self.calculusContentLayout = QVBoxLayout(self.calculusScrollContent)
        self.calculusContentLayout.setSpacing(8)
        self.calculusContentLayout.setObjectName("calculusContentLayout")
        self.derivGroup = QGroupBox(self.calculusScrollContent)
        self.derivGroup.setObjectName("derivGroup")
        self.derivLayout = QFormLayout(self.derivGroup)
        self.derivLayout.setObjectName("derivLayout")
        self.derivOrderLabel = QLabel(self.derivGroup)
        self.derivOrderLabel.setObjectName("derivOrderLabel")

        self.derivLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.derivOrderLabel)

        self.derivOrderCombo = QComboBox(self.derivGroup)
        self.derivOrderCombo.addItem("")
        self.derivOrderCombo.addItem("")
        self.derivOrderCombo.addItem("")
        self.derivOrderCombo.setObjectName("derivOrderCombo")

        self.derivLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.derivOrderCombo)

        self.derivMethodLabel = QLabel(self.derivGroup)
        self.derivMethodLabel.setObjectName("derivMethodLabel")

        self.derivLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.derivMethodLabel)

        self.derivMethodCombo = QComboBox(self.derivGroup)
        self.derivMethodCombo.addItem("")
        self.derivMethodCombo.addItem("")
        self.derivMethodCombo.addItem("")
        self.derivMethodCombo.setObjectName("derivMethodCombo")

        self.derivLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.derivMethodCombo)

        self.derivWindowLabel = QLabel(self.derivGroup)
        self.derivWindowLabel.setObjectName("derivWindowLabel")

        self.derivLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.derivWindowLabel)

        self.derivWindowSpin = QSpinBox(self.derivGroup)
        self.derivWindowSpin.setObjectName("derivWindowSpin")
        self.derivWindowSpin.setMinimum(3)
        self.derivWindowSpin.setMaximum(51)
        self.derivWindowSpin.setSingleStep(2)
        self.derivWindowSpin.setValue(7)

        self.derivLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.derivWindowSpin)

        self.derivSmoothCheck = QCheckBox(self.derivGroup)
        self.derivSmoothCheck.setObjectName("derivSmoothCheck")

        self.derivLayout.setWidget(3, QFormLayout.ItemRole.SpanningRole, self.derivSmoothCheck)

        self.derivButtonsLayout = QHBoxLayout()
        self.derivButtonsLayout.setObjectName("derivButtonsLayout")
        self.derivPreviewBtn = QPushButton(self.derivGroup)
        self.derivPreviewBtn.setObjectName("derivPreviewBtn")

        self.derivButtonsLayout.addWidget(self.derivPreviewBtn)

        self.derivApplyBtn = QPushButton(self.derivGroup)
        self.derivApplyBtn.setObjectName("derivApplyBtn")

        self.derivButtonsLayout.addWidget(self.derivApplyBtn)


        self.derivLayout.setLayout(4, QFormLayout.ItemRole.SpanningRole, self.derivButtonsLayout)


        self.calculusContentLayout.addWidget(self.derivGroup)

        self.integGroup = QGroupBox(self.calculusScrollContent)
        self.integGroup.setObjectName("integGroup")
        self.integLayout = QFormLayout(self.integGroup)
        self.integLayout.setObjectName("integLayout")
        self.integMethodLabel = QLabel(self.integGroup)
        self.integMethodLabel.setObjectName("integMethodLabel")

        self.integLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.integMethodLabel)

        self.integMethodCombo = QComboBox(self.integGroup)
        self.integMethodCombo.addItem("")
        self.integMethodCombo.addItem("")
        self.integMethodCombo.addItem("")
        self.integMethodCombo.setObjectName("integMethodCombo")

        self.integLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.integMethodCombo)

        self.integButtonsLayout = QHBoxLayout()
        self.integButtonsLayout.setObjectName("integButtonsLayout")
        self.integPreviewBtn = QPushButton(self.integGroup)
        self.integPreviewBtn.setObjectName("integPreviewBtn")

        self.integButtonsLayout.addWidget(self.integPreviewBtn)

        self.integApplyBtn = QPushButton(self.integGroup)
        self.integApplyBtn.setObjectName("integApplyBtn")

        self.integButtonsLayout.addWidget(self.integApplyBtn)


        self.integLayout.setLayout(1, QFormLayout.ItemRole.SpanningRole, self.integButtonsLayout)


        self.calculusContentLayout.addWidget(self.integGroup)

        self.areaGroup = QGroupBox(self.calculusScrollContent)
        self.areaGroup.setObjectName("areaGroup")
        self.areaLayout = QFormLayout(self.areaGroup)
        self.areaLayout.setObjectName("areaLayout")
        self.areaTypeLabel = QLabel(self.areaGroup)
        self.areaTypeLabel.setObjectName("areaTypeLabel")

        self.areaLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.areaTypeLabel)

        self.areaTypeCombo = QComboBox(self.areaGroup)
        self.areaTypeCombo.addItem("")
        self.areaTypeCombo.addItem("")
        self.areaTypeCombo.setObjectName("areaTypeCombo")

        self.areaLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.areaTypeCombo)

        self.areaApplyBtn = QPushButton(self.areaGroup)
        self.areaApplyBtn.setObjectName("areaApplyBtn")

        self.areaLayout.setWidget(1, QFormLayout.ItemRole.SpanningRole, self.areaApplyBtn)


        self.calculusContentLayout.addWidget(self.areaGroup)

        self.calculusSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.calculusContentLayout.addItem(self.calculusSpacer)

        self.calculusScrollArea.setWidget(self.calculusScrollContent)

        self.calculusTabLayout.addWidget(self.calculusScrollArea)

        self.tabWidget.addTab(self.calculusTab, "")
        self.filtersTab = QWidget()
        self.filtersTab.setObjectName("filtersTab")
        self.filtersTabLayout = QVBoxLayout(self.filtersTab)
        self.filtersTabLayout.setObjectName("filtersTabLayout")
        self.filtersScrollArea = QScrollArea(self.filtersTab)
        self.filtersScrollArea.setObjectName("filtersScrollArea")
        self.filtersScrollArea.setWidgetResizable(True)
        self.filtersScrollContent = QWidget()
        self.filtersScrollContent.setObjectName("filtersScrollContent")
        self.filtersContentLayout = QVBoxLayout(self.filtersScrollContent)
        self.filtersContentLayout.setSpacing(8)
        self.filtersContentLayout.setObjectName("filtersContentLayout")
        self.smoothGroup = QGroupBox(self.filtersScrollContent)
        self.smoothGroup.setObjectName("smoothGroup")
        self.smoothLayout = QFormLayout(self.smoothGroup)
        self.smoothLayout.setObjectName("smoothLayout")
        self.smoothMethodLabel = QLabel(self.smoothGroup)
        self.smoothMethodLabel.setObjectName("smoothMethodLabel")

        self.smoothLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.smoothMethodLabel)

        self.smoothMethodCombo = QComboBox(self.smoothGroup)
        self.smoothMethodCombo.addItem("")
        self.smoothMethodCombo.addItem("")
        self.smoothMethodCombo.addItem("")
        self.smoothMethodCombo.addItem("")
        self.smoothMethodCombo.addItem("")
        self.smoothMethodCombo.setObjectName("smoothMethodCombo")

        self.smoothLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.smoothMethodCombo)

        self.smoothWindowLabel = QLabel(self.smoothGroup)
        self.smoothWindowLabel.setObjectName("smoothWindowLabel")

        self.smoothLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.smoothWindowLabel)

        self.smoothWindowSpin = QSpinBox(self.smoothGroup)
        self.smoothWindowSpin.setObjectName("smoothWindowSpin")
        self.smoothWindowSpin.setMinimum(3)
        self.smoothWindowSpin.setMaximum(101)
        self.smoothWindowSpin.setSingleStep(2)
        self.smoothWindowSpin.setValue(5)

        self.smoothLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.smoothWindowSpin)

        self.smoothSigmaLabel = QLabel(self.smoothGroup)
        self.smoothSigmaLabel.setObjectName("smoothSigmaLabel")

        self.smoothLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.smoothSigmaLabel)

        self.smoothSigmaSpin = QDoubleSpinBox(self.smoothGroup)
        self.smoothSigmaSpin.setObjectName("smoothSigmaSpin")
        self.smoothSigmaSpin.setMinimum(0.100000000000000)
        self.smoothSigmaSpin.setMaximum(10.000000000000000)
        self.smoothSigmaSpin.setValue(1.000000000000000)

        self.smoothLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.smoothSigmaSpin)

        self.smoothButtonsLayout = QHBoxLayout()
        self.smoothButtonsLayout.setObjectName("smoothButtonsLayout")
        self.smoothPreviewBtn = QPushButton(self.smoothGroup)
        self.smoothPreviewBtn.setObjectName("smoothPreviewBtn")

        self.smoothButtonsLayout.addWidget(self.smoothPreviewBtn)

        self.smoothApplyBtn = QPushButton(self.smoothGroup)
        self.smoothApplyBtn.setObjectName("smoothApplyBtn")

        self.smoothButtonsLayout.addWidget(self.smoothApplyBtn)


        self.smoothLayout.setLayout(3, QFormLayout.ItemRole.SpanningRole, self.smoothButtonsLayout)


        self.filtersContentLayout.addWidget(self.smoothGroup)

        self.outlierGroup = QGroupBox(self.filtersScrollContent)
        self.outlierGroup.setObjectName("outlierGroup")
        self.outlierLayout = QFormLayout(self.outlierGroup)
        self.outlierLayout.setObjectName("outlierLayout")
        self.outlierMethodLabel = QLabel(self.outlierGroup)
        self.outlierMethodLabel.setObjectName("outlierMethodLabel")

        self.outlierLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.outlierMethodLabel)

        self.outlierMethodCombo = QComboBox(self.outlierGroup)
        self.outlierMethodCombo.addItem("")
        self.outlierMethodCombo.addItem("")
        self.outlierMethodCombo.addItem("")
        self.outlierMethodCombo.setObjectName("outlierMethodCombo")

        self.outlierLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.outlierMethodCombo)

        self.outlierThresholdLabel = QLabel(self.outlierGroup)
        self.outlierThresholdLabel.setObjectName("outlierThresholdLabel")

        self.outlierLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.outlierThresholdLabel)

        self.outlierThresholdSpin = QDoubleSpinBox(self.outlierGroup)
        self.outlierThresholdSpin.setObjectName("outlierThresholdSpin")
        self.outlierThresholdSpin.setMinimum(1.000000000000000)
        self.outlierThresholdSpin.setMaximum(10.000000000000000)
        self.outlierThresholdSpin.setValue(3.000000000000000)

        self.outlierLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.outlierThresholdSpin)

        self.outlierButtonsLayout = QHBoxLayout()
        self.outlierButtonsLayout.setObjectName("outlierButtonsLayout")
        self.outlierPreviewBtn = QPushButton(self.outlierGroup)
        self.outlierPreviewBtn.setObjectName("outlierPreviewBtn")

        self.outlierButtonsLayout.addWidget(self.outlierPreviewBtn)

        self.outlierApplyBtn = QPushButton(self.outlierGroup)
        self.outlierApplyBtn.setObjectName("outlierApplyBtn")

        self.outlierButtonsLayout.addWidget(self.outlierApplyBtn)


        self.outlierLayout.setLayout(2, QFormLayout.ItemRole.SpanningRole, self.outlierButtonsLayout)


        self.filtersContentLayout.addWidget(self.outlierGroup)

        self.fftGroup = QGroupBox(self.filtersScrollContent)
        self.fftGroup.setObjectName("fftGroup")
        self.fftLayout = QFormLayout(self.fftGroup)
        self.fftLayout.setObjectName("fftLayout")
        self.fftWindowLabel = QLabel(self.fftGroup)
        self.fftWindowLabel.setObjectName("fftWindowLabel")

        self.fftLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.fftWindowLabel)

        self.fftWindowCombo = QComboBox(self.fftGroup)
        self.fftWindowCombo.addItem("")
        self.fftWindowCombo.addItem("")
        self.fftWindowCombo.addItem("")
        self.fftWindowCombo.addItem("")
        self.fftWindowCombo.addItem("")
        self.fftWindowCombo.setObjectName("fftWindowCombo")

        self.fftLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.fftWindowCombo)

        self.fftDetrendCheck = QCheckBox(self.fftGroup)
        self.fftDetrendCheck.setObjectName("fftDetrendCheck")
        self.fftDetrendCheck.setChecked(True)

        self.fftLayout.setWidget(1, QFormLayout.ItemRole.SpanningRole, self.fftDetrendCheck)

        self.fftApplyBtn = QPushButton(self.fftGroup)
        self.fftApplyBtn.setObjectName("fftApplyBtn")

        self.fftLayout.setWidget(2, QFormLayout.ItemRole.SpanningRole, self.fftApplyBtn)


        self.filtersContentLayout.addWidget(self.fftGroup)

        self.corrGroup = QGroupBox(self.filtersScrollContent)
        self.corrGroup.setObjectName("corrGroup")
        self.corrLayout = QFormLayout(self.corrGroup)
        self.corrLayout.setObjectName("corrLayout")
        self.corrModeLabel = QLabel(self.corrGroup)
        self.corrModeLabel.setObjectName("corrModeLabel")

        self.corrLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.corrModeLabel)

        self.corrModeCombo = QComboBox(self.corrGroup)
        self.corrModeCombo.addItem("")
        self.corrModeCombo.addItem("")
        self.corrModeCombo.setObjectName("corrModeCombo")

        self.corrLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.corrModeCombo)

        self.corrNormalizeCheck = QCheckBox(self.corrGroup)
        self.corrNormalizeCheck.setObjectName("corrNormalizeCheck")
        self.corrNormalizeCheck.setChecked(True)

        self.corrLayout.setWidget(1, QFormLayout.ItemRole.SpanningRole, self.corrNormalizeCheck)

        self.corrApplyBtn = QPushButton(self.corrGroup)
        self.corrApplyBtn.setObjectName("corrApplyBtn")

        self.corrLayout.setWidget(2, QFormLayout.ItemRole.SpanningRole, self.corrApplyBtn)


        self.filtersContentLayout.addWidget(self.corrGroup)

        self.digitalFiltersGroup = QGroupBox(self.filtersScrollContent)
        self.digitalFiltersGroup.setObjectName("digitalFiltersGroup")
        self.digitalFiltersLayout = QFormLayout(self.digitalFiltersGroup)
        self.digitalFiltersLayout.setObjectName("digitalFiltersLayout")
        self.filterTypeLabel = QLabel(self.digitalFiltersGroup)
        self.filterTypeLabel.setObjectName("filterTypeLabel")

        self.digitalFiltersLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.filterTypeLabel)

        self.filterTypeCombo = QComboBox(self.digitalFiltersGroup)
        self.filterTypeCombo.addItem("")
        self.filterTypeCombo.addItem("")
        self.filterTypeCombo.addItem("")
        self.filterTypeCombo.addItem("")
        self.filterTypeCombo.setObjectName("filterTypeCombo")

        self.digitalFiltersLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.filterTypeCombo)

        self.filterCutoffLabel = QLabel(self.digitalFiltersGroup)
        self.filterCutoffLabel.setObjectName("filterCutoffLabel")

        self.digitalFiltersLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.filterCutoffLabel)

        self.filterCutoffSpin = QDoubleSpinBox(self.digitalFiltersGroup)
        self.filterCutoffSpin.setObjectName("filterCutoffSpin")
        self.filterCutoffSpin.setMinimum(0.100000000000000)
        self.filterCutoffSpin.setMaximum(1000.000000000000000)
        self.filterCutoffSpin.setValue(10.000000000000000)

        self.digitalFiltersLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.filterCutoffSpin)

        self.filterCutoffHighLabel = QLabel(self.digitalFiltersGroup)
        self.filterCutoffHighLabel.setObjectName("filterCutoffHighLabel")

        self.digitalFiltersLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.filterCutoffHighLabel)

        self.filterCutoffHighSpin = QDoubleSpinBox(self.digitalFiltersGroup)
        self.filterCutoffHighSpin.setObjectName("filterCutoffHighSpin")
        self.filterCutoffHighSpin.setMinimum(0.100000000000000)
        self.filterCutoffHighSpin.setMaximum(1000.000000000000000)
        self.filterCutoffHighSpin.setValue(50.000000000000000)

        self.digitalFiltersLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.filterCutoffHighSpin)

        self.filterOrderLabel = QLabel(self.digitalFiltersGroup)
        self.filterOrderLabel.setObjectName("filterOrderLabel")

        self.digitalFiltersLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.filterOrderLabel)

        self.filterOrderSpin = QSpinBox(self.digitalFiltersGroup)
        self.filterOrderSpin.setObjectName("filterOrderSpin")
        self.filterOrderSpin.setMinimum(1)
        self.filterOrderSpin.setMaximum(10)
        self.filterOrderSpin.setValue(4)

        self.digitalFiltersLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.filterOrderSpin)

        self.filterMethodLabel = QLabel(self.digitalFiltersGroup)
        self.filterMethodLabel.setObjectName("filterMethodLabel")

        self.digitalFiltersLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.filterMethodLabel)

        self.filterMethodCombo = QComboBox(self.digitalFiltersGroup)
        self.filterMethodCombo.addItem("")
        self.filterMethodCombo.addItem("")
        self.filterMethodCombo.addItem("")
        self.filterMethodCombo.addItem("")
        self.filterMethodCombo.addItem("")
        self.filterMethodCombo.setObjectName("filterMethodCombo")

        self.digitalFiltersLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.filterMethodCombo)

        self.filterButtonsLayout = QHBoxLayout()
        self.filterButtonsLayout.setObjectName("filterButtonsLayout")
        self.filterPreviewBtn = QPushButton(self.digitalFiltersGroup)
        self.filterPreviewBtn.setObjectName("filterPreviewBtn")

        self.filterButtonsLayout.addWidget(self.filterPreviewBtn)

        self.filterApplyBtn = QPushButton(self.digitalFiltersGroup)
        self.filterApplyBtn.setObjectName("filterApplyBtn")

        self.filterButtonsLayout.addWidget(self.filterApplyBtn)


        self.digitalFiltersLayout.setLayout(5, QFormLayout.ItemRole.SpanningRole, self.filterButtonsLayout)


        self.filtersContentLayout.addWidget(self.digitalFiltersGroup)

        self.filtersSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.filtersContentLayout.addItem(self.filtersSpacer)

        self.filtersScrollArea.setWidget(self.filtersScrollContent)

        self.filtersTabLayout.addWidget(self.filtersScrollArea)

        self.tabWidget.addTab(self.filtersTab, "")
        self.syncTab = QWidget()
        self.syncTab.setObjectName("syncTab")
        self.syncTabLayout = QVBoxLayout(self.syncTab)
        self.syncTabLayout.setObjectName("syncTabLayout")
        self.syncScrollArea = QScrollArea(self.syncTab)
        self.syncScrollArea.setObjectName("syncScrollArea")
        self.syncScrollArea.setWidgetResizable(True)
        self.syncScrollContent = QWidget()
        self.syncScrollContent.setObjectName("syncScrollContent")
        self.syncContentLayout = QVBoxLayout(self.syncScrollContent)
        self.syncContentLayout.setSpacing(8)
        self.syncContentLayout.setObjectName("syncContentLayout")
        self.syncDatasetsGroup = QGroupBox(self.syncScrollContent)
        self.syncDatasetsGroup.setObjectName("syncDatasetsGroup")
        self.syncDatasetsLayout = QVBoxLayout(self.syncDatasetsGroup)
        self.syncDatasetsLayout.setObjectName("syncDatasetsLayout")
        self.syncDatasetsList = QListWidget(self.syncDatasetsGroup)
        self.syncDatasetsList.setObjectName("syncDatasetsList")
        self.syncDatasetsList.setSelectionMode(QAbstractItemView.MultiSelection)
        self.syncDatasetsList.setMaximumHeight(150)

        self.syncDatasetsLayout.addWidget(self.syncDatasetsList)

        self.syncRefreshBtn = QPushButton(self.syncDatasetsGroup)
        self.syncRefreshBtn.setObjectName("syncRefreshBtn")

        self.syncDatasetsLayout.addWidget(self.syncRefreshBtn)


        self.syncContentLayout.addWidget(self.syncDatasetsGroup)

        self.syncMethodGroup = QGroupBox(self.syncScrollContent)
        self.syncMethodGroup.setObjectName("syncMethodGroup")
        self.syncMethodLayout = QFormLayout(self.syncMethodGroup)
        self.syncMethodLayout.setObjectName("syncMethodLayout")
        self.syncMethodLabel = QLabel(self.syncMethodGroup)
        self.syncMethodLabel.setObjectName("syncMethodLabel")

        self.syncMethodLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.syncMethodLabel)

        self.syncMethodCombo = QComboBox(self.syncMethodGroup)
        self.syncMethodCombo.addItem("")
        self.syncMethodCombo.addItem("")
        self.syncMethodCombo.setObjectName("syncMethodCombo")

        self.syncMethodLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.syncMethodCombo)


        self.syncContentLayout.addWidget(self.syncMethodGroup)

        self.syncGridGroup = QGroupBox(self.syncScrollContent)
        self.syncGridGroup.setObjectName("syncGridGroup")
        self.syncGridLayout = QFormLayout(self.syncGridGroup)
        self.syncGridLayout.setObjectName("syncGridLayout")
        self.syncGridMethodLabel = QLabel(self.syncGridGroup)
        self.syncGridMethodLabel.setObjectName("syncGridMethodLabel")

        self.syncGridLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.syncGridMethodLabel)

        self.syncGridMethodCombo = QComboBox(self.syncGridGroup)
        self.syncGridMethodCombo.addItem("")
        self.syncGridMethodCombo.addItem("")
        self.syncGridMethodCombo.addItem("")
        self.syncGridMethodCombo.addItem("")
        self.syncGridMethodCombo.setObjectName("syncGridMethodCombo")

        self.syncGridLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.syncGridMethodCombo)

        self.syncDtFixedCheck = QCheckBox(self.syncGridGroup)
        self.syncDtFixedCheck.setObjectName("syncDtFixedCheck")

        self.syncGridLayout.setWidget(1, QFormLayout.ItemRole.SpanningRole, self.syncDtFixedCheck)

        self.syncDtValueLabel = QLabel(self.syncGridGroup)
        self.syncDtValueLabel.setObjectName("syncDtValueLabel")

        self.syncGridLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.syncDtValueLabel)

        self.syncDtValueSpin = QDoubleSpinBox(self.syncGridGroup)
        self.syncDtValueSpin.setObjectName("syncDtValueSpin")
        self.syncDtValueSpin.setEnabled(False)
        self.syncDtValueSpin.setMinimum(0.001000000000000)
        self.syncDtValueSpin.setMaximum(1000.000000000000000)
        self.syncDtValueSpin.setValue(1.000000000000000)
        self.syncDtValueSpin.setDecimals(3)

        self.syncGridLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.syncDtValueSpin)


        self.syncContentLayout.addWidget(self.syncGridGroup)

        self.syncInterpGroup = QGroupBox(self.syncScrollContent)
        self.syncInterpGroup.setObjectName("syncInterpGroup")
        self.syncInterpLayout = QFormLayout(self.syncInterpGroup)
        self.syncInterpLayout.setObjectName("syncInterpLayout")
        self.syncInterpMethodLabel = QLabel(self.syncInterpGroup)
        self.syncInterpMethodLabel.setObjectName("syncInterpMethodLabel")

        self.syncInterpLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.syncInterpMethodLabel)

        self.syncInterpMethodCombo = QComboBox(self.syncInterpGroup)
        self.syncInterpMethodCombo.addItem("")
        self.syncInterpMethodCombo.addItem("")
        self.syncInterpMethodCombo.addItem("")
        self.syncInterpMethodCombo.setObjectName("syncInterpMethodCombo")

        self.syncInterpLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.syncInterpMethodCombo)


        self.syncContentLayout.addWidget(self.syncInterpGroup)

        self.kalmanGroup = QGroupBox(self.syncScrollContent)
        self.kalmanGroup.setObjectName("kalmanGroup")
        self.kalmanLayout = QFormLayout(self.kalmanGroup)
        self.kalmanLayout.setObjectName("kalmanLayout")
        self.syncProcessNoiseLabel = QLabel(self.kalmanGroup)
        self.syncProcessNoiseLabel.setObjectName("syncProcessNoiseLabel")

        self.kalmanLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.syncProcessNoiseLabel)

        self.syncProcessNoiseSpin = QDoubleSpinBox(self.kalmanGroup)
        self.syncProcessNoiseSpin.setObjectName("syncProcessNoiseSpin")
        self.syncProcessNoiseSpin.setMinimum(0.000100000000000)
        self.syncProcessNoiseSpin.setMaximum(1.000000000000000)
        self.syncProcessNoiseSpin.setValue(0.010000000000000)
        self.syncProcessNoiseSpin.setDecimals(4)

        self.kalmanLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.syncProcessNoiseSpin)

        self.syncMeasurementNoiseLabel = QLabel(self.kalmanGroup)
        self.syncMeasurementNoiseLabel.setObjectName("syncMeasurementNoiseLabel")

        self.kalmanLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.syncMeasurementNoiseLabel)

        self.syncMeasurementNoiseSpin = QDoubleSpinBox(self.kalmanGroup)
        self.syncMeasurementNoiseSpin.setObjectName("syncMeasurementNoiseSpin")
        self.syncMeasurementNoiseSpin.setMinimum(0.001000000000000)
        self.syncMeasurementNoiseSpin.setMaximum(10.000000000000000)
        self.syncMeasurementNoiseSpin.setValue(0.100000000000000)
        self.syncMeasurementNoiseSpin.setDecimals(3)

        self.kalmanLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.syncMeasurementNoiseSpin)


        self.syncContentLayout.addWidget(self.kalmanGroup)

        self.syncOutputGroup = QGroupBox(self.syncScrollContent)
        self.syncOutputGroup.setObjectName("syncOutputGroup")
        self.syncOutputLayout = QVBoxLayout(self.syncOutputGroup)
        self.syncOutputLayout.setObjectName("syncOutputLayout")
        self.syncCreateNewCheck = QCheckBox(self.syncOutputGroup)
        self.syncCreateNewCheck.setObjectName("syncCreateNewCheck")
        self.syncCreateNewCheck.setChecked(True)

        self.syncOutputLayout.addWidget(self.syncCreateNewCheck)

        self.syncKeepOriginalCheck = QCheckBox(self.syncOutputGroup)
        self.syncKeepOriginalCheck.setObjectName("syncKeepOriginalCheck")
        self.syncKeepOriginalCheck.setChecked(True)

        self.syncOutputLayout.addWidget(self.syncKeepOriginalCheck)


        self.syncContentLayout.addWidget(self.syncOutputGroup)

        self.syncButtonsLayout = QHBoxLayout()
        self.syncButtonsLayout.setObjectName("syncButtonsLayout")
        self.syncPreviewBtn = QPushButton(self.syncScrollContent)
        self.syncPreviewBtn.setObjectName("syncPreviewBtn")

        self.syncButtonsLayout.addWidget(self.syncPreviewBtn)

        self.syncApplyBtn = QPushButton(self.syncScrollContent)
        self.syncApplyBtn.setObjectName("syncApplyBtn")

        self.syncButtonsLayout.addWidget(self.syncApplyBtn)


        self.syncContentLayout.addLayout(self.syncButtonsLayout)

        self.syncInfoLabel = QLabel(self.syncScrollContent)
        self.syncInfoLabel.setObjectName("syncInfoLabel")
        self.syncInfoLabel.setWordWrap(True)

        self.syncContentLayout.addWidget(self.syncInfoLabel)

        self.syncSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.syncContentLayout.addItem(self.syncSpacer)

        self.syncScrollArea.setWidget(self.syncScrollContent)

        self.syncTabLayout.addWidget(self.syncScrollArea)

        self.tabWidget.addTab(self.syncTab, "")
        self.streamingTab = QWidget()
        self.streamingTab.setObjectName("streamingTab")
        self.streamingTabLayout = QVBoxLayout(self.streamingTab)
        self.streamingTabLayout.setObjectName("streamingTabLayout")
        self.streamingScrollArea = QScrollArea(self.streamingTab)
        self.streamingScrollArea.setObjectName("streamingScrollArea")
        self.streamingScrollArea.setWidgetResizable(True)
        self.streamingScrollContent = QWidget()
        self.streamingScrollContent.setObjectName("streamingScrollContent")
        self.streamingContentLayout = QVBoxLayout(self.streamingScrollContent)
        self.streamingContentLayout.setSpacing(8)
        self.streamingContentLayout.setObjectName("streamingContentLayout")
        self.streamControlGroup = QGroupBox(self.streamingScrollContent)
        self.streamControlGroup.setObjectName("streamControlGroup")
        self.streamControlLayout = QFormLayout(self.streamControlGroup)
        self.streamControlLayout.setObjectName("streamControlLayout")
        self.streamStatusLabelTitle = QLabel(self.streamControlGroup)
        self.streamStatusLabelTitle.setObjectName("streamStatusLabelTitle")

        self.streamControlLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.streamStatusLabelTitle)

        self.streamStatus = QLabel(self.streamControlGroup)
        self.streamStatus.setObjectName("streamStatus")

        self.streamControlLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.streamStatus)

        self.streamRateLabel = QLabel(self.streamControlGroup)
        self.streamRateLabel.setObjectName("streamRateLabel")

        self.streamControlLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.streamRateLabel)

        self.streamRateSpin = QSpinBox(self.streamControlGroup)
        self.streamRateSpin.setObjectName("streamRateSpin")
        self.streamRateSpin.setMinimum(1)
        self.streamRateSpin.setMaximum(60)
        self.streamRateSpin.setValue(10)

        self.streamControlLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.streamRateSpin)

        self.streamWindowLabel = QLabel(self.streamControlGroup)
        self.streamWindowLabel.setObjectName("streamWindowLabel")

        self.streamControlLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.streamWindowLabel)

        self.streamWindowSpin = QSpinBox(self.streamControlGroup)
        self.streamWindowSpin.setObjectName("streamWindowSpin")
        self.streamWindowSpin.setMinimum(100)
        self.streamWindowSpin.setMaximum(100000)
        self.streamWindowSpin.setValue(1000)

        self.streamControlLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.streamWindowSpin)

        self.streamScrollModeLabel = QLabel(self.streamControlGroup)
        self.streamScrollModeLabel.setObjectName("streamScrollModeLabel")

        self.streamControlLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.streamScrollModeLabel)

        self.streamScrollModeCombo = QComboBox(self.streamControlGroup)
        self.streamScrollModeCombo.addItem("")
        self.streamScrollModeCombo.addItem("")
        self.streamScrollModeCombo.addItem("")
        self.streamScrollModeCombo.setObjectName("streamScrollModeCombo")

        self.streamControlLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.streamScrollModeCombo)


        self.streamingContentLayout.addWidget(self.streamControlGroup)

        self.bufferGroup = QGroupBox(self.streamingScrollContent)
        self.bufferGroup.setObjectName("bufferGroup")
        self.bufferLayout = QFormLayout(self.bufferGroup)
        self.bufferLayout.setObjectName("bufferLayout")
        self.bufferSizeLabel = QLabel(self.bufferGroup)
        self.bufferSizeLabel.setObjectName("bufferSizeLabel")

        self.bufferLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.bufferSizeLabel)

        self.bufferSizeSpin = QSpinBox(self.bufferGroup)
        self.bufferSizeSpin.setObjectName("bufferSizeSpin")
        self.bufferSizeSpin.setMinimum(1000)
        self.bufferSizeSpin.setMaximum(10000000)
        self.bufferSizeSpin.setValue(100000)

        self.bufferLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.bufferSizeSpin)

        self.bufferCurrentLabelTitle = QLabel(self.bufferGroup)
        self.bufferCurrentLabelTitle.setObjectName("bufferCurrentLabelTitle")

        self.bufferLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.bufferCurrentLabelTitle)

        self.bufferCurrentLabel = QLabel(self.bufferGroup)
        self.bufferCurrentLabel.setObjectName("bufferCurrentLabel")

        self.bufferLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.bufferCurrentLabel)

        self.autoDecimateCheck = QCheckBox(self.bufferGroup)
        self.autoDecimateCheck.setObjectName("autoDecimateCheck")
        self.autoDecimateCheck.setChecked(True)

        self.bufferLayout.setWidget(2, QFormLayout.ItemRole.SpanningRole, self.autoDecimateCheck)


        self.streamingContentLayout.addWidget(self.bufferGroup)

        self.streamButtonsLayout = QHBoxLayout()
        self.streamButtonsLayout.setObjectName("streamButtonsLayout")
        self.streamStartBtn = QPushButton(self.streamingScrollContent)
        self.streamStartBtn.setObjectName("streamStartBtn")

        self.streamButtonsLayout.addWidget(self.streamStartBtn)

        self.streamPauseBtn = QPushButton(self.streamingScrollContent)
        self.streamPauseBtn.setObjectName("streamPauseBtn")

        self.streamButtonsLayout.addWidget(self.streamPauseBtn)

        self.streamStopBtn = QPushButton(self.streamingScrollContent)
        self.streamStopBtn.setObjectName("streamStopBtn")

        self.streamButtonsLayout.addWidget(self.streamStopBtn)


        self.streamingContentLayout.addLayout(self.streamButtonsLayout)

        self.streamStatsGroup = QGroupBox(self.streamingScrollContent)
        self.streamStatsGroup.setObjectName("streamStatsGroup")
        self.streamStatsLayout = QFormLayout(self.streamStatsGroup)
        self.streamStatsLayout.setObjectName("streamStatsLayout")
        self.streamFpsLabelTitle = QLabel(self.streamStatsGroup)
        self.streamFpsLabelTitle.setObjectName("streamFpsLabelTitle")

        self.streamStatsLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.streamFpsLabelTitle)

        self.streamFpsLabel = QLabel(self.streamStatsGroup)
        self.streamFpsLabel.setObjectName("streamFpsLabel")

        self.streamStatsLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.streamFpsLabel)

        self.streamLatencyLabelTitle = QLabel(self.streamStatsGroup)
        self.streamLatencyLabelTitle.setObjectName("streamLatencyLabelTitle")

        self.streamStatsLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.streamLatencyLabelTitle)

        self.streamLatencyLabel = QLabel(self.streamStatsGroup)
        self.streamLatencyLabel.setObjectName("streamLatencyLabel")

        self.streamStatsLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.streamLatencyLabel)

        self.streamPointsSecLabelTitle = QLabel(self.streamStatsGroup)
        self.streamPointsSecLabelTitle.setObjectName("streamPointsSecLabelTitle")

        self.streamStatsLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.streamPointsSecLabelTitle)

        self.streamPointsSecLabel = QLabel(self.streamStatsGroup)
        self.streamPointsSecLabel.setObjectName("streamPointsSecLabel")

        self.streamStatsLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.streamPointsSecLabel)


        self.streamingContentLayout.addWidget(self.streamStatsGroup)

        self.streamingSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.streamingContentLayout.addItem(self.streamingSpacer)

        self.streamingScrollArea.setWidget(self.streamingScrollContent)

        self.streamingTabLayout.addWidget(self.streamingScrollArea)

        self.tabWidget.addTab(self.streamingTab, "")
        self.exportTab = QWidget()
        self.exportTab.setObjectName("exportTab")
        self.exportTabLayout = QVBoxLayout(self.exportTab)
        self.exportTabLayout.setObjectName("exportTabLayout")
        self.exportScrollArea = QScrollArea(self.exportTab)
        self.exportScrollArea.setObjectName("exportScrollArea")
        self.exportScrollArea.setWidgetResizable(True)
        self.exportScrollContent = QWidget()
        self.exportScrollContent.setObjectName("exportScrollContent")
        self.exportContentLayout = QVBoxLayout(self.exportScrollContent)
        self.exportContentLayout.setSpacing(8)
        self.exportContentLayout.setObjectName("exportContentLayout")
        self.exportFormatGroup = QGroupBox(self.exportScrollContent)
        self.exportFormatGroup.setObjectName("exportFormatGroup")
        self.exportFormatLayout = QFormLayout(self.exportFormatGroup)
        self.exportFormatLayout.setObjectName("exportFormatLayout")
        self.exportFormatLabel = QLabel(self.exportFormatGroup)
        self.exportFormatLabel.setObjectName("exportFormatLabel")

        self.exportFormatLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.exportFormatLabel)

        self.exportFormatCombo = QComboBox(self.exportFormatGroup)
        self.exportFormatCombo.addItem("")
        self.exportFormatCombo.addItem("")
        self.exportFormatCombo.addItem("")
        self.exportFormatCombo.addItem("")
        self.exportFormatCombo.addItem("")
        self.exportFormatCombo.setObjectName("exportFormatCombo")

        self.exportFormatLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.exportFormatCombo)


        self.exportContentLayout.addWidget(self.exportFormatGroup)

        self.exportOptionsGroup = QGroupBox(self.exportScrollContent)
        self.exportOptionsGroup.setObjectName("exportOptionsGroup")
        self.exportOptionsLayout = QVBoxLayout(self.exportOptionsGroup)
        self.exportOptionsLayout.setObjectName("exportOptionsLayout")
        self.exportMetadataCheck = QCheckBox(self.exportOptionsGroup)
        self.exportMetadataCheck.setObjectName("exportMetadataCheck")
        self.exportMetadataCheck.setChecked(True)

        self.exportOptionsLayout.addWidget(self.exportMetadataCheck)

        self.exportTimestampsCheck = QCheckBox(self.exportOptionsGroup)
        self.exportTimestampsCheck.setObjectName("exportTimestampsCheck")
        self.exportTimestampsCheck.setChecked(True)

        self.exportOptionsLayout.addWidget(self.exportTimestampsCheck)

        self.exportInterpFlagsCheck = QCheckBox(self.exportOptionsGroup)
        self.exportInterpFlagsCheck.setObjectName("exportInterpFlagsCheck")

        self.exportOptionsLayout.addWidget(self.exportInterpFlagsCheck)

        self.exportSelectedOnlyCheck = QCheckBox(self.exportOptionsGroup)
        self.exportSelectedOnlyCheck.setObjectName("exportSelectedOnlyCheck")

        self.exportOptionsLayout.addWidget(self.exportSelectedOnlyCheck)


        self.exportContentLayout.addWidget(self.exportOptionsGroup)

        self.exportButtonsLayout = QVBoxLayout()
        self.exportButtonsLayout.setObjectName("exportButtonsLayout")
        self.exportDataBtn = QPushButton(self.exportScrollContent)
        self.exportDataBtn.setObjectName("exportDataBtn")

        self.exportButtonsLayout.addWidget(self.exportDataBtn)

        self.exportSessionBtn = QPushButton(self.exportScrollContent)
        self.exportSessionBtn.setObjectName("exportSessionBtn")

        self.exportButtonsLayout.addWidget(self.exportSessionBtn)

        self.exportPlotBtn = QPushButton(self.exportScrollContent)
        self.exportPlotBtn.setObjectName("exportPlotBtn")

        self.exportButtonsLayout.addWidget(self.exportPlotBtn)


        self.exportContentLayout.addLayout(self.exportButtonsLayout)

        self.exportSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.exportContentLayout.addItem(self.exportSpacer)

        self.exportScrollArea.setWidget(self.exportScrollContent)

        self.exportTabLayout.addWidget(self.exportScrollArea)

        self.tabWidget.addTab(self.exportTab, "")
        self.settingsTab = QWidget()
        self.settingsTab.setObjectName("settingsTab")
        self.settingsTabLayout = QVBoxLayout(self.settingsTab)
        self.settingsTabLayout.setObjectName("settingsTabLayout")
        self.settingsScrollArea = QScrollArea(self.settingsTab)
        self.settingsScrollArea.setObjectName("settingsScrollArea")
        self.settingsScrollArea.setWidgetResizable(True)
        self.settingsScrollContent = QWidget()
        self.settingsScrollContent.setObjectName("settingsScrollContent")
        self.settingsContentLayout = QVBoxLayout(self.settingsScrollContent)
        self.settingsContentLayout.setSpacing(8)
        self.settingsContentLayout.setObjectName("settingsContentLayout")
        self.vizGroup = QGroupBox(self.settingsScrollContent)
        self.vizGroup.setObjectName("vizGroup")
        self.vizLayout = QFormLayout(self.vizGroup)
        self.vizLayout.setObjectName("vizLayout")
        self.themeLabel = QLabel(self.vizGroup)
        self.themeLabel.setObjectName("themeLabel")

        self.vizLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.themeLabel)

        self.themeCombo = QComboBox(self.vizGroup)
        self.themeCombo.addItem("")
        self.themeCombo.addItem("")
        self.themeCombo.addItem("")
        self.themeCombo.addItem("")
        self.themeCombo.setObjectName("themeCombo")

        self.vizLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.themeCombo)

        self.plotStyleLabel = QLabel(self.vizGroup)
        self.plotStyleLabel.setObjectName("plotStyleLabel")

        self.vizLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.plotStyleLabel)

        self.plotStyleCombo = QComboBox(self.vizGroup)
        self.plotStyleCombo.addItem("")
        self.plotStyleCombo.addItem("")
        self.plotStyleCombo.addItem("")
        self.plotStyleCombo.addItem("")
        self.plotStyleCombo.addItem("")
        self.plotStyleCombo.setObjectName("plotStyleCombo")

        self.vizLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.plotStyleCombo)

        self.antialiasingCheck = QCheckBox(self.vizGroup)
        self.antialiasingCheck.setObjectName("antialiasingCheck")
        self.antialiasingCheck.setChecked(True)

        self.vizLayout.setWidget(2, QFormLayout.ItemRole.SpanningRole, self.antialiasingCheck)

        self.plotDpiLabel = QLabel(self.vizGroup)
        self.plotDpiLabel.setObjectName("plotDpiLabel")

        self.vizLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.plotDpiLabel)

        self.plotDpiSpin = QSpinBox(self.vizGroup)
        self.plotDpiSpin.setObjectName("plotDpiSpin")
        self.plotDpiSpin.setMinimum(72)
        self.plotDpiSpin.setMaximum(300)
        self.plotDpiSpin.setValue(100)

        self.vizLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.plotDpiSpin)


        self.settingsContentLayout.addWidget(self.vizGroup)

        self.perfGroup = QGroupBox(self.settingsScrollContent)
        self.perfGroup.setObjectName("perfGroup")
        self.perfLayout = QFormLayout(self.perfGroup)
        self.perfLayout.setObjectName("perfLayout")
        self.directRenderLabel = QLabel(self.perfGroup)
        self.directRenderLabel.setObjectName("directRenderLabel")

        self.perfLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.directRenderLabel)

        self.directRenderLimitSpin = QSpinBox(self.perfGroup)
        self.directRenderLimitSpin.setObjectName("directRenderLimitSpin")
        self.directRenderLimitSpin.setMinimum(1000)
        self.directRenderLimitSpin.setMaximum(1000000)
        self.directRenderLimitSpin.setValue(10000)

        self.perfLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.directRenderLimitSpin)

        self.targetPointsLabel = QLabel(self.perfGroup)
        self.targetPointsLabel.setObjectName("targetPointsLabel")

        self.perfLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.targetPointsLabel)

        self.targetDisplayPointsSpin = QSpinBox(self.perfGroup)
        self.targetDisplayPointsSpin.setObjectName("targetDisplayPointsSpin")
        self.targetDisplayPointsSpin.setMinimum(1000)
        self.targetDisplayPointsSpin.setMaximum(50000)
        self.targetDisplayPointsSpin.setValue(5000)

        self.perfLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.targetDisplayPointsSpin)

        self.decimationLabel = QLabel(self.perfGroup)
        self.decimationLabel.setObjectName("decimationLabel")

        self.perfLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.decimationLabel)

        self.decimationMethodCombo = QComboBox(self.perfGroup)
        self.decimationMethodCombo.addItem("")
        self.decimationMethodCombo.addItem("")
        self.decimationMethodCombo.addItem("")
        self.decimationMethodCombo.addItem("")
        self.decimationMethodCombo.setObjectName("decimationMethodCombo")

        self.perfLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.decimationMethodCombo)

        self.useThreadingCheck = QCheckBox(self.perfGroup)
        self.useThreadingCheck.setObjectName("useThreadingCheck")
        self.useThreadingCheck.setChecked(True)

        self.perfLayout.setWidget(3, QFormLayout.ItemRole.SpanningRole, self.useThreadingCheck)


        self.settingsContentLayout.addWidget(self.perfGroup)

        self.dataGroup = QGroupBox(self.settingsScrollContent)
        self.dataGroup.setObjectName("dataGroup")
        self.dataLayout = QFormLayout(self.dataGroup)
        self.dataLayout.setObjectName("dataLayout")
        self.dateFormatLabel = QLabel(self.dataGroup)
        self.dateFormatLabel.setObjectName("dateFormatLabel")

        self.dataLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.dateFormatLabel)

        self.dateFormatCombo = QComboBox(self.dataGroup)
        self.dateFormatCombo.addItem("")
        self.dateFormatCombo.addItem("")
        self.dateFormatCombo.addItem("")
        self.dateFormatCombo.addItem("")
        self.dateFormatCombo.setObjectName("dateFormatCombo")

        self.dataLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.dateFormatCombo)

        self.numericPrecisionLabel = QLabel(self.dataGroup)
        self.numericPrecisionLabel.setObjectName("numericPrecisionLabel")

        self.dataLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.numericPrecisionLabel)

        self.numericPrecisionSpin = QSpinBox(self.dataGroup)
        self.numericPrecisionSpin.setObjectName("numericPrecisionSpin")
        self.numericPrecisionSpin.setMinimum(1)
        self.numericPrecisionSpin.setMaximum(15)
        self.numericPrecisionSpin.setValue(6)

        self.dataLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.numericPrecisionSpin)

        self.autoDetectTypesCheck = QCheckBox(self.dataGroup)
        self.autoDetectTypesCheck.setObjectName("autoDetectTypesCheck")
        self.autoDetectTypesCheck.setChecked(True)

        self.dataLayout.setWidget(2, QFormLayout.ItemRole.SpanningRole, self.autoDetectTypesCheck)


        self.settingsContentLayout.addWidget(self.dataGroup)

        self.settingsButtonsLayout = QHBoxLayout()
        self.settingsButtonsLayout.setObjectName("settingsButtonsLayout")
        self.settingsApplyBtn = QPushButton(self.settingsScrollContent)
        self.settingsApplyBtn.setObjectName("settingsApplyBtn")

        self.settingsButtonsLayout.addWidget(self.settingsApplyBtn)

        self.settingsResetBtn = QPushButton(self.settingsScrollContent)
        self.settingsResetBtn.setObjectName("settingsResetBtn")

        self.settingsButtonsLayout.addWidget(self.settingsResetBtn)


        self.settingsContentLayout.addLayout(self.settingsButtonsLayout)

        self.settingsSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.settingsContentLayout.addItem(self.settingsSpacer)

        self.settingsScrollArea.setWidget(self.settingsScrollContent)

        self.settingsTabLayout.addWidget(self.settingsScrollArea)

        self.tabWidget.addTab(self.settingsTab, "")
        self.historyTab = QWidget()
        self.historyTab.setObjectName("historyTab")
        self.historyTabLayout = QVBoxLayout(self.historyTab)
        self.historyTabLayout.setObjectName("historyTabLayout")
        self.historyList = QListWidget(self.historyTab)
        self.historyList.setObjectName("historyList")

        self.historyTabLayout.addWidget(self.historyList)

        self.clearHistoryBtn = QPushButton(self.historyTab)
        self.clearHistoryBtn.setObjectName("clearHistoryBtn")

        self.historyTabLayout.addWidget(self.clearHistoryBtn)

        self.tabWidget.addTab(self.historyTab, "")

        self.mainLayout.addWidget(self.tabWidget)


        self.retranslateUi(OperationsPanel)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(OperationsPanel)
    # setupUi

    def retranslateUi(self, OperationsPanel):
        OperationsPanel.setWindowTitle(QCoreApplication.translate("OperationsPanel", "Operations Panel", None))
        self.headerLabel.setText(QCoreApplication.translate("OperationsPanel", "\u2699\ufe0f Opera\u00e7\u00f5es", None))
        self.headerLabel.setStyleSheet(QCoreApplication.translate("OperationsPanel", "color: #0d6efd; padding: 4px;", None))
        self.seriesGroup.setTitle(QCoreApplication.translate("OperationsPanel", "\ud83c\udfaf S\u00e9rie para Opera\u00e7\u00f5es", None))
        self.seriesLabel.setText(QCoreApplication.translate("OperationsPanel", "S\u00e9rie:", None))
        self.seriesCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", "(Nenhum dataset carregado)", None))

#if QT_CONFIG(tooltip)
        self.seriesCombo.setToolTip(QCoreApplication.translate("OperationsPanel", "Selecione a s\u00e9rie para aplicar as opera\u00e7\u00f5es", None))
#endif // QT_CONFIG(tooltip)
        self.interpMethodGroup.setTitle(QCoreApplication.translate("OperationsPanel", "\ud83d\udcd0 M\u00e9todo", None))
        self.interpMethodLabel.setText(QCoreApplication.translate("OperationsPanel", "M\u00e9todo:", None))
        self.interpMethodCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", "linear", None))
        self.interpMethodCombo.setItemText(1, QCoreApplication.translate("OperationsPanel", "cubic_spline", None))
        self.interpMethodCombo.setItemText(2, QCoreApplication.translate("OperationsPanel", "smoothing_spline", None))
        self.interpMethodCombo.setItemText(3, QCoreApplication.translate("OperationsPanel", "akima", None))
        self.interpMethodCombo.setItemText(4, QCoreApplication.translate("OperationsPanel", "pchip", None))
        self.interpMethodCombo.setItemText(5, QCoreApplication.translate("OperationsPanel", "polynomial", None))
        self.interpMethodCombo.setItemText(6, QCoreApplication.translate("OperationsPanel", "mls", None))
        self.interpMethodCombo.setItemText(7, QCoreApplication.translate("OperationsPanel", "gpr", None))
        self.interpMethodCombo.setItemText(8, QCoreApplication.translate("OperationsPanel", "lomb_scargle", None))
        self.interpMethodCombo.setItemText(9, QCoreApplication.translate("OperationsPanel", "resample_grid", None))

#if QT_CONFIG(tooltip)
        self.interpMethodCombo.setToolTip(QCoreApplication.translate("OperationsPanel", "M\u00e9todo de interpola\u00e7\u00e3o a utilizar", None))
#endif // QT_CONFIG(tooltip)
        self.interpParamsGroup.setTitle(QCoreApplication.translate("OperationsPanel", "\ud83d\udd27 Par\u00e2metros", None))
        self.interpPointsLabel.setText(QCoreApplication.translate("OperationsPanel", "Pontos:", None))
#if QT_CONFIG(tooltip)
        self.interpPointsSpin.setToolTip(QCoreApplication.translate("OperationsPanel", "N\u00famero de pontos de sa\u00edda", None))
#endif // QT_CONFIG(tooltip)
        self.interpSmoothLabel.setText(QCoreApplication.translate("OperationsPanel", "Suaviza\u00e7\u00e3o:", None))
#if QT_CONFIG(tooltip)
        self.interpSmoothSpin.setToolTip(QCoreApplication.translate("OperationsPanel", "Fator de suaviza\u00e7\u00e3o (0 = nenhuma)", None))
#endif // QT_CONFIG(tooltip)
        self.interpDegreeLabel.setText(QCoreApplication.translate("OperationsPanel", "Grau:", None))
#if QT_CONFIG(tooltip)
        self.interpDegreeSpin.setToolTip(QCoreApplication.translate("OperationsPanel", "Grau do polin\u00f4mio (para m\u00e9todos polinomiais)", None))
#endif // QT_CONFIG(tooltip)
        self.interpExtrapolateCheck.setText(QCoreApplication.translate("OperationsPanel", "Permitir extrapola\u00e7\u00e3o", None))
#if QT_CONFIG(tooltip)
        self.interpExtrapolateCheck.setToolTip(QCoreApplication.translate("OperationsPanel", "Extrapolar al\u00e9m do range dos dados", None))
#endif // QT_CONFIG(tooltip)
        self.interpPreviewBtn.setText(QCoreApplication.translate("OperationsPanel", "\ud83d\udc41\ufe0f Preview", None))
#if QT_CONFIG(tooltip)
        self.interpPreviewBtn.setToolTip(QCoreApplication.translate("OperationsPanel", "Visualizar resultado antes de aplicar", None))
#endif // QT_CONFIG(tooltip)
        self.interpApplyBtn.setText(QCoreApplication.translate("OperationsPanel", "\u2705 Aplicar", None))
#if QT_CONFIG(tooltip)
        self.interpApplyBtn.setToolTip(QCoreApplication.translate("OperationsPanel", "Aplicar interpola\u00e7\u00e3o \u00e0 s\u00e9rie selecionada", None))
#endif // QT_CONFIG(tooltip)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.interpTab), QCoreApplication.translate("OperationsPanel", "\ud83d\udcd0", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.interpTab), QCoreApplication.translate("OperationsPanel", "Interpola\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.derivGroup.setTitle(QCoreApplication.translate("OperationsPanel", "\ud83d\udcc8 Derivadas", None))
        self.derivOrderLabel.setText(QCoreApplication.translate("OperationsPanel", "Ordem:", None))
        self.derivOrderCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", "1\u00aa Ordem", None))
        self.derivOrderCombo.setItemText(1, QCoreApplication.translate("OperationsPanel", "2\u00aa Ordem", None))
        self.derivOrderCombo.setItemText(2, QCoreApplication.translate("OperationsPanel", "3\u00aa Ordem", None))

#if QT_CONFIG(tooltip)
        self.derivOrderCombo.setToolTip(QCoreApplication.translate("OperationsPanel", "Ordem da derivada", None))
#endif // QT_CONFIG(tooltip)
        self.derivMethodLabel.setText(QCoreApplication.translate("OperationsPanel", "M\u00e9todo:", None))
        self.derivMethodCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", "finite_diff", None))
        self.derivMethodCombo.setItemText(1, QCoreApplication.translate("OperationsPanel", "savitzky_golay", None))
        self.derivMethodCombo.setItemText(2, QCoreApplication.translate("OperationsPanel", "spline_derivative", None))

#if QT_CONFIG(tooltip)
        self.derivMethodCombo.setToolTip(QCoreApplication.translate("OperationsPanel", "M\u00e9todo de c\u00e1lculo da derivada", None))
#endif // QT_CONFIG(tooltip)
        self.derivWindowLabel.setText(QCoreApplication.translate("OperationsPanel", "Janela:", None))
#if QT_CONFIG(tooltip)
        self.derivWindowSpin.setToolTip(QCoreApplication.translate("OperationsPanel", "Tamanho da janela (para Savitzky-Golay)", None))
#endif // QT_CONFIG(tooltip)
        self.derivSmoothCheck.setText(QCoreApplication.translate("OperationsPanel", "Suavizar antes", None))
#if QT_CONFIG(tooltip)
        self.derivSmoothCheck.setToolTip(QCoreApplication.translate("OperationsPanel", "Aplicar suaviza\u00e7\u00e3o antes de derivar", None))
#endif // QT_CONFIG(tooltip)
        self.derivPreviewBtn.setText(QCoreApplication.translate("OperationsPanel", "\ud83d\udc41\ufe0f Preview", None))
        self.derivApplyBtn.setText(QCoreApplication.translate("OperationsPanel", "\ud83d\udcca Calcular Derivada", None))
        self.integGroup.setTitle(QCoreApplication.translate("OperationsPanel", "\u222b Integrais", None))
        self.integMethodLabel.setText(QCoreApplication.translate("OperationsPanel", "M\u00e9todo:", None))
        self.integMethodCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", "trapezoid", None))
        self.integMethodCombo.setItemText(1, QCoreApplication.translate("OperationsPanel", "simpson", None))
        self.integMethodCombo.setItemText(2, QCoreApplication.translate("OperationsPanel", "cumulative", None))

#if QT_CONFIG(tooltip)
        self.integMethodCombo.setToolTip(QCoreApplication.translate("OperationsPanel", "M\u00e9todo de integra\u00e7\u00e3o num\u00e9rica", None))
#endif // QT_CONFIG(tooltip)
        self.integPreviewBtn.setText(QCoreApplication.translate("OperationsPanel", "\ud83d\udc41\ufe0f Preview", None))
        self.integApplyBtn.setText(QCoreApplication.translate("OperationsPanel", "\ud83d\udcca Calcular Integral", None))
        self.areaGroup.setTitle(QCoreApplication.translate("OperationsPanel", "\ud83d\udccf \u00c1rea", None))
        self.areaTypeLabel.setText(QCoreApplication.translate("OperationsPanel", "Tipo:", None))
        self.areaTypeCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", "\u00c1rea sob a curva", None))
        self.areaTypeCombo.setItemText(1, QCoreApplication.translate("OperationsPanel", "\u00c1rea entre curvas", None))

#if QT_CONFIG(tooltip)
        self.areaTypeCombo.setToolTip(QCoreApplication.translate("OperationsPanel", "Tipo de c\u00e1lculo de \u00e1rea", None))
#endif // QT_CONFIG(tooltip)
        self.areaApplyBtn.setText(QCoreApplication.translate("OperationsPanel", "\ud83d\udcca Calcular \u00c1rea", None))
#if QT_CONFIG(tooltip)
        self.areaApplyBtn.setToolTip(QCoreApplication.translate("OperationsPanel", "Calcular \u00e1rea sob a curva ou entre curvas", None))
#endif // QT_CONFIG(tooltip)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.calculusTab), QCoreApplication.translate("OperationsPanel", "\ud83e\uddee", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.calculusTab), QCoreApplication.translate("OperationsPanel", "C\u00e1lculos (Derivadas/Integrais)", None))
#endif // QT_CONFIG(tooltip)
        self.smoothGroup.setTitle(QCoreApplication.translate("OperationsPanel", "\u3030\ufe0f Suaviza\u00e7\u00e3o", None))
        self.smoothMethodLabel.setText(QCoreApplication.translate("OperationsPanel", "M\u00e9todo:", None))
        self.smoothMethodCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", "gaussian", None))
        self.smoothMethodCombo.setItemText(1, QCoreApplication.translate("OperationsPanel", "moving_average", None))
        self.smoothMethodCombo.setItemText(2, QCoreApplication.translate("OperationsPanel", "savitzky_golay", None))
        self.smoothMethodCombo.setItemText(3, QCoreApplication.translate("OperationsPanel", "median", None))
        self.smoothMethodCombo.setItemText(4, QCoreApplication.translate("OperationsPanel", "exponential", None))

#if QT_CONFIG(tooltip)
        self.smoothMethodCombo.setToolTip(QCoreApplication.translate("OperationsPanel", "M\u00e9todo de suaviza\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.smoothWindowLabel.setText(QCoreApplication.translate("OperationsPanel", "Janela:", None))
#if QT_CONFIG(tooltip)
        self.smoothWindowSpin.setToolTip(QCoreApplication.translate("OperationsPanel", "Tamanho da janela de suaviza\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.smoothSigmaLabel.setText(QCoreApplication.translate("OperationsPanel", "Sigma:", None))
#if QT_CONFIG(tooltip)
        self.smoothSigmaSpin.setToolTip(QCoreApplication.translate("OperationsPanel", "Sigma para filtro Gaussiano", None))
#endif // QT_CONFIG(tooltip)
        self.smoothPreviewBtn.setText(QCoreApplication.translate("OperationsPanel", "\ud83d\udc41\ufe0f Preview", None))
        self.smoothApplyBtn.setText(QCoreApplication.translate("OperationsPanel", "\u3030\ufe0f Aplicar Suaviza\u00e7\u00e3o", None))
        self.outlierGroup.setTitle(QCoreApplication.translate("OperationsPanel", "\ud83d\udeab Outliers", None))
        self.outlierMethodLabel.setText(QCoreApplication.translate("OperationsPanel", "M\u00e9todo:", None))
        self.outlierMethodCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", "zscore", None))
        self.outlierMethodCombo.setItemText(1, QCoreApplication.translate("OperationsPanel", "iqr", None))
        self.outlierMethodCombo.setItemText(2, QCoreApplication.translate("OperationsPanel", "mad", None))

#if QT_CONFIG(tooltip)
        self.outlierMethodCombo.setToolTip(QCoreApplication.translate("OperationsPanel", "M\u00e9todo de detec\u00e7\u00e3o de outliers", None))
#endif // QT_CONFIG(tooltip)
        self.outlierThresholdLabel.setText(QCoreApplication.translate("OperationsPanel", "Limiar:", None))
#if QT_CONFIG(tooltip)
        self.outlierThresholdSpin.setToolTip(QCoreApplication.translate("OperationsPanel", "Limiar para detec\u00e7\u00e3o (ex: 3 sigmas)", None))
#endif // QT_CONFIG(tooltip)
        self.outlierPreviewBtn.setText(QCoreApplication.translate("OperationsPanel", "\ud83d\udc41\ufe0f Preview", None))
        self.outlierApplyBtn.setText(QCoreApplication.translate("OperationsPanel", "\ud83d\udeab Remover Outliers", None))
        self.fftGroup.setTitle(QCoreApplication.translate("OperationsPanel", "\ud83d\udcca FFT Analysis", None))
        self.fftWindowLabel.setText(QCoreApplication.translate("OperationsPanel", "Window:", None))
        self.fftWindowCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", "hann", None))
        self.fftWindowCombo.setItemText(1, QCoreApplication.translate("OperationsPanel", "hamming", None))
        self.fftWindowCombo.setItemText(2, QCoreApplication.translate("OperationsPanel", "blackman", None))
        self.fftWindowCombo.setItemText(3, QCoreApplication.translate("OperationsPanel", "bartlett", None))
        self.fftWindowCombo.setItemText(4, QCoreApplication.translate("OperationsPanel", "none", None))

#if QT_CONFIG(tooltip)
        self.fftWindowCombo.setToolTip(QCoreApplication.translate("OperationsPanel", "Window function for FFT", None))
#endif // QT_CONFIG(tooltip)
        self.fftDetrendCheck.setText(QCoreApplication.translate("OperationsPanel", "Remove Trend", None))
#if QT_CONFIG(tooltip)
        self.fftDetrendCheck.setToolTip(QCoreApplication.translate("OperationsPanel", "Remove linear trend before FFT", None))
#endif // QT_CONFIG(tooltip)
        self.fftApplyBtn.setText(QCoreApplication.translate("OperationsPanel", "\ud83d\udcca Compute FFT", None))
#if QT_CONFIG(tooltip)
        self.fftApplyBtn.setToolTip(QCoreApplication.translate("OperationsPanel", "Calcular Transformada R\u00e1pida de Fourier", None))
#endif // QT_CONFIG(tooltip)
        self.corrGroup.setTitle(QCoreApplication.translate("OperationsPanel", "\ud83d\udd17 Correlation", None))
        self.corrModeLabel.setText(QCoreApplication.translate("OperationsPanel", "Mode:", None))
        self.corrModeCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", "auto", None))
        self.corrModeCombo.setItemText(1, QCoreApplication.translate("OperationsPanel", "cross", None))

#if QT_CONFIG(tooltip)
        self.corrModeCombo.setToolTip(QCoreApplication.translate("OperationsPanel", "Auto-correlation or cross-correlation", None))
#endif // QT_CONFIG(tooltip)
        self.corrNormalizeCheck.setText(QCoreApplication.translate("OperationsPanel", "Normalize", None))
#if QT_CONFIG(tooltip)
        self.corrNormalizeCheck.setToolTip(QCoreApplication.translate("OperationsPanel", "Normalize correlation to [-1, 1]", None))
#endif // QT_CONFIG(tooltip)
        self.corrApplyBtn.setText(QCoreApplication.translate("OperationsPanel", "\ud83d\udd17 Compute Correlation", None))
#if QT_CONFIG(tooltip)
        self.corrApplyBtn.setToolTip(QCoreApplication.translate("OperationsPanel", "Calcular auto-correla\u00e7\u00e3o ou correla\u00e7\u00e3o cruzada", None))
#endif // QT_CONFIG(tooltip)
        self.digitalFiltersGroup.setTitle(QCoreApplication.translate("OperationsPanel", "\ud83c\udf9b\ufe0f Digital Filters", None))
        self.filterTypeLabel.setText(QCoreApplication.translate("OperationsPanel", "Type:", None))
        self.filterTypeCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", "lowpass", None))
        self.filterTypeCombo.setItemText(1, QCoreApplication.translate("OperationsPanel", "highpass", None))
        self.filterTypeCombo.setItemText(2, QCoreApplication.translate("OperationsPanel", "bandpass", None))
        self.filterTypeCombo.setItemText(3, QCoreApplication.translate("OperationsPanel", "bandstop", None))

#if QT_CONFIG(tooltip)
        self.filterTypeCombo.setToolTip(QCoreApplication.translate("OperationsPanel", "Filter type", None))
#endif // QT_CONFIG(tooltip)
        self.filterCutoffLabel.setText(QCoreApplication.translate("OperationsPanel", "Cutoff (Hz):", None))
#if QT_CONFIG(tooltip)
        self.filterCutoffSpin.setToolTip(QCoreApplication.translate("OperationsPanel", "Cutoff frequency (Hz)", None))
#endif // QT_CONFIG(tooltip)
        self.filterCutoffHighLabel.setText(QCoreApplication.translate("OperationsPanel", "High Cutoff (Hz):", None))
#if QT_CONFIG(tooltip)
        self.filterCutoffHighSpin.setToolTip(QCoreApplication.translate("OperationsPanel", "High cutoff frequency (Hz)", None))
#endif // QT_CONFIG(tooltip)
        self.filterOrderLabel.setText(QCoreApplication.translate("OperationsPanel", "Order:", None))
#if QT_CONFIG(tooltip)
        self.filterOrderSpin.setToolTip(QCoreApplication.translate("OperationsPanel", "Filter order (higher = sharper)", None))
#endif // QT_CONFIG(tooltip)
        self.filterMethodLabel.setText(QCoreApplication.translate("OperationsPanel", "Method:", None))
        self.filterMethodCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", "butter", None))
        self.filterMethodCombo.setItemText(1, QCoreApplication.translate("OperationsPanel", "chebyshev1", None))
        self.filterMethodCombo.setItemText(2, QCoreApplication.translate("OperationsPanel", "chebyshev2", None))
        self.filterMethodCombo.setItemText(3, QCoreApplication.translate("OperationsPanel", "elliptic", None))
        self.filterMethodCombo.setItemText(4, QCoreApplication.translate("OperationsPanel", "bessel", None))

#if QT_CONFIG(tooltip)
        self.filterMethodCombo.setToolTip(QCoreApplication.translate("OperationsPanel", "Filter design method", None))
#endif // QT_CONFIG(tooltip)
        self.filterPreviewBtn.setText(QCoreApplication.translate("OperationsPanel", "\ud83d\udc41\ufe0f Preview", None))
        self.filterApplyBtn.setText(QCoreApplication.translate("OperationsPanel", "\ud83c\udf9b\ufe0f Apply Filter", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.filtersTab), QCoreApplication.translate("OperationsPanel", "\ud83c\udf9a\ufe0f", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.filtersTab), QCoreApplication.translate("OperationsPanel", "Filtros", None))
#endif // QT_CONFIG(tooltip)
        self.syncDatasetsGroup.setTitle(QCoreApplication.translate("OperationsPanel", "\ud83d\udcca Datasets para Sincronizar", None))
#if QT_CONFIG(tooltip)
        self.syncDatasetsList.setToolTip(QCoreApplication.translate("OperationsPanel", "Selecione os datasets para sincronizar (m\u00ednimo 2)", None))
#endif // QT_CONFIG(tooltip)
        self.syncRefreshBtn.setText(QCoreApplication.translate("OperationsPanel", "\ud83d\udd04 Atualizar Lista", None))
#if QT_CONFIG(tooltip)
        self.syncRefreshBtn.setToolTip(QCoreApplication.translate("OperationsPanel", "Recarregar lista de datasets dispon\u00edveis", None))
#endif // QT_CONFIG(tooltip)
        self.syncMethodGroup.setTitle(QCoreApplication.translate("OperationsPanel", "\u2699\ufe0f M\u00e9todo de Sincroniza\u00e7\u00e3o", None))
        self.syncMethodLabel.setText(QCoreApplication.translate("OperationsPanel", "M\u00e9todo:", None))
        self.syncMethodCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", "common_grid_interpolate", None))
        self.syncMethodCombo.setItemText(1, QCoreApplication.translate("OperationsPanel", "kalman_align", None))

#if QT_CONFIG(tooltip)
        self.syncMethodCombo.setToolTip(QCoreApplication.translate("OperationsPanel", "common_grid_interpolate: Interpola todas as s\u00e9ries para uma grade temporal comum\n"
"kalman_align: Usa filtro de Kalman para alinhamento suave", None))
#endif // QT_CONFIG(tooltip)
        self.syncGridGroup.setTitle(QCoreApplication.translate("OperationsPanel", "\ud83d\udccf Grade Temporal", None))
        self.syncGridMethodLabel.setText(QCoreApplication.translate("OperationsPanel", "C\u00e1lculo dt:", None))
        self.syncGridMethodCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", "median", None))
        self.syncGridMethodCombo.setItemText(1, QCoreApplication.translate("OperationsPanel", "min", None))
        self.syncGridMethodCombo.setItemText(2, QCoreApplication.translate("OperationsPanel", "max", None))
        self.syncGridMethodCombo.setItemText(3, QCoreApplication.translate("OperationsPanel", "mean", None))

#if QT_CONFIG(tooltip)
        self.syncGridMethodCombo.setToolTip(QCoreApplication.translate("OperationsPanel", "Como calcular o intervalo de tempo (dt):\n"
"median: Mediana dos intervalos (mais robusto)\n"
"min: Menor intervalo (mais pontos)\n"
"max: Maior intervalo (menos pontos)\n"
"mean: M\u00e9dia dos intervalos", None))
#endif // QT_CONFIG(tooltip)
        self.syncDtFixedCheck.setText(QCoreApplication.translate("OperationsPanel", "Usar dt fixo", None))
#if QT_CONFIG(tooltip)
        self.syncDtFixedCheck.setToolTip(QCoreApplication.translate("OperationsPanel", "Definir intervalo de tempo manualmente", None))
#endif // QT_CONFIG(tooltip)
        self.syncDtValueLabel.setText(QCoreApplication.translate("OperationsPanel", "dt fixo:", None))
#if QT_CONFIG(tooltip)
        self.syncDtValueSpin.setToolTip(QCoreApplication.translate("OperationsPanel", "Intervalo de tempo fixo em segundos", None))
#endif // QT_CONFIG(tooltip)
        self.syncDtValueSpin.setSuffix(QCoreApplication.translate("OperationsPanel", " s", None))
        self.syncInterpGroup.setTitle(QCoreApplication.translate("OperationsPanel", "\ud83d\udcd0 Interpola\u00e7\u00e3o", None))
        self.syncInterpMethodLabel.setText(QCoreApplication.translate("OperationsPanel", "M\u00e9todo:", None))
        self.syncInterpMethodCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", "linear", None))
        self.syncInterpMethodCombo.setItemText(1, QCoreApplication.translate("OperationsPanel", "cubic", None))
        self.syncInterpMethodCombo.setItemText(2, QCoreApplication.translate("OperationsPanel", "nearest", None))

#if QT_CONFIG(tooltip)
        self.syncInterpMethodCombo.setToolTip(QCoreApplication.translate("OperationsPanel", "M\u00e9todo de interpola\u00e7\u00e3o para grade comum:\n"
"linear: Interpola\u00e7\u00e3o linear (r\u00e1pido)\n"
"cubic: Spline c\u00fabica (suave)\n"
"nearest: Vizinho mais pr\u00f3ximo (preserva valores)", None))
#endif // QT_CONFIG(tooltip)
        self.kalmanGroup.setTitle(QCoreApplication.translate("OperationsPanel", "\ud83c\udfaf Filtro Kalman", None))
        self.syncProcessNoiseLabel.setText(QCoreApplication.translate("OperationsPanel", "Process Noise:", None))
#if QT_CONFIG(tooltip)
        self.syncProcessNoiseSpin.setToolTip(QCoreApplication.translate("OperationsPanel", "Ru\u00eddo do processo (menor = mais suave)", None))
#endif // QT_CONFIG(tooltip)
        self.syncMeasurementNoiseLabel.setText(QCoreApplication.translate("OperationsPanel", "Measurement Noise:", None))
#if QT_CONFIG(tooltip)
        self.syncMeasurementNoiseSpin.setToolTip(QCoreApplication.translate("OperationsPanel", "Ru\u00eddo da medi\u00e7\u00e3o (menor = mais confian\u00e7a nos dados)", None))
#endif // QT_CONFIG(tooltip)
        self.syncOutputGroup.setTitle(QCoreApplication.translate("OperationsPanel", "\ud83d\udce4 Sa\u00edda", None))
        self.syncCreateNewCheck.setText(QCoreApplication.translate("OperationsPanel", "Criar novo dataset sincronizado", None))
#if QT_CONFIG(tooltip)
        self.syncCreateNewCheck.setToolTip(QCoreApplication.translate("OperationsPanel", "Criar um novo dataset com todas as s\u00e9ries sincronizadas", None))
#endif // QT_CONFIG(tooltip)
        self.syncKeepOriginalCheck.setText(QCoreApplication.translate("OperationsPanel", "Manter datasets originais", None))
#if QT_CONFIG(tooltip)
        self.syncKeepOriginalCheck.setToolTip(QCoreApplication.translate("OperationsPanel", "N\u00e3o modificar os datasets originais", None))
#endif // QT_CONFIG(tooltip)
        self.syncPreviewBtn.setText(QCoreApplication.translate("OperationsPanel", "\ud83d\udc41\ufe0f Preview", None))
#if QT_CONFIG(tooltip)
        self.syncPreviewBtn.setToolTip(QCoreApplication.translate("OperationsPanel", "Visualizar resultado da sincroniza\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.syncApplyBtn.setText(QCoreApplication.translate("OperationsPanel", "\ud83d\udd17 Sincronizar", None))
#if QT_CONFIG(tooltip)
        self.syncApplyBtn.setToolTip(QCoreApplication.translate("OperationsPanel", "Aplicar sincroniza\u00e7\u00e3o aos datasets selecionados", None))
#endif // QT_CONFIG(tooltip)
        self.syncInfoLabel.setText(QCoreApplication.translate("OperationsPanel", "\ud83d\udca1 A sincroniza\u00e7\u00e3o alinha m\u00faltiplos datasets para uma\n"
"grade temporal comum, permitindo compara\u00e7\u00f5es diretas.", None))
        self.syncInfoLabel.setStyleSheet(QCoreApplication.translate("OperationsPanel", "color: #6c757d; font-size: 10px;", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.syncTab), QCoreApplication.translate("OperationsPanel", "\ud83d\udd17", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.syncTab), QCoreApplication.translate("OperationsPanel", "Sincroniza\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.streamControlGroup.setTitle(QCoreApplication.translate("OperationsPanel", "\ud83d\udce1 Controle de Streaming", None))
        self.streamStatusLabelTitle.setText(QCoreApplication.translate("OperationsPanel", "Status:", None))
        self.streamStatus.setText(QCoreApplication.translate("OperationsPanel", "\u23f9\ufe0f Parado", None))
        self.streamStatus.setStyleSheet(QCoreApplication.translate("OperationsPanel", "font-weight: bold; color: #6c757d;", None))
        self.streamRateLabel.setText(QCoreApplication.translate("OperationsPanel", "Taxa:", None))
#if QT_CONFIG(tooltip)
        self.streamRateSpin.setToolTip(QCoreApplication.translate("OperationsPanel", "Taxa de atualiza\u00e7\u00e3o do gr\u00e1fico (frames por segundo)", None))
#endif // QT_CONFIG(tooltip)
        self.streamRateSpin.setSuffix(QCoreApplication.translate("OperationsPanel", " FPS", None))
        self.streamWindowLabel.setText(QCoreApplication.translate("OperationsPanel", "Janela:", None))
#if QT_CONFIG(tooltip)
        self.streamWindowSpin.setToolTip(QCoreApplication.translate("OperationsPanel", "N\u00famero de pontos vis\u00edveis na janela", None))
#endif // QT_CONFIG(tooltip)
        self.streamScrollModeLabel.setText(QCoreApplication.translate("OperationsPanel", "Scroll:", None))
        self.streamScrollModeCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", "Auto-scroll", None))
        self.streamScrollModeCombo.setItemText(1, QCoreApplication.translate("OperationsPanel", "Fixo", None))
        self.streamScrollModeCombo.setItemText(2, QCoreApplication.translate("OperationsPanel", "Follow Last", None))

#if QT_CONFIG(tooltip)
        self.streamScrollModeCombo.setToolTip(QCoreApplication.translate("OperationsPanel", "Modo de rolagem do gr\u00e1fico", None))
#endif // QT_CONFIG(tooltip)
        self.bufferGroup.setTitle(QCoreApplication.translate("OperationsPanel", "\ud83d\udcca Buffer de Dados", None))
        self.bufferSizeLabel.setText(QCoreApplication.translate("OperationsPanel", "Tamanho:", None))
#if QT_CONFIG(tooltip)
        self.bufferSizeSpin.setToolTip(QCoreApplication.translate("OperationsPanel", "Tamanho m\u00e1ximo do buffer de dados", None))
#endif // QT_CONFIG(tooltip)
        self.bufferCurrentLabelTitle.setText(QCoreApplication.translate("OperationsPanel", "Atual:", None))
        self.bufferCurrentLabel.setText(QCoreApplication.translate("OperationsPanel", "0 / 100000", None))
        self.bufferCurrentLabel.setStyleSheet(QCoreApplication.translate("OperationsPanel", "color: #6c757d;", None))
        self.autoDecimateCheck.setText(QCoreApplication.translate("OperationsPanel", "Auto-decima\u00e7\u00e3o", None))
#if QT_CONFIG(tooltip)
        self.autoDecimateCheck.setToolTip(QCoreApplication.translate("OperationsPanel", "Reduzir automaticamente pontos para melhor performance", None))
#endif // QT_CONFIG(tooltip)
        self.streamStartBtn.setText(QCoreApplication.translate("OperationsPanel", "\u25b6\ufe0f Iniciar", None))
#if QT_CONFIG(tooltip)
        self.streamStartBtn.setToolTip(QCoreApplication.translate("OperationsPanel", "Iniciar streaming de dados", None))
#endif // QT_CONFIG(tooltip)
        self.streamPauseBtn.setText(QCoreApplication.translate("OperationsPanel", "\u23f8\ufe0f Pausar", None))
#if QT_CONFIG(tooltip)
        self.streamPauseBtn.setToolTip(QCoreApplication.translate("OperationsPanel", "Pausar streaming", None))
#endif // QT_CONFIG(tooltip)
        self.streamStopBtn.setText(QCoreApplication.translate("OperationsPanel", "\u23f9\ufe0f Parar", None))
#if QT_CONFIG(tooltip)
        self.streamStopBtn.setToolTip(QCoreApplication.translate("OperationsPanel", "Parar streaming e limpar buffer", None))
#endif // QT_CONFIG(tooltip)
        self.streamStatsGroup.setTitle(QCoreApplication.translate("OperationsPanel", "\ud83d\udcc8 Estat\u00edsticas em Tempo Real", None))
        self.streamFpsLabelTitle.setText(QCoreApplication.translate("OperationsPanel", "FPS Real:", None))
        self.streamFpsLabel.setText(QCoreApplication.translate("OperationsPanel", "0 FPS", None))
        self.streamLatencyLabelTitle.setText(QCoreApplication.translate("OperationsPanel", "Lat\u00eancia:", None))
        self.streamLatencyLabel.setText(QCoreApplication.translate("OperationsPanel", "0 ms", None))
        self.streamPointsSecLabelTitle.setText(QCoreApplication.translate("OperationsPanel", "Pontos/s:", None))
        self.streamPointsSecLabel.setText(QCoreApplication.translate("OperationsPanel", "0 pts/s", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.streamingTab), QCoreApplication.translate("OperationsPanel", "\ud83d\udce1", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.streamingTab), QCoreApplication.translate("OperationsPanel", "Streaming", None))
#endif // QT_CONFIG(tooltip)
        self.exportFormatGroup.setTitle(QCoreApplication.translate("OperationsPanel", "\ud83d\udcc4 Formato", None))
        self.exportFormatLabel.setText(QCoreApplication.translate("OperationsPanel", "Formato:", None))
        self.exportFormatCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", "CSV", None))
        self.exportFormatCombo.setItemText(1, QCoreApplication.translate("OperationsPanel", "Excel (.xlsx)", None))
        self.exportFormatCombo.setItemText(2, QCoreApplication.translate("OperationsPanel", "Parquet", None))
        self.exportFormatCombo.setItemText(3, QCoreApplication.translate("OperationsPanel", "HDF5", None))
        self.exportFormatCombo.setItemText(4, QCoreApplication.translate("OperationsPanel", "JSON", None))

#if QT_CONFIG(tooltip)
        self.exportFormatCombo.setToolTip(QCoreApplication.translate("OperationsPanel", "Formato de exporta\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.exportOptionsGroup.setTitle(QCoreApplication.translate("OperationsPanel", "\u2699\ufe0f Op\u00e7\u00f5es", None))
        self.exportMetadataCheck.setText(QCoreApplication.translate("OperationsPanel", "Incluir metadados", None))
#if QT_CONFIG(tooltip)
        self.exportMetadataCheck.setToolTip(QCoreApplication.translate("OperationsPanel", "Incluir informa\u00e7\u00f5es de processamento", None))
#endif // QT_CONFIG(tooltip)
        self.exportTimestampsCheck.setText(QCoreApplication.translate("OperationsPanel", "Incluir timestamps", None))
#if QT_CONFIG(tooltip)
        self.exportTimestampsCheck.setToolTip(QCoreApplication.translate("OperationsPanel", "Exportar coluna de timestamps", None))
#endif // QT_CONFIG(tooltip)
        self.exportInterpFlagsCheck.setText(QCoreApplication.translate("OperationsPanel", "Flags de interpola\u00e7\u00e3o", None))
#if QT_CONFIG(tooltip)
        self.exportInterpFlagsCheck.setToolTip(QCoreApplication.translate("OperationsPanel", "Marcar pontos interpolados", None))
#endif // QT_CONFIG(tooltip)
        self.exportSelectedOnlyCheck.setText(QCoreApplication.translate("OperationsPanel", "Apenas s\u00e9ries selecionadas", None))
#if QT_CONFIG(tooltip)
        self.exportSelectedOnlyCheck.setToolTip(QCoreApplication.translate("OperationsPanel", "Exportar apenas s\u00e9ries selecionadas", None))
#endif // QT_CONFIG(tooltip)
        self.exportDataBtn.setText(QCoreApplication.translate("OperationsPanel", "\ud83d\udcbe Exportar Dados", None))
#if QT_CONFIG(tooltip)
        self.exportDataBtn.setToolTip(QCoreApplication.translate("OperationsPanel", "Exportar dados para arquivo", None))
#endif // QT_CONFIG(tooltip)
        self.exportSessionBtn.setText(QCoreApplication.translate("OperationsPanel", "\ud83d\udce6 Exportar Sess\u00e3o", None))
#if QT_CONFIG(tooltip)
        self.exportSessionBtn.setToolTip(QCoreApplication.translate("OperationsPanel", "Exportar configura\u00e7\u00e3o e estado da sess\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.exportPlotBtn.setText(QCoreApplication.translate("OperationsPanel", "\ud83d\uddbc\ufe0f Exportar Gr\u00e1fico", None))
#if QT_CONFIG(tooltip)
        self.exportPlotBtn.setToolTip(QCoreApplication.translate("OperationsPanel", "Exportar visualiza\u00e7\u00e3o atual como imagem", None))
#endif // QT_CONFIG(tooltip)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.exportTab), QCoreApplication.translate("OperationsPanel", "\ud83d\udcbe", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.exportTab), QCoreApplication.translate("OperationsPanel", "Exporta\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.vizGroup.setTitle(QCoreApplication.translate("OperationsPanel", "\ud83d\udcca Visualiza\u00e7\u00e3o", None))
        self.themeLabel.setText(QCoreApplication.translate("OperationsPanel", "Tema:", None))
        self.themeCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", "Claro", None))
        self.themeCombo.setItemText(1, QCoreApplication.translate("OperationsPanel", "Escuro", None))
        self.themeCombo.setItemText(2, QCoreApplication.translate("OperationsPanel", "Alto Contraste", None))
        self.themeCombo.setItemText(3, QCoreApplication.translate("OperationsPanel", "Sistema", None))

#if QT_CONFIG(tooltip)
        self.themeCombo.setToolTip(QCoreApplication.translate("OperationsPanel", "Tema de cores da aplica\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.plotStyleLabel.setText(QCoreApplication.translate("OperationsPanel", "Estilo Gr\u00e1fico:", None))
        self.plotStyleCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", "default", None))
        self.plotStyleCombo.setItemText(1, QCoreApplication.translate("OperationsPanel", "seaborn", None))
        self.plotStyleCombo.setItemText(2, QCoreApplication.translate("OperationsPanel", "ggplot", None))
        self.plotStyleCombo.setItemText(3, QCoreApplication.translate("OperationsPanel", "dark_background", None))
        self.plotStyleCombo.setItemText(4, QCoreApplication.translate("OperationsPanel", "bmh", None))

#if QT_CONFIG(tooltip)
        self.plotStyleCombo.setToolTip(QCoreApplication.translate("OperationsPanel", "Estilo dos gr\u00e1ficos matplotlib", None))
#endif // QT_CONFIG(tooltip)
        self.antialiasingCheck.setText(QCoreApplication.translate("OperationsPanel", "Anti-aliasing", None))
#if QT_CONFIG(tooltip)
        self.antialiasingCheck.setToolTip(QCoreApplication.translate("OperationsPanel", "Suaviza\u00e7\u00e3o de linhas nos gr\u00e1ficos", None))
#endif // QT_CONFIG(tooltip)
        self.plotDpiLabel.setText(QCoreApplication.translate("OperationsPanel", "DPI:", None))
#if QT_CONFIG(tooltip)
        self.plotDpiSpin.setToolTip(QCoreApplication.translate("OperationsPanel", "Resolu\u00e7\u00e3o dos gr\u00e1ficos (DPI)", None))
#endif // QT_CONFIG(tooltip)
        self.perfGroup.setTitle(QCoreApplication.translate("OperationsPanel", "\u26a1 Performance", None))
        self.directRenderLabel.setText(QCoreApplication.translate("OperationsPanel", "Render Direto:", None))
#if QT_CONFIG(tooltip)
        self.directRenderLimitSpin.setToolTip(QCoreApplication.translate("OperationsPanel", "Pontos m\u00e1ximos para renderiza\u00e7\u00e3o direta sem decima\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.targetPointsLabel.setText(QCoreApplication.translate("OperationsPanel", "Pontos Alvo:", None))
#if QT_CONFIG(tooltip)
        self.targetDisplayPointsSpin.setToolTip(QCoreApplication.translate("OperationsPanel", "N\u00famero alvo de pontos ap\u00f3s decima\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.decimationLabel.setText(QCoreApplication.translate("OperationsPanel", "Decima\u00e7\u00e3o:", None))
        self.decimationMethodCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", "MINMAX", None))
        self.decimationMethodCombo.setItemText(1, QCoreApplication.translate("OperationsPanel", "LTTB", None))
        self.decimationMethodCombo.setItemText(2, QCoreApplication.translate("OperationsPanel", "RANDOM", None))
        self.decimationMethodCombo.setItemText(3, QCoreApplication.translate("OperationsPanel", "EVERY_NTH", None))

#if QT_CONFIG(tooltip)
        self.decimationMethodCombo.setToolTip(QCoreApplication.translate("OperationsPanel", "Algoritmo de decima\u00e7\u00e3o para grandes volumes", None))
#endif // QT_CONFIG(tooltip)
        self.useThreadingCheck.setText(QCoreApplication.translate("OperationsPanel", "Multi-threading", None))
#if QT_CONFIG(tooltip)
        self.useThreadingCheck.setToolTip(QCoreApplication.translate("OperationsPanel", "Usar threads para opera\u00e7\u00f5es pesadas", None))
#endif // QT_CONFIG(tooltip)
        self.dataGroup.setTitle(QCoreApplication.translate("OperationsPanel", "\ud83d\udcc1 Dados", None))
        self.dateFormatLabel.setText(QCoreApplication.translate("OperationsPanel", "Formato Data:", None))
        self.dateFormatCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", "%Y-%m-%d %H:%M:%S", None))
        self.dateFormatCombo.setItemText(1, QCoreApplication.translate("OperationsPanel", "%d/%m/%Y %H:%M:%S", None))
        self.dateFormatCombo.setItemText(2, QCoreApplication.translate("OperationsPanel", "%m/%d/%Y %H:%M:%S", None))
        self.dateFormatCombo.setItemText(3, QCoreApplication.translate("OperationsPanel", "ISO 8601", None))

#if QT_CONFIG(tooltip)
        self.dateFormatCombo.setToolTip(QCoreApplication.translate("OperationsPanel", "Formato padr\u00e3o para exibi\u00e7\u00e3o de datas", None))
#endif // QT_CONFIG(tooltip)
        self.numericPrecisionLabel.setText(QCoreApplication.translate("OperationsPanel", "Precis\u00e3o:", None))
#if QT_CONFIG(tooltip)
        self.numericPrecisionSpin.setToolTip(QCoreApplication.translate("OperationsPanel", "Casas decimais para exibi\u00e7\u00e3o de n\u00fameros", None))
#endif // QT_CONFIG(tooltip)
        self.autoDetectTypesCheck.setText(QCoreApplication.translate("OperationsPanel", "Auto-detectar tipos", None))
#if QT_CONFIG(tooltip)
        self.autoDetectTypesCheck.setToolTip(QCoreApplication.translate("OperationsPanel", "Detectar automaticamente tipos de dados ao carregar", None))
#endif // QT_CONFIG(tooltip)
        self.settingsApplyBtn.setText(QCoreApplication.translate("OperationsPanel", "\u2705 Aplicar", None))
#if QT_CONFIG(tooltip)
        self.settingsApplyBtn.setToolTip(QCoreApplication.translate("OperationsPanel", "Aplicar configura\u00e7\u00f5es", None))
#endif // QT_CONFIG(tooltip)
        self.settingsResetBtn.setText(QCoreApplication.translate("OperationsPanel", "\ud83d\udd04 Restaurar Padr\u00f5es", None))
#if QT_CONFIG(tooltip)
        self.settingsResetBtn.setToolTip(QCoreApplication.translate("OperationsPanel", "Restaurar todas as configura\u00e7\u00f5es para os valores padr\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.settingsTab), QCoreApplication.translate("OperationsPanel", "\u2699\ufe0f", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.settingsTab), QCoreApplication.translate("OperationsPanel", "Configura\u00e7\u00f5es", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.historyList.setToolTip(QCoreApplication.translate("OperationsPanel", "Hist\u00f3rico de opera\u00e7\u00f5es realizadas (duplo-clique para repetir)", None))
#endif // QT_CONFIG(tooltip)
        self.clearHistoryBtn.setText(QCoreApplication.translate("OperationsPanel", "\ud83d\uddd1\ufe0f Limpar Hist\u00f3rico", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.historyTab), QCoreApplication.translate("OperationsPanel", "\ud83d\udcdc", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.historyTab), QCoreApplication.translate("OperationsPanel", "Hist\u00f3rico", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

