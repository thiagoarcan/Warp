# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'filterDialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QDoubleSpinBox, QFormLayout,
    QGroupBox, QLabel, QSizePolicy, QSpacerItem,
    QSpinBox, QTabWidget, QVBoxLayout, QWidget)

class Ui_FilterDialog(object):
    def setupUi(self, FilterDialog):
        if not FilterDialog.objectName():
            FilterDialog.setObjectName(u"FilterDialog")
        FilterDialog.resize(650, 550)
        FilterDialog.setMinimumSize(QSize(600, 500))
        FilterDialog.setModal(True)
        self.mainLayout = QVBoxLayout(FilterDialog)
        self.mainLayout.setSpacing(12)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(16, 16, 16, 16)
        self.headerLabel = QLabel(FilterDialog)
        self.headerLabel.setObjectName(u"headerLabel")

        self.mainLayout.addWidget(self.headerLabel)

        self.filterTabs = QTabWidget(FilterDialog)
        self.filterTabs.setObjectName(u"filterTabs")
        self.butterworthTab = QWidget()
        self.butterworthTab.setObjectName(u"butterworthTab")
        self.butterworthTabLayout = QVBoxLayout(self.butterworthTab)
        self.butterworthTabLayout.setSpacing(10)
        self.butterworthTabLayout.setObjectName(u"butterworthTabLayout")
        self.butterTypeGroup = QGroupBox(self.butterworthTab)
        self.butterTypeGroup.setObjectName(u"butterTypeGroup")
        self.butterTypeLayout = QFormLayout(self.butterTypeGroup)
        self.butterTypeLayout.setObjectName(u"butterTypeLayout")
        self.butterTypeLabel = QLabel(self.butterTypeGroup)
        self.butterTypeLabel.setObjectName(u"butterTypeLabel")

        self.butterTypeLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.butterTypeLabel)

        self.butterType = QComboBox(self.butterTypeGroup)
        self.butterType.addItem("")
        self.butterType.addItem("")
        self.butterType.addItem("")
        self.butterType.addItem("")
        self.butterType.setObjectName(u"butterType")

        self.butterTypeLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.butterType)


        self.butterworthTabLayout.addWidget(self.butterTypeGroup)

        self.butterParamsGroup = QGroupBox(self.butterworthTab)
        self.butterParamsGroup.setObjectName(u"butterParamsGroup")
        self.butterParamsLayout = QFormLayout(self.butterParamsGroup)
        self.butterParamsLayout.setObjectName(u"butterParamsLayout")
        self.butterOrderLabel = QLabel(self.butterParamsGroup)
        self.butterOrderLabel.setObjectName(u"butterOrderLabel")

        self.butterParamsLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.butterOrderLabel)

        self.butterOrder = QSpinBox(self.butterParamsGroup)
        self.butterOrder.setObjectName(u"butterOrder")
        self.butterOrder.setMinimum(1)
        self.butterOrder.setMaximum(10)
        self.butterOrder.setValue(4)

        self.butterParamsLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.butterOrder)

        self.butterCutoffLowLabel = QLabel(self.butterParamsGroup)
        self.butterCutoffLowLabel.setObjectName(u"butterCutoffLowLabel")

        self.butterParamsLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.butterCutoffLowLabel)

        self.butterCutoffLow = QDoubleSpinBox(self.butterParamsGroup)
        self.butterCutoffLow.setObjectName(u"butterCutoffLow")
        self.butterCutoffLow.setDecimals(3)
        self.butterCutoffLow.setMinimum(0.001000000000000)
        self.butterCutoffLow.setMaximum(1000.000000000000000)
        self.butterCutoffLow.setValue(1.000000000000000)

        self.butterParamsLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.butterCutoffLow)

        self.butterCutoffHighLabel = QLabel(self.butterParamsGroup)
        self.butterCutoffHighLabel.setObjectName(u"butterCutoffHighLabel")

        self.butterParamsLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.butterCutoffHighLabel)

        self.butterCutoffHigh = QDoubleSpinBox(self.butterParamsGroup)
        self.butterCutoffHigh.setObjectName(u"butterCutoffHigh")
        self.butterCutoffHigh.setDecimals(3)
        self.butterCutoffHigh.setMinimum(0.001000000000000)
        self.butterCutoffHigh.setMaximum(1000.000000000000000)
        self.butterCutoffHigh.setValue(10.000000000000000)

        self.butterParamsLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.butterCutoffHigh)

        self.butterFsLabel = QLabel(self.butterParamsGroup)
        self.butterFsLabel.setObjectName(u"butterFsLabel")

        self.butterParamsLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.butterFsLabel)

        self.butterFs = QDoubleSpinBox(self.butterParamsGroup)
        self.butterFs.setObjectName(u"butterFs")
        self.butterFs.setDecimals(1)
        self.butterFs.setMinimum(0.100000000000000)
        self.butterFs.setMaximum(10000.000000000000000)
        self.butterFs.setValue(100.000000000000000)

        self.butterParamsLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.butterFs)

        self.butterAutoFs = QCheckBox(self.butterParamsGroup)
        self.butterAutoFs.setObjectName(u"butterAutoFs")
        self.butterAutoFs.setChecked(True)

        self.butterParamsLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.butterAutoFs)


        self.butterworthTabLayout.addWidget(self.butterParamsGroup)

        self.butterAdvGroup = QGroupBox(self.butterworthTab)
        self.butterAdvGroup.setObjectName(u"butterAdvGroup")
        self.butterAdvLayout = QFormLayout(self.butterAdvGroup)
        self.butterAdvLayout.setObjectName(u"butterAdvLayout")
        self.butterPadlenLabel = QLabel(self.butterAdvGroup)
        self.butterPadlenLabel.setObjectName(u"butterPadlenLabel")

        self.butterAdvLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.butterPadlenLabel)

        self.butterPadlen = QSpinBox(self.butterAdvGroup)
        self.butterPadlen.setObjectName(u"butterPadlen")
        self.butterPadlen.setMinimum(0)
        self.butterPadlen.setMaximum(1000)
        self.butterPadlen.setValue(0)

        self.butterAdvLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.butterPadlen)

        self.butterForwardBackward = QCheckBox(self.butterAdvGroup)
        self.butterForwardBackward.setObjectName(u"butterForwardBackward")
        self.butterForwardBackward.setChecked(True)

        self.butterAdvLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.butterForwardBackward)


        self.butterworthTabLayout.addWidget(self.butterAdvGroup)

        self.butterworthSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.butterworthTabLayout.addItem(self.butterworthSpacer)

        self.filterTabs.addTab(self.butterworthTab, "")
        self.outliersTab = QWidget()
        self.outliersTab.setObjectName(u"outliersTab")
        self.outliersTabLayout = QVBoxLayout(self.outliersTab)
        self.outliersTabLayout.setSpacing(10)
        self.outliersTabLayout.setObjectName(u"outliersTabLayout")
        self.outlierMethodGroup = QGroupBox(self.outliersTab)
        self.outlierMethodGroup.setObjectName(u"outlierMethodGroup")
        self.outlierMethodLayout = QFormLayout(self.outlierMethodGroup)
        self.outlierMethodLayout.setObjectName(u"outlierMethodLayout")
        self.outlierMethodLabel = QLabel(self.outlierMethodGroup)
        self.outlierMethodLabel.setObjectName(u"outlierMethodLabel")

        self.outlierMethodLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.outlierMethodLabel)

        self.outlierMethod = QComboBox(self.outlierMethodGroup)
        self.outlierMethod.addItem("")
        self.outlierMethod.addItem("")
        self.outlierMethod.addItem("")
        self.outlierMethod.addItem("")
        self.outlierMethod.setObjectName(u"outlierMethod")

        self.outlierMethodLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.outlierMethod)


        self.outliersTabLayout.addWidget(self.outlierMethodGroup)

        self.outlierParamsGroup = QGroupBox(self.outliersTab)
        self.outlierParamsGroup.setObjectName(u"outlierParamsGroup")
        self.outlierParamsLayout = QFormLayout(self.outlierParamsGroup)
        self.outlierParamsLayout.setObjectName(u"outlierParamsLayout")
        self.outlierThresholdLabel = QLabel(self.outlierParamsGroup)
        self.outlierThresholdLabel.setObjectName(u"outlierThresholdLabel")

        self.outlierParamsLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.outlierThresholdLabel)

        self.outlierThreshold = QDoubleSpinBox(self.outlierParamsGroup)
        self.outlierThreshold.setObjectName(u"outlierThreshold")
        self.outlierThreshold.setDecimals(2)
        self.outlierThreshold.setMinimum(0.500000000000000)
        self.outlierThreshold.setMaximum(10.000000000000000)
        self.outlierThreshold.setValue(1.500000000000000)

        self.outlierParamsLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.outlierThreshold)

        self.outlierLowerLabel = QLabel(self.outlierParamsGroup)
        self.outlierLowerLabel.setObjectName(u"outlierLowerLabel")

        self.outlierParamsLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.outlierLowerLabel)

        self.outlierLower = QDoubleSpinBox(self.outlierParamsGroup)
        self.outlierLower.setObjectName(u"outlierLower")
        self.outlierLower.setDecimals(1)
        self.outlierLower.setMinimum(0.000000000000000)
        self.outlierLower.setMaximum(50.000000000000000)
        self.outlierLower.setValue(5.000000000000000)

        self.outlierParamsLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.outlierLower)

        self.outlierUpperLabel = QLabel(self.outlierParamsGroup)
        self.outlierUpperLabel.setObjectName(u"outlierUpperLabel")

        self.outlierParamsLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.outlierUpperLabel)

        self.outlierUpper = QDoubleSpinBox(self.outlierParamsGroup)
        self.outlierUpper.setObjectName(u"outlierUpper")
        self.outlierUpper.setDecimals(1)
        self.outlierUpper.setMinimum(50.000000000000000)
        self.outlierUpper.setMaximum(100.000000000000000)
        self.outlierUpper.setValue(95.000000000000000)

        self.outlierParamsLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.outlierUpper)


        self.outliersTabLayout.addWidget(self.outlierParamsGroup)

        self.outlierTreatmentGroup = QGroupBox(self.outliersTab)
        self.outlierTreatmentGroup.setObjectName(u"outlierTreatmentGroup")
        self.outlierTreatmentLayout = QFormLayout(self.outlierTreatmentGroup)
        self.outlierTreatmentLayout.setObjectName(u"outlierTreatmentLayout")
        self.outlierActionLabel = QLabel(self.outlierTreatmentGroup)
        self.outlierActionLabel.setObjectName(u"outlierActionLabel")

        self.outlierTreatmentLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.outlierActionLabel)

        self.outlierAction = QComboBox(self.outlierTreatmentGroup)
        self.outlierAction.addItem("")
        self.outlierAction.addItem("")
        self.outlierAction.addItem("")
        self.outlierAction.addItem("")
        self.outlierAction.addItem("")
        self.outlierAction.setObjectName(u"outlierAction")

        self.outlierTreatmentLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.outlierAction)

        self.outlierWindowLabel = QLabel(self.outlierTreatmentGroup)
        self.outlierWindowLabel.setObjectName(u"outlierWindowLabel")

        self.outlierTreatmentLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.outlierWindowLabel)

        self.outlierWindow = QSpinBox(self.outlierTreatmentGroup)
        self.outlierWindow.setObjectName(u"outlierWindow")
        self.outlierWindow.setMinimum(1)
        self.outlierWindow.setMaximum(100)
        self.outlierWindow.setValue(10)

        self.outlierTreatmentLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.outlierWindow)


        self.outliersTabLayout.addWidget(self.outlierTreatmentGroup)

        self.outliersSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.outliersTabLayout.addItem(self.outliersSpacer)

        self.filterTabs.addTab(self.outliersTab, "")
        self.rollingTab = QWidget()
        self.rollingTab.setObjectName(u"rollingTab")
        self.rollingTabLayout = QVBoxLayout(self.rollingTab)
        self.rollingTabLayout.setSpacing(10)
        self.rollingTabLayout.setObjectName(u"rollingTabLayout")
        self.rollingTypeGroup = QGroupBox(self.rollingTab)
        self.rollingTypeGroup.setObjectName(u"rollingTypeGroup")
        self.rollingTypeLayout = QFormLayout(self.rollingTypeGroup)
        self.rollingTypeLayout.setObjectName(u"rollingTypeLayout")
        self.rollingTypeLabel = QLabel(self.rollingTypeGroup)
        self.rollingTypeLabel.setObjectName(u"rollingTypeLabel")

        self.rollingTypeLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.rollingTypeLabel)

        self.rollingType = QComboBox(self.rollingTypeGroup)
        self.rollingType.addItem("")
        self.rollingType.addItem("")
        self.rollingType.addItem("")
        self.rollingType.addItem("")
        self.rollingType.addItem("")
        self.rollingType.addItem("")
        self.rollingType.addItem("")
        self.rollingType.addItem("")
        self.rollingType.addItem("")
        self.rollingType.setObjectName(u"rollingType")

        self.rollingTypeLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.rollingType)


        self.rollingTabLayout.addWidget(self.rollingTypeGroup)

        self.rollingParamsGroup = QGroupBox(self.rollingTab)
        self.rollingParamsGroup.setObjectName(u"rollingParamsGroup")
        self.rollingParamsLayout = QFormLayout(self.rollingParamsGroup)
        self.rollingParamsLayout.setObjectName(u"rollingParamsLayout")
        self.rollingWindowLabel = QLabel(self.rollingParamsGroup)
        self.rollingWindowLabel.setObjectName(u"rollingWindowLabel")

        self.rollingParamsLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.rollingWindowLabel)

        self.rollingWindow = QSpinBox(self.rollingParamsGroup)
        self.rollingWindow.setObjectName(u"rollingWindow")
        self.rollingWindow.setMinimum(2)
        self.rollingWindow.setMaximum(1000)
        self.rollingWindow.setValue(5)

        self.rollingParamsLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.rollingWindow)

        self.rollingMinPeriodsLabel = QLabel(self.rollingParamsGroup)
        self.rollingMinPeriodsLabel.setObjectName(u"rollingMinPeriodsLabel")

        self.rollingParamsLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.rollingMinPeriodsLabel)

        self.rollingMinPeriods = QSpinBox(self.rollingParamsGroup)
        self.rollingMinPeriods.setObjectName(u"rollingMinPeriods")
        self.rollingMinPeriods.setMinimum(1)
        self.rollingMinPeriods.setMaximum(100)
        self.rollingMinPeriods.setValue(1)

        self.rollingParamsLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.rollingMinPeriods)

        self.rollingCenter = QCheckBox(self.rollingParamsGroup)
        self.rollingCenter.setObjectName(u"rollingCenter")

        self.rollingParamsLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.rollingCenter)

        self.rollingQuantileLabel = QLabel(self.rollingParamsGroup)
        self.rollingQuantileLabel.setObjectName(u"rollingQuantileLabel")

        self.rollingParamsLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.rollingQuantileLabel)

        self.rollingQuantile = QDoubleSpinBox(self.rollingParamsGroup)
        self.rollingQuantile.setObjectName(u"rollingQuantile")
        self.rollingQuantile.setDecimals(2)
        self.rollingQuantile.setMinimum(0.000000000000000)
        self.rollingQuantile.setMaximum(1.000000000000000)
        self.rollingQuantile.setSingleStep(0.050000000000000)
        self.rollingQuantile.setValue(0.500000000000000)

        self.rollingParamsLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.rollingQuantile)


        self.rollingTabLayout.addWidget(self.rollingParamsGroup)

        self.rollingOptionsGroup = QGroupBox(self.rollingTab)
        self.rollingOptionsGroup.setObjectName(u"rollingOptionsGroup")
        self.rollingOptionsLayout = QFormLayout(self.rollingOptionsGroup)
        self.rollingOptionsLayout.setObjectName(u"rollingOptionsLayout")
        self.rollingWinTypeLabel = QLabel(self.rollingOptionsGroup)
        self.rollingWinTypeLabel.setObjectName(u"rollingWinTypeLabel")

        self.rollingOptionsLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.rollingWinTypeLabel)

        self.rollingWinType = QComboBox(self.rollingOptionsGroup)
        self.rollingWinType.addItem("")
        self.rollingWinType.addItem("")
        self.rollingWinType.addItem("")
        self.rollingWinType.addItem("")
        self.rollingWinType.addItem("")
        self.rollingWinType.addItem("")
        self.rollingWinType.addItem("")
        self.rollingWinType.setObjectName(u"rollingWinType")

        self.rollingOptionsLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.rollingWinType)


        self.rollingTabLayout.addWidget(self.rollingOptionsGroup)

        self.rollingSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.rollingTabLayout.addItem(self.rollingSpacer)

        self.filterTabs.addTab(self.rollingTab, "")

        self.mainLayout.addWidget(self.filterTabs)

        self.buttonBox = QDialogButtonBox(FilterDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Apply|QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.mainLayout.addWidget(self.buttonBox)


        self.retranslateUi(FilterDialog)
        self.buttonBox.accepted.connect(FilterDialog.accept)
        self.buttonBox.rejected.connect(FilterDialog.reject)

        self.filterTabs.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(FilterDialog)
    # setupUi

    def retranslateUi(self, FilterDialog):
        FilterDialog.setWindowTitle(QCoreApplication.translate("FilterDialog", u"\ud83d\udd27 Configurar Filtro de Dados", None))
        self.headerLabel.setText(QCoreApplication.translate("FilterDialog", u"\ud83d\udd27 Configurar Filtro de Dados", None))
        self.headerLabel.setStyleSheet(QCoreApplication.translate("FilterDialog", u"font-size: 14pt; font-weight: bold; color: #0d6efd; padding: 10px;", None))
        self.butterTypeGroup.setTitle(QCoreApplication.translate("FilterDialog", u"\ud83d\udcca Tipo de Filtro", None))
        self.butterTypeLabel.setText(QCoreApplication.translate("FilterDialog", u"Tipo:", None))
        self.butterType.setItemText(0, QCoreApplication.translate("FilterDialog", u"lowpass", None))
        self.butterType.setItemText(1, QCoreApplication.translate("FilterDialog", u"highpass", None))
        self.butterType.setItemText(2, QCoreApplication.translate("FilterDialog", u"bandpass", None))
        self.butterType.setItemText(3, QCoreApplication.translate("FilterDialog", u"bandstop", None))

#if QT_CONFIG(tooltip)
        self.butterType.setToolTip(QCoreApplication.translate("FilterDialog", u"Tipo de filtro Butterworth:\n"
"\u2022 lowpass: Permite frequ\u00eancias baixas\n"
"\u2022 highpass: Permite frequ\u00eancias altas\n"
"\u2022 bandpass: Permite faixa de frequ\u00eancias\n"
"\u2022 bandstop: Bloqueia faixa de frequ\u00eancias", None))
#endif // QT_CONFIG(tooltip)
        self.butterParamsGroup.setTitle(QCoreApplication.translate("FilterDialog", u"\ud83d\udd27 Par\u00e2metros", None))
        self.butterOrderLabel.setText(QCoreApplication.translate("FilterDialog", u"Ordem:", None))
#if QT_CONFIG(tooltip)
        self.butterOrder.setToolTip(QCoreApplication.translate("FilterDialog", u"Ordem do filtro (1-10). Ordens maiores = corte mais abrupto.", None))
#endif // QT_CONFIG(tooltip)
        self.butterCutoffLowLabel.setText(QCoreApplication.translate("FilterDialog", u"Freq. Corte (baixa):", None))
#if QT_CONFIG(tooltip)
        self.butterCutoffLow.setToolTip(QCoreApplication.translate("FilterDialog", u"Frequ\u00eancia de corte inferior", None))
#endif // QT_CONFIG(tooltip)
        self.butterCutoffLow.setSuffix(QCoreApplication.translate("FilterDialog", u" Hz", None))
        self.butterCutoffHighLabel.setText(QCoreApplication.translate("FilterDialog", u"Freq. Corte (alta):", None))
#if QT_CONFIG(tooltip)
        self.butterCutoffHigh.setToolTip(QCoreApplication.translate("FilterDialog", u"Frequ\u00eancia de corte superior", None))
#endif // QT_CONFIG(tooltip)
        self.butterCutoffHigh.setSuffix(QCoreApplication.translate("FilterDialog", u" Hz", None))
        self.butterFsLabel.setText(QCoreApplication.translate("FilterDialog", u"Taxa Amostragem:", None))
#if QT_CONFIG(tooltip)
        self.butterFs.setToolTip(QCoreApplication.translate("FilterDialog", u"Taxa de amostragem dos dados", None))
#endif // QT_CONFIG(tooltip)
        self.butterFs.setSuffix(QCoreApplication.translate("FilterDialog", u" Hz", None))
#if QT_CONFIG(tooltip)
        self.butterAutoFs.setToolTip(QCoreApplication.translate("FilterDialog", u"Estima taxa de amostragem automaticamente a partir dos timestamps", None))
#endif // QT_CONFIG(tooltip)
        self.butterAutoFs.setText(QCoreApplication.translate("FilterDialog", u"Auto-detectar taxa", None))
        self.butterAdvGroup.setTitle(QCoreApplication.translate("FilterDialog", u"\u2699\ufe0f Op\u00e7\u00f5es Avan\u00e7adas", None))
        self.butterPadlenLabel.setText(QCoreApplication.translate("FilterDialog", u"Padding:", None))
#if QT_CONFIG(tooltip)
        self.butterPadlen.setToolTip(QCoreApplication.translate("FilterDialog", u"Padding nas bordas para evitar artefatos. 0 = autom\u00e1tico.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.butterForwardBackward.setToolTip(QCoreApplication.translate("FilterDialog", u"Aplicar filtro bidirecionalmente. Elimina defasagem, duplica ordem efetiva.", None))
#endif // QT_CONFIG(tooltip)
        self.butterForwardBackward.setText(QCoreApplication.translate("FilterDialog", u"Filtfilt (zero-phase)", None))
        self.filterTabs.setTabText(self.filterTabs.indexOf(self.butterworthTab), QCoreApplication.translate("FilterDialog", u"\ud83d\udcc8 Butterworth", None))
        self.outlierMethodGroup.setTitle(QCoreApplication.translate("FilterDialog", u"\ud83d\udcca M\u00e9todo de Detec\u00e7\u00e3o", None))
        self.outlierMethodLabel.setText(QCoreApplication.translate("FilterDialog", u"M\u00e9todo:", None))
        self.outlierMethod.setItemText(0, QCoreApplication.translate("FilterDialog", u"iqr", None))
        self.outlierMethod.setItemText(1, QCoreApplication.translate("FilterDialog", u"zscore", None))
        self.outlierMethod.setItemText(2, QCoreApplication.translate("FilterDialog", u"mad", None))
        self.outlierMethod.setItemText(3, QCoreApplication.translate("FilterDialog", u"percentile", None))

#if QT_CONFIG(tooltip)
        self.outlierMethod.setToolTip(QCoreApplication.translate("FilterDialog", u"M\u00e9todo para detectar outliers", None))
#endif // QT_CONFIG(tooltip)
        self.outlierParamsGroup.setTitle(QCoreApplication.translate("FilterDialog", u"\ud83d\udd27 Par\u00e2metros", None))
        self.outlierThresholdLabel.setText(QCoreApplication.translate("FilterDialog", u"Limiar:", None))
#if QT_CONFIG(tooltip)
        self.outlierThreshold.setToolTip(QCoreApplication.translate("FilterDialog", u"Limiar para detec\u00e7\u00e3o de outliers", None))
#endif // QT_CONFIG(tooltip)
        self.outlierLowerLabel.setText(QCoreApplication.translate("FilterDialog", u"Percentil Inferior:", None))
#if QT_CONFIG(tooltip)
        self.outlierLower.setToolTip(QCoreApplication.translate("FilterDialog", u"Percentil inferior (para m\u00e9todo percentile)", None))
#endif // QT_CONFIG(tooltip)
        self.outlierLower.setSuffix(QCoreApplication.translate("FilterDialog", u" %", None))
        self.outlierUpperLabel.setText(QCoreApplication.translate("FilterDialog", u"Percentil Superior:", None))
#if QT_CONFIG(tooltip)
        self.outlierUpper.setToolTip(QCoreApplication.translate("FilterDialog", u"Percentil superior (para m\u00e9todo percentile)", None))
#endif // QT_CONFIG(tooltip)
        self.outlierUpper.setSuffix(QCoreApplication.translate("FilterDialog", u" %", None))
        self.outlierTreatmentGroup.setTitle(QCoreApplication.translate("FilterDialog", u"\ud83d\udd04 Tratamento dos Outliers", None))
        self.outlierActionLabel.setText(QCoreApplication.translate("FilterDialog", u"A\u00e7\u00e3o:", None))
        self.outlierAction.setItemText(0, QCoreApplication.translate("FilterDialog", u"remove", None))
        self.outlierAction.setItemText(1, QCoreApplication.translate("FilterDialog", u"replace_nan", None))
        self.outlierAction.setItemText(2, QCoreApplication.translate("FilterDialog", u"replace_mean", None))
        self.outlierAction.setItemText(3, QCoreApplication.translate("FilterDialog", u"replace_median", None))
        self.outlierAction.setItemText(4, QCoreApplication.translate("FilterDialog", u"interpolate", None))

#if QT_CONFIG(tooltip)
        self.outlierAction.setToolTip(QCoreApplication.translate("FilterDialog", u"O que fazer com outliers detectados", None))
#endif // QT_CONFIG(tooltip)
        self.outlierWindowLabel.setText(QCoreApplication.translate("FilterDialog", u"Janela Local:", None))
#if QT_CONFIG(tooltip)
        self.outlierWindow.setToolTip(QCoreApplication.translate("FilterDialog", u"Janela para c\u00e1lculo local de estat\u00edsticas. 1 = estat\u00edsticas globais.", None))
#endif // QT_CONFIG(tooltip)
        self.filterTabs.setTabText(self.filterTabs.indexOf(self.outliersTab), QCoreApplication.translate("FilterDialog", u"\ud83d\udeab Outliers", None))
        self.rollingTypeGroup.setTitle(QCoreApplication.translate("FilterDialog", u"\ud83d\udcca Opera\u00e7\u00e3o Rolling", None))
        self.rollingTypeLabel.setText(QCoreApplication.translate("FilterDialog", u"Tipo:", None))
        self.rollingType.setItemText(0, QCoreApplication.translate("FilterDialog", u"mean", None))
        self.rollingType.setItemText(1, QCoreApplication.translate("FilterDialog", u"median", None))
        self.rollingType.setItemText(2, QCoreApplication.translate("FilterDialog", u"std", None))
        self.rollingType.setItemText(3, QCoreApplication.translate("FilterDialog", u"var", None))
        self.rollingType.setItemText(4, QCoreApplication.translate("FilterDialog", u"min", None))
        self.rollingType.setItemText(5, QCoreApplication.translate("FilterDialog", u"max", None))
        self.rollingType.setItemText(6, QCoreApplication.translate("FilterDialog", u"sum", None))
        self.rollingType.setItemText(7, QCoreApplication.translate("FilterDialog", u"count", None))
        self.rollingType.setItemText(8, QCoreApplication.translate("FilterDialog", u"quantile", None))

#if QT_CONFIG(tooltip)
        self.rollingType.setToolTip(QCoreApplication.translate("FilterDialog", u"Opera\u00e7\u00e3o a aplicar na janela m\u00f3vel", None))
#endif // QT_CONFIG(tooltip)
        self.rollingParamsGroup.setTitle(QCoreApplication.translate("FilterDialog", u"\ud83d\udd27 Par\u00e2metros", None))
        self.rollingWindowLabel.setText(QCoreApplication.translate("FilterDialog", u"Janela:", None))
#if QT_CONFIG(tooltip)
        self.rollingWindow.setToolTip(QCoreApplication.translate("FilterDialog", u"Tamanho da janela m\u00f3vel em pontos", None))
#endif // QT_CONFIG(tooltip)
        self.rollingMinPeriodsLabel.setText(QCoreApplication.translate("FilterDialog", u"Min. Per\u00edodos:", None))
#if QT_CONFIG(tooltip)
        self.rollingMinPeriods.setToolTip(QCoreApplication.translate("FilterDialog", u"N\u00famero m\u00ednimo de pontos necess\u00e1rios", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.rollingCenter.setToolTip(QCoreApplication.translate("FilterDialog", u"Se marcado, o resultado \u00e9 alinhado ao centro da janela", None))
#endif // QT_CONFIG(tooltip)
        self.rollingCenter.setText(QCoreApplication.translate("FilterDialog", u"Centralizar janela", None))
        self.rollingQuantileLabel.setText(QCoreApplication.translate("FilterDialog", u"Quantil:", None))
#if QT_CONFIG(tooltip)
        self.rollingQuantile.setToolTip(QCoreApplication.translate("FilterDialog", u"Valor do quantil (para tipo 'quantile')", None))
#endif // QT_CONFIG(tooltip)
        self.rollingOptionsGroup.setTitle(QCoreApplication.translate("FilterDialog", u"\u2699\ufe0f Op\u00e7\u00f5es", None))
        self.rollingWinTypeLabel.setText(QCoreApplication.translate("FilterDialog", u"Tipo Janela:", None))
        self.rollingWinType.setItemText(0, QCoreApplication.translate("FilterDialog", u"boxcar", None))
        self.rollingWinType.setItemText(1, QCoreApplication.translate("FilterDialog", u"triang", None))
        self.rollingWinType.setItemText(2, QCoreApplication.translate("FilterDialog", u"blackman", None))
        self.rollingWinType.setItemText(3, QCoreApplication.translate("FilterDialog", u"hamming", None))
        self.rollingWinType.setItemText(4, QCoreApplication.translate("FilterDialog", u"bartlett", None))
        self.rollingWinType.setItemText(5, QCoreApplication.translate("FilterDialog", u"gaussian", None))
        self.rollingWinType.setItemText(6, QCoreApplication.translate("FilterDialog", u"exponential", None))

#if QT_CONFIG(tooltip)
        self.rollingWinType.setToolTip(QCoreApplication.translate("FilterDialog", u"Tipo de janela para pondera\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.filterTabs.setTabText(self.filterTabs.indexOf(self.rollingTab), QCoreApplication.translate("FilterDialog", u"\ud83d\udcca Rolling", None))
    # retranslateUi

