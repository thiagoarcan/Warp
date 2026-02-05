# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'smoothingConfigDialog.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QDoubleSpinBox,
    QFormLayout, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QVBoxLayout,
    QWidget)

class Ui_SmoothingConfigDialog(object):
    def setupUi(self, SmoothingConfigDialog):
        if not SmoothingConfigDialog.objectName():
            SmoothingConfigDialog.setObjectName(u"SmoothingConfigDialog")
        SmoothingConfigDialog.resize(350, 200)
        SmoothingConfigDialog.setModal(True)
        self.mainLayout = QVBoxLayout(SmoothingConfigDialog)
        self.mainLayout.setSpacing(12)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(16, 16, 16, 16)
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.methodLabel = QLabel(SmoothingConfigDialog)
        self.methodLabel.setObjectName(u"methodLabel")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.methodLabel)

        self.methodCombo = QComboBox(SmoothingConfigDialog)
        self.methodCombo.addItem("")
        self.methodCombo.addItem("")
        self.methodCombo.addItem("")
        self.methodCombo.addItem("")
        self.methodCombo.setObjectName(u"methodCombo")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.methodCombo)

        self.windowLabel = QLabel(SmoothingConfigDialog)
        self.windowLabel.setObjectName(u"windowLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.windowLabel)

        self.windowSpin = QSpinBox(SmoothingConfigDialog)
        self.windowSpin.setObjectName(u"windowSpin")
        self.windowSpin.setMinimum(3)
        self.windowSpin.setMaximum(101)
        self.windowSpin.setSingleStep(2)
        self.windowSpin.setValue(5)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.windowSpin)

        self.sigmaLabel = QLabel(SmoothingConfigDialog)
        self.sigmaLabel.setObjectName(u"sigmaLabel")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.sigmaLabel)

        self.sigmaSpin = QDoubleSpinBox(SmoothingConfigDialog)
        self.sigmaSpin.setObjectName(u"sigmaSpin")
        self.sigmaSpin.setMinimum(0.100000000000000)
        self.sigmaSpin.setMaximum(10.000000000000000)
        self.sigmaSpin.setSingleStep(0.100000000000000)
        self.sigmaSpin.setValue(1.000000000000000)
        self.sigmaSpin.setDecimals(1)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.sigmaSpin)


        self.mainLayout.addLayout(self.formLayout)

        self.verticalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mainLayout.addItem(self.verticalSpacer)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.buttonSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.buttonSpacer)

        self.cancelBtn = QPushButton(SmoothingConfigDialog)
        self.cancelBtn.setObjectName(u"cancelBtn")

        self.buttonLayout.addWidget(self.cancelBtn)

        self.applyBtn = QPushButton(SmoothingConfigDialog)
        self.applyBtn.setObjectName(u"applyBtn")

        self.buttonLayout.addWidget(self.applyBtn)


        self.mainLayout.addLayout(self.buttonLayout)


        self.retranslateUi(SmoothingConfigDialog)

        self.applyBtn.setDefault(True)


        QMetaObject.connectSlotsByName(SmoothingConfigDialog)
    # setupUi

    def retranslateUi(self, SmoothingConfigDialog):
        SmoothingConfigDialog.setWindowTitle(QCoreApplication.translate("SmoothingConfigDialog", u"Suaviza\u00e7\u00e3o Visual", None))
        self.methodLabel.setText(QCoreApplication.translate("SmoothingConfigDialog", u"M\u00e9todo:", None))
        self.methodCombo.setItemText(0, QCoreApplication.translate("SmoothingConfigDialog", u"Moving Average", None))
        self.methodCombo.setItemText(1, QCoreApplication.translate("SmoothingConfigDialog", u"Gaussian", None))
        self.methodCombo.setItemText(2, QCoreApplication.translate("SmoothingConfigDialog", u"Savitzky Golay", None))
        self.methodCombo.setItemText(3, QCoreApplication.translate("SmoothingConfigDialog", u"Median", None))

#if QT_CONFIG(tooltip)
        self.methodCombo.setToolTip(QCoreApplication.translate("SmoothingConfigDialog", u"M\u00e9todo de suaviza\u00e7\u00e3o visual", None))
#endif // QT_CONFIG(tooltip)
        self.windowLabel.setText(QCoreApplication.translate("SmoothingConfigDialog", u"Janela:", None))
#if QT_CONFIG(tooltip)
        self.windowSpin.setToolTip(QCoreApplication.translate("SmoothingConfigDialog", u"Tamanho da janela de suaviza\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.sigmaLabel.setText(QCoreApplication.translate("SmoothingConfigDialog", u"Sigma:", None))
#if QT_CONFIG(tooltip)
        self.sigmaSpin.setToolTip(QCoreApplication.translate("SmoothingConfigDialog", u"Sigma para suaviza\u00e7\u00e3o Gaussiana", None))
#endif // QT_CONFIG(tooltip)
        self.cancelBtn.setText(QCoreApplication.translate("SmoothingConfigDialog", u"Cancelar", None))
        self.applyBtn.setText(QCoreApplication.translate("SmoothingConfigDialog", u"Aplicar", None))
    # retranslateUi

