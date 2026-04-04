# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'queryBuilderWidget.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QFormLayout,
    QGroupBox, QLabel, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QTextEdit, QVBoxLayout,
    QWidget)

class Ui_QueryBuilderWidget(object):
    def setupUi(self, QueryBuilderWidget):
        if not QueryBuilderWidget.objectName():
            QueryBuilderWidget.setObjectName(u"QueryBuilderWidget")
        QueryBuilderWidget.resize(350, 300)
        self.mainLayout = QVBoxLayout(QueryBuilderWidget)
        self.mainLayout.setSpacing(8)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.queryLayout = QFormLayout()
        self.queryLayout.setObjectName(u"queryLayout")
        self.seriesLabel = QLabel(QueryBuilderWidget)
        self.seriesLabel.setObjectName(u"seriesLabel")

        self.queryLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.seriesLabel)

        self.seriesCombo = QComboBox(QueryBuilderWidget)
        self.seriesCombo.setObjectName(u"seriesCombo")

        self.queryLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.seriesCombo)

        self.operatorLabel = QLabel(QueryBuilderWidget)
        self.operatorLabel.setObjectName(u"operatorLabel")

        self.queryLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.operatorLabel)

        self.operatorCombo = QComboBox(QueryBuilderWidget)
        self.operatorCombo.addItem("")
        self.operatorCombo.addItem("")
        self.operatorCombo.addItem("")
        self.operatorCombo.addItem("")
        self.operatorCombo.addItem("")
        self.operatorCombo.addItem("")
        self.operatorCombo.setObjectName(u"operatorCombo")

        self.queryLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.operatorCombo)

        self.valueTypeLabel = QLabel(QueryBuilderWidget)
        self.valueTypeLabel.setObjectName(u"valueTypeLabel")

        self.queryLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.valueTypeLabel)

        self.valueTypeCombo = QComboBox(QueryBuilderWidget)
        self.valueTypeCombo.addItem("")
        self.valueTypeCombo.addItem("")
        self.valueTypeCombo.addItem("")
        self.valueTypeCombo.setObjectName(u"valueTypeCombo")

        self.queryLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.valueTypeCombo)

        self.valueLabel = QLabel(QueryBuilderWidget)
        self.valueLabel.setObjectName(u"valueLabel")

        self.queryLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.valueLabel)

        self.numberInput = QDoubleSpinBox(QueryBuilderWidget)
        self.numberInput.setObjectName(u"numberInput")
        self.numberInput.setDecimals(6)
        self.numberInput.setMinimum(-1000000.000000000000000)
        self.numberInput.setMaximum(1000000.000000000000000)

        self.queryLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.numberInput)

        self.statsCombo = QComboBox(QueryBuilderWidget)
        self.statsCombo.addItem("")
        self.statsCombo.addItem("")
        self.statsCombo.addItem("")
        self.statsCombo.addItem("")
        self.statsCombo.addItem("")
        self.statsCombo.setObjectName(u"statsCombo")

        self.queryLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.statsCombo)

        self.percentileInput = QSpinBox(QueryBuilderWidget)
        self.percentileInput.setObjectName(u"percentileInput")
        self.percentileInput.setMinimum(1)
        self.percentileInput.setMaximum(99)
        self.percentileInput.setValue(50)

        self.queryLayout.setWidget(5, QFormLayout.ItemRole.FieldRole, self.percentileInput)


        self.mainLayout.addLayout(self.queryLayout)

        self.previewGroup = QGroupBox(QueryBuilderWidget)
        self.previewGroup.setObjectName(u"previewGroup")
        self.previewLayout = QVBoxLayout(self.previewGroup)
        self.previewLayout.setObjectName(u"previewLayout")
        self.queryPreview = QTextEdit(self.previewGroup)
        self.queryPreview.setObjectName(u"queryPreview")
        self.queryPreview.setReadOnly(True)
        self.queryPreview.setMaximumHeight(60)

        self.previewLayout.addWidget(self.queryPreview)


        self.mainLayout.addWidget(self.previewGroup)

        self.executeBtn = QPushButton(QueryBuilderWidget)
        self.executeBtn.setObjectName(u"executeBtn")

        self.mainLayout.addWidget(self.executeBtn)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mainLayout.addItem(self.verticalSpacer)


        self.retranslateUi(QueryBuilderWidget)

        QMetaObject.connectSlotsByName(QueryBuilderWidget)
    # setupUi

    def retranslateUi(self, QueryBuilderWidget):
        self.seriesLabel.setText(QCoreApplication.translate("QueryBuilderWidget", u"Series:", None))
        self.operatorLabel.setText(QCoreApplication.translate("QueryBuilderWidget", u"Operator:", None))
        self.operatorCombo.setItemText(0, QCoreApplication.translate("QueryBuilderWidget", u">", None))
        self.operatorCombo.setItemText(1, QCoreApplication.translate("QueryBuilderWidget", u">=", None))
        self.operatorCombo.setItemText(2, QCoreApplication.translate("QueryBuilderWidget", u"<", None))
        self.operatorCombo.setItemText(3, QCoreApplication.translate("QueryBuilderWidget", u"<=", None))
        self.operatorCombo.setItemText(4, QCoreApplication.translate("QueryBuilderWidget", u"==", None))
        self.operatorCombo.setItemText(5, QCoreApplication.translate("QueryBuilderWidget", u"!=", None))

        self.valueTypeLabel.setText(QCoreApplication.translate("QueryBuilderWidget", u"Value Type:", None))
        self.valueTypeCombo.setItemText(0, QCoreApplication.translate("QueryBuilderWidget", u"Number", None))
        self.valueTypeCombo.setItemText(1, QCoreApplication.translate("QueryBuilderWidget", u"Statistics", None))
        self.valueTypeCombo.setItemText(2, QCoreApplication.translate("QueryBuilderWidget", u"Percentile", None))

        self.valueLabel.setText(QCoreApplication.translate("QueryBuilderWidget", u"Value:", None))
        self.statsCombo.setItemText(0, QCoreApplication.translate("QueryBuilderWidget", u"mean", None))
        self.statsCombo.setItemText(1, QCoreApplication.translate("QueryBuilderWidget", u"max", None))
        self.statsCombo.setItemText(2, QCoreApplication.translate("QueryBuilderWidget", u"min", None))
        self.statsCombo.setItemText(3, QCoreApplication.translate("QueryBuilderWidget", u"std", None))
        self.statsCombo.setItemText(4, QCoreApplication.translate("QueryBuilderWidget", u"median", None))

        self.percentileInput.setSuffix(QCoreApplication.translate("QueryBuilderWidget", u"%", None))
        self.previewGroup.setTitle(QCoreApplication.translate("QueryBuilderWidget", u"Query Preview", None))
        self.executeBtn.setText(QCoreApplication.translate("QueryBuilderWidget", u"Execute Query", None))
        pass
    # retranslateUi

