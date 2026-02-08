
################################################################################
## Form generated from reading UI file 'queryBuilderWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
)


class Ui_QueryBuilderWidget:
    def setupUi(self, QueryBuilderWidget):
        if not QueryBuilderWidget.objectName():
            QueryBuilderWidget.setObjectName("QueryBuilderWidget")
        QueryBuilderWidget.resize(350, 300)
        self.mainLayout = QVBoxLayout(QueryBuilderWidget)
        self.mainLayout.setSpacing(8)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.queryLayout = QFormLayout()
        self.queryLayout.setObjectName("queryLayout")
        self.seriesLabel = QLabel(QueryBuilderWidget)
        self.seriesLabel.setObjectName("seriesLabel")

        self.queryLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.seriesLabel)

        self.seriesCombo = QComboBox(QueryBuilderWidget)
        self.seriesCombo.setObjectName("seriesCombo")

        self.queryLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.seriesCombo)

        self.operatorLabel = QLabel(QueryBuilderWidget)
        self.operatorLabel.setObjectName("operatorLabel")

        self.queryLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.operatorLabel)

        self.operatorCombo = QComboBox(QueryBuilderWidget)
        self.operatorCombo.addItem("")
        self.operatorCombo.addItem("")
        self.operatorCombo.addItem("")
        self.operatorCombo.addItem("")
        self.operatorCombo.addItem("")
        self.operatorCombo.addItem("")
        self.operatorCombo.setObjectName("operatorCombo")

        self.queryLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.operatorCombo)

        self.valueTypeLabel = QLabel(QueryBuilderWidget)
        self.valueTypeLabel.setObjectName("valueTypeLabel")

        self.queryLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.valueTypeLabel)

        self.valueTypeCombo = QComboBox(QueryBuilderWidget)
        self.valueTypeCombo.addItem("")
        self.valueTypeCombo.addItem("")
        self.valueTypeCombo.addItem("")
        self.valueTypeCombo.setObjectName("valueTypeCombo")

        self.queryLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.valueTypeCombo)

        self.valueLabel = QLabel(QueryBuilderWidget)
        self.valueLabel.setObjectName("valueLabel")

        self.queryLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.valueLabel)

        self.numberInput = QDoubleSpinBox(QueryBuilderWidget)
        self.numberInput.setObjectName("numberInput")
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
        self.statsCombo.setObjectName("statsCombo")

        self.queryLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.statsCombo)

        self.percentileInput = QSpinBox(QueryBuilderWidget)
        self.percentileInput.setObjectName("percentileInput")
        self.percentileInput.setMinimum(1)
        self.percentileInput.setMaximum(99)
        self.percentileInput.setValue(50)

        self.queryLayout.setWidget(5, QFormLayout.ItemRole.FieldRole, self.percentileInput)


        self.mainLayout.addLayout(self.queryLayout)

        self.previewGroup = QGroupBox(QueryBuilderWidget)
        self.previewGroup.setObjectName("previewGroup")
        self.previewLayout = QVBoxLayout(self.previewGroup)
        self.previewLayout.setObjectName("previewLayout")
        self.queryPreview = QTextEdit(self.previewGroup)
        self.queryPreview.setObjectName("queryPreview")
        self.queryPreview.setReadOnly(True)
        self.queryPreview.setMaximumHeight(60)

        self.previewLayout.addWidget(self.queryPreview)


        self.mainLayout.addWidget(self.previewGroup)

        self.executeBtn = QPushButton(QueryBuilderWidget)
        self.executeBtn.setObjectName("executeBtn")

        self.mainLayout.addWidget(self.executeBtn)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mainLayout.addItem(self.verticalSpacer)


        self.retranslateUi(QueryBuilderWidget)

        QMetaObject.connectSlotsByName(QueryBuilderWidget)
    # setupUi

    def retranslateUi(self, QueryBuilderWidget):
        self.seriesLabel.setText(QCoreApplication.translate("QueryBuilderWidget", "Series:", None))
        self.operatorLabel.setText(QCoreApplication.translate("QueryBuilderWidget", "Operator:", None))
        self.operatorCombo.setItemText(0, QCoreApplication.translate("QueryBuilderWidget", ">", None))
        self.operatorCombo.setItemText(1, QCoreApplication.translate("QueryBuilderWidget", ">=", None))
        self.operatorCombo.setItemText(2, QCoreApplication.translate("QueryBuilderWidget", "<", None))
        self.operatorCombo.setItemText(3, QCoreApplication.translate("QueryBuilderWidget", "<=", None))
        self.operatorCombo.setItemText(4, QCoreApplication.translate("QueryBuilderWidget", "==", None))
        self.operatorCombo.setItemText(5, QCoreApplication.translate("QueryBuilderWidget", "!=", None))

        self.valueTypeLabel.setText(QCoreApplication.translate("QueryBuilderWidget", "Value Type:", None))
        self.valueTypeCombo.setItemText(0, QCoreApplication.translate("QueryBuilderWidget", "Number", None))
        self.valueTypeCombo.setItemText(1, QCoreApplication.translate("QueryBuilderWidget", "Statistics", None))
        self.valueTypeCombo.setItemText(2, QCoreApplication.translate("QueryBuilderWidget", "Percentile", None))

        self.valueLabel.setText(QCoreApplication.translate("QueryBuilderWidget", "Value:", None))
        self.statsCombo.setItemText(0, QCoreApplication.translate("QueryBuilderWidget", "mean", None))
        self.statsCombo.setItemText(1, QCoreApplication.translate("QueryBuilderWidget", "max", None))
        self.statsCombo.setItemText(2, QCoreApplication.translate("QueryBuilderWidget", "min", None))
        self.statsCombo.setItemText(3, QCoreApplication.translate("QueryBuilderWidget", "std", None))
        self.statsCombo.setItemText(4, QCoreApplication.translate("QueryBuilderWidget", "median", None))

        self.percentileInput.setSuffix(QCoreApplication.translate("QueryBuilderWidget", "%", None))
        self.previewGroup.setTitle(QCoreApplication.translate("QueryBuilderWidget", "Query Preview", None))
        self.executeBtn.setText(QCoreApplication.translate("QueryBuilderWidget", "Execute Query", None))
    # retranslateUi

