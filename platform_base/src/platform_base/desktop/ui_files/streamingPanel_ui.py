
################################################################################
## Form generated from reading UI file 'streamingPanel.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSpacerItem,
    QSpinBox,
    QVBoxLayout,
)


class Ui_StreamingPanel:
    def setupUi(self, StreamingPanel):
        if not StreamingPanel.objectName():
            StreamingPanel.setObjectName("StreamingPanel")
        StreamingPanel.resize(350, 600)
        StreamingPanel.setMinimumSize(QSize(200, 300))
        StreamingPanel.setStyleSheet("\n"
"QWidget {\n"
"    background-color: #ffffff;\n"
"}\n"
"QGroupBox {\n"
"    font-weight: bold;\n"
"    border: 1px solid #e9ecef;\n"
"    border-radius: 6px;\n"
"    margin-top: 8px;\n"
"    padding-top: 8px;\n"
"    background-color: #f8f9fa;\n"
"}\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 8px;\n"
"    padding: 2px 6px;\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #e9ecef;\n"
"    border-radius: 3px;\n"
"}\n"
"QPushButton {\n"
"    background-color: #0d6efd;\n"
"    color: white;\n"
"    border: none;\n"
"    padding: 6px 12px;\n"
"    border-radius: 4px;\n"
"    font-weight: bold;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #0b5ed7;\n"
"}\n"
"QPushButton:disabled {\n"
"    background-color: #6c757d;\n"
"}\n"
"QPushButton#playBtn {\n"
"    background-color: #198754;\n"
"}\n"
"QPushButton#playBtn:hover {\n"
"    background-color: #157347;\n"
"}\n"
"QPushButton#pauseBtn {\n"
"    background-color: #ffc107;\n"
"    color: #212529;\n"
"}\n"
"QPushButto"
                        "n#stopBtn {\n"
"    background-color: #dc3545;\n"
"}\n"
"QSlider::groove:horizontal {\n"
"    border: 1px solid #ced4da;\n"
"    height: 8px;\n"
"    background: #e9ecef;\n"
"    margin: 2px 0;\n"
"    border-radius: 4px;\n"
"}\n"
"QSlider::handle:horizontal {\n"
"    background: #0d6efd;\n"
"    border: 1px solid #0b5ed7;\n"
"    width: 18px;\n"
"    margin: -5px 0;\n"
"    border-radius: 9px;\n"
"}\n"
"QProgressBar {\n"
"    border: 1px solid #ced4da;\n"
"    border-radius: 4px;\n"
"    text-align: center;\n"
"    background-color: #e9ecef;\n"
"}\n"
"QProgressBar::chunk {\n"
"    background-color: #0d6efd;\n"
"    border-radius: 3px;\n"
"}\n"
"   ")
        self.mainLayout = QVBoxLayout(StreamingPanel)
        self.mainLayout.setSpacing(8)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.headerLabel = QLabel(StreamingPanel)
        self.headerLabel.setObjectName("headerLabel")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.headerLabel.setFont(font)

        self.mainLayout.addWidget(self.headerLabel)

        self.statusGroup = QGroupBox(StreamingPanel)
        self.statusGroup.setObjectName("statusGroup")
        self.statusLayout = QGridLayout(self.statusGroup)
        self.statusLayout.setObjectName("statusLayout")
        self.statusLayout.setContentsMargins(8, 12, 8, 8)
        self.statusIconLabel = QLabel(self.statusGroup)
        self.statusIconLabel.setObjectName("statusIconLabel")
        font1 = QFont()
        font1.setPointSize(16)
        self.statusIconLabel.setFont(font1)

        self.statusLayout.addWidget(self.statusIconLabel, 0, 0, 1, 1)

        self.statusTextLabel = QLabel(self.statusGroup)
        self.statusTextLabel.setObjectName("statusTextLabel")
        font2 = QFont()
        font2.setBold(True)
        self.statusTextLabel.setFont(font2)

        self.statusLayout.addWidget(self.statusTextLabel, 0, 1, 1, 1)

        self.rateLabel = QLabel(self.statusGroup)
        self.rateLabel.setObjectName("rateLabel")

        self.statusLayout.addWidget(self.rateLabel, 1, 0, 1, 1)

        self.rateValueLabel = QLabel(self.statusGroup)
        self.rateValueLabel.setObjectName("rateValueLabel")

        self.statusLayout.addWidget(self.rateValueLabel, 1, 1, 1, 1)

        self.bufferLabel = QLabel(self.statusGroup)
        self.bufferLabel.setObjectName("bufferLabel")

        self.statusLayout.addWidget(self.bufferLabel, 2, 0, 1, 1)

        self.bufferProgress = QProgressBar(self.statusGroup)
        self.bufferProgress.setObjectName("bufferProgress")
        self.bufferProgress.setMaximum(100)
        self.bufferProgress.setValue(0)
        self.bufferProgress.setTextVisible(True)

        self.statusLayout.addWidget(self.bufferProgress, 2, 1, 1, 1)


        self.mainLayout.addWidget(self.statusGroup)

        self.controlsGroup = QGroupBox(StreamingPanel)
        self.controlsGroup.setObjectName("controlsGroup")
        self.controlsLayout = QVBoxLayout(self.controlsGroup)
        self.controlsLayout.setObjectName("controlsLayout")
        self.controlsLayout.setContentsMargins(8, 12, 8, 8)
        self.playbackButtonsLayout = QHBoxLayout()
        self.playbackButtonsLayout.setObjectName("playbackButtonsLayout")
        self.playBtn = QPushButton(self.controlsGroup)
        self.playBtn.setObjectName("playBtn")

        self.playbackButtonsLayout.addWidget(self.playBtn)

        self.pauseBtn = QPushButton(self.controlsGroup)
        self.pauseBtn.setObjectName("pauseBtn")
        self.pauseBtn.setEnabled(False)

        self.playbackButtonsLayout.addWidget(self.pauseBtn)

        self.stopBtn = QPushButton(self.controlsGroup)
        self.stopBtn.setObjectName("stopBtn")
        self.stopBtn.setEnabled(False)

        self.playbackButtonsLayout.addWidget(self.stopBtn)


        self.controlsLayout.addLayout(self.playbackButtonsLayout)

        self.positionLayout = QHBoxLayout()
        self.positionLayout.setObjectName("positionLayout")
        self.positionLabel = QLabel(self.controlsGroup)
        self.positionLabel.setObjectName("positionLabel")
        self.positionLabel.setMinimumSize(QSize(50, 0))

        self.positionLayout.addWidget(self.positionLabel)

        self.positionSlider = QSlider(self.controlsGroup)
        self.positionSlider.setObjectName("positionSlider")
        self.positionSlider.setEnabled(False)
        self.positionSlider.setOrientation(Qt.Horizontal)
        self.positionSlider.setTickPosition(QSlider.TicksBelow)
        self.positionSlider.setTickInterval(10)

        self.positionLayout.addWidget(self.positionSlider)

        self.durationLabel = QLabel(self.controlsGroup)
        self.durationLabel.setObjectName("durationLabel")
        self.durationLabel.setMinimumSize(QSize(50, 0))
        self.durationLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.positionLayout.addWidget(self.durationLabel)


        self.controlsLayout.addLayout(self.positionLayout)

        self.speedLayout = QHBoxLayout()
        self.speedLayout.setObjectName("speedLayout")
        self.speedLabel = QLabel(self.controlsGroup)
        self.speedLabel.setObjectName("speedLabel")

        self.speedLayout.addWidget(self.speedLabel)

        self.speedSlider = QSlider(self.controlsGroup)
        self.speedSlider.setObjectName("speedSlider")
        self.speedSlider.setMinimum(25)
        self.speedSlider.setMaximum(400)
        self.speedSlider.setValue(100)
        self.speedSlider.setOrientation(Qt.Horizontal)

        self.speedLayout.addWidget(self.speedSlider)

        self.speedValueLabel = QLabel(self.controlsGroup)
        self.speedValueLabel.setObjectName("speedValueLabel")
        self.speedValueLabel.setMinimumSize(QSize(40, 0))
        self.speedValueLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.speedLayout.addWidget(self.speedValueLabel)


        self.controlsLayout.addLayout(self.speedLayout)


        self.mainLayout.addWidget(self.controlsGroup)

        self.sourceGroup = QGroupBox(StreamingPanel)
        self.sourceGroup.setObjectName("sourceGroup")
        self.sourceLayout = QFormLayout(self.sourceGroup)
        self.sourceLayout.setObjectName("sourceLayout")
        self.sourceLayout.setContentsMargins(8, 12, 8, 8)
        self.sourceTypeLabel = QLabel(self.sourceGroup)
        self.sourceTypeLabel.setObjectName("sourceTypeLabel")

        self.sourceLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.sourceTypeLabel)

        self.sourceTypeCombo = QComboBox(self.sourceGroup)
        self.sourceTypeCombo.addItem("")
        self.sourceTypeCombo.addItem("")
        self.sourceTypeCombo.addItem("")
        self.sourceTypeCombo.addItem("")
        self.sourceTypeCombo.addItem("")
        self.sourceTypeCombo.setObjectName("sourceTypeCombo")

        self.sourceLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.sourceTypeCombo)

        self.sourcePathLabel = QLabel(self.sourceGroup)
        self.sourcePathLabel.setObjectName("sourcePathLabel")

        self.sourceLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.sourcePathLabel)

        self.pathLayout = QHBoxLayout()
        self.pathLayout.setObjectName("pathLayout")
        self.sourcePathEdit = QLineEdit(self.sourceGroup)
        self.sourcePathEdit.setObjectName("sourcePathEdit")

        self.pathLayout.addWidget(self.sourcePathEdit)

        self.browseBtn = QPushButton(self.sourceGroup)
        self.browseBtn.setObjectName("browseBtn")
        self.browseBtn.setMaximumSize(QSize(30, 16777215))

        self.pathLayout.addWidget(self.browseBtn)


        self.sourceLayout.setLayout(1, QFormLayout.ItemRole.FieldRole, self.pathLayout)

        self.connectLayout = QHBoxLayout()
        self.connectLayout.setObjectName("connectLayout")
        self.connectBtn = QPushButton(self.sourceGroup)
        self.connectBtn.setObjectName("connectBtn")

        self.connectLayout.addWidget(self.connectBtn)

        self.disconnectBtn = QPushButton(self.sourceGroup)
        self.disconnectBtn.setObjectName("disconnectBtn")
        self.disconnectBtn.setEnabled(False)

        self.connectLayout.addWidget(self.disconnectBtn)


        self.sourceLayout.setLayout(2, QFormLayout.ItemRole.SpanningRole, self.connectLayout)


        self.mainLayout.addWidget(self.sourceGroup)

        self.settingsGroup = QGroupBox(StreamingPanel)
        self.settingsGroup.setObjectName("settingsGroup")
        self.settingsLayout = QFormLayout(self.settingsGroup)
        self.settingsLayout.setObjectName("settingsLayout")
        self.settingsLayout.setContentsMargins(8, 12, 8, 8)
        self.bufferSizeLabel = QLabel(self.settingsGroup)
        self.bufferSizeLabel.setObjectName("bufferSizeLabel")

        self.settingsLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.bufferSizeLabel)

        self.bufferSizeSpin = QSpinBox(self.settingsGroup)
        self.bufferSizeSpin.setObjectName("bufferSizeSpin")
        self.bufferSizeSpin.setMinimum(100)
        self.bufferSizeSpin.setMaximum(100000)
        self.bufferSizeSpin.setValue(10000)

        self.settingsLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.bufferSizeSpin)

        self.updateRateLabel = QLabel(self.settingsGroup)
        self.updateRateLabel.setObjectName("updateRateLabel")

        self.settingsLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.updateRateLabel)

        self.updateRateSpin = QSpinBox(self.settingsGroup)
        self.updateRateSpin.setObjectName("updateRateSpin")
        self.updateRateSpin.setMinimum(10)
        self.updateRateSpin.setMaximum(5000)
        self.updateRateSpin.setValue(100)

        self.settingsLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.updateRateSpin)

        self.autoScrollCheck = QCheckBox(self.settingsGroup)
        self.autoScrollCheck.setObjectName("autoScrollCheck")
        self.autoScrollCheck.setChecked(True)

        self.settingsLayout.setWidget(2, QFormLayout.ItemRole.SpanningRole, self.autoScrollCheck)

        self.recordCheck = QCheckBox(self.settingsGroup)
        self.recordCheck.setObjectName("recordCheck")

        self.settingsLayout.setWidget(3, QFormLayout.ItemRole.SpanningRole, self.recordCheck)


        self.mainLayout.addWidget(self.settingsGroup)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mainLayout.addItem(self.verticalSpacer)


        self.retranslateUi(StreamingPanel)

        QMetaObject.connectSlotsByName(StreamingPanel)
    # setupUi

    def retranslateUi(self, StreamingPanel):
        StreamingPanel.setWindowTitle(QCoreApplication.translate("StreamingPanel", "Streaming Panel", None))
        self.headerLabel.setText(QCoreApplication.translate("StreamingPanel", "\u25b6\ufe0f Streaming de Dados", None))
        self.headerLabel.setStyleSheet(QCoreApplication.translate("StreamingPanel", "color: #198754; padding: 4px;", None))
        self.statusGroup.setTitle(QCoreApplication.translate("StreamingPanel", "\ud83d\udce1 Status da Conex\u00e3o", None))
        self.statusIconLabel.setText(QCoreApplication.translate("StreamingPanel", "\u26aa", None))
        self.statusTextLabel.setText(QCoreApplication.translate("StreamingPanel", "Desconectado", None))
        self.rateLabel.setText(QCoreApplication.translate("StreamingPanel", "Taxa:", None))
        self.rateValueLabel.setText(QCoreApplication.translate("StreamingPanel", "0 pts/s", None))
        self.bufferLabel.setText(QCoreApplication.translate("StreamingPanel", "Buffer:", None))
        self.bufferProgress.setFormat(QCoreApplication.translate("StreamingPanel", "%p%", None))
        self.controlsGroup.setTitle(QCoreApplication.translate("StreamingPanel", "\ud83c\udfae Controles de Playback", None))
        self.playBtn.setText(QCoreApplication.translate("StreamingPanel", "\u25b6 Play", None))
#if QT_CONFIG(tooltip)
        self.playBtn.setToolTip(QCoreApplication.translate("StreamingPanel", "Iniciar reprodu\u00e7\u00e3o do streaming", None))
#endif // QT_CONFIG(tooltip)
        self.pauseBtn.setText(QCoreApplication.translate("StreamingPanel", "\u23f8 Pause", None))
#if QT_CONFIG(tooltip)
        self.pauseBtn.setToolTip(QCoreApplication.translate("StreamingPanel", "Pausar reprodu\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.stopBtn.setText(QCoreApplication.translate("StreamingPanel", "\u23f9 Stop", None))
#if QT_CONFIG(tooltip)
        self.stopBtn.setToolTip(QCoreApplication.translate("StreamingPanel", "Parar reprodu\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.positionLabel.setText(QCoreApplication.translate("StreamingPanel", "00:00", None))
        self.durationLabel.setText(QCoreApplication.translate("StreamingPanel", "00:00", None))
        self.speedLabel.setText(QCoreApplication.translate("StreamingPanel", "Velocidade:", None))
        self.speedValueLabel.setText(QCoreApplication.translate("StreamingPanel", "1.0x", None))
        self.sourceGroup.setTitle(QCoreApplication.translate("StreamingPanel", "\ud83d\udcc2 Fonte de Dados", None))
        self.sourceTypeLabel.setText(QCoreApplication.translate("StreamingPanel", "Tipo:", None))
        self.sourceTypeCombo.setItemText(0, QCoreApplication.translate("StreamingPanel", "Arquivo Local", None))
        self.sourceTypeCombo.setItemText(1, QCoreApplication.translate("StreamingPanel", "Simula\u00e7\u00e3o", None))
        self.sourceTypeCombo.setItemText(2, QCoreApplication.translate("StreamingPanel", "TCP/IP", None))
        self.sourceTypeCombo.setItemText(3, QCoreApplication.translate("StreamingPanel", "Serial", None))
        self.sourceTypeCombo.setItemText(4, QCoreApplication.translate("StreamingPanel", "OPC-UA", None))

#if QT_CONFIG(tooltip)
        self.sourceTypeCombo.setToolTip(QCoreApplication.translate("StreamingPanel", "Tipo de fonte de dados", None))
#endif // QT_CONFIG(tooltip)
        self.sourcePathLabel.setText(QCoreApplication.translate("StreamingPanel", "Endere\u00e7o:", None))
        self.sourcePathEdit.setPlaceholderText(QCoreApplication.translate("StreamingPanel", "Caminho ou endere\u00e7o da fonte", None))
        self.browseBtn.setText(QCoreApplication.translate("StreamingPanel", "...", None))
#if QT_CONFIG(tooltip)
        self.browseBtn.setToolTip(QCoreApplication.translate("StreamingPanel", "Selecionar arquivo", None))
#endif // QT_CONFIG(tooltip)
        self.connectBtn.setText(QCoreApplication.translate("StreamingPanel", "\ud83d\udd17 Conectar", None))
#if QT_CONFIG(tooltip)
        self.connectBtn.setToolTip(QCoreApplication.translate("StreamingPanel", "Conectar \u00e0 fonte de dados", None))
#endif // QT_CONFIG(tooltip)
        self.disconnectBtn.setText(QCoreApplication.translate("StreamingPanel", "\ud83d\udd0c Desconectar", None))
#if QT_CONFIG(tooltip)
        self.disconnectBtn.setToolTip(QCoreApplication.translate("StreamingPanel", "Desconectar da fonte", None))
#endif // QT_CONFIG(tooltip)
        self.settingsGroup.setTitle(QCoreApplication.translate("StreamingPanel", "\u2699\ufe0f Configura\u00e7\u00f5es", None))
        self.bufferSizeLabel.setText(QCoreApplication.translate("StreamingPanel", "Buffer (pts):", None))
#if QT_CONFIG(tooltip)
        self.bufferSizeSpin.setToolTip(QCoreApplication.translate("StreamingPanel", "Tamanho do buffer de dados", None))
#endif // QT_CONFIG(tooltip)
        self.updateRateLabel.setText(QCoreApplication.translate("StreamingPanel", "Atualiza\u00e7\u00e3o (ms):", None))
#if QT_CONFIG(tooltip)
        self.updateRateSpin.setToolTip(QCoreApplication.translate("StreamingPanel", "Taxa de atualiza\u00e7\u00e3o da visualiza\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.autoScrollCheck.setText(QCoreApplication.translate("StreamingPanel", "Auto-scroll", None))
#if QT_CONFIG(tooltip)
        self.autoScrollCheck.setToolTip(QCoreApplication.translate("StreamingPanel", "Rolar automaticamente para novos dados", None))
#endif // QT_CONFIG(tooltip)
        self.recordCheck.setText(QCoreApplication.translate("StreamingPanel", "Gravar dados", None))
#if QT_CONFIG(tooltip)
        self.recordCheck.setToolTip(QCoreApplication.translate("StreamingPanel", "Salvar dados recebidos em arquivo", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

