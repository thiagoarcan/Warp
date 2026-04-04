# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mathAnalysisDialog.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QSpinBox,
    QVBoxLayout, QWidget)

class Ui_MathAnalysisDialog(object):
    def setupUi(self, MathAnalysisDialog):
        if not MathAnalysisDialog.objectName():
            MathAnalysisDialog.setObjectName(u"MathAnalysisDialog")
        MathAnalysisDialog.resize(400, 350)
        MathAnalysisDialog.setMinimumSize(QSize(350, 200))
        MathAnalysisDialog.setModal(True)
        self.mainLayout = QVBoxLayout(MathAnalysisDialog)
        self.mainLayout.setSpacing(12)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(16, 16, 16, 16)
        self.derivativeGroup = QGroupBox(MathAnalysisDialog)
        self.derivativeGroup.setObjectName(u"derivativeGroup")
        self.derivativeLayout = QFormLayout(self.derivativeGroup)
        self.derivativeLayout.setObjectName(u"derivativeLayout")
        self.derivOrderLabel = QLabel(self.derivativeGroup)
        self.derivOrderLabel.setObjectName(u"derivOrderLabel")

        self.derivativeLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.derivOrderLabel)

        self.derivativeOrder = QSpinBox(self.derivativeGroup)
        self.derivativeOrder.setObjectName(u"derivativeOrder")
        self.derivativeOrder.setMinimum(1)
        self.derivativeOrder.setMaximum(3)
        self.derivativeOrder.setValue(1)

        self.derivativeLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.derivativeOrder)

        self.derivMethodLabel = QLabel(self.derivativeGroup)
        self.derivMethodLabel.setObjectName(u"derivMethodLabel")

        self.derivativeLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.derivMethodLabel)

        self.derivativeMethod = QComboBox(self.derivativeGroup)
        self.derivativeMethod.addItem("")
        self.derivativeMethod.addItem("")
        self.derivativeMethod.addItem("")
        self.derivativeMethod.addItem("")
        self.derivativeMethod.setObjectName(u"derivativeMethod")

        self.derivativeLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.derivativeMethod)

        self.enableSmoothing = QCheckBox(self.derivativeGroup)
        self.enableSmoothing.setObjectName(u"enableSmoothing")

        self.derivativeLayout.setWidget(2, QFormLayout.ItemRole.SpanningRole, self.enableSmoothing)

        self.smoothWindowLabel = QLabel(self.derivativeGroup)
        self.smoothWindowLabel.setObjectName(u"smoothWindowLabel")

        self.derivativeLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.smoothWindowLabel)

        self.smoothingWindow = QSpinBox(self.derivativeGroup)
        self.smoothingWindow.setObjectName(u"smoothingWindow")
        self.smoothingWindow.setEnabled(False)
        self.smoothingWindow.setMinimum(3)
        self.smoothingWindow.setMaximum(101)
        self.smoothingWindow.setSingleStep(2)
        self.smoothingWindow.setValue(5)

        self.derivativeLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.smoothingWindow)


        self.mainLayout.addWidget(self.derivativeGroup)

        self.integralGroup = QGroupBox(MathAnalysisDialog)
        self.integralGroup.setObjectName(u"integralGroup")
        self.integralLayout = QFormLayout(self.integralGroup)
        self.integralLayout.setObjectName(u"integralLayout")
        self.integralMethodLabel = QLabel(self.integralGroup)
        self.integralMethodLabel.setObjectName(u"integralMethodLabel")

        self.integralLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.integralMethodLabel)

        self.integralMethod = QComboBox(self.integralGroup)
        self.integralMethod.addItem("")
        self.integralMethod.addItem("")
        self.integralMethod.addItem("")
        self.integralMethod.setObjectName(u"integralMethod")

        self.integralLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.integralMethod)


        self.mainLayout.addWidget(self.integralGroup)

        self.smoothingGroup = QGroupBox(MathAnalysisDialog)
        self.smoothingGroup.setObjectName(u"smoothingGroup")
        self.smoothingLayout = QFormLayout(self.smoothingGroup)
        self.smoothingLayout.setObjectName(u"smoothingLayout")
        self.smoothMethodLabel = QLabel(self.smoothingGroup)
        self.smoothMethodLabel.setObjectName(u"smoothMethodLabel")

        self.smoothingLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.smoothMethodLabel)

        self.smoothMethod = QComboBox(self.smoothingGroup)
        self.smoothMethod.addItem("")
        self.smoothMethod.addItem("")
        self.smoothMethod.addItem("")
        self.smoothMethod.addItem("")
        self.smoothMethod.setObjectName(u"smoothMethod")

        self.smoothingLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.smoothMethod)

        self.windowSizeLabel = QLabel(self.smoothingGroup)
        self.windowSizeLabel.setObjectName(u"windowSizeLabel")

        self.smoothingLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.windowSizeLabel)

        self.windowSize = QSpinBox(self.smoothingGroup)
        self.windowSize.setObjectName(u"windowSize")
        self.windowSize.setMinimum(3)
        self.windowSize.setMaximum(201)
        self.windowSize.setSingleStep(2)
        self.windowSize.setValue(11)

        self.smoothingLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.windowSize)

        self.polyorderLabel = QLabel(self.smoothingGroup)
        self.polyorderLabel.setObjectName(u"polyorderLabel")

        self.smoothingLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.polyorderLabel)

        self.polyorder = QSpinBox(self.smoothingGroup)
        self.polyorder.setObjectName(u"polyorder")
        self.polyorder.setMinimum(1)
        self.polyorder.setMaximum(10)
        self.polyorder.setValue(3)

        self.smoothingLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.polyorder)


        self.mainLayout.addWidget(self.smoothingGroup)

        self.interpolationGroup = QGroupBox(MathAnalysisDialog)
        self.interpolationGroup.setObjectName(u"interpolationGroup")
        self.interpolationLayout = QFormLayout(self.interpolationGroup)
        self.interpolationLayout.setObjectName(u"interpolationLayout")
        self.interpMethodLabel = QLabel(self.interpolationGroup)
        self.interpMethodLabel.setObjectName(u"interpMethodLabel")

        self.interpolationLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.interpMethodLabel)

        self.interp_method = QComboBox(self.interpolationGroup)
        self.interp_method.addItem("")
        self.interp_method.addItem("")
        self.interp_method.addItem("")
        self.interp_method.addItem("")
        self.interp_method.setObjectName(u"interp_method")

        self.interpolationLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.interp_method)


        self.mainLayout.addWidget(self.interpolationGroup)

        self.resampleGroup = QGroupBox(MathAnalysisDialog)
        self.resampleGroup.setObjectName(u"resampleGroup")
        self.resampleLayout = QFormLayout(self.resampleGroup)
        self.resampleLayout.setObjectName(u"resampleLayout")
        self.resampleMethodLabel = QLabel(self.resampleGroup)
        self.resampleMethodLabel.setObjectName(u"resampleMethodLabel")

        self.resampleLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.resampleMethodLabel)

        self.resample_method = QComboBox(self.resampleGroup)
        self.resample_method.addItem("")
        self.resample_method.addItem("")
        self.resample_method.addItem("")
        self.resample_method.setObjectName(u"resample_method")

        self.resampleLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.resample_method)

        self.targetPointsLabel = QLabel(self.resampleGroup)
        self.targetPointsLabel.setObjectName(u"targetPointsLabel")

        self.resampleLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.targetPointsLabel)

        self.target_points = QSpinBox(self.resampleGroup)
        self.target_points.setObjectName(u"target_points")
        self.target_points.setMinimum(10)
        self.target_points.setMaximum(100000)
        self.target_points.setValue(1000)

        self.resampleLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.target_points)


        self.mainLayout.addWidget(self.resampleGroup)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mainLayout.addItem(self.verticalSpacer)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.buttonSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.buttonSpacer)

        self.cancelBtn = QPushButton(MathAnalysisDialog)
        self.cancelBtn.setObjectName(u"cancelBtn")

        self.buttonLayout.addWidget(self.cancelBtn)

        self.applyBtn = QPushButton(MathAnalysisDialog)
        self.applyBtn.setObjectName(u"applyBtn")

        self.buttonLayout.addWidget(self.applyBtn)


        self.mainLayout.addLayout(self.buttonLayout)


        self.retranslateUi(MathAnalysisDialog)

        self.applyBtn.setDefault(True)


        QMetaObject.connectSlotsByName(MathAnalysisDialog)
    # setupUi

    def retranslateUi(self, MathAnalysisDialog):
        MathAnalysisDialog.setWindowTitle(QCoreApplication.translate("MathAnalysisDialog", u"Mathematical Analysis", None))
        self.derivativeGroup.setTitle(QCoreApplication.translate("MathAnalysisDialog", u"\ud83d\udcd0 Derivative Options", None))
        self.derivOrderLabel.setText(QCoreApplication.translate("MathAnalysisDialog", u"Order:", None))
        self.derivMethodLabel.setText(QCoreApplication.translate("MathAnalysisDialog", u"Method:", None))
        self.derivativeMethod.setItemText(0, QCoreApplication.translate("MathAnalysisDialog", u"finite_diff", None))
        self.derivativeMethod.setItemText(1, QCoreApplication.translate("MathAnalysisDialog", u"central_diff", None))
        self.derivativeMethod.setItemText(2, QCoreApplication.translate("MathAnalysisDialog", u"savitzky_golay", None))
        self.derivativeMethod.setItemText(3, QCoreApplication.translate("MathAnalysisDialog", u"spline_derivative", None))

        self.enableSmoothing.setText(QCoreApplication.translate("MathAnalysisDialog", u"Enable post-smoothing", None))
        self.smoothWindowLabel.setText(QCoreApplication.translate("MathAnalysisDialog", u"Window Size:", None))
        self.integralGroup.setTitle(QCoreApplication.translate("MathAnalysisDialog", u"\u222b Integral Options", None))
        self.integralMethodLabel.setText(QCoreApplication.translate("MathAnalysisDialog", u"Method:", None))
        self.integralMethod.setItemText(0, QCoreApplication.translate("MathAnalysisDialog", u"trapezoid", None))
        self.integralMethod.setItemText(1, QCoreApplication.translate("MathAnalysisDialog", u"simpson", None))
        self.integralMethod.setItemText(2, QCoreApplication.translate("MathAnalysisDialog", u"cumulative_trapezoid", None))

        self.smoothingGroup.setTitle(QCoreApplication.translate("MathAnalysisDialog", u"\u3030\ufe0f Smoothing Options", None))
        self.smoothMethodLabel.setText(QCoreApplication.translate("MathAnalysisDialog", u"Method:", None))
        self.smoothMethod.setItemText(0, QCoreApplication.translate("MathAnalysisDialog", u"moving_average", None))
        self.smoothMethod.setItemText(1, QCoreApplication.translate("MathAnalysisDialog", u"savitzky_golay", None))
        self.smoothMethod.setItemText(2, QCoreApplication.translate("MathAnalysisDialog", u"gaussian", None))
        self.smoothMethod.setItemText(3, QCoreApplication.translate("MathAnalysisDialog", u"exponential", None))

        self.windowSizeLabel.setText(QCoreApplication.translate("MathAnalysisDialog", u"Window Size:", None))
        self.polyorderLabel.setText(QCoreApplication.translate("MathAnalysisDialog", u"Polynomial Order:", None))
        self.interpolationGroup.setTitle(QCoreApplication.translate("MathAnalysisDialog", u"\ud83d\udcc8 Interpolation Options", None))
        self.interpMethodLabel.setText(QCoreApplication.translate("MathAnalysisDialog", u"Method:", None))
        self.interp_method.setItemText(0, QCoreApplication.translate("MathAnalysisDialog", u"linear", None))
        self.interp_method.setItemText(1, QCoreApplication.translate("MathAnalysisDialog", u"cubic", None))
        self.interp_method.setItemText(2, QCoreApplication.translate("MathAnalysisDialog", u"spline", None))
        self.interp_method.setItemText(3, QCoreApplication.translate("MathAnalysisDialog", u"akima", None))

        self.resampleGroup.setTitle(QCoreApplication.translate("MathAnalysisDialog", u"\ud83d\udcca Resample Options", None))
        self.resampleMethodLabel.setText(QCoreApplication.translate("MathAnalysisDialog", u"Method:", None))
        self.resample_method.setItemText(0, QCoreApplication.translate("MathAnalysisDialog", u"lttb", None))
        self.resample_method.setItemText(1, QCoreApplication.translate("MathAnalysisDialog", u"linear", None))
        self.resample_method.setItemText(2, QCoreApplication.translate("MathAnalysisDialog", u"mean", None))

        self.targetPointsLabel.setText(QCoreApplication.translate("MathAnalysisDialog", u"Target Points:", None))
        self.cancelBtn.setText(QCoreApplication.translate("MathAnalysisDialog", u"Cancel", None))
        self.applyBtn.setText(QCoreApplication.translate("MathAnalysisDialog", u"Apply", None))
    # retranslateUi

