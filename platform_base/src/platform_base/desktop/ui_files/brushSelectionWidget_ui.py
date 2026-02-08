
################################################################################
## Form generated from reading UI file 'brushSelectionWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
)


class Ui_BrushSelectionWidget:
    def setupUi(self, BrushSelectionWidget):
        if not BrushSelectionWidget.objectName():
            BrushSelectionWidget.setObjectName("BrushSelectionWidget")
        BrushSelectionWidget.resize(400, 300)
        self.mainLayout = QVBoxLayout(BrushSelectionWidget)
        self.mainLayout.setSpacing(4)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(4, 4, 4, 4)
        self.toolbarLayout = QHBoxLayout()
        self.toolbarLayout.setObjectName("toolbarLayout")
        self.enableSelectionBtn = QPushButton(BrushSelectionWidget)
        self.enableSelectionBtn.setObjectName("enableSelectionBtn")
        self.enableSelectionBtn.setCheckable(True)

        self.toolbarLayout.addWidget(self.enableSelectionBtn)

        self.selectBtn = QPushButton(BrushSelectionWidget)
        self.selectBtn.setObjectName("selectBtn")

        self.toolbarLayout.addWidget(self.selectBtn)

        self.clearSelectionBtn = QPushButton(BrushSelectionWidget)
        self.clearSelectionBtn.setObjectName("clearSelectionBtn")

        self.toolbarLayout.addWidget(self.clearSelectionBtn)

        self.toolbarSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.toolbarLayout.addItem(self.toolbarSpacer)

        self.selectionInfoLabel = QLabel(BrushSelectionWidget)
        self.selectionInfoLabel.setObjectName("selectionInfoLabel")

        self.toolbarLayout.addWidget(self.selectionInfoLabel)


        self.mainLayout.addLayout(self.toolbarLayout)

        self.plotWidget = QFrame(BrushSelectionWidget)
        self.plotWidget.setObjectName("plotWidget")
        self.plotWidget.setFrameShape(QFrame.StyledPanel)
        self.plotLayout = QVBoxLayout(self.plotWidget)
        self.plotLayout.setContentsMargins(0, 0, 0, 0)
        self.plotLayout.setObjectName("plotLayout")

        self.mainLayout.addWidget(self.plotWidget)


        self.retranslateUi(BrushSelectionWidget)

        QMetaObject.connectSlotsByName(BrushSelectionWidget)
    # setupUi

    def retranslateUi(self, BrushSelectionWidget):
        self.enableSelectionBtn.setText(QCoreApplication.translate("BrushSelectionWidget", "Enable Selection", None))
        self.selectBtn.setText(QCoreApplication.translate("BrushSelectionWidget", "Select", None))
        self.clearSelectionBtn.setText(QCoreApplication.translate("BrushSelectionWidget", "Clear", None))
        self.selectionInfoLabel.setText(QCoreApplication.translate("BrushSelectionWidget", "0 points selected", None))
    # retranslateUi

