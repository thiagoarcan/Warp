
################################################################################
## Form generated from reading UI file 'streamingControls.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, Qt
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSpacerItem,
    QVBoxLayout,
)


class Ui_StreamingControls:
    def setupUi(self, StreamingControls):
        if not StreamingControls.objectName():
            StreamingControls.setObjectName("StreamingControls")
        StreamingControls.resize(500, 120)
        self.mainLayout = QVBoxLayout(StreamingControls)
        self.mainLayout.setSpacing(8)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.timelineLayout = QHBoxLayout()
        self.timelineLayout.setObjectName("timelineLayout")
        self.positionLabel = QLabel(StreamingControls)
        self.positionLabel.setObjectName("positionLabel")
        self.positionLabel.setMinimumWidth(50)

        self.timelineLayout.addWidget(self.positionLabel)

        self.timeline = QSlider(StreamingControls)
        self.timeline.setObjectName("timeline")
        self.timeline.setOrientation(Qt.Horizontal)
        self.timeline.setMinimum(0)
        self.timeline.setMaximum(1000)

        self.timelineLayout.addWidget(self.timeline)

        self.durationLabel = QLabel(StreamingControls)
        self.durationLabel.setObjectName("durationLabel")
        self.durationLabel.setMinimumWidth(50)

        self.timelineLayout.addWidget(self.durationLabel)


        self.mainLayout.addLayout(self.timelineLayout)

        self.controlsLayout = QHBoxLayout()
        self.controlsLayout.setObjectName("controlsLayout")
        self.playBtn = QPushButton(StreamingControls)
        self.playBtn.setObjectName("playBtn")
        self.playBtn.setMinimumWidth(40)

        self.controlsLayout.addWidget(self.playBtn)

        self.pauseBtn = QPushButton(StreamingControls)
        self.pauseBtn.setObjectName("pauseBtn")
        self.pauseBtn.setMinimumWidth(40)

        self.controlsLayout.addWidget(self.pauseBtn)

        self.stopBtn = QPushButton(StreamingControls)
        self.stopBtn.setObjectName("stopBtn")
        self.stopBtn.setMinimumWidth(40)

        self.controlsLayout.addWidget(self.stopBtn)

        self.controlsSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.controlsLayout.addItem(self.controlsSpacer)

        self.speedLabel = QLabel(StreamingControls)
        self.speedLabel.setObjectName("speedLabel")

        self.controlsLayout.addWidget(self.speedLabel)

        self.speedSpinbox = QDoubleSpinBox(StreamingControls)
        self.speedSpinbox.setObjectName("speedSpinbox")
        self.speedSpinbox.setMinimum(0.100000000000000)
        self.speedSpinbox.setMaximum(10.000000000000000)
        self.speedSpinbox.setSingleStep(0.100000000000000)
        self.speedSpinbox.setValue(1.000000000000000)

        self.controlsLayout.addWidget(self.speedSpinbox)

        self.windowLabel = QLabel(StreamingControls)
        self.windowLabel.setObjectName("windowLabel")

        self.controlsLayout.addWidget(self.windowLabel)

        self.windowSpinbox = QDoubleSpinBox(StreamingControls)
        self.windowSpinbox.setObjectName("windowSpinbox")
        self.windowSpinbox.setMinimum(1.000000000000000)
        self.windowSpinbox.setMaximum(3600.000000000000000)
        self.windowSpinbox.setValue(10.000000000000000)

        self.controlsLayout.addWidget(self.windowSpinbox)


        self.mainLayout.addLayout(self.controlsLayout)


        self.retranslateUi(StreamingControls)

        QMetaObject.connectSlotsByName(StreamingControls)
    # setupUi

    def retranslateUi(self, StreamingControls):
        self.positionLabel.setText(QCoreApplication.translate("StreamingControls", "00:00", None))
        self.durationLabel.setText(QCoreApplication.translate("StreamingControls", "00:00", None))
        self.playBtn.setText(QCoreApplication.translate("StreamingControls", "\u25b6", None))
#if QT_CONFIG(tooltip)
        self.playBtn.setToolTip(QCoreApplication.translate("StreamingControls", "Play", None))
#endif // QT_CONFIG(tooltip)
        self.pauseBtn.setText(QCoreApplication.translate("StreamingControls", "\u23f8", None))
#if QT_CONFIG(tooltip)
        self.pauseBtn.setToolTip(QCoreApplication.translate("StreamingControls", "Pause", None))
#endif // QT_CONFIG(tooltip)
        self.stopBtn.setText(QCoreApplication.translate("StreamingControls", "\u23f9", None))
#if QT_CONFIG(tooltip)
        self.stopBtn.setToolTip(QCoreApplication.translate("StreamingControls", "Stop", None))
#endif // QT_CONFIG(tooltip)
        self.speedLabel.setText(QCoreApplication.translate("StreamingControls", "Speed:", None))
        self.speedSpinbox.setSuffix(QCoreApplication.translate("StreamingControls", "x", None))
        self.windowLabel.setText(QCoreApplication.translate("StreamingControls", "Window:", None))
        self.windowSpinbox.setSuffix(QCoreApplication.translate("StreamingControls", "s", None))
    # retranslateUi

