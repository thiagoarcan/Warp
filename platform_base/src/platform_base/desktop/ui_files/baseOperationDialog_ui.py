# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'baseOperationDialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QSizePolicy,
    QSpacerItem, QSplitter, QVBoxLayout, QWidget)

class Ui_BaseOperationDialog(object):
    def setupUi(self, BaseOperationDialog):
        if not BaseOperationDialog.objectName():
            BaseOperationDialog.setObjectName(u"BaseOperationDialog")
        BaseOperationDialog.resize(900, 700)
        BaseOperationDialog.setModal(True)
        self.mainLayout = QVBoxLayout(BaseOperationDialog)
        self.mainLayout.setSpacing(8)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(12, 12, 12, 12)
        self.splitter = QSplitter(BaseOperationDialog)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.parametersScrollArea = QScrollArea(self.splitter)
        self.parametersScrollArea.setObjectName(u"parametersScrollArea")
        self.parametersScrollArea.setWidgetResizable(True)
        self.parametersScrollArea.setMinimumWidth(300)
        self.parametersContent = QWidget()
        self.parametersContent.setObjectName(u"parametersContent")
        self.parametersLayout = QVBoxLayout(self.parametersContent)
        self.parametersLayout.setSpacing(8)
        self.parametersLayout.setObjectName(u"parametersLayout")
        self.parametersHeader = QLabel(self.parametersContent)
        self.parametersHeader.setObjectName(u"parametersHeader")

        self.parametersLayout.addWidget(self.parametersHeader)

        self.parametersSpacerBottom = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.parametersLayout.addItem(self.parametersSpacerBottom)

        self.parametersScrollArea.setWidget(self.parametersContent)
        self.splitter.addWidget(self.parametersScrollArea)
        self.previewContainer = QWidget(self.splitter)
        self.previewContainer.setObjectName(u"previewContainer")
        self.previewContainer.setMinimumWidth(400)
        self.previewLayout = QVBoxLayout(self.previewContainer)
        self.previewLayout.setSpacing(8)
        self.previewLayout.setObjectName(u"previewLayout")
        self.previewLayout.setContentsMargins(0, 0, 0, 0)
        self.previewHeader = QLabel(self.previewContainer)
        self.previewHeader.setObjectName(u"previewHeader")

        self.previewLayout.addWidget(self.previewHeader)

        self.previewStatus = QLabel(self.previewContainer)
        self.previewStatus.setObjectName(u"previewStatus")

        self.previewLayout.addWidget(self.previewStatus)

        self.splitter.addWidget(self.previewContainer)

        self.mainLayout.addWidget(self.splitter)

        self.buttonFrame = QFrame(BaseOperationDialog)
        self.buttonFrame.setObjectName(u"buttonFrame")
        self.buttonFrame.setFrameShape(QFrame.NoFrame)
        self.buttonLayout = QHBoxLayout(self.buttonFrame)
        self.buttonLayout.setSpacing(8)
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.resetBtn = QPushButton(self.buttonFrame)
        self.resetBtn.setObjectName(u"resetBtn")

        self.buttonLayout.addWidget(self.resetBtn)

        self.previewBtn = QPushButton(self.buttonFrame)
        self.previewBtn.setObjectName(u"previewBtn")

        self.buttonLayout.addWidget(self.previewBtn)

        self.buttonSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.buttonSpacer)

        self.cancelBtn = QPushButton(self.buttonFrame)
        self.cancelBtn.setObjectName(u"cancelBtn")

        self.buttonLayout.addWidget(self.cancelBtn)

        self.applyBtn = QPushButton(self.buttonFrame)
        self.applyBtn.setObjectName(u"applyBtn")

        self.buttonLayout.addWidget(self.applyBtn)


        self.mainLayout.addWidget(self.buttonFrame)


        self.retranslateUi(BaseOperationDialog)

        self.applyBtn.setDefault(True)


        QMetaObject.connectSlotsByName(BaseOperationDialog)
    # setupUi

    def retranslateUi(self, BaseOperationDialog):
        BaseOperationDialog.setWindowTitle(QCoreApplication.translate("BaseOperationDialog", u"Operation", None))
        self.parametersHeader.setText(QCoreApplication.translate("BaseOperationDialog", u"Parameters", None))
        self.parametersHeader.setStyleSheet(QCoreApplication.translate("BaseOperationDialog", u"font-size: 14px; font-weight: bold;", None))
        self.previewHeader.setText(QCoreApplication.translate("BaseOperationDialog", u"Preview", None))
        self.previewHeader.setStyleSheet(QCoreApplication.translate("BaseOperationDialog", u"font-size: 14px; font-weight: bold;", None))
        self.previewStatus.setText(QCoreApplication.translate("BaseOperationDialog", u"Ready", None))
        self.previewStatus.setStyleSheet(QCoreApplication.translate("BaseOperationDialog", u"color: gray; font-size: 10px;", None))
        self.resetBtn.setText(QCoreApplication.translate("BaseOperationDialog", u"Reset", None))
#if QT_CONFIG(tooltip)
        self.resetBtn.setToolTip(QCoreApplication.translate("BaseOperationDialog", u"Reset all parameters to default values", None))
#endif // QT_CONFIG(tooltip)
        self.previewBtn.setText(QCoreApplication.translate("BaseOperationDialog", u"Preview", None))
#if QT_CONFIG(tooltip)
        self.previewBtn.setToolTip(QCoreApplication.translate("BaseOperationDialog", u"Update preview with current parameters", None))
#endif // QT_CONFIG(tooltip)
        self.cancelBtn.setText(QCoreApplication.translate("BaseOperationDialog", u"Cancel", None))
        self.applyBtn.setText(QCoreApplication.translate("BaseOperationDialog", u"Apply", None))
    # retranslateUi

