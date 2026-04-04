# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'conditionalSelectionDialog.ui'
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
    QGroupBox, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_ConditionalSelectionDialog(object):
    def setupUi(self, ConditionalSelectionDialog):
        if not ConditionalSelectionDialog.objectName():
            ConditionalSelectionDialog.setObjectName(u"ConditionalSelectionDialog")
        ConditionalSelectionDialog.resize(400, 350)
        ConditionalSelectionDialog.setModal(True)
        self.mainLayout = QVBoxLayout(ConditionalSelectionDialog)
        self.mainLayout.setSpacing(8)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(12, 12, 12, 12)
        self.thresholdGroup = QGroupBox(ConditionalSelectionDialog)
        self.thresholdGroup.setObjectName(u"thresholdGroup")
        self.thresholdLayout = QHBoxLayout(self.thresholdGroup)
        self.thresholdLayout.setObjectName(u"thresholdLayout")
        self.thresholdLabel = QLabel(self.thresholdGroup)
        self.thresholdLabel.setObjectName(u"thresholdLabel")

        self.thresholdLayout.addWidget(self.thresholdLabel)

        self.thresholdOperator = QComboBox(self.thresholdGroup)
        self.thresholdOperator.addItem("")
        self.thresholdOperator.addItem("")
        self.thresholdOperator.addItem("")
        self.thresholdOperator.addItem("")
        self.thresholdOperator.addItem("")
        self.thresholdOperator.addItem("")
        self.thresholdOperator.setObjectName(u"thresholdOperator")

        self.thresholdLayout.addWidget(self.thresholdOperator)

        self.thresholdSpin = QDoubleSpinBox(self.thresholdGroup)
        self.thresholdSpin.setObjectName(u"thresholdSpin")
        self.thresholdSpin.setMinimum(-1000000.000000000000000)
        self.thresholdSpin.setMaximum(1000000.000000000000000)
        self.thresholdSpin.setSingleStep(0.100000000000000)
        self.thresholdSpin.setDecimals(6)

        self.thresholdLayout.addWidget(self.thresholdSpin)

        self.applyThresholdBtn = QPushButton(self.thresholdGroup)
        self.applyThresholdBtn.setObjectName(u"applyThresholdBtn")

        self.thresholdLayout.addWidget(self.applyThresholdBtn)


        self.mainLayout.addWidget(self.thresholdGroup)

        self.percentileGroup = QGroupBox(ConditionalSelectionDialog)
        self.percentileGroup.setObjectName(u"percentileGroup")
        self.percentileLayout = QHBoxLayout(self.percentileGroup)
        self.percentileLayout.setObjectName(u"percentileLayout")
        self.percentileType = QComboBox(self.percentileGroup)
        self.percentileType.addItem("")
        self.percentileType.addItem("")
        self.percentileType.setObjectName(u"percentileType")

        self.percentileLayout.addWidget(self.percentileType)

        self.percentileSpin = QSpinBox(self.percentileGroup)
        self.percentileSpin.setObjectName(u"percentileSpin")
        self.percentileSpin.setMinimum(1)
        self.percentileSpin.setMaximum(100)
        self.percentileSpin.setValue(10)

        self.percentileLayout.addWidget(self.percentileSpin)

        self.applyPercentileBtn = QPushButton(self.percentileGroup)
        self.applyPercentileBtn.setObjectName(u"applyPercentileBtn")

        self.percentileLayout.addWidget(self.applyPercentileBtn)


        self.mainLayout.addWidget(self.percentileGroup)

        self.expressionGroup = QGroupBox(ConditionalSelectionDialog)
        self.expressionGroup.setObjectName(u"expressionGroup")
        self.expressionLayout = QVBoxLayout(self.expressionGroup)
        self.expressionLayout.setObjectName(u"expressionLayout")
        self.conditionEdit = QTextEdit(self.expressionGroup)
        self.conditionEdit.setObjectName(u"conditionEdit")
        self.conditionEdit.setMaximumHeight(80)

        self.expressionLayout.addWidget(self.conditionEdit)


        self.mainLayout.addWidget(self.expressionGroup)

        self.modeGroup = QGroupBox(ConditionalSelectionDialog)
        self.modeGroup.setObjectName(u"modeGroup")
        self.modeLayout = QHBoxLayout(self.modeGroup)
        self.modeLayout.setObjectName(u"modeLayout")
        self.modeLabel = QLabel(self.modeGroup)
        self.modeLabel.setObjectName(u"modeLabel")

        self.modeLayout.addWidget(self.modeLabel)

        self.modeCombo = QComboBox(self.modeGroup)
        self.modeCombo.addItem("")
        self.modeCombo.addItem("")
        self.modeCombo.addItem("")
        self.modeCombo.addItem("")
        self.modeCombo.setObjectName(u"modeCombo")

        self.modeLayout.addWidget(self.modeCombo)

        self.modeSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.modeLayout.addItem(self.modeSpacer)


        self.mainLayout.addWidget(self.modeGroup)

        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mainLayout.addItem(self.verticalSpacer)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.buttonSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.buttonSpacer)

        self.applyBtn = QPushButton(ConditionalSelectionDialog)
        self.applyBtn.setObjectName(u"applyBtn")

        self.buttonLayout.addWidget(self.applyBtn)

        self.closeBtn = QPushButton(ConditionalSelectionDialog)
        self.closeBtn.setObjectName(u"closeBtn")

        self.buttonLayout.addWidget(self.closeBtn)


        self.mainLayout.addLayout(self.buttonLayout)


        self.retranslateUi(ConditionalSelectionDialog)

        self.applyBtn.setDefault(True)


        QMetaObject.connectSlotsByName(ConditionalSelectionDialog)
    # setupUi

    def retranslateUi(self, ConditionalSelectionDialog):
        ConditionalSelectionDialog.setWindowTitle(QCoreApplication.translate("ConditionalSelectionDialog", u"Conditional Selection", None))
        self.thresholdGroup.setTitle(QCoreApplication.translate("ConditionalSelectionDialog", u"\ud83d\udd22 Threshold Condition", None))
        self.thresholdLabel.setText(QCoreApplication.translate("ConditionalSelectionDialog", u"value", None))
        self.thresholdOperator.setItemText(0, QCoreApplication.translate("ConditionalSelectionDialog", u">", None))
        self.thresholdOperator.setItemText(1, QCoreApplication.translate("ConditionalSelectionDialog", u">=", None))
        self.thresholdOperator.setItemText(2, QCoreApplication.translate("ConditionalSelectionDialog", u"<", None))
        self.thresholdOperator.setItemText(3, QCoreApplication.translate("ConditionalSelectionDialog", u"<=", None))
        self.thresholdOperator.setItemText(4, QCoreApplication.translate("ConditionalSelectionDialog", u"==", None))
        self.thresholdOperator.setItemText(5, QCoreApplication.translate("ConditionalSelectionDialog", u"!=", None))

        self.applyThresholdBtn.setText(QCoreApplication.translate("ConditionalSelectionDialog", u"Apply", None))
#if QT_CONFIG(tooltip)
        self.applyThresholdBtn.setToolTip(QCoreApplication.translate("ConditionalSelectionDialog", u"Apply threshold condition to expression", None))
#endif // QT_CONFIG(tooltip)
        self.percentileGroup.setTitle(QCoreApplication.translate("ConditionalSelectionDialog", u"\ud83d\udcca Percentile Condition", None))
        self.percentileType.setItemText(0, QCoreApplication.translate("ConditionalSelectionDialog", u"Top", None))
        self.percentileType.setItemText(1, QCoreApplication.translate("ConditionalSelectionDialog", u"Bottom", None))

        self.percentileSpin.setSuffix(QCoreApplication.translate("ConditionalSelectionDialog", u"%", None))
        self.applyPercentileBtn.setText(QCoreApplication.translate("ConditionalSelectionDialog", u"Apply", None))
#if QT_CONFIG(tooltip)
        self.applyPercentileBtn.setToolTip(QCoreApplication.translate("ConditionalSelectionDialog", u"Apply percentile condition to expression", None))
#endif // QT_CONFIG(tooltip)
        self.expressionGroup.setTitle(QCoreApplication.translate("ConditionalSelectionDialog", u"\ud83d\udcdd Custom Expression", None))
        self.conditionEdit.setPlaceholderText(QCoreApplication.translate("ConditionalSelectionDialog", u"Enter a Python expression using 'value' or 'values' array\n"
"Examples:\n"
"  value > 0\n"
"  value >= np.percentile(values, 90)\n"
"  (value > 10) & (value < 100)", None))
        self.modeGroup.setTitle(QCoreApplication.translate("ConditionalSelectionDialog", u"\u2699\ufe0f Selection Mode", None))
        self.modeLabel.setText(QCoreApplication.translate("ConditionalSelectionDialog", u"Mode:", None))
        self.modeCombo.setItemText(0, QCoreApplication.translate("ConditionalSelectionDialog", u"Replace", None))
        self.modeCombo.setItemText(1, QCoreApplication.translate("ConditionalSelectionDialog", u"Add", None))
        self.modeCombo.setItemText(2, QCoreApplication.translate("ConditionalSelectionDialog", u"Subtract", None))
        self.modeCombo.setItemText(3, QCoreApplication.translate("ConditionalSelectionDialog", u"Intersect", None))

        self.applyBtn.setText(QCoreApplication.translate("ConditionalSelectionDialog", u"Apply Selection", None))
        self.closeBtn.setText(QCoreApplication.translate("ConditionalSelectionDialog", u"Close", None))
    # retranslateUi

