# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'operationPreviewDialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QFormLayout, QFrame, QGroupBox, QLabel,
    QSizePolicy, QSpacerItem, QSplitter, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_OperationPreviewDialog(object):
    def setupUi(self, OperationPreviewDialog):
        if not OperationPreviewDialog.objectName():
            OperationPreviewDialog.setObjectName(u"OperationPreviewDialog")
        OperationPreviewDialog.resize(800, 600)
        OperationPreviewDialog.setMinimumSize(QSize(600, 400))
        OperationPreviewDialog.setModal(True)
        self.mainLayout = QVBoxLayout(OperationPreviewDialog)
        self.mainLayout.setSpacing(8)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(12, 12, 12, 12)
        self.titleLabel = QLabel(OperationPreviewDialog)
        self.titleLabel.setObjectName(u"titleLabel")

        self.mainLayout.addWidget(self.titleLabel)

        self.mainSplitter = QSplitter(OperationPreviewDialog)
        self.mainSplitter.setObjectName(u"mainSplitter")
        self.mainSplitter.setOrientation(Qt.Horizontal)
        self.canvasFrame = QFrame(self.mainSplitter)
        self.canvasFrame.setObjectName(u"canvasFrame")
        self.canvasFrame.setFrameShape(QFrame.StyledPanel)
        self.canvasFrame.setMinimumWidth(400)
        self.canvasLayout = QVBoxLayout(self.canvasFrame)
        self.canvasLayout.setContentsMargins(0, 0, 0, 0)
        self.canvasLayout.setObjectName(u"canvasLayout")
        self.mainSplitter.addWidget(self.canvasFrame)
        self.infoPanel = QWidget(self.mainSplitter)
        self.infoPanel.setObjectName(u"infoPanel")
        self.infoPanel.setMinimumWidth(200)
        self.infoLayout = QVBoxLayout(self.infoPanel)
        self.infoLayout.setSpacing(8)
        self.infoLayout.setObjectName(u"infoLayout")
        self.infoLayout.setContentsMargins(0, 0, 0, 0)
        self.paramsGroup = QGroupBox(self.infoPanel)
        self.paramsGroup.setObjectName(u"paramsGroup")
        self.paramsLayout = QVBoxLayout(self.paramsGroup)
        self.paramsLayout.setObjectName(u"paramsLayout")
        self.paramsText = QTextEdit(self.paramsGroup)
        self.paramsText.setObjectName(u"paramsText")
        self.paramsText.setReadOnly(True)
        self.paramsText.setMaximumHeight(100)

        self.paramsLayout.addWidget(self.paramsText)


        self.infoLayout.addWidget(self.paramsGroup)

        self.statsGroup = QGroupBox(self.infoPanel)
        self.statsGroup.setObjectName(u"statsGroup")
        self.statsLayout = QFormLayout(self.statsGroup)
        self.statsLayout.setObjectName(u"statsLayout")
        self.origMeanLabel = QLabel(self.statsGroup)
        self.origMeanLabel.setObjectName(u"origMeanLabel")

        self.statsLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.origMeanLabel)

        self.origMeanValue = QLabel(self.statsGroup)
        self.origMeanValue.setObjectName(u"origMeanValue")

        self.statsLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.origMeanValue)

        self.resultMeanLabel = QLabel(self.statsGroup)
        self.resultMeanLabel.setObjectName(u"resultMeanLabel")

        self.statsLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.resultMeanLabel)

        self.resultMeanValue = QLabel(self.statsGroup)
        self.resultMeanValue.setObjectName(u"resultMeanValue")

        self.statsLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.resultMeanValue)

        self.origStdLabel = QLabel(self.statsGroup)
        self.origStdLabel.setObjectName(u"origStdLabel")

        self.statsLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.origStdLabel)

        self.origStdValue = QLabel(self.statsGroup)
        self.origStdValue.setObjectName(u"origStdValue")

        self.statsLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.origStdValue)

        self.resultStdLabel = QLabel(self.statsGroup)
        self.resultStdLabel.setObjectName(u"resultStdLabel")

        self.statsLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.resultStdLabel)

        self.resultStdValue = QLabel(self.statsGroup)
        self.resultStdValue.setObjectName(u"resultStdValue")

        self.statsLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.resultStdValue)


        self.infoLayout.addWidget(self.statsGroup)

        self.infoSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.infoLayout.addItem(self.infoSpacer)

        self.mainSplitter.addWidget(self.infoPanel)

        self.mainLayout.addWidget(self.mainSplitter)

        self.buttonBox = QDialogButtonBox(OperationPreviewDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Apply|QDialogButtonBox.Cancel)

        self.mainLayout.addWidget(self.buttonBox)


        self.retranslateUi(OperationPreviewDialog)

        QMetaObject.connectSlotsByName(OperationPreviewDialog)
    # setupUi

    def retranslateUi(self, OperationPreviewDialog):
        OperationPreviewDialog.setWindowTitle(QCoreApplication.translate("OperationPreviewDialog", u"Operation Preview", None))
        self.titleLabel.setText(QCoreApplication.translate("OperationPreviewDialog", u"\ud83d\udd0d Preview: Operation", None))
        self.titleLabel.setStyleSheet(QCoreApplication.translate("OperationPreviewDialog", u"font-size: 16px; font-weight: bold; color: #0d6efd;", None))
        self.paramsGroup.setTitle(QCoreApplication.translate("OperationPreviewDialog", u"\ud83d\udcdd Par\u00e2metros", None))
        self.statsGroup.setTitle(QCoreApplication.translate("OperationPreviewDialog", u"\ud83d\udcca Estat\u00edsticas", None))
        self.origMeanLabel.setText(QCoreApplication.translate("OperationPreviewDialog", u"Original Mean:", None))
        self.origMeanValue.setText(QCoreApplication.translate("OperationPreviewDialog", u"-", None))
        self.resultMeanLabel.setText(QCoreApplication.translate("OperationPreviewDialog", u"Result Mean:", None))
        self.resultMeanValue.setText(QCoreApplication.translate("OperationPreviewDialog", u"-", None))
        self.origStdLabel.setText(QCoreApplication.translate("OperationPreviewDialog", u"Original Std:", None))
        self.origStdValue.setText(QCoreApplication.translate("OperationPreviewDialog", u"-", None))
        self.resultStdLabel.setText(QCoreApplication.translate("OperationPreviewDialog", u"Result Std:", None))
        self.resultStdValue.setText(QCoreApplication.translate("OperationPreviewDialog", u"-", None))
    # retranslateUi

