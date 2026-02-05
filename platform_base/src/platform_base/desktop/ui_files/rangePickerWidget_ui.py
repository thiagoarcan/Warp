# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'rangePickerWidget.ui'
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
from PySide6.QtWidgets import (QApplication, QDoubleSpinBox, QFrame, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_RangePickerWidget(object):
    def setupUi(self, RangePickerWidget):
        if not RangePickerWidget.objectName():
            RangePickerWidget.setObjectName(u"RangePickerWidget")
        RangePickerWidget.resize(400, 200)
        self.mainLayout = QVBoxLayout(RangePickerWidget)
        self.mainLayout.setSpacing(8)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.rangeLayout = QHBoxLayout()
        self.rangeLayout.setObjectName(u"rangeLayout")
        self.startLabel = QLabel(RangePickerWidget)
        self.startLabel.setObjectName(u"startLabel")

        self.rangeLayout.addWidget(self.startLabel)

        self.startSpinbox = QDoubleSpinBox(RangePickerWidget)
        self.startSpinbox.setObjectName(u"startSpinbox")
        self.startSpinbox.setDecimals(6)
        self.startSpinbox.setMinimum(-1000000.000000000000000)
        self.startSpinbox.setMaximum(1000000.000000000000000)

        self.rangeLayout.addWidget(self.startSpinbox)

        self.endLabel = QLabel(RangePickerWidget)
        self.endLabel.setObjectName(u"endLabel")

        self.rangeLayout.addWidget(self.endLabel)

        self.endSpinbox = QDoubleSpinBox(RangePickerWidget)
        self.endSpinbox.setObjectName(u"endSpinbox")
        self.endSpinbox.setDecimals(6)
        self.endSpinbox.setMinimum(-1000000.000000000000000)
        self.endSpinbox.setMaximum(1000000.000000000000000)

        self.rangeLayout.addWidget(self.endSpinbox)


        self.mainLayout.addLayout(self.rangeLayout)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.leftSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.leftSpacer)

        self.selectBtn = QPushButton(RangePickerWidget)
        self.selectBtn.setObjectName(u"selectBtn")

        self.buttonLayout.addWidget(self.selectBtn)

        self.resetBtn = QPushButton(RangePickerWidget)
        self.resetBtn.setObjectName(u"resetBtn")

        self.buttonLayout.addWidget(self.resetBtn)


        self.mainLayout.addLayout(self.buttonLayout)

        self.plotWidget = QFrame(RangePickerWidget)
        self.plotWidget.setObjectName(u"plotWidget")
        self.plotWidget.setFrameShape(QFrame.StyledPanel)
        self.plotWidget.setMinimumHeight(100)

        self.mainLayout.addWidget(self.plotWidget)


        self.retranslateUi(RangePickerWidget)

        QMetaObject.connectSlotsByName(RangePickerWidget)
    # setupUi

    def retranslateUi(self, RangePickerWidget):
        self.startLabel.setText(QCoreApplication.translate("RangePickerWidget", u"Start:", None))
        self.endLabel.setText(QCoreApplication.translate("RangePickerWidget", u"End:", None))
        self.selectBtn.setText(QCoreApplication.translate("RangePickerWidget", u"Select Range", None))
        self.resetBtn.setText(QCoreApplication.translate("RangePickerWidget", u"Reset", None))
        pass
    # retranslateUi

