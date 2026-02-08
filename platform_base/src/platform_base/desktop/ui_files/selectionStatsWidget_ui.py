
################################################################################
## Form generated from reading UI file 'selectionStatsWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize, Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QProgressBar,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
)


class Ui_SelectionStatsWidget:
    def setupUi(self, SelectionStatsWidget):
        if not SelectionStatsWidget.objectName():
            SelectionStatsWidget.setObjectName("SelectionStatsWidget")
        SelectionStatsWidget.resize(250, 200)
        SelectionStatsWidget.setMinimumSize(QSize(200, 150))
        self.mainLayout = QVBoxLayout(SelectionStatsWidget)
        self.mainLayout.setSpacing(6)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.countGroup = QGroupBox(SelectionStatsWidget)
        self.countGroup.setObjectName("countGroup")
        self.countLayout = QFormLayout(self.countGroup)
        self.countLayout.setObjectName("countLayout")
        self.totalLabel = QLabel(self.countGroup)
        self.totalLabel.setObjectName("totalLabel")

        self.countLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.totalLabel)

        self.totalPointsLabel = QLabel(self.countGroup)
        self.totalPointsLabel.setObjectName("totalPointsLabel")
        self.totalPointsLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.countLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.totalPointsLabel)

        self.selectedLabel = QLabel(self.countGroup)
        self.selectedLabel.setObjectName("selectedLabel")

        self.countLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.selectedLabel)

        self.selectedPointsLabel = QLabel(self.countGroup)
        self.selectedPointsLabel.setObjectName("selectedPointsLabel")
        self.selectedPointsLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.countLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.selectedPointsLabel)

        self.ratioLabel = QLabel(self.countGroup)
        self.ratioLabel.setObjectName("ratioLabel")

        self.countLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.ratioLabel)

        self.selectionRatioLabel = QLabel(self.countGroup)
        self.selectionRatioLabel.setObjectName("selectionRatioLabel")
        self.selectionRatioLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.countLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.selectionRatioLabel)

        self.selectionProgress = QProgressBar(self.countGroup)
        self.selectionProgress.setObjectName("selectionProgress")
        self.selectionProgress.setValue(0)
        self.selectionProgress.setTextVisible(False)
        self.selectionProgress.setMaximumHeight(8)

        self.countLayout.setWidget(3, QFormLayout.ItemRole.SpanningRole, self.selectionProgress)


        self.mainLayout.addWidget(self.countGroup)

        self.statsGroup = QGroupBox(SelectionStatsWidget)
        self.statsGroup.setObjectName("statsGroup")
        self.statsLayout = QFormLayout(self.statsGroup)
        self.statsLayout.setObjectName("statsLayout")
        self.minLabel = QLabel(self.statsGroup)
        self.minLabel.setObjectName("minLabel")

        self.statsLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.minLabel)

        self.minValueLabel = QLabel(self.statsGroup)
        self.minValueLabel.setObjectName("minValueLabel")
        self.minValueLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.statsLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.minValueLabel)

        self.maxLabel = QLabel(self.statsGroup)
        self.maxLabel.setObjectName("maxLabel")

        self.statsLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.maxLabel)

        self.maxValueLabel = QLabel(self.statsGroup)
        self.maxValueLabel.setObjectName("maxValueLabel")
        self.maxValueLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.statsLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.maxValueLabel)

        self.meanLabel = QLabel(self.statsGroup)
        self.meanLabel.setObjectName("meanLabel")

        self.statsLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.meanLabel)

        self.meanValueLabel = QLabel(self.statsGroup)
        self.meanValueLabel.setObjectName("meanValueLabel")
        self.meanValueLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.statsLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.meanValueLabel)

        self.stdLabel = QLabel(self.statsGroup)
        self.stdLabel.setObjectName("stdLabel")

        self.statsLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.stdLabel)

        self.stdValueLabel = QLabel(self.statsGroup)
        self.stdValueLabel.setObjectName("stdValueLabel")
        self.stdValueLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.statsLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.stdValueLabel)


        self.mainLayout.addWidget(self.statsGroup)

        self.timeGroup = QGroupBox(SelectionStatsWidget)
        self.timeGroup.setObjectName("timeGroup")
        self.timeLayout = QFormLayout(self.timeGroup)
        self.timeLayout.setObjectName("timeLayout")
        self.rangesLabel = QLabel(self.timeGroup)
        self.rangesLabel.setObjectName("rangesLabel")

        self.timeLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.rangesLabel)

        self.timeRangesLabel = QLabel(self.timeGroup)
        self.timeRangesLabel.setObjectName("timeRangesLabel")
        self.timeRangesLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.timeLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.timeRangesLabel)

        self.durationLabel = QLabel(self.timeGroup)
        self.durationLabel.setObjectName("durationLabel")

        self.timeLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.durationLabel)

        self.totalDurationLabel = QLabel(self.timeGroup)
        self.totalDurationLabel.setObjectName("totalDurationLabel")
        self.totalDurationLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.timeLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.totalDurationLabel)


        self.mainLayout.addWidget(self.timeGroup)

        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mainLayout.addItem(self.verticalSpacer)


        self.retranslateUi(SelectionStatsWidget)

        QMetaObject.connectSlotsByName(SelectionStatsWidget)
    # setupUi

    def retranslateUi(self, SelectionStatsWidget):
        self.countGroup.setTitle(QCoreApplication.translate("SelectionStatsWidget", "\ud83d\udcca Selection Count", None))
        self.totalLabel.setText(QCoreApplication.translate("SelectionStatsWidget", "Total Points:", None))
        self.totalPointsLabel.setText(QCoreApplication.translate("SelectionStatsWidget", "0", None))
        self.totalPointsLabel.setStyleSheet(QCoreApplication.translate("SelectionStatsWidget", "font-weight: bold;", None))
        self.selectedLabel.setText(QCoreApplication.translate("SelectionStatsWidget", "Selected:", None))
        self.selectedPointsLabel.setText(QCoreApplication.translate("SelectionStatsWidget", "0", None))
        self.selectedPointsLabel.setStyleSheet(QCoreApplication.translate("SelectionStatsWidget", "font-weight: bold; color: #0078d4;", None))
        self.ratioLabel.setText(QCoreApplication.translate("SelectionStatsWidget", "Ratio:", None))
        self.selectionRatioLabel.setText(QCoreApplication.translate("SelectionStatsWidget", "0.0%", None))
        self.statsGroup.setTitle(QCoreApplication.translate("SelectionStatsWidget", "\ud83d\udcc8 Value Statistics", None))
        self.minLabel.setText(QCoreApplication.translate("SelectionStatsWidget", "Min:", None))
        self.minValueLabel.setText(QCoreApplication.translate("SelectionStatsWidget", "-", None))
        self.maxLabel.setText(QCoreApplication.translate("SelectionStatsWidget", "Max:", None))
        self.maxValueLabel.setText(QCoreApplication.translate("SelectionStatsWidget", "-", None))
        self.meanLabel.setText(QCoreApplication.translate("SelectionStatsWidget", "Mean:", None))
        self.meanValueLabel.setText(QCoreApplication.translate("SelectionStatsWidget", "-", None))
        self.stdLabel.setText(QCoreApplication.translate("SelectionStatsWidget", "Std Dev:", None))
        self.stdValueLabel.setText(QCoreApplication.translate("SelectionStatsWidget", "-", None))
        self.timeGroup.setTitle(QCoreApplication.translate("SelectionStatsWidget", "\u23f1\ufe0f Time Range", None))
        self.rangesLabel.setText(QCoreApplication.translate("SelectionStatsWidget", "Ranges:", None))
        self.timeRangesLabel.setText(QCoreApplication.translate("SelectionStatsWidget", "-", None))
        self.durationLabel.setText(QCoreApplication.translate("SelectionStatsWidget", "Duration:", None))
        self.totalDurationLabel.setText(QCoreApplication.translate("SelectionStatsWidget", "-", None))
    # retranslateUi

