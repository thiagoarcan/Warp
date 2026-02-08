
################################################################################
## Form generated from reading UI file 'baseOperationDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QVBoxLayout,
    QWidget,
)


class Ui_BaseOperationDialog:
    def setupUi(self, BaseOperationDialog):
        if not BaseOperationDialog.objectName():
            BaseOperationDialog.setObjectName("BaseOperationDialog")
        BaseOperationDialog.resize(900, 700)
        BaseOperationDialog.setModal(True)
        self.mainLayout = QVBoxLayout(BaseOperationDialog)
        self.mainLayout.setSpacing(8)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(12, 12, 12, 12)
        self.splitter = QSplitter(BaseOperationDialog)
        self.splitter.setObjectName("splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.parametersScrollArea = QScrollArea(self.splitter)
        self.parametersScrollArea.setObjectName("parametersScrollArea")
        self.parametersScrollArea.setWidgetResizable(True)
        self.parametersScrollArea.setMinimumWidth(300)
        self.parametersContent = QWidget()
        self.parametersContent.setObjectName("parametersContent")
        self.parametersLayout = QVBoxLayout(self.parametersContent)
        self.parametersLayout.setSpacing(8)
        self.parametersLayout.setObjectName("parametersLayout")
        self.parametersHeader = QLabel(self.parametersContent)
        self.parametersHeader.setObjectName("parametersHeader")

        self.parametersLayout.addWidget(self.parametersHeader)

        self.parametersSpacerBottom = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.parametersLayout.addItem(self.parametersSpacerBottom)

        self.parametersScrollArea.setWidget(self.parametersContent)
        self.splitter.addWidget(self.parametersScrollArea)
        self.previewContainer = QWidget(self.splitter)
        self.previewContainer.setObjectName("previewContainer")
        self.previewContainer.setMinimumWidth(400)
        self.previewLayout = QVBoxLayout(self.previewContainer)
        self.previewLayout.setSpacing(8)
        self.previewLayout.setObjectName("previewLayout")
        self.previewLayout.setContentsMargins(0, 0, 0, 0)
        self.previewHeader = QLabel(self.previewContainer)
        self.previewHeader.setObjectName("previewHeader")

        self.previewLayout.addWidget(self.previewHeader)

        self.previewStatus = QLabel(self.previewContainer)
        self.previewStatus.setObjectName("previewStatus")

        self.previewLayout.addWidget(self.previewStatus)

        self.splitter.addWidget(self.previewContainer)

        self.mainLayout.addWidget(self.splitter)

        self.buttonFrame = QFrame(BaseOperationDialog)
        self.buttonFrame.setObjectName("buttonFrame")
        self.buttonFrame.setFrameShape(QFrame.NoFrame)
        self.buttonLayout = QHBoxLayout(self.buttonFrame)
        self.buttonLayout.setSpacing(8)
        self.buttonLayout.setObjectName("buttonLayout")
        self.resetBtn = QPushButton(self.buttonFrame)
        self.resetBtn.setObjectName("resetBtn")

        self.buttonLayout.addWidget(self.resetBtn)

        self.previewBtn = QPushButton(self.buttonFrame)
        self.previewBtn.setObjectName("previewBtn")

        self.buttonLayout.addWidget(self.previewBtn)

        self.buttonSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.buttonSpacer)

        self.cancelBtn = QPushButton(self.buttonFrame)
        self.cancelBtn.setObjectName("cancelBtn")

        self.buttonLayout.addWidget(self.cancelBtn)

        self.applyBtn = QPushButton(self.buttonFrame)
        self.applyBtn.setObjectName("applyBtn")

        self.buttonLayout.addWidget(self.applyBtn)


        self.mainLayout.addWidget(self.buttonFrame)


        self.retranslateUi(BaseOperationDialog)

        self.applyBtn.setDefault(True)


        QMetaObject.connectSlotsByName(BaseOperationDialog)
    # setupUi

    def retranslateUi(self, BaseOperationDialog):
        BaseOperationDialog.setWindowTitle(QCoreApplication.translate("BaseOperationDialog", "Operation", None))
        self.parametersHeader.setText(QCoreApplication.translate("BaseOperationDialog", "Parameters", None))
        self.parametersHeader.setStyleSheet(QCoreApplication.translate("BaseOperationDialog", "font-size: 14px; font-weight: bold;", None))
        self.previewHeader.setText(QCoreApplication.translate("BaseOperationDialog", "Preview", None))
        self.previewHeader.setStyleSheet(QCoreApplication.translate("BaseOperationDialog", "font-size: 14px; font-weight: bold;", None))
        self.previewStatus.setText(QCoreApplication.translate("BaseOperationDialog", "Ready", None))
        self.previewStatus.setStyleSheet(QCoreApplication.translate("BaseOperationDialog", "color: gray; font-size: 10px;", None))
        self.resetBtn.setText(QCoreApplication.translate("BaseOperationDialog", "Reset", None))
#if QT_CONFIG(tooltip)
        self.resetBtn.setToolTip(QCoreApplication.translate("BaseOperationDialog", "Reset all parameters to default values", None))
#endif // QT_CONFIG(tooltip)
        self.previewBtn.setText(QCoreApplication.translate("BaseOperationDialog", "Preview", None))
#if QT_CONFIG(tooltip)
        self.previewBtn.setToolTip(QCoreApplication.translate("BaseOperationDialog", "Update preview with current parameters", None))
#endif // QT_CONFIG(tooltip)
        self.cancelBtn.setText(QCoreApplication.translate("BaseOperationDialog", "Cancel", None))
        self.applyBtn.setText(QCoreApplication.translate("BaseOperationDialog", "Apply", None))
    # retranslateUi

