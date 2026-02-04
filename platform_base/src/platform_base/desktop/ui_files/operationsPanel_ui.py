# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'operationsPanel.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QSpinBox, QTabWidget,
    QVBoxLayout, QWidget)

from platform_base.ui.panels.operations_panel import StableComboBox

class Ui_OperationsPanel(object):
    def setupUi(self, OperationsPanel):
        if not OperationsPanel.objectName():
            OperationsPanel.setObjectName(u"OperationsPanel")
        OperationsPanel.resize(350, 700)
        OperationsPanel.setMinimumSize(QSize(150, 400))
        OperationsPanel.setStyleSheet(u"\n"
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
"QPushButton[objectName=\"secondary\"] {\n"
"    background-color: #6c757d;\n"
"}\n"
"QPushButton[objectName=\"success\"] {\n"
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
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(4, 4, 4, 4)
        self.headerLabel = QLabel(OperationsPanel)
        self.headerLabel.setObjectName(u"headerLabel")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.headerLabel.setFont(font)

        self.mainLayout.addWidget(self.headerLabel)

        self.seriesGroup = QGroupBox(OperationsPanel)
        self.seriesGroup.setObjectName(u"seriesGroup")
        self.seriesLayout = QFormLayout(self.seriesGroup)
        self.seriesLayout.setObjectName(u"seriesLayout")
        self.seriesLayout.setContentsMargins(6, 10, 6, 6)
        self.seriesLabel = QLabel(self.seriesGroup)
        self.seriesLabel.setObjectName(u"seriesLabel")

        self.seriesLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.seriesLabel)

        self.seriesCombo = QComboBox(self.seriesGroup)
        self.seriesCombo.addItem("")
        self.seriesCombo.setObjectName(u"seriesCombo")
        self.seriesCombo.setEnabled(False)
        self.seriesCombo.setMinimumSize(QSize(150, 0))

        self.seriesLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.seriesCombo)


        self.mainLayout.addWidget(self.seriesGroup)

        self.tabWidget = QTabWidget(OperationsPanel)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setTabPosition(QTabWidget.North)
        self.tabWidget.setUsesScrollButtons(True)
        self.interpTab = QWidget()
        self.interpTab.setObjectName(u"interpTab")
        self.interpTabLayout = QVBoxLayout(self.interpTab)
        self.interpTabLayout.setObjectName(u"interpTabLayout")
        self.interpScrollArea = QScrollArea(self.interpTab)
        self.interpScrollArea.setObjectName(u"interpScrollArea")
        self.interpScrollArea.setWidgetResizable(True)
        self.interpScrollContent = QWidget()
        self.interpScrollContent.setObjectName(u"interpScrollContent")
        self.interpContentLayout = QVBoxLayout(self.interpScrollContent)
        self.interpContentLayout.setSpacing(8)
        self.interpContentLayout.setObjectName(u"interpContentLayout")
        self.interpMethodGroup = QGroupBox(self.interpScrollContent)
        self.interpMethodGroup.setObjectName(u"interpMethodGroup")
        self.interpMethodLayout = QFormLayout(self.interpMethodGroup)
        self.interpMethodLayout.setObjectName(u"interpMethodLayout")
        self.interpMethodLabel = QLabel(self.interpMethodGroup)
        self.interpMethodLabel.setObjectName(u"interpMethodLabel")

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
        self.interpMethodCombo.setObjectName(u"interpMethodCombo")

        self.interpMethodLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.interpMethodCombo)


        self.interpContentLayout.addWidget(self.interpMethodGroup)

        self.interpParamsGroup = QGroupBox(self.interpScrollContent)
        self.interpParamsGroup.setObjectName(u"interpParamsGroup")
        self.interpParamsLayout = QFormLayout(self.interpParamsGroup)
        self.interpParamsLayout.setObjectName(u"interpParamsLayout")
        self.interpPointsLabel = QLabel(self.interpParamsGroup)
        self.interpPointsLabel.setObjectName(u"interpPointsLabel")

        self.interpParamsLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.interpPointsLabel)

        self.interpPointsSpin = QSpinBox(self.interpParamsGroup)
        self.interpPointsSpin.setObjectName(u"interpPointsSpin")
        self.interpPointsSpin.setMinimum(10)
        self.interpPointsSpin.setMaximum(100000)
        self.interpPointsSpin.setValue(1000)

        self.interpParamsLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.interpPointsSpin)

        self.interpSmoothLabel = QLabel(self.interpParamsGroup)
        self.interpSmoothLabel.setObjectName(u"interpSmoothLabel")

        self.interpParamsLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.interpSmoothLabel)

        self.interpSmoothSpin = QDoubleSpinBox(self.interpParamsGroup)
        self.interpSmoothSpin.setObjectName(u"interpSmoothSpin")
        self.interpSmoothSpin.setDecimals(2)
        self.interpSmoothSpin.setMaximum(1.000000000000000)
        self.interpSmoothSpin.setSingleStep(0.010000000000000)

        self.interpParamsLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.interpSmoothSpin)

        self.interpDegreeLabel = QLabel(self.interpParamsGroup)
        self.interpDegreeLabel.setObjectName(u"interpDegreeLabel")

        self.interpParamsLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.interpDegreeLabel)

        self.interpDegreeSpin = QSpinBox(self.interpParamsGroup)
        self.interpDegreeSpin.setObjectName(u"interpDegreeSpin")
        self.interpDegreeSpin.setMinimum(1)
        self.interpDegreeSpin.setMaximum(10)
        self.interpDegreeSpin.setValue(3)

        self.interpParamsLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.interpDegreeSpin)

        self.interpExtrapolateCheck = QCheckBox(self.interpParamsGroup)
        self.interpExtrapolateCheck.setObjectName(u"interpExtrapolateCheck")

        self.interpParamsLayout.setWidget(3, QFormLayout.ItemRole.SpanningRole, self.interpExtrapolateCheck)


        self.interpContentLayout.addWidget(self.interpParamsGroup)

        self.interpButtonsLayout = QHBoxLayout()
        self.interpButtonsLayout.setObjectName(u"interpButtonsLayout")
        self.interpPreviewBtn = QPushButton(self.interpScrollContent)
        self.interpPreviewBtn.setObjectName(u"interpPreviewBtn")

        self.interpButtonsLayout.addWidget(self.interpPreviewBtn)

        self.interpApplyBtn = QPushButton(self.interpScrollContent)
        self.interpApplyBtn.setObjectName(u"interpApplyBtn")

        self.interpButtonsLayout.addWidget(self.interpApplyBtn)


        self.interpContentLayout.addLayout(self.interpButtonsLayout)

        self.interpSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.interpContentLayout.addItem(self.interpSpacer)

        self.interpScrollArea.setWidget(self.interpScrollContent)

        self.interpTabLayout.addWidget(self.interpScrollArea)

        self.tabWidget.addTab(self.interpTab, "")
        self.calculusTab = QWidget()
        self.calculusTab.setObjectName(u"calculusTab")
        self.calculusTabLayout = QVBoxLayout(self.calculusTab)
        self.calculusTabLayout.setObjectName(u"calculusTabLayout")
        self.calculusScrollArea = QScrollArea(self.calculusTab)
        self.calculusScrollArea.setObjectName(u"calculusScrollArea")
        self.calculusScrollArea.setWidgetResizable(True)
        self.calculusScrollContent = QWidget()
        self.calculusScrollContent.setObjectName(u"calculusScrollContent")
        self.calculusContentLayout = QVBoxLayout(self.calculusScrollContent)
        self.calculusContentLayout.setSpacing(8)
        self.calculusContentLayout.setObjectName(u"calculusContentLayout")
        self.derivGroup = QGroupBox(self.calculusScrollContent)
        self.derivGroup.setObjectName(u"derivGroup")
        self.derivLayout = QFormLayout(self.derivGroup)
        self.derivLayout.setObjectName(u"derivLayout")
        self.derivOrderLabel = QLabel(self.derivGroup)
        self.derivOrderLabel.setObjectName(u"derivOrderLabel")

        self.derivLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.derivOrderLabel)

        self.derivOrderCombo = QComboBox(self.derivGroup)
        self.derivOrderCombo.addItem("")
        self.derivOrderCombo.addItem("")
        self.derivOrderCombo.addItem("")
        self.derivOrderCombo.setObjectName(u"derivOrderCombo")

        self.derivLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.derivOrderCombo)

        self.derivMethodLabel = QLabel(self.derivGroup)
        self.derivMethodLabel.setObjectName(u"derivMethodLabel")

        self.derivLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.derivMethodLabel)

        self.derivMethodCombo = QComboBox(self.derivGroup)
        self.derivMethodCombo.addItem("")
        self.derivMethodCombo.addItem("")
        self.derivMethodCombo.addItem("")
        self.derivMethodCombo.setObjectName(u"derivMethodCombo")

        self.derivLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.derivMethodCombo)

        self.derivWindowLabel = QLabel(self.derivGroup)
        self.derivWindowLabel.setObjectName(u"derivWindowLabel")

        self.derivLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.derivWindowLabel)

        self.derivWindowSpin = QSpinBox(self.derivGroup)
        self.derivWindowSpin.setObjectName(u"derivWindowSpin")
        self.derivWindowSpin.setMinimum(3)
        self.derivWindowSpin.setMaximum(51)
        self.derivWindowSpin.setSingleStep(2)
        self.derivWindowSpin.setValue(7)

        self.derivLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.derivWindowSpin)

        self.derivSmoothCheck = QCheckBox(self.derivGroup)
        self.derivSmoothCheck.setObjectName(u"derivSmoothCheck")

        self.derivLayout.setWidget(3, QFormLayout.ItemRole.SpanningRole, self.derivSmoothCheck)

        self.derivButtonsLayout = QHBoxLayout()
        self.derivButtonsLayout.setObjectName(u"derivButtonsLayout")
        self.derivPreviewBtn = QPushButton(self.derivGroup)
        self.derivPreviewBtn.setObjectName(u"derivPreviewBtn")

        self.derivButtonsLayout.addWidget(self.derivPreviewBtn)

        self.derivApplyBtn = QPushButton(self.derivGroup)
        self.derivApplyBtn.setObjectName(u"derivApplyBtn")

        self.derivButtonsLayout.addWidget(self.derivApplyBtn)


        self.derivLayout.setLayout(4, QFormLayout.ItemRole.SpanningRole, self.derivButtonsLayout)


        self.calculusContentLayout.addWidget(self.derivGroup)

        self.integGroup = QGroupBox(self.calculusScrollContent)
        self.integGroup.setObjectName(u"integGroup")
        self.integLayout = QFormLayout(self.integGroup)
        self.integLayout.setObjectName(u"integLayout")
        self.integMethodLabel = QLabel(self.integGroup)
        self.integMethodLabel.setObjectName(u"integMethodLabel")

        self.integLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.integMethodLabel)

        self.integMethodCombo = QComboBox(self.integGroup)
        self.integMethodCombo.addItem("")
        self.integMethodCombo.addItem("")
        self.integMethodCombo.addItem("")
        self.integMethodCombo.setObjectName(u"integMethodCombo")

        self.integLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.integMethodCombo)

        self.integButtonsLayout = QHBoxLayout()
        self.integButtonsLayout.setObjectName(u"integButtonsLayout")
        self.integPreviewBtn = QPushButton(self.integGroup)
        self.integPreviewBtn.setObjectName(u"integPreviewBtn")

        self.integButtonsLayout.addWidget(self.integPreviewBtn)

        self.integApplyBtn = QPushButton(self.integGroup)
        self.integApplyBtn.setObjectName(u"integApplyBtn")

        self.integButtonsLayout.addWidget(self.integApplyBtn)


        self.integLayout.setLayout(1, QFormLayout.ItemRole.SpanningRole, self.integButtonsLayout)


        self.calculusContentLayout.addWidget(self.integGroup)

        self.calculusSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.calculusContentLayout.addItem(self.calculusSpacer)

        self.calculusScrollArea.setWidget(self.calculusScrollContent)

        self.calculusTabLayout.addWidget(self.calculusScrollArea)

        self.tabWidget.addTab(self.calculusTab, "")
        self.filtersTab = QWidget()
        self.filtersTab.setObjectName(u"filtersTab")
        self.filtersTabLayout = QVBoxLayout(self.filtersTab)
        self.filtersTabLayout.setObjectName(u"filtersTabLayout")
        self.filtersPlaceholder = QLabel(self.filtersTab)
        self.filtersPlaceholder.setObjectName(u"filtersPlaceholder")
        self.filtersPlaceholder.setAlignment(Qt.AlignCenter)

        self.filtersTabLayout.addWidget(self.filtersPlaceholder)

        self.tabWidget.addTab(self.filtersTab, "")
        self.syncTab = QWidget()
        self.syncTab.setObjectName(u"syncTab")
        self.syncTabLayout = QVBoxLayout(self.syncTab)
        self.syncTabLayout.setObjectName(u"syncTabLayout")
        self.syncPlaceholder = QLabel(self.syncTab)
        self.syncPlaceholder.setObjectName(u"syncPlaceholder")
        self.syncPlaceholder.setAlignment(Qt.AlignCenter)

        self.syncTabLayout.addWidget(self.syncPlaceholder)

        self.tabWidget.addTab(self.syncTab, "")
        self.streamingTab = QWidget()
        self.streamingTab.setObjectName(u"streamingTab")
        self.streamingTabLayout = QVBoxLayout(self.streamingTab)
        self.streamingTabLayout.setObjectName(u"streamingTabLayout")
        self.streamingPlaceholder = QLabel(self.streamingTab)
        self.streamingPlaceholder.setObjectName(u"streamingPlaceholder")
        self.streamingPlaceholder.setAlignment(Qt.AlignCenter)

        self.streamingTabLayout.addWidget(self.streamingPlaceholder)

        self.tabWidget.addTab(self.streamingTab, "")
        self.exportTab = QWidget()
        self.exportTab.setObjectName(u"exportTab")
        self.exportTabLayout = QVBoxLayout(self.exportTab)
        self.exportTabLayout.setObjectName(u"exportTabLayout")
        self.exportPlaceholder = QLabel(self.exportTab)
        self.exportPlaceholder.setObjectName(u"exportPlaceholder")
        self.exportPlaceholder.setAlignment(Qt.AlignCenter)

        self.exportTabLayout.addWidget(self.exportPlaceholder)

        self.tabWidget.addTab(self.exportTab, "")
        self.historyTab = QWidget()
        self.historyTab.setObjectName(u"historyTab")
        self.historyTabLayout = QVBoxLayout(self.historyTab)
        self.historyTabLayout.setObjectName(u"historyTabLayout")
        self.historyList = QListWidget(self.historyTab)
        self.historyList.setObjectName(u"historyList")

        self.historyTabLayout.addWidget(self.historyList)

        self.clearHistoryBtn = QPushButton(self.historyTab)
        self.clearHistoryBtn.setObjectName(u"clearHistoryBtn")

        self.historyTabLayout.addWidget(self.clearHistoryBtn)

        self.tabWidget.addTab(self.historyTab, "")

        self.mainLayout.addWidget(self.tabWidget)


        self.retranslateUi(OperationsPanel)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(OperationsPanel)
    # setupUi

    def retranslateUi(self, OperationsPanel):
        OperationsPanel.setWindowTitle(QCoreApplication.translate("OperationsPanel", u"Operations Panel", None))
        self.headerLabel.setText(QCoreApplication.translate("OperationsPanel", u"\u2699\ufe0f Opera\u00e7\u00f5es", None))
        self.headerLabel.setStyleSheet(QCoreApplication.translate("OperationsPanel", u"color: #0d6efd; padding: 4px;", None))
        self.seriesGroup.setTitle(QCoreApplication.translate("OperationsPanel", u"\ud83c\udfaf S\u00e9rie para Opera\u00e7\u00f5es", None))
        self.seriesLabel.setText(QCoreApplication.translate("OperationsPanel", u"S\u00e9rie:", None))
        self.seriesCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", u"(Nenhum dataset carregado)", None))

#if QT_CONFIG(tooltip)
        self.seriesCombo.setToolTip(QCoreApplication.translate("OperationsPanel", u"Selecione a s\u00e9rie para aplicar as opera\u00e7\u00f5es", None))
#endif // QT_CONFIG(tooltip)
        self.interpMethodGroup.setTitle(QCoreApplication.translate("OperationsPanel", u"\ud83d\udcd0 M\u00e9todo", None))
        self.interpMethodLabel.setText(QCoreApplication.translate("OperationsPanel", u"M\u00e9todo:", None))
        self.interpMethodCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", u"linear", None))
        self.interpMethodCombo.setItemText(1, QCoreApplication.translate("OperationsPanel", u"cubic_spline", None))
        self.interpMethodCombo.setItemText(2, QCoreApplication.translate("OperationsPanel", u"smoothing_spline", None))
        self.interpMethodCombo.setItemText(3, QCoreApplication.translate("OperationsPanel", u"akima", None))
        self.interpMethodCombo.setItemText(4, QCoreApplication.translate("OperationsPanel", u"pchip", None))
        self.interpMethodCombo.setItemText(5, QCoreApplication.translate("OperationsPanel", u"polynomial", None))
        self.interpMethodCombo.setItemText(6, QCoreApplication.translate("OperationsPanel", u"mls", None))
        self.interpMethodCombo.setItemText(7, QCoreApplication.translate("OperationsPanel", u"gpr", None))
        self.interpMethodCombo.setItemText(8, QCoreApplication.translate("OperationsPanel", u"lomb_scargle", None))
        self.interpMethodCombo.setItemText(9, QCoreApplication.translate("OperationsPanel", u"resample_grid", None))

#if QT_CONFIG(tooltip)
        self.interpMethodCombo.setToolTip(QCoreApplication.translate("OperationsPanel", u"M\u00e9todo de interpola\u00e7\u00e3o a utilizar", None))
#endif // QT_CONFIG(tooltip)
        self.interpParamsGroup.setTitle(QCoreApplication.translate("OperationsPanel", u"\ud83d\udd27 Par\u00e2metros", None))
        self.interpPointsLabel.setText(QCoreApplication.translate("OperationsPanel", u"Pontos:", None))
#if QT_CONFIG(tooltip)
        self.interpPointsSpin.setToolTip(QCoreApplication.translate("OperationsPanel", u"N\u00famero de pontos de sa\u00edda", None))
#endif // QT_CONFIG(tooltip)
        self.interpSmoothLabel.setText(QCoreApplication.translate("OperationsPanel", u"Suaviza\u00e7\u00e3o:", None))
#if QT_CONFIG(tooltip)
        self.interpSmoothSpin.setToolTip(QCoreApplication.translate("OperationsPanel", u"Fator de suaviza\u00e7\u00e3o (0 = nenhuma)", None))
#endif // QT_CONFIG(tooltip)
        self.interpDegreeLabel.setText(QCoreApplication.translate("OperationsPanel", u"Grau:", None))
#if QT_CONFIG(tooltip)
        self.interpDegreeSpin.setToolTip(QCoreApplication.translate("OperationsPanel", u"Grau do polin\u00f4mio (para m\u00e9todos polinomiais)", None))
#endif // QT_CONFIG(tooltip)
        self.interpExtrapolateCheck.setText(QCoreApplication.translate("OperationsPanel", u"Permitir extrapola\u00e7\u00e3o", None))
#if QT_CONFIG(tooltip)
        self.interpExtrapolateCheck.setToolTip(QCoreApplication.translate("OperationsPanel", u"Extrapolar al\u00e9m do range dos dados", None))
#endif // QT_CONFIG(tooltip)
        self.interpPreviewBtn.setText(QCoreApplication.translate("OperationsPanel", u"\ud83d\udc41\ufe0f Preview", None))
#if QT_CONFIG(tooltip)
        self.interpPreviewBtn.setToolTip(QCoreApplication.translate("OperationsPanel", u"Visualizar resultado antes de aplicar", None))
#endif // QT_CONFIG(tooltip)
        self.interpApplyBtn.setText(QCoreApplication.translate("OperationsPanel", u"\u2705 Aplicar", None))
#if QT_CONFIG(tooltip)
        self.interpApplyBtn.setToolTip(QCoreApplication.translate("OperationsPanel", u"Aplicar interpola\u00e7\u00e3o \u00e0 s\u00e9rie selecionada", None))
#endif // QT_CONFIG(tooltip)
        self.interpApplyBtn.setObjectName(QCoreApplication.translate("OperationsPanel", u"success", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.interpTab), QCoreApplication.translate("OperationsPanel", u"\ud83d\udcd0", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.interpTab), QCoreApplication.translate("OperationsPanel", u"Interpola\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.derivGroup.setTitle(QCoreApplication.translate("OperationsPanel", u"\ud83d\udcc8 Derivadas", None))
        self.derivOrderLabel.setText(QCoreApplication.translate("OperationsPanel", u"Ordem:", None))
        self.derivOrderCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", u"1\u00aa Ordem", None))
        self.derivOrderCombo.setItemText(1, QCoreApplication.translate("OperationsPanel", u"2\u00aa Ordem", None))
        self.derivOrderCombo.setItemText(2, QCoreApplication.translate("OperationsPanel", u"3\u00aa Ordem", None))

#if QT_CONFIG(tooltip)
        self.derivOrderCombo.setToolTip(QCoreApplication.translate("OperationsPanel", u"Ordem da derivada", None))
#endif // QT_CONFIG(tooltip)
        self.derivMethodLabel.setText(QCoreApplication.translate("OperationsPanel", u"M\u00e9todo:", None))
        self.derivMethodCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", u"finite_diff", None))
        self.derivMethodCombo.setItemText(1, QCoreApplication.translate("OperationsPanel", u"savitzky_golay", None))
        self.derivMethodCombo.setItemText(2, QCoreApplication.translate("OperationsPanel", u"spline_derivative", None))

#if QT_CONFIG(tooltip)
        self.derivMethodCombo.setToolTip(QCoreApplication.translate("OperationsPanel", u"M\u00e9todo de c\u00e1lculo da derivada", None))
#endif // QT_CONFIG(tooltip)
        self.derivWindowLabel.setText(QCoreApplication.translate("OperationsPanel", u"Janela:", None))
#if QT_CONFIG(tooltip)
        self.derivWindowSpin.setToolTip(QCoreApplication.translate("OperationsPanel", u"Tamanho da janela (para Savitzky-Golay)", None))
#endif // QT_CONFIG(tooltip)
        self.derivSmoothCheck.setText(QCoreApplication.translate("OperationsPanel", u"Suavizar antes", None))
#if QT_CONFIG(tooltip)
        self.derivSmoothCheck.setToolTip(QCoreApplication.translate("OperationsPanel", u"Aplicar suaviza\u00e7\u00e3o antes de derivar", None))
#endif // QT_CONFIG(tooltip)
        self.derivPreviewBtn.setText(QCoreApplication.translate("OperationsPanel", u"\ud83d\udc41\ufe0f Preview", None))
        self.derivPreviewBtn.setObjectName(QCoreApplication.translate("OperationsPanel", u"secondary", None))
        self.derivApplyBtn.setText(QCoreApplication.translate("OperationsPanel", u"\ud83d\udcca Calcular Derivada", None))
        self.integGroup.setTitle(QCoreApplication.translate("OperationsPanel", u"\u222b Integrais", None))
        self.integMethodLabel.setText(QCoreApplication.translate("OperationsPanel", u"M\u00e9todo:", None))
        self.integMethodCombo.setItemText(0, QCoreApplication.translate("OperationsPanel", u"trapezoid", None))
        self.integMethodCombo.setItemText(1, QCoreApplication.translate("OperationsPanel", u"simpson", None))
        self.integMethodCombo.setItemText(2, QCoreApplication.translate("OperationsPanel", u"cumulative", None))

#if QT_CONFIG(tooltip)
        self.integMethodCombo.setToolTip(QCoreApplication.translate("OperationsPanel", u"M\u00e9todo de integra\u00e7\u00e3o num\u00e9rica", None))
#endif // QT_CONFIG(tooltip)
        self.integPreviewBtn.setText(QCoreApplication.translate("OperationsPanel", u"\ud83d\udc41\ufe0f Preview", None))
        self.integPreviewBtn.setObjectName(QCoreApplication.translate("OperationsPanel", u"secondary", None))
        self.integApplyBtn.setText(QCoreApplication.translate("OperationsPanel", u"\ud83d\udcca Calcular Integral", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.calculusTab), QCoreApplication.translate("OperationsPanel", u"\ud83d\udcc8", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.calculusTab), QCoreApplication.translate("OperationsPanel", u"C\u00e1lculos (Derivadas/Integrais)", None))
#endif // QT_CONFIG(tooltip)
        self.filtersPlaceholder.setText(QCoreApplication.translate("OperationsPanel", u"Filtros (a ser implementado via promoted widget)", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.filtersTab), QCoreApplication.translate("OperationsPanel", u"\ud83d\udd27", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.filtersTab), QCoreApplication.translate("OperationsPanel", u"Filtros", None))
#endif // QT_CONFIG(tooltip)
        self.syncPlaceholder.setText(QCoreApplication.translate("OperationsPanel", u"Sincroniza\u00e7\u00e3o (a ser implementado via promoted widget)", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.syncTab), QCoreApplication.translate("OperationsPanel", u"\ud83d\udd04", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.syncTab), QCoreApplication.translate("OperationsPanel", u"Sincroniza\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.streamingPlaceholder.setText(QCoreApplication.translate("OperationsPanel", u"Streaming (a ser implementado via promoted widget)", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.streamingTab), QCoreApplication.translate("OperationsPanel", u"\u25b6\ufe0f", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.streamingTab), QCoreApplication.translate("OperationsPanel", u"Streaming", None))
#endif // QT_CONFIG(tooltip)
        self.exportPlaceholder.setText(QCoreApplication.translate("OperationsPanel", u"Exporta\u00e7\u00e3o (a ser implementado via promoted widget)", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.exportTab), QCoreApplication.translate("OperationsPanel", u"\ud83d\udce4", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.exportTab), QCoreApplication.translate("OperationsPanel", u"Exporta\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.historyList.setToolTip(QCoreApplication.translate("OperationsPanel", u"Hist\u00f3rico de opera\u00e7\u00f5es realizadas", None))
#endif // QT_CONFIG(tooltip)
        self.clearHistoryBtn.setText(QCoreApplication.translate("OperationsPanel", u"\ud83d\uddd1\ufe0f Limpar Hist\u00f3rico", None))
        self.clearHistoryBtn.setObjectName(QCoreApplication.translate("OperationsPanel", u"secondary", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.historyTab), QCoreApplication.translate("OperationsPanel", u"\ud83d\udcdc", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.historyTab), QCoreApplication.translate("OperationsPanel", u"Hist\u00f3rico", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

