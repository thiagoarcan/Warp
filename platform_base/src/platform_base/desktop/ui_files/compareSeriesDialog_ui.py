# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'compareSeriesDialog.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_CompareSeriesDialog(object):
    def setupUi(self, CompareSeriesDialog):
        if not CompareSeriesDialog.objectName():
            CompareSeriesDialog.setObjectName(u"CompareSeriesDialog")
        CompareSeriesDialog.resize(450, 400)
        CompareSeriesDialog.setMinimumWidth(400)
        CompareSeriesDialog.setModal(True)
        self.mainLayout = QVBoxLayout(CompareSeriesDialog)
        self.mainLayout.setSpacing(12)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(16, 16, 16, 16)
        self.seriesGroup = QGroupBox(CompareSeriesDialog)
        self.seriesGroup.setObjectName(u"seriesGroup")
        self.seriesLayout = QFormLayout(self.seriesGroup)
        self.seriesLayout.setObjectName(u"seriesLayout")
        self.series1Label = QLabel(self.seriesGroup)
        self.series1Label.setObjectName(u"series1Label")

        self.seriesLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.series1Label)

        self.series1Combo = QComboBox(self.seriesGroup)
        self.series1Combo.setObjectName(u"series1Combo")

        self.seriesLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.series1Combo)

        self.series2Label = QLabel(self.seriesGroup)
        self.series2Label.setObjectName(u"series2Label")

        self.seriesLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.series2Label)

        self.series2Combo = QComboBox(self.seriesGroup)
        self.series2Combo.setObjectName(u"series2Combo")

        self.seriesLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.series2Combo)


        self.mainLayout.addWidget(self.seriesGroup)

        self.metricsGroup = QGroupBox(CompareSeriesDialog)
        self.metricsGroup.setObjectName(u"metricsGroup")
        self.metricsLayout = QVBoxLayout(self.metricsGroup)
        self.metricsLayout.setObjectName(u"metricsLayout")
        self.correlationCheck = QCheckBox(self.metricsGroup)
        self.correlationCheck.setObjectName(u"correlationCheck")
        self.correlationCheck.setChecked(True)

        self.metricsLayout.addWidget(self.correlationCheck)

        self.rmseCheck = QCheckBox(self.metricsGroup)
        self.rmseCheck.setObjectName(u"rmseCheck")
        self.rmseCheck.setChecked(True)

        self.metricsLayout.addWidget(self.rmseCheck)

        self.maeCheck = QCheckBox(self.metricsGroup)
        self.maeCheck.setObjectName(u"maeCheck")

        self.metricsLayout.addWidget(self.maeCheck)

        self.dtwCheck = QCheckBox(self.metricsGroup)
        self.dtwCheck.setObjectName(u"dtwCheck")

        self.metricsLayout.addWidget(self.dtwCheck)


        self.mainLayout.addWidget(self.metricsGroup)

        self.resultsGroup = QGroupBox(CompareSeriesDialog)
        self.resultsGroup.setObjectName(u"resultsGroup")
        self.resultsLayout = QVBoxLayout(self.resultsGroup)
        self.resultsLayout.setObjectName(u"resultsLayout")
        self.resultText = QTextEdit(self.resultsGroup)
        self.resultText.setObjectName(u"resultText")
        self.resultText.setReadOnly(True)

        self.resultsLayout.addWidget(self.resultText)


        self.mainLayout.addWidget(self.resultsGroup)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.compareBtn = QPushButton(CompareSeriesDialog)
        self.compareBtn.setObjectName(u"compareBtn")

        self.buttonLayout.addWidget(self.compareBtn)

        self.buttonSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.buttonSpacer)

        self.closeBtn = QPushButton(CompareSeriesDialog)
        self.closeBtn.setObjectName(u"closeBtn")

        self.buttonLayout.addWidget(self.closeBtn)


        self.mainLayout.addLayout(self.buttonLayout)


        self.retranslateUi(CompareSeriesDialog)

        self.closeBtn.setDefault(True)


        QMetaObject.connectSlotsByName(CompareSeriesDialog)
    # setupUi

    def retranslateUi(self, CompareSeriesDialog):
        CompareSeriesDialog.setWindowTitle(QCoreApplication.translate("CompareSeriesDialog", u"Comparar S\u00e9ries", None))
        self.seriesGroup.setTitle(QCoreApplication.translate("CompareSeriesDialog", u"\ud83d\udcca S\u00e9ries para Comparar", None))
        self.series1Label.setText(QCoreApplication.translate("CompareSeriesDialog", u"S\u00e9rie 1:", None))
        self.series2Label.setText(QCoreApplication.translate("CompareSeriesDialog", u"S\u00e9rie 2:", None))
        self.metricsGroup.setTitle(QCoreApplication.translate("CompareSeriesDialog", u"\ud83d\udcd0 M\u00e9tricas", None))
        self.correlationCheck.setText(QCoreApplication.translate("CompareSeriesDialog", u"Correla\u00e7\u00e3o (Pearson)", None))
        self.rmseCheck.setText(QCoreApplication.translate("CompareSeriesDialog", u"RMSE (Root Mean Square Error)", None))
        self.maeCheck.setText(QCoreApplication.translate("CompareSeriesDialog", u"MAE (Mean Absolute Error)", None))
        self.dtwCheck.setText(QCoreApplication.translate("CompareSeriesDialog", u"DTW Distance (Dynamic Time Warping)", None))
        self.resultsGroup.setTitle(QCoreApplication.translate("CompareSeriesDialog", u"\ud83d\udccb Resultados", None))
        self.resultText.setPlaceholderText(QCoreApplication.translate("CompareSeriesDialog", u"Os resultados da compara\u00e7\u00e3o ser\u00e3o exibidos aqui...", None))
        self.compareBtn.setText(QCoreApplication.translate("CompareSeriesDialog", u"Comparar", None))
        self.closeBtn.setText(QCoreApplication.translate("CompareSeriesDialog", u"Fechar", None))
    # retranslateUi

