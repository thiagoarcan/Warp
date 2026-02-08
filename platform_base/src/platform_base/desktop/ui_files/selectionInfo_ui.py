
################################################################################
## Form generated from reading UI file 'selectionInfo.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
)


class Ui_SelectionInfo:
    def setupUi(self, SelectionInfo):
        if not SelectionInfo.objectName():
            SelectionInfo.setObjectName("SelectionInfo")
        SelectionInfo.resize(250, 150)
        self.mainLayout = QVBoxLayout(SelectionInfo)
        self.mainLayout.setSpacing(4)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.countLayout = QHBoxLayout()
        self.countLayout.setObjectName("countLayout")
        self.countLabel = QLabel(SelectionInfo)
        self.countLabel.setObjectName("countLabel")

        self.countLayout.addWidget(self.countLabel)

        self.countValue = QLabel(SelectionInfo)
        self.countValue.setObjectName("countValue")
        self.countValue.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.countLayout.addWidget(self.countValue)

        self.percentageLabel = QLabel(SelectionInfo)
        self.percentageLabel.setObjectName("percentageLabel")

        self.countLayout.addWidget(self.percentageLabel)


        self.mainLayout.addLayout(self.countLayout)

        self.statsGroup = QGroupBox(SelectionInfo)
        self.statsGroup.setObjectName("statsGroup")
        self.statsLayout = QFormLayout(self.statsGroup)
        self.statsLayout.setObjectName("statsLayout")
        self.minLabelTitle = QLabel(self.statsGroup)
        self.minLabelTitle.setObjectName("minLabelTitle")

        self.statsLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.minLabelTitle)

        self.minLabel = QLabel(self.statsGroup)
        self.minLabel.setObjectName("minLabel")
        self.minLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.statsLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.minLabel)

        self.maxLabelTitle = QLabel(self.statsGroup)
        self.maxLabelTitle.setObjectName("maxLabelTitle")

        self.statsLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.maxLabelTitle)

        self.maxLabel = QLabel(self.statsGroup)
        self.maxLabel.setObjectName("maxLabel")
        self.maxLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.statsLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.maxLabel)

        self.meanLabelTitle = QLabel(self.statsGroup)
        self.meanLabelTitle.setObjectName("meanLabelTitle")

        self.statsLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.meanLabelTitle)

        self.meanLabel = QLabel(self.statsGroup)
        self.meanLabel.setObjectName("meanLabel")
        self.meanLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.statsLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.meanLabel)

        self.stdLabelTitle = QLabel(self.statsGroup)
        self.stdLabelTitle.setObjectName("stdLabelTitle")

        self.statsLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.stdLabelTitle)

        self.stdLabel = QLabel(self.statsGroup)
        self.stdLabel.setObjectName("stdLabel")
        self.stdLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.statsLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.stdLabel)


        self.mainLayout.addWidget(self.statsGroup)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mainLayout.addItem(self.verticalSpacer)


        self.retranslateUi(SelectionInfo)

        QMetaObject.connectSlotsByName(SelectionInfo)
    # setupUi

    def retranslateUi(self, SelectionInfo):
        self.countLabel.setText(QCoreApplication.translate("SelectionInfo", "Selected:", None))
        self.countValue.setText(QCoreApplication.translate("SelectionInfo", "0 / 0 points", None))
        self.countValue.setStyleSheet(QCoreApplication.translate("SelectionInfo", "font-weight: bold;", None))
        self.percentageLabel.setText(QCoreApplication.translate("SelectionInfo", "(0%)", None))
        self.percentageLabel.setStyleSheet(QCoreApplication.translate("SelectionInfo", "color: gray;", None))
        self.statsGroup.setTitle(QCoreApplication.translate("SelectionInfo", "Statistics", None))
        self.minLabelTitle.setText(QCoreApplication.translate("SelectionInfo", "Min:", None))
        self.minLabel.setText(QCoreApplication.translate("SelectionInfo", "-", None))
        self.maxLabelTitle.setText(QCoreApplication.translate("SelectionInfo", "Max:", None))
        self.maxLabel.setText(QCoreApplication.translate("SelectionInfo", "-", None))
        self.meanLabelTitle.setText(QCoreApplication.translate("SelectionInfo", "Mean:", None))
        self.meanLabel.setText(QCoreApplication.translate("SelectionInfo", "-", None))
        self.stdLabelTitle.setText(QCoreApplication.translate("SelectionInfo", "Std Dev:", None))
        self.stdLabel.setText(QCoreApplication.translate("SelectionInfo", "-", None))
    # retranslateUi

