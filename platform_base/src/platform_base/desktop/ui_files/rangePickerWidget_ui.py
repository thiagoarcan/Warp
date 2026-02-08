
################################################################################
## Form generated from reading UI file 'rangePickerWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
)


class Ui_RangePickerWidget:
    def setupUi(self, RangePickerWidget):
        if not RangePickerWidget.objectName():
            RangePickerWidget.setObjectName("RangePickerWidget")
        RangePickerWidget.resize(400, 200)
        self.mainLayout = QVBoxLayout(RangePickerWidget)
        self.mainLayout.setSpacing(8)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.rangeLayout = QHBoxLayout()
        self.rangeLayout.setObjectName("rangeLayout")
        self.startLabel = QLabel(RangePickerWidget)
        self.startLabel.setObjectName("startLabel")

        self.rangeLayout.addWidget(self.startLabel)

        self.startSpinbox = QDoubleSpinBox(RangePickerWidget)
        self.startSpinbox.setObjectName("startSpinbox")
        self.startSpinbox.setDecimals(6)
        self.startSpinbox.setMinimum(-1000000.000000000000000)
        self.startSpinbox.setMaximum(1000000.000000000000000)

        self.rangeLayout.addWidget(self.startSpinbox)

        self.endLabel = QLabel(RangePickerWidget)
        self.endLabel.setObjectName("endLabel")

        self.rangeLayout.addWidget(self.endLabel)

        self.endSpinbox = QDoubleSpinBox(RangePickerWidget)
        self.endSpinbox.setObjectName("endSpinbox")
        self.endSpinbox.setDecimals(6)
        self.endSpinbox.setMinimum(-1000000.000000000000000)
        self.endSpinbox.setMaximum(1000000.000000000000000)

        self.rangeLayout.addWidget(self.endSpinbox)


        self.mainLayout.addLayout(self.rangeLayout)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName("buttonLayout")
        self.leftSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.leftSpacer)

        self.selectBtn = QPushButton(RangePickerWidget)
        self.selectBtn.setObjectName("selectBtn")

        self.buttonLayout.addWidget(self.selectBtn)

        self.resetBtn = QPushButton(RangePickerWidget)
        self.resetBtn.setObjectName("resetBtn")

        self.buttonLayout.addWidget(self.resetBtn)


        self.mainLayout.addLayout(self.buttonLayout)

        self.plotWidget = QFrame(RangePickerWidget)
        self.plotWidget.setObjectName("plotWidget")
        self.plotWidget.setFrameShape(QFrame.StyledPanel)
        self.plotWidget.setMinimumHeight(100)

        self.mainLayout.addWidget(self.plotWidget)


        self.retranslateUi(RangePickerWidget)

        QMetaObject.connectSlotsByName(RangePickerWidget)
    # setupUi

    def retranslateUi(self, RangePickerWidget):
        self.startLabel.setText(QCoreApplication.translate("RangePickerWidget", "Start:", None))
        self.endLabel.setText(QCoreApplication.translate("RangePickerWidget", "End:", None))
        self.selectBtn.setText(QCoreApplication.translate("RangePickerWidget", "Select Range", None))
        self.resetBtn.setText(QCoreApplication.translate("RangePickerWidget", "Reset", None))
    # retranslateUi

