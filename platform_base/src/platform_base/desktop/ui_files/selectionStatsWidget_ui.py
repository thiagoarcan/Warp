# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'selectionStatsWidget.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QGroupBox, QLabel,
    QProgressBar, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_SelectionStatsWidget(object):
    def setupUi(self, SelectionStatsWidget):
        if not SelectionStatsWidget.objectName():
            SelectionStatsWidget.setObjectName(u"SelectionStatsWidget")
        SelectionStatsWidget.resize(250, 200)
        SelectionStatsWidget.setMinimumSize(QSize(200, 150))
        self.mainLayout = QVBoxLayout(SelectionStatsWidget)
        self.mainLayout.setSpacing(6)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.countGroup = QGroupBox(SelectionStatsWidget)
        self.countGroup.setObjectName(u"countGroup")
        self.countLayout = QFormLayout(self.countGroup)
        self.countLayout.setObjectName(u"countLayout")
        self.totalLabel = QLabel(self.countGroup)
        self.totalLabel.setObjectName(u"totalLabel")

        self.countLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.totalLabel)

        self.totalPointsLabel = QLabel(self.countGroup)
        self.totalPointsLabel.setObjectName(u"totalPointsLabel")
        self.totalPointsLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.countLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.totalPointsLabel)

        self.selectedLabel = QLabel(self.countGroup)
        self.selectedLabel.setObjectName(u"selectedLabel")

        self.countLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.selectedLabel)

        self.selectedPointsLabel = QLabel(self.countGroup)
        self.selectedPointsLabel.setObjectName(u"selectedPointsLabel")
        self.selectedPointsLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.countLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.selectedPointsLabel)

        self.ratioLabel = QLabel(self.countGroup)
        self.ratioLabel.setObjectName(u"ratioLabel")

        self.countLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.ratioLabel)

        self.selectionRatioLabel = QLabel(self.countGroup)
        self.selectionRatioLabel.setObjectName(u"selectionRatioLabel")
        self.selectionRatioLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.countLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.selectionRatioLabel)

        self.selectionProgress = QProgressBar(self.countGroup)
        self.selectionProgress.setObjectName(u"selectionProgress")
        self.selectionProgress.setValue(0)
        self.selectionProgress.setTextVisible(False)
        self.selectionProgress.setMaximumHeight(8)

        self.countLayout.setWidget(3, QFormLayout.ItemRole.SpanningRole, self.selectionProgress)


        self.mainLayout.addWidget(self.countGroup)

        self.statsGroup = QGroupBox(SelectionStatsWidget)
        self.statsGroup.setObjectName(u"statsGroup")
        self.statsLayout = QFormLayout(self.statsGroup)
        self.statsLayout.setObjectName(u"statsLayout")
        self.minLabel = QLabel(self.statsGroup)
        self.minLabel.setObjectName(u"minLabel")

        self.statsLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.minLabel)

        self.minValueLabel = QLabel(self.statsGroup)
        self.minValueLabel.setObjectName(u"minValueLabel")
        self.minValueLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.statsLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.minValueLabel)

        self.maxLabel = QLabel(self.statsGroup)
        self.maxLabel.setObjectName(u"maxLabel")

        self.statsLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.maxLabel)

        self.maxValueLabel = QLabel(self.statsGroup)
        self.maxValueLabel.setObjectName(u"maxValueLabel")
        self.maxValueLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.statsLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.maxValueLabel)

        self.meanLabel = QLabel(self.statsGroup)
        self.meanLabel.setObjectName(u"meanLabel")

        self.statsLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.meanLabel)

        self.meanValueLabel = QLabel(self.statsGroup)
        self.meanValueLabel.setObjectName(u"meanValueLabel")
        self.meanValueLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.statsLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.meanValueLabel)

        self.stdLabel = QLabel(self.statsGroup)
        self.stdLabel.setObjectName(u"stdLabel")

        self.statsLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.stdLabel)

        self.stdValueLabel = QLabel(self.statsGroup)
        self.stdValueLabel.setObjectName(u"stdValueLabel")
        self.stdValueLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.statsLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.stdValueLabel)


        self.mainLayout.addWidget(self.statsGroup)

        self.timeGroup = QGroupBox(SelectionStatsWidget)
        self.timeGroup.setObjectName(u"timeGroup")
        self.timeLayout = QFormLayout(self.timeGroup)
        self.timeLayout.setObjectName(u"timeLayout")
        self.rangesLabel = QLabel(self.timeGroup)
        self.rangesLabel.setObjectName(u"rangesLabel")

        self.timeLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.rangesLabel)

        self.timeRangesLabel = QLabel(self.timeGroup)
        self.timeRangesLabel.setObjectName(u"timeRangesLabel")
        self.timeRangesLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.timeLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.timeRangesLabel)

        self.durationLabel = QLabel(self.timeGroup)
        self.durationLabel.setObjectName(u"durationLabel")

        self.timeLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.durationLabel)

        self.totalDurationLabel = QLabel(self.timeGroup)
        self.totalDurationLabel.setObjectName(u"totalDurationLabel")
        self.totalDurationLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.timeLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.totalDurationLabel)


        self.mainLayout.addWidget(self.timeGroup)

        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mainLayout.addItem(self.verticalSpacer)


        self.retranslateUi(SelectionStatsWidget)

        QMetaObject.connectSlotsByName(SelectionStatsWidget)
    # setupUi

    def retranslateUi(self, SelectionStatsWidget):
        self.countGroup.setTitle(QCoreApplication.translate("SelectionStatsWidget", u"\ud83d\udcca Selection Count", None))
        self.totalLabel.setText(QCoreApplication.translate("SelectionStatsWidget", u"Total Points:", None))
        self.totalPointsLabel.setText(QCoreApplication.translate("SelectionStatsWidget", u"0", None))
        self.totalPointsLabel.setStyleSheet(QCoreApplication.translate("SelectionStatsWidget", u"font-weight: bold;", None))
        self.selectedLabel.setText(QCoreApplication.translate("SelectionStatsWidget", u"Selected:", None))
        self.selectedPointsLabel.setText(QCoreApplication.translate("SelectionStatsWidget", u"0", None))
        self.selectedPointsLabel.setStyleSheet(QCoreApplication.translate("SelectionStatsWidget", u"font-weight: bold; color: #0078d4;", None))
        self.ratioLabel.setText(QCoreApplication.translate("SelectionStatsWidget", u"Ratio:", None))
        self.selectionRatioLabel.setText(QCoreApplication.translate("SelectionStatsWidget", u"0.0%", None))
        self.statsGroup.setTitle(QCoreApplication.translate("SelectionStatsWidget", u"\ud83d\udcc8 Value Statistics", None))
        self.minLabel.setText(QCoreApplication.translate("SelectionStatsWidget", u"Min:", None))
        self.minValueLabel.setText(QCoreApplication.translate("SelectionStatsWidget", u"-", None))
        self.maxLabel.setText(QCoreApplication.translate("SelectionStatsWidget", u"Max:", None))
        self.maxValueLabel.setText(QCoreApplication.translate("SelectionStatsWidget", u"-", None))
        self.meanLabel.setText(QCoreApplication.translate("SelectionStatsWidget", u"Mean:", None))
        self.meanValueLabel.setText(QCoreApplication.translate("SelectionStatsWidget", u"-", None))
        self.stdLabel.setText(QCoreApplication.translate("SelectionStatsWidget", u"Std Dev:", None))
        self.stdValueLabel.setText(QCoreApplication.translate("SelectionStatsWidget", u"-", None))
        self.timeGroup.setTitle(QCoreApplication.translate("SelectionStatsWidget", u"\u23f1\ufe0f Time Range", None))
        self.rangesLabel.setText(QCoreApplication.translate("SelectionStatsWidget", u"Ranges:", None))
        self.timeRangesLabel.setText(QCoreApplication.translate("SelectionStatsWidget", u"-", None))
        self.durationLabel.setText(QCoreApplication.translate("SelectionStatsWidget", u"Duration:", None))
        self.totalDurationLabel.setText(QCoreApplication.translate("SelectionStatsWidget", u"-", None))
        pass
    # retranslateUi

