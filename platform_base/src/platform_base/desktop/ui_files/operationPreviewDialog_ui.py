
################################################################################
## Form generated from reading UI file 'operationPreviewDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize, Qt
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class Ui_OperationPreviewDialog:
    def setupUi(self, OperationPreviewDialog):
        if not OperationPreviewDialog.objectName():
            OperationPreviewDialog.setObjectName("OperationPreviewDialog")
        OperationPreviewDialog.resize(800, 600)
        OperationPreviewDialog.setMinimumSize(QSize(600, 400))
        OperationPreviewDialog.setModal(True)
        self.mainLayout = QVBoxLayout(OperationPreviewDialog)
        self.mainLayout.setSpacing(8)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(12, 12, 12, 12)
        self.titleLabel = QLabel(OperationPreviewDialog)
        self.titleLabel.setObjectName("titleLabel")

        self.mainLayout.addWidget(self.titleLabel)

        self.mainSplitter = QSplitter(OperationPreviewDialog)
        self.mainSplitter.setObjectName("mainSplitter")
        self.mainSplitter.setOrientation(Qt.Horizontal)
        self.canvasFrame = QFrame(self.mainSplitter)
        self.canvasFrame.setObjectName("canvasFrame")
        self.canvasFrame.setFrameShape(QFrame.StyledPanel)
        self.canvasFrame.setMinimumWidth(400)
        self.canvasLayout = QVBoxLayout(self.canvasFrame)
        self.canvasLayout.setContentsMargins(0, 0, 0, 0)
        self.canvasLayout.setObjectName("canvasLayout")
        self.mainSplitter.addWidget(self.canvasFrame)
        self.infoPanel = QWidget(self.mainSplitter)
        self.infoPanel.setObjectName("infoPanel")
        self.infoPanel.setMinimumWidth(200)
        self.infoLayout = QVBoxLayout(self.infoPanel)
        self.infoLayout.setSpacing(8)
        self.infoLayout.setObjectName("infoLayout")
        self.infoLayout.setContentsMargins(0, 0, 0, 0)
        self.paramsGroup = QGroupBox(self.infoPanel)
        self.paramsGroup.setObjectName("paramsGroup")
        self.paramsLayout = QVBoxLayout(self.paramsGroup)
        self.paramsLayout.setObjectName("paramsLayout")
        self.paramsText = QTextEdit(self.paramsGroup)
        self.paramsText.setObjectName("paramsText")
        self.paramsText.setReadOnly(True)
        self.paramsText.setMaximumHeight(100)

        self.paramsLayout.addWidget(self.paramsText)


        self.infoLayout.addWidget(self.paramsGroup)

        self.statsGroup = QGroupBox(self.infoPanel)
        self.statsGroup.setObjectName("statsGroup")
        self.statsLayout = QFormLayout(self.statsGroup)
        self.statsLayout.setObjectName("statsLayout")
        self.origMeanLabel = QLabel(self.statsGroup)
        self.origMeanLabel.setObjectName("origMeanLabel")

        self.statsLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.origMeanLabel)

        self.origMeanValue = QLabel(self.statsGroup)
        self.origMeanValue.setObjectName("origMeanValue")

        self.statsLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.origMeanValue)

        self.resultMeanLabel = QLabel(self.statsGroup)
        self.resultMeanLabel.setObjectName("resultMeanLabel")

        self.statsLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.resultMeanLabel)

        self.resultMeanValue = QLabel(self.statsGroup)
        self.resultMeanValue.setObjectName("resultMeanValue")

        self.statsLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.resultMeanValue)

        self.origStdLabel = QLabel(self.statsGroup)
        self.origStdLabel.setObjectName("origStdLabel")

        self.statsLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.origStdLabel)

        self.origStdValue = QLabel(self.statsGroup)
        self.origStdValue.setObjectName("origStdValue")

        self.statsLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.origStdValue)

        self.resultStdLabel = QLabel(self.statsGroup)
        self.resultStdLabel.setObjectName("resultStdLabel")

        self.statsLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.resultStdLabel)

        self.resultStdValue = QLabel(self.statsGroup)
        self.resultStdValue.setObjectName("resultStdValue")

        self.statsLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.resultStdValue)


        self.infoLayout.addWidget(self.statsGroup)

        self.infoSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.infoLayout.addItem(self.infoSpacer)

        self.mainSplitter.addWidget(self.infoPanel)

        self.mainLayout.addWidget(self.mainSplitter)

        self.buttonBox = QDialogButtonBox(OperationPreviewDialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Apply|QDialogButtonBox.Cancel)

        self.mainLayout.addWidget(self.buttonBox)


        self.retranslateUi(OperationPreviewDialog)

        QMetaObject.connectSlotsByName(OperationPreviewDialog)
    # setupUi

    def retranslateUi(self, OperationPreviewDialog):
        OperationPreviewDialog.setWindowTitle(QCoreApplication.translate("OperationPreviewDialog", "Operation Preview", None))
        self.titleLabel.setText(QCoreApplication.translate("OperationPreviewDialog", "\ud83d\udd0d Preview: Operation", None))
        self.titleLabel.setStyleSheet(QCoreApplication.translate("OperationPreviewDialog", "font-size: 16px; font-weight: bold; color: #0d6efd;", None))
        self.paramsGroup.setTitle(QCoreApplication.translate("OperationPreviewDialog", "\ud83d\udcdd Par\u00e2metros", None))
        self.statsGroup.setTitle(QCoreApplication.translate("OperationPreviewDialog", "\ud83d\udcca Estat\u00edsticas", None))
        self.origMeanLabel.setText(QCoreApplication.translate("OperationPreviewDialog", "Original Mean:", None))
        self.origMeanValue.setText(QCoreApplication.translate("OperationPreviewDialog", "-", None))
        self.resultMeanLabel.setText(QCoreApplication.translate("OperationPreviewDialog", "Result Mean:", None))
        self.resultMeanValue.setText(QCoreApplication.translate("OperationPreviewDialog", "-", None))
        self.origStdLabel.setText(QCoreApplication.translate("OperationPreviewDialog", "Original Std:", None))
        self.origStdValue.setText(QCoreApplication.translate("OperationPreviewDialog", "-", None))
        self.resultStdLabel.setText(QCoreApplication.translate("OperationPreviewDialog", "Result Std:", None))
        self.resultStdValue.setText(QCoreApplication.translate("OperationPreviewDialog", "-", None))
    # retranslateUi

