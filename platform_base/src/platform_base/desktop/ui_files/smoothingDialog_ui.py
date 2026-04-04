# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'smoothingDialog.ui'
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
    QGroupBox, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QSlider, QSpacerItem, QSpinBox,
    QVBoxLayout, QWidget)

class Ui_SmoothingDialog(object):
    def setupUi(self, SmoothingDialog):
        if not SmoothingDialog.objectName():
            SmoothingDialog.setObjectName(u"SmoothingDialog")
        SmoothingDialog.resize(550, 520)
        SmoothingDialog.setModal(True)
        self.mainLayout = QVBoxLayout(SmoothingDialog)
        self.mainLayout.setSpacing(12)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(16, 16, 16, 16)
        self.headerLabel = QLabel(SmoothingDialog)
        self.headerLabel.setObjectName(u"headerLabel")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.headerLabel.setFont(font)

        self.mainLayout.addWidget(self.headerLabel)

        self.methodGroup = QGroupBox(SmoothingDialog)
        self.methodGroup.setObjectName(u"methodGroup")
        self.methodLayout = QFormLayout(self.methodGroup)
        self.methodLayout.setObjectName(u"methodLayout")
        self.methodLabel = QLabel(self.methodGroup)
        self.methodLabel.setObjectName(u"methodLabel")

        self.methodLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.methodLabel)

        self.methodCombo = QComboBox(self.methodGroup)
        self.methodCombo.addItem("")
        self.methodCombo.addItem("")
        self.methodCombo.addItem("")
        self.methodCombo.addItem("")
        self.methodCombo.addItem("")
        self.methodCombo.setObjectName(u"methodCombo")

        self.methodLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.methodCombo)


        self.mainLayout.addWidget(self.methodGroup)

        self.generalParamsGroup = QGroupBox(SmoothingDialog)
        self.generalParamsGroup.setObjectName(u"generalParamsGroup")
        self.generalParamsLayout = QFormLayout(self.generalParamsGroup)
        self.generalParamsLayout.setObjectName(u"generalParamsLayout")
        self.windowLabel = QLabel(self.generalParamsGroup)
        self.windowLabel.setObjectName(u"windowLabel")

        self.generalParamsLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.windowLabel)

        self.windowLayout = QHBoxLayout()
        self.windowLayout.setObjectName(u"windowLayout")
        self.windowSpin = QSpinBox(self.generalParamsGroup)
        self.windowSpin.setObjectName(u"windowSpin")
        self.windowSpin.setMinimum(3)
        self.windowSpin.setMaximum(101)
        self.windowSpin.setSingleStep(2)
        self.windowSpin.setValue(7)

        self.windowLayout.addWidget(self.windowSpin)

        self.windowSlider = QSlider(self.generalParamsGroup)
        self.windowSlider.setObjectName(u"windowSlider")
        self.windowSlider.setMinimum(3)
        self.windowSlider.setMaximum(101)
        self.windowSlider.setSingleStep(2)
        self.windowSlider.setValue(7)
        self.windowSlider.setOrientation(Qt.Horizontal)
        self.windowSlider.setTickPosition(QSlider.TicksBelow)
        self.windowSlider.setTickInterval(10)

        self.windowLayout.addWidget(self.windowSlider)


        self.generalParamsLayout.setLayout(0, QFormLayout.ItemRole.FieldRole, self.windowLayout)

        self.sigmaLabel = QLabel(self.generalParamsGroup)
        self.sigmaLabel.setObjectName(u"sigmaLabel")

        self.generalParamsLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.sigmaLabel)

        self.sigmaLayout = QHBoxLayout()
        self.sigmaLayout.setObjectName(u"sigmaLayout")
        self.sigmaSpin = QDoubleSpinBox(self.generalParamsGroup)
        self.sigmaSpin.setObjectName(u"sigmaSpin")
        self.sigmaSpin.setMinimum(0.100000000000000)
        self.sigmaSpin.setMaximum(10.000000000000000)
        self.sigmaSpin.setSingleStep(0.100000000000000)
        self.sigmaSpin.setValue(1.000000000000000)
        self.sigmaSpin.setDecimals(1)

        self.sigmaLayout.addWidget(self.sigmaSpin)

        self.sigmaSlider = QSlider(self.generalParamsGroup)
        self.sigmaSlider.setObjectName(u"sigmaSlider")
        self.sigmaSlider.setMinimum(1)
        self.sigmaSlider.setMaximum(100)
        self.sigmaSlider.setValue(10)
        self.sigmaSlider.setOrientation(Qt.Horizontal)
        self.sigmaSlider.setTickPosition(QSlider.TicksBelow)
        self.sigmaSlider.setTickInterval(10)

        self.sigmaLayout.addWidget(self.sigmaSlider)


        self.generalParamsLayout.setLayout(1, QFormLayout.ItemRole.FieldRole, self.sigmaLayout)

        self.boundaryLabel = QLabel(self.generalParamsGroup)
        self.boundaryLabel.setObjectName(u"boundaryLabel")

        self.generalParamsLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.boundaryLabel)

        self.boundaryModeCombo = QComboBox(self.generalParamsGroup)
        self.boundaryModeCombo.addItem("")
        self.boundaryModeCombo.addItem("")
        self.boundaryModeCombo.addItem("")
        self.boundaryModeCombo.addItem("")
        self.boundaryModeCombo.addItem("")
        self.boundaryModeCombo.setObjectName(u"boundaryModeCombo")

        self.generalParamsLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.boundaryModeCombo)

        self.preserveNanCheck = QCheckBox(self.generalParamsGroup)
        self.preserveNanCheck.setObjectName(u"preserveNanCheck")
        self.preserveNanCheck.setChecked(True)

        self.generalParamsLayout.setWidget(3, QFormLayout.ItemRole.SpanningRole, self.preserveNanCheck)


        self.mainLayout.addWidget(self.generalParamsGroup)

        self.savgolGroup = QGroupBox(SmoothingDialog)
        self.savgolGroup.setObjectName(u"savgolGroup")
        self.savgolGroup.setVisible(False)
        self.savgolLayout = QFormLayout(self.savgolGroup)
        self.savgolLayout.setObjectName(u"savgolLayout")
        self.polyorderLabel = QLabel(self.savgolGroup)
        self.polyorderLabel.setObjectName(u"polyorderLabel")

        self.savgolLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.polyorderLabel)

        self.polyorderSpin = QSpinBox(self.savgolGroup)
        self.polyorderSpin.setObjectName(u"polyorderSpin")
        self.polyorderSpin.setMinimum(1)
        self.polyorderSpin.setMaximum(10)
        self.polyorderSpin.setValue(3)

        self.savgolLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.polyorderSpin)

        self.derivLabel = QLabel(self.savgolGroup)
        self.derivLabel.setObjectName(u"derivLabel")

        self.savgolLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.derivLabel)

        self.derivSpin = QSpinBox(self.savgolGroup)
        self.derivSpin.setObjectName(u"derivSpin")
        self.derivSpin.setMinimum(0)
        self.derivSpin.setMaximum(5)
        self.derivSpin.setValue(0)

        self.savgolLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.derivSpin)

        self.deltaLabel = QLabel(self.savgolGroup)
        self.deltaLabel.setObjectName(u"deltaLabel")

        self.savgolLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.deltaLabel)

        self.deltaSpin = QDoubleSpinBox(self.savgolGroup)
        self.deltaSpin.setObjectName(u"deltaSpin")
        self.deltaSpin.setMinimum(0.001000000000000)
        self.deltaSpin.setMaximum(100.000000000000000)
        self.deltaSpin.setValue(1.000000000000000)
        self.deltaSpin.setDecimals(3)

        self.savgolLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.deltaSpin)


        self.mainLayout.addWidget(self.savgolGroup)

        self.expGroup = QGroupBox(SmoothingDialog)
        self.expGroup.setObjectName(u"expGroup")
        self.expGroup.setVisible(False)
        self.expLayout = QFormLayout(self.expGroup)
        self.expLayout.setObjectName(u"expLayout")
        self.alphaLabel = QLabel(self.expGroup)
        self.alphaLabel.setObjectName(u"alphaLabel")

        self.expLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.alphaLabel)

        self.alphaSpin = QDoubleSpinBox(self.expGroup)
        self.alphaSpin.setObjectName(u"alphaSpin")
        self.alphaSpin.setMinimum(0.010000000000000)
        self.alphaSpin.setMaximum(1.000000000000000)
        self.alphaSpin.setSingleStep(0.050000000000000)
        self.alphaSpin.setValue(0.300000000000000)
        self.alphaSpin.setDecimals(2)

        self.expLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.alphaSpin)

        self.adjustCheck = QCheckBox(self.expGroup)
        self.adjustCheck.setObjectName(u"adjustCheck")
        self.adjustCheck.setChecked(True)

        self.expLayout.setWidget(1, QFormLayout.ItemRole.SpanningRole, self.adjustCheck)


        self.mainLayout.addWidget(self.expGroup)

        self.verticalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mainLayout.addItem(self.verticalSpacer)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.previewButton = QPushButton(SmoothingDialog)
        self.previewButton.setObjectName(u"previewButton")

        self.buttonLayout.addWidget(self.previewButton)

        self.buttonSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.buttonSpacer)

        self.buttonBox = QDialogButtonBox(SmoothingDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.buttonLayout.addWidget(self.buttonBox)


        self.mainLayout.addLayout(self.buttonLayout)


        self.retranslateUi(SmoothingDialog)
        self.buttonBox.accepted.connect(SmoothingDialog.accept)
        self.buttonBox.rejected.connect(SmoothingDialog.reject)

        QMetaObject.connectSlotsByName(SmoothingDialog)
    # setupUi

    def retranslateUi(self, SmoothingDialog):
        SmoothingDialog.setWindowTitle(QCoreApplication.translate("SmoothingDialog", u"\u3030\ufe0f Configurar Suaviza\u00e7\u00e3o de Dados", None))
        self.headerLabel.setText(QCoreApplication.translate("SmoothingDialog", u"\u3030\ufe0f Configurar Suaviza\u00e7\u00e3o de Dados", None))
        self.headerLabel.setStyleSheet(QCoreApplication.translate("SmoothingDialog", u"color: #0d6efd; padding: 8px;", None))
        self.methodGroup.setTitle(QCoreApplication.translate("SmoothingDialog", u"\ud83d\udcca M\u00e9todo de Suaviza\u00e7\u00e3o", None))
        self.methodLabel.setText(QCoreApplication.translate("SmoothingDialog", u"M\u00e9todo:", None))
        self.methodCombo.setItemText(0, QCoreApplication.translate("SmoothingDialog", u"gaussian", None))
        self.methodCombo.setItemText(1, QCoreApplication.translate("SmoothingDialog", u"moving_average", None))
        self.methodCombo.setItemText(2, QCoreApplication.translate("SmoothingDialog", u"savitzky_golay", None))
        self.methodCombo.setItemText(3, QCoreApplication.translate("SmoothingDialog", u"exponential", None))
        self.methodCombo.setItemText(4, QCoreApplication.translate("SmoothingDialog", u"median", None))

#if QT_CONFIG(tooltip)
        self.methodCombo.setToolTip(QCoreApplication.translate("SmoothingDialog", u"M\u00e9todo de suaviza\u00e7\u00e3o a aplicar:\n"
"\u2022 gaussian: Filtro Gaussiano\n"
"\u2022 moving_average: M\u00e9dia m\u00f3vel simples\n"
"\u2022 savitzky_golay: Suaviza\u00e7\u00e3o polinomial local\n"
"\u2022 exponential: Suaviza\u00e7\u00e3o exponencial\n"
"\u2022 median: Filtro mediana", None))
#endif // QT_CONFIG(tooltip)
        self.generalParamsGroup.setTitle(QCoreApplication.translate("SmoothingDialog", u"\ud83d\udd27 Par\u00e2metros Gerais", None))
        self.windowLabel.setText(QCoreApplication.translate("SmoothingDialog", u"Tamanho Janela:", None))
#if QT_CONFIG(tooltip)
        self.windowSpin.setToolTip(QCoreApplication.translate("SmoothingDialog", u"Tamanho da janela de suaviza\u00e7\u00e3o (\u00edmpar).\n"
"Valores maiores = mais suaviza\u00e7\u00e3o.", None))
#endif // QT_CONFIG(tooltip)
        self.sigmaLabel.setText(QCoreApplication.translate("SmoothingDialog", u"Sigma (\u03c3):", None))
#if QT_CONFIG(tooltip)
        self.sigmaSpin.setToolTip(QCoreApplication.translate("SmoothingDialog", u"Desvio padr\u00e3o da Gaussiana.\n"
"Valores maiores = suaviza\u00e7\u00e3o mais ampla.", None))
#endif // QT_CONFIG(tooltip)
        self.boundaryLabel.setText(QCoreApplication.translate("SmoothingDialog", u"Modo Borda:", None))
        self.boundaryModeCombo.setItemText(0, QCoreApplication.translate("SmoothingDialog", u"reflect", None))
        self.boundaryModeCombo.setItemText(1, QCoreApplication.translate("SmoothingDialog", u"constant", None))
        self.boundaryModeCombo.setItemText(2, QCoreApplication.translate("SmoothingDialog", u"nearest", None))
        self.boundaryModeCombo.setItemText(3, QCoreApplication.translate("SmoothingDialog", u"mirror", None))
        self.boundaryModeCombo.setItemText(4, QCoreApplication.translate("SmoothingDialog", u"wrap", None))

#if QT_CONFIG(tooltip)
        self.boundaryModeCombo.setToolTip(QCoreApplication.translate("SmoothingDialog", u"Como tratar as bordas dos dados:\n"
"\u2022 reflect: Reflete os valores (padr\u00e3o)\n"
"\u2022 constant: Usa valor constante\n"
"\u2022 nearest: Repete o valor mais pr\u00f3ximo\n"
"\u2022 mirror: Espelha sem repetir extremo\n"
"\u2022 wrap: Assume continuidade circular", None))
#endif // QT_CONFIG(tooltip)
        self.preserveNanCheck.setText(QCoreApplication.translate("SmoothingDialog", u"Preservar valores NaN", None))
#if QT_CONFIG(tooltip)
        self.preserveNanCheck.setToolTip(QCoreApplication.translate("SmoothingDialog", u"Mant\u00e9m posi\u00e7\u00f5es de NaN ap\u00f3s suaviza\u00e7\u00e3o.\n"
"\u00datil para n\u00e3o propagar dados faltantes.", None))
#endif // QT_CONFIG(tooltip)
        self.savgolGroup.setTitle(QCoreApplication.translate("SmoothingDialog", u"\ud83d\udcd0 Par\u00e2metros Savitzky-Golay", None))
        self.polyorderLabel.setText(QCoreApplication.translate("SmoothingDialog", u"Ordem Polinomial:", None))
#if QT_CONFIG(tooltip)
        self.polyorderSpin.setToolTip(QCoreApplication.translate("SmoothingDialog", u"Ordem do polin\u00f4mio de ajuste.\n"
"Deve ser menor que o tamanho da janela.", None))
#endif // QT_CONFIG(tooltip)
        self.derivLabel.setText(QCoreApplication.translate("SmoothingDialog", u"Ordem Derivada:", None))
#if QT_CONFIG(tooltip)
        self.derivSpin.setToolTip(QCoreApplication.translate("SmoothingDialog", u"Ordem da derivada a calcular.\n"
"0 = apenas suaviza\u00e7\u00e3o (sem derivar).", None))
#endif // QT_CONFIG(tooltip)
        self.deltaLabel.setText(QCoreApplication.translate("SmoothingDialog", u"Delta (espa\u00e7amento):", None))
#if QT_CONFIG(tooltip)
        self.deltaSpin.setToolTip(QCoreApplication.translate("SmoothingDialog", u"Espa\u00e7amento entre pontos.\n"
"Usado no c\u00e1lculo de derivadas.", None))
#endif // QT_CONFIG(tooltip)
        self.expGroup.setTitle(QCoreApplication.translate("SmoothingDialog", u"\ud83d\udcc8 Par\u00e2metros Exponencial", None))
        self.alphaLabel.setText(QCoreApplication.translate("SmoothingDialog", u"Alpha (fator de suaviza\u00e7\u00e3o):", None))
#if QT_CONFIG(tooltip)
        self.alphaSpin.setToolTip(QCoreApplication.translate("SmoothingDialog", u"Fator de suaviza\u00e7\u00e3o exponencial (0-1).\n"
"Valores menores = mais suaviza\u00e7\u00e3o.", None))
#endif // QT_CONFIG(tooltip)
        self.adjustCheck.setText(QCoreApplication.translate("SmoothingDialog", u"Ajustar para compensar per\u00edodo inicial", None))
#if QT_CONFIG(tooltip)
        self.adjustCheck.setToolTip(QCoreApplication.translate("SmoothingDialog", u"Ajusta os pesos iniciais para compensar\n"
"o per\u00edodo de aquecimento da m\u00e9dia exponencial.", None))
#endif // QT_CONFIG(tooltip)
        self.previewButton.setText(QCoreApplication.translate("SmoothingDialog", u"\ud83d\udc41\ufe0f Preview", None))
#if QT_CONFIG(tooltip)
        self.previewButton.setToolTip(QCoreApplication.translate("SmoothingDialog", u"Visualizar resultado sem aplicar", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

