
################################################################################
## Form generated from reading UI file 'mathAnalysisDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QVBoxLayout,
)


class Ui_MathAnalysisDialog:
    def setupUi(self, MathAnalysisDialog):
        if not MathAnalysisDialog.objectName():
            MathAnalysisDialog.setObjectName("MathAnalysisDialog")
        MathAnalysisDialog.resize(400, 350)
        MathAnalysisDialog.setMinimumSize(QSize(350, 200))
        MathAnalysisDialog.setModal(True)
        self.mainLayout = QVBoxLayout(MathAnalysisDialog)
        self.mainLayout.setSpacing(12)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(16, 16, 16, 16)
        self.derivativeGroup = QGroupBox(MathAnalysisDialog)
        self.derivativeGroup.setObjectName("derivativeGroup")
        self.derivativeLayout = QFormLayout(self.derivativeGroup)
        self.derivativeLayout.setObjectName("derivativeLayout")
        self.derivOrderLabel = QLabel(self.derivativeGroup)
        self.derivOrderLabel.setObjectName("derivOrderLabel")

        self.derivativeLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.derivOrderLabel)

        self.derivativeOrder = QSpinBox(self.derivativeGroup)
        self.derivativeOrder.setObjectName("derivativeOrder")
        self.derivativeOrder.setMinimum(1)
        self.derivativeOrder.setMaximum(5)
        self.derivativeOrder.setValue(1)

        self.derivativeLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.derivativeOrder)

        self.derivMethodLabel = QLabel(self.derivativeGroup)
        self.derivMethodLabel.setObjectName("derivMethodLabel")

        self.derivativeLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.derivMethodLabel)

        self.derivativeMethod = QComboBox(self.derivativeGroup)
        self.derivativeMethod.addItem("")
        self.derivativeMethod.addItem("")
        self.derivativeMethod.addItem("")
        self.derivativeMethod.addItem("")
        self.derivativeMethod.setObjectName("derivativeMethod")

        self.derivativeLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.derivativeMethod)

        self.enableSmoothing = QCheckBox(self.derivativeGroup)
        self.enableSmoothing.setObjectName("enableSmoothing")

        self.derivativeLayout.setWidget(2, QFormLayout.ItemRole.SpanningRole, self.enableSmoothing)

        self.smoothWindowLabel = QLabel(self.derivativeGroup)
        self.smoothWindowLabel.setObjectName("smoothWindowLabel")

        self.derivativeLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.smoothWindowLabel)

        self.smoothingWindow = QSpinBox(self.derivativeGroup)
        self.smoothingWindow.setObjectName("smoothingWindow")
        self.smoothingWindow.setEnabled(False)
        self.smoothingWindow.setMinimum(3)
        self.smoothingWindow.setMaximum(101)
        self.smoothingWindow.setSingleStep(2)
        self.smoothingWindow.setValue(5)

        self.derivativeLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.smoothingWindow)


        self.mainLayout.addWidget(self.derivativeGroup)

        self.integralGroup = QGroupBox(MathAnalysisDialog)
        self.integralGroup.setObjectName("integralGroup")
        self.integralLayout = QFormLayout(self.integralGroup)
        self.integralLayout.setObjectName("integralLayout")
        self.integralMethodLabel = QLabel(self.integralGroup)
        self.integralMethodLabel.setObjectName("integralMethodLabel")

        self.integralLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.integralMethodLabel)

        self.integralMethod = QComboBox(self.integralGroup)
        self.integralMethod.addItem("")
        self.integralMethod.addItem("")
        self.integralMethod.addItem("")
        self.integralMethod.setObjectName("integralMethod")

        self.integralLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.integralMethod)


        self.mainLayout.addWidget(self.integralGroup)

        self.smoothingGroup = QGroupBox(MathAnalysisDialog)
        self.smoothingGroup.setObjectName("smoothingGroup")
        self.smoothingLayout = QFormLayout(self.smoothingGroup)
        self.smoothingLayout.setObjectName("smoothingLayout")
        self.smoothMethodLabel = QLabel(self.smoothingGroup)
        self.smoothMethodLabel.setObjectName("smoothMethodLabel")

        self.smoothingLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.smoothMethodLabel)

        self.smoothMethod = QComboBox(self.smoothingGroup)
        self.smoothMethod.addItem("")
        self.smoothMethod.addItem("")
        self.smoothMethod.addItem("")
        self.smoothMethod.addItem("")
        self.smoothMethod.setObjectName("smoothMethod")

        self.smoothingLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.smoothMethod)

        self.windowSizeLabel = QLabel(self.smoothingGroup)
        self.windowSizeLabel.setObjectName("windowSizeLabel")

        self.smoothingLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.windowSizeLabel)

        self.windowSize = QSpinBox(self.smoothingGroup)
        self.windowSize.setObjectName("windowSize")
        self.windowSize.setMinimum(3)
        self.windowSize.setMaximum(201)
        self.windowSize.setSingleStep(2)
        self.windowSize.setValue(11)

        self.smoothingLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.windowSize)

        self.polyorderLabel = QLabel(self.smoothingGroup)
        self.polyorderLabel.setObjectName("polyorderLabel")

        self.smoothingLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.polyorderLabel)

        self.polyorder = QSpinBox(self.smoothingGroup)
        self.polyorder.setObjectName("polyorder")
        self.polyorder.setMinimum(1)
        self.polyorder.setMaximum(10)
        self.polyorder.setValue(3)

        self.smoothingLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.polyorder)


        self.mainLayout.addWidget(self.smoothingGroup)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mainLayout.addItem(self.verticalSpacer)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName("buttonLayout")
        self.buttonSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.buttonSpacer)

        self.cancelBtn = QPushButton(MathAnalysisDialog)
        self.cancelBtn.setObjectName("cancelBtn")

        self.buttonLayout.addWidget(self.cancelBtn)

        self.applyBtn = QPushButton(MathAnalysisDialog)
        self.applyBtn.setObjectName("applyBtn")

        self.buttonLayout.addWidget(self.applyBtn)


        self.mainLayout.addLayout(self.buttonLayout)


        self.retranslateUi(MathAnalysisDialog)

        self.applyBtn.setDefault(True)


        QMetaObject.connectSlotsByName(MathAnalysisDialog)
    # setupUi

    def retranslateUi(self, MathAnalysisDialog):
        MathAnalysisDialog.setWindowTitle(QCoreApplication.translate("MathAnalysisDialog", "Mathematical Analysis", None))
        self.derivativeGroup.setTitle(QCoreApplication.translate("MathAnalysisDialog", "\ud83d\udcd0 Derivative Options", None))
        self.derivOrderLabel.setText(QCoreApplication.translate("MathAnalysisDialog", "Order:", None))
        self.derivMethodLabel.setText(QCoreApplication.translate("MathAnalysisDialog", "Method:", None))
        self.derivativeMethod.setItemText(0, QCoreApplication.translate("MathAnalysisDialog", "central_diff", None))
        self.derivativeMethod.setItemText(1, QCoreApplication.translate("MathAnalysisDialog", "forward_diff", None))
        self.derivativeMethod.setItemText(2, QCoreApplication.translate("MathAnalysisDialog", "backward_diff", None))
        self.derivativeMethod.setItemText(3, QCoreApplication.translate("MathAnalysisDialog", "savitzky_golay", None))

        self.enableSmoothing.setText(QCoreApplication.translate("MathAnalysisDialog", "Enable post-smoothing", None))
        self.smoothWindowLabel.setText(QCoreApplication.translate("MathAnalysisDialog", "Window Size:", None))
        self.integralGroup.setTitle(QCoreApplication.translate("MathAnalysisDialog", "\u222b Integral Options", None))
        self.integralMethodLabel.setText(QCoreApplication.translate("MathAnalysisDialog", "Method:", None))
        self.integralMethod.setItemText(0, QCoreApplication.translate("MathAnalysisDialog", "trapezoid", None))
        self.integralMethod.setItemText(1, QCoreApplication.translate("MathAnalysisDialog", "simpson", None))
        self.integralMethod.setItemText(2, QCoreApplication.translate("MathAnalysisDialog", "cumulative_trapezoid", None))

        self.smoothingGroup.setTitle(QCoreApplication.translate("MathAnalysisDialog", "\u3030\ufe0f Smoothing Options", None))
        self.smoothMethodLabel.setText(QCoreApplication.translate("MathAnalysisDialog", "Method:", None))
        self.smoothMethod.setItemText(0, QCoreApplication.translate("MathAnalysisDialog", "moving_average", None))
        self.smoothMethod.setItemText(1, QCoreApplication.translate("MathAnalysisDialog", "savitzky_golay", None))
        self.smoothMethod.setItemText(2, QCoreApplication.translate("MathAnalysisDialog", "gaussian", None))
        self.smoothMethod.setItemText(3, QCoreApplication.translate("MathAnalysisDialog", "exponential", None))

        self.windowSizeLabel.setText(QCoreApplication.translate("MathAnalysisDialog", "Window Size:", None))
        self.polyorderLabel.setText(QCoreApplication.translate("MathAnalysisDialog", "Polynomial Order:", None))
        self.cancelBtn.setText(QCoreApplication.translate("MathAnalysisDialog", "Cancel", None))
        self.applyBtn.setText(QCoreApplication.translate("MathAnalysisDialog", "Apply", None))
    # retranslateUi

