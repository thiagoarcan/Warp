
################################################################################
## Form generated from reading UI file 'streamingControlWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSpacerItem,
    QSpinBox,
    QVBoxLayout,
)


class Ui_StreamingControlWidget:
    def setupUi(self, StreamingControlWidget):
        if not StreamingControlWidget.objectName():
            StreamingControlWidget.setObjectName("StreamingControlWidget")
        StreamingControlWidget.resize(600, 280)
        self.mainLayout = QVBoxLayout(StreamingControlWidget)
        self.mainLayout.setSpacing(8)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.playbackGroup = QGroupBox(StreamingControlWidget)
        self.playbackGroup.setObjectName("playbackGroup")
        self.playbackLayout = QHBoxLayout(self.playbackGroup)
        self.playbackLayout.setObjectName("playbackLayout")
        self.playPauseBtn = QPushButton(self.playbackGroup)
        self.playPauseBtn.setObjectName("playPauseBtn")
        self.playPauseBtn.setCheckable(True)
        self.playPauseBtn.setMinimumWidth(80)

        self.playbackLayout.addWidget(self.playPauseBtn)

        self.stopBtn = QPushButton(self.playbackGroup)
        self.stopBtn.setObjectName("stopBtn")

        self.playbackLayout.addWidget(self.stopBtn)

        self.loopCheckbox = QCheckBox(self.playbackGroup)
        self.loopCheckbox.setObjectName("loopCheckbox")

        self.playbackLayout.addWidget(self.loopCheckbox)

        self.playbackSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.playbackLayout.addItem(self.playbackSpacer)


        self.mainLayout.addWidget(self.playbackGroup)

        self.timeGroup = QGroupBox(StreamingControlWidget)
        self.timeGroup.setObjectName("timeGroup")
        self.timeLayout = QVBoxLayout(self.timeGroup)
        self.timeLayout.setObjectName("timeLayout")
        self.timeSliderLayout = QHBoxLayout()
        self.timeSliderLayout.setObjectName("timeSliderLayout")
        self.timeLabelStart = QLabel(self.timeGroup)
        self.timeLabelStart.setObjectName("timeLabelStart")
        font = QFont()
        font.setFamilies(["Consolas"])
        self.timeLabelStart.setFont(font)

        self.timeSliderLayout.addWidget(self.timeLabelStart)

        self.timeSlider = QSlider(self.timeGroup)
        self.timeSlider.setObjectName("timeSlider")
        self.timeSlider.setOrientation(Qt.Horizontal)
        self.timeSlider.setMinimum(0)
        self.timeSlider.setMaximum(1000)
        self.timeSlider.setTickPosition(QSlider.TicksBelow)
        self.timeSlider.setTickInterval(100)

        self.timeSliderLayout.addWidget(self.timeSlider)

        self.timeLabelEnd = QLabel(self.timeGroup)
        self.timeLabelEnd.setObjectName("timeLabelEnd")
        self.timeLabelEnd.setFont(font)

        self.timeSliderLayout.addWidget(self.timeLabelEnd)


        self.timeLayout.addLayout(self.timeSliderLayout)

        self.timeInfoLayout = QHBoxLayout()
        self.timeInfoLayout.setObjectName("timeInfoLayout")
        self.currentTimeLabel = QLabel(self.timeGroup)
        self.currentTimeLabel.setObjectName("currentTimeLabel")
        font1 = QFont()
        font1.setPointSize(10)
        font1.setBold(True)
        self.currentTimeLabel.setFont(font1)

        self.timeInfoLayout.addWidget(self.currentTimeLabel)

        self.timeInfoSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.timeInfoLayout.addItem(self.timeInfoSpacer)

        self.progressBar = QProgressBar(self.timeGroup)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)
        self.progressBar.setMaximumWidth(150)

        self.timeInfoLayout.addWidget(self.progressBar)


        self.timeLayout.addLayout(self.timeInfoLayout)


        self.mainLayout.addWidget(self.timeGroup)

        self.settingsGroup = QGroupBox(StreamingControlWidget)
        self.settingsGroup.setObjectName("settingsGroup")
        self.settingsLayout = QFormLayout(self.settingsGroup)
        self.settingsLayout.setObjectName("settingsLayout")
        self.speedLabel = QLabel(self.settingsGroup)
        self.speedLabel.setObjectName("speedLabel")

        self.settingsLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.speedLabel)

        self.speedSpinbox = QDoubleSpinBox(self.settingsGroup)
        self.speedSpinbox.setObjectName("speedSpinbox")
        self.speedSpinbox.setMinimum(0.100000000000000)
        self.speedSpinbox.setMaximum(10.000000000000000)
        self.speedSpinbox.setSingleStep(0.100000000000000)
        self.speedSpinbox.setValue(1.000000000000000)

        self.settingsLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.speedSpinbox)

        self.windowSizeLabel = QLabel(self.settingsGroup)
        self.windowSizeLabel.setObjectName("windowSizeLabel")

        self.settingsLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.windowSizeLabel)

        self.windowSizeSpinbox = QSpinBox(self.settingsGroup)
        self.windowSizeSpinbox.setObjectName("windowSizeSpinbox")
        self.windowSizeSpinbox.setMinimum(1)
        self.windowSizeSpinbox.setMaximum(3600)
        self.windowSizeSpinbox.setValue(60)

        self.settingsLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.windowSizeSpinbox)

        self.intervalLabel = QLabel(self.settingsGroup)
        self.intervalLabel.setObjectName("intervalLabel")

        self.settingsLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.intervalLabel)

        self.intervalSpinbox = QSpinBox(self.settingsGroup)
        self.intervalSpinbox.setObjectName("intervalSpinbox")
        self.intervalSpinbox.setMinimum(10)
        self.intervalSpinbox.setMaximum(1000)
        self.intervalSpinbox.setValue(50)

        self.settingsLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.intervalSpinbox)


        self.mainLayout.addWidget(self.settingsGroup)

        self.filtersGroup = QGroupBox(StreamingControlWidget)
        self.filtersGroup.setObjectName("filtersGroup")
        self.filtersLayout = QHBoxLayout(self.filtersGroup)
        self.filtersLayout.setObjectName("filtersLayout")
        self.hideNanCheckbox = QCheckBox(self.filtersGroup)
        self.hideNanCheckbox.setObjectName("hideNanCheckbox")
        self.hideNanCheckbox.setChecked(True)

        self.filtersLayout.addWidget(self.hideNanCheckbox)

        self.hideInterpolatedCheckbox = QCheckBox(self.filtersGroup)
        self.hideInterpolatedCheckbox.setObjectName("hideInterpolatedCheckbox")
        self.hideInterpolatedCheckbox.setChecked(False)

        self.filtersLayout.addWidget(self.hideInterpolatedCheckbox)

        self.filtersSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.filtersLayout.addItem(self.filtersSpacer)


        self.mainLayout.addWidget(self.filtersGroup)

        self.statusGroup = QGroupBox(StreamingControlWidget)
        self.statusGroup.setObjectName("statusGroup")
        self.statusLayout = QHBoxLayout(self.statusGroup)
        self.statusLayout.setObjectName("statusLayout")
        self.statusLeftLayout = QFormLayout()
        self.statusLeftLayout.setObjectName("statusLeftLayout")
        self.totalPointsLabelText = QLabel(self.statusGroup)
        self.totalPointsLabelText.setObjectName("totalPointsLabelText")

        self.statusLeftLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.totalPointsLabelText)

        self.totalPointsLabel = QLabel(self.statusGroup)
        self.totalPointsLabel.setObjectName("totalPointsLabel")
        font2 = QFont()
        font2.setBold(True)
        self.totalPointsLabel.setFont(font2)

        self.statusLeftLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.totalPointsLabel)

        self.eligiblePointsLabelText = QLabel(self.statusGroup)
        self.eligiblePointsLabelText.setObjectName("eligiblePointsLabelText")

        self.statusLeftLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.eligiblePointsLabelText)

        self.eligiblePointsLabel = QLabel(self.statusGroup)
        self.eligiblePointsLabel.setObjectName("eligiblePointsLabel")
        self.eligiblePointsLabel.setFont(font2)

        self.statusLeftLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.eligiblePointsLabel)


        self.statusLayout.addLayout(self.statusLeftLayout)

        self.statusRightLayout = QFormLayout()
        self.statusRightLayout.setObjectName("statusRightLayout")
        self.windowPointsLabelText = QLabel(self.statusGroup)
        self.windowPointsLabelText.setObjectName("windowPointsLabelText")

        self.statusRightLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.windowPointsLabelText)

        self.windowPointsLabel = QLabel(self.statusGroup)
        self.windowPointsLabel.setObjectName("windowPointsLabel")
        self.windowPointsLabel.setFont(font2)

        self.statusRightLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.windowPointsLabel)

        self.fpsLabelText = QLabel(self.statusGroup)
        self.fpsLabelText.setObjectName("fpsLabelText")

        self.statusRightLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.fpsLabelText)

        self.fpsLabel = QLabel(self.statusGroup)
        self.fpsLabel.setObjectName("fpsLabel")
        self.fpsLabel.setFont(font2)

        self.statusRightLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.fpsLabel)


        self.statusLayout.addLayout(self.statusRightLayout)


        self.mainLayout.addWidget(self.statusGroup)


        self.retranslateUi(StreamingControlWidget)

        QMetaObject.connectSlotsByName(StreamingControlWidget)
    # setupUi

    def retranslateUi(self, StreamingControlWidget):
        StreamingControlWidget.setWindowTitle(QCoreApplication.translate("StreamingControlWidget", "Streaming Controls", None))
        self.playbackGroup.setTitle(QCoreApplication.translate("StreamingControlWidget", "\u25b6\ufe0f Controles de Playback", None))
        self.playPauseBtn.setText(QCoreApplication.translate("StreamingControlWidget", "\u25b6 Play", None))
#if QT_CONFIG(tooltip)
        self.playPauseBtn.setToolTip(QCoreApplication.translate("StreamingControlWidget", "Iniciar/pausar reprodu\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.stopBtn.setText(QCoreApplication.translate("StreamingControlWidget", "\u2b1b Stop", None))
#if QT_CONFIG(tooltip)
        self.stopBtn.setToolTip(QCoreApplication.translate("StreamingControlWidget", "Parar reprodu\u00e7\u00e3o e voltar ao in\u00edcio", None))
#endif // QT_CONFIG(tooltip)
        self.loopCheckbox.setText(QCoreApplication.translate("StreamingControlWidget", "\ud83d\udd01 Loop", None))
#if QT_CONFIG(tooltip)
        self.loopCheckbox.setToolTip(QCoreApplication.translate("StreamingControlWidget", "Repetir automaticamente ao final", None))
#endif // QT_CONFIG(tooltip)
        self.timeGroup.setTitle(QCoreApplication.translate("StreamingControlWidget", "\u23f1\ufe0f Timeline", None))
        self.timeLabelStart.setText(QCoreApplication.translate("StreamingControlWidget", "00:00", None))
#if QT_CONFIG(tooltip)
        self.timeSlider.setToolTip(QCoreApplication.translate("StreamingControlWidget", "Arraste para navegar no tempo", None))
#endif // QT_CONFIG(tooltip)
        self.timeLabelEnd.setText(QCoreApplication.translate("StreamingControlWidget", "00:00", None))
        self.currentTimeLabel.setText(QCoreApplication.translate("StreamingControlWidget", "Current: 00:00", None))
        self.settingsGroup.setTitle(QCoreApplication.translate("StreamingControlWidget", "\u2699\ufe0f Configura\u00e7\u00f5es", None))
        self.speedLabel.setText(QCoreApplication.translate("StreamingControlWidget", "Velocidade:", None))
        self.speedSpinbox.setSuffix(QCoreApplication.translate("StreamingControlWidget", "\u00d7", None))
#if QT_CONFIG(tooltip)
        self.speedSpinbox.setToolTip(QCoreApplication.translate("StreamingControlWidget", "Velocidade de reprodu\u00e7\u00e3o (0.1 a 10\u00d7)", None))
#endif // QT_CONFIG(tooltip)
        self.windowSizeLabel.setText(QCoreApplication.translate("StreamingControlWidget", "Janela:", None))
        self.windowSizeSpinbox.setSuffix(QCoreApplication.translate("StreamingControlWidget", " segundos", None))
#if QT_CONFIG(tooltip)
        self.windowSizeSpinbox.setToolTip(QCoreApplication.translate("StreamingControlWidget", "Tamanho da janela de visualiza\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.intervalLabel.setText(QCoreApplication.translate("StreamingControlWidget", "Intervalo:", None))
        self.intervalSpinbox.setSuffix(QCoreApplication.translate("StreamingControlWidget", " ms", None))
#if QT_CONFIG(tooltip)
        self.intervalSpinbox.setToolTip(QCoreApplication.translate("StreamingControlWidget", "Intervalo de atualiza\u00e7\u00e3o em milissegundos", None))
#endif // QT_CONFIG(tooltip)
        self.filtersGroup.setTitle(QCoreApplication.translate("StreamingControlWidget", "\ud83d\udd0d Filtros", None))
        self.hideNanCheckbox.setText(QCoreApplication.translate("StreamingControlWidget", "Ocultar NaN", None))
#if QT_CONFIG(tooltip)
        self.hideNanCheckbox.setToolTip(QCoreApplication.translate("StreamingControlWidget", "Ocultar pontos com valores NaN", None))
#endif // QT_CONFIG(tooltip)
        self.hideInterpolatedCheckbox.setText(QCoreApplication.translate("StreamingControlWidget", "Ocultar interpolados", None))
#if QT_CONFIG(tooltip)
        self.hideInterpolatedCheckbox.setToolTip(QCoreApplication.translate("StreamingControlWidget", "Ocultar pontos interpolados", None))
#endif // QT_CONFIG(tooltip)
        self.statusGroup.setTitle(QCoreApplication.translate("StreamingControlWidget", "\ud83d\udcca Status", None))
        self.totalPointsLabelText.setText(QCoreApplication.translate("StreamingControlWidget", "Total:", None))
        self.totalPointsLabel.setText(QCoreApplication.translate("StreamingControlWidget", "0", None))
        self.eligiblePointsLabelText.setText(QCoreApplication.translate("StreamingControlWidget", "Eleg\u00edveis:", None))
        self.eligiblePointsLabel.setText(QCoreApplication.translate("StreamingControlWidget", "0", None))
        self.windowPointsLabelText.setText(QCoreApplication.translate("StreamingControlWidget", "Na janela:", None))
        self.windowPointsLabel.setText(QCoreApplication.translate("StreamingControlWidget", "0", None))
        self.fpsLabelText.setText(QCoreApplication.translate("StreamingControlWidget", "FPS:", None))
        self.fpsLabel.setText(QCoreApplication.translate("StreamingControlWidget", "0.0", None))
    # retranslateUi

