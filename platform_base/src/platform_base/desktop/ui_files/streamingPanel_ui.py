# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'streamingPanel.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFormLayout,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QProgressBar, QPushButton, QSizePolicy,
    QSlider, QSpacerItem, QSpinBox, QVBoxLayout,
    QWidget)

class Ui_StreamingPanel(object):
    def setupUi(self, StreamingPanel):
        if not StreamingPanel.objectName():
            StreamingPanel.setObjectName(u"StreamingPanel")
        StreamingPanel.resize(350, 600)
        StreamingPanel.setMinimumSize(QSize(200, 300))
        StreamingPanel.setStyleSheet(u"\n"
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
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.headerLabel = QLabel(StreamingPanel)
        self.headerLabel.setObjectName(u"headerLabel")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.headerLabel.setFont(font)

        self.mainLayout.addWidget(self.headerLabel)

        self.statusGroup = QGroupBox(StreamingPanel)
        self.statusGroup.setObjectName(u"statusGroup")
        self.statusLayout = QGridLayout(self.statusGroup)
        self.statusLayout.setObjectName(u"statusLayout")
        self.statusLayout.setContentsMargins(8, 12, 8, 8)
        self.statusIconLabel = QLabel(self.statusGroup)
        self.statusIconLabel.setObjectName(u"statusIconLabel")
        font1 = QFont()
        font1.setPointSize(16)
        self.statusIconLabel.setFont(font1)

        self.statusLayout.addWidget(self.statusIconLabel, 0, 0, 1, 1)

        self.statusTextLabel = QLabel(self.statusGroup)
        self.statusTextLabel.setObjectName(u"statusTextLabel")
        font2 = QFont()
        font2.setBold(True)
        self.statusTextLabel.setFont(font2)

        self.statusLayout.addWidget(self.statusTextLabel, 0, 1, 1, 1)

        self.rateLabel = QLabel(self.statusGroup)
        self.rateLabel.setObjectName(u"rateLabel")

        self.statusLayout.addWidget(self.rateLabel, 1, 0, 1, 1)

        self.rateValueLabel = QLabel(self.statusGroup)
        self.rateValueLabel.setObjectName(u"rateValueLabel")

        self.statusLayout.addWidget(self.rateValueLabel, 1, 1, 1, 1)

        self.bufferLabel = QLabel(self.statusGroup)
        self.bufferLabel.setObjectName(u"bufferLabel")

        self.statusLayout.addWidget(self.bufferLabel, 2, 0, 1, 1)

        self.bufferProgress = QProgressBar(self.statusGroup)
        self.bufferProgress.setObjectName(u"bufferProgress")
        self.bufferProgress.setMaximum(100)
        self.bufferProgress.setValue(0)
        self.bufferProgress.setTextVisible(True)

        self.statusLayout.addWidget(self.bufferProgress, 2, 1, 1, 1)


        self.mainLayout.addWidget(self.statusGroup)

        self.controlsGroup = QGroupBox(StreamingPanel)
        self.controlsGroup.setObjectName(u"controlsGroup")
        self.controlsLayout = QVBoxLayout(self.controlsGroup)
        self.controlsLayout.setObjectName(u"controlsLayout")
        self.controlsLayout.setContentsMargins(8, 12, 8, 8)
        self.playbackButtonsLayout = QHBoxLayout()
        self.playbackButtonsLayout.setObjectName(u"playbackButtonsLayout")
        self.playBtn = QPushButton(self.controlsGroup)
        self.playBtn.setObjectName(u"playBtn")

        self.playbackButtonsLayout.addWidget(self.playBtn)

        self.pauseBtn = QPushButton(self.controlsGroup)
        self.pauseBtn.setObjectName(u"pauseBtn")
        self.pauseBtn.setEnabled(False)

        self.playbackButtonsLayout.addWidget(self.pauseBtn)

        self.stopBtn = QPushButton(self.controlsGroup)
        self.stopBtn.setObjectName(u"stopBtn")
        self.stopBtn.setEnabled(False)

        self.playbackButtonsLayout.addWidget(self.stopBtn)


        self.controlsLayout.addLayout(self.playbackButtonsLayout)

        self.positionLayout = QHBoxLayout()
        self.positionLayout.setObjectName(u"positionLayout")
        self.positionLabel = QLabel(self.controlsGroup)
        self.positionLabel.setObjectName(u"positionLabel")
        self.positionLabel.setMinimumSize(QSize(50, 0))

        self.positionLayout.addWidget(self.positionLabel)

        self.positionSlider = QSlider(self.controlsGroup)
        self.positionSlider.setObjectName(u"positionSlider")
        self.positionSlider.setEnabled(False)
        self.positionSlider.setOrientation(Qt.Horizontal)
        self.positionSlider.setTickPosition(QSlider.TicksBelow)
        self.positionSlider.setTickInterval(10)

        self.positionLayout.addWidget(self.positionSlider)

        self.durationLabel = QLabel(self.controlsGroup)
        self.durationLabel.setObjectName(u"durationLabel")
        self.durationLabel.setMinimumSize(QSize(50, 0))
        self.durationLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.positionLayout.addWidget(self.durationLabel)


        self.controlsLayout.addLayout(self.positionLayout)

        self.speedLayout = QHBoxLayout()
        self.speedLayout.setObjectName(u"speedLayout")
        self.speedLabel = QLabel(self.controlsGroup)
        self.speedLabel.setObjectName(u"speedLabel")

        self.speedLayout.addWidget(self.speedLabel)

        self.speedSlider = QSlider(self.controlsGroup)
        self.speedSlider.setObjectName(u"speedSlider")
        self.speedSlider.setMinimum(25)
        self.speedSlider.setMaximum(400)
        self.speedSlider.setValue(100)
        self.speedSlider.setOrientation(Qt.Horizontal)

        self.speedLayout.addWidget(self.speedSlider)

        self.speedValueLabel = QLabel(self.controlsGroup)
        self.speedValueLabel.setObjectName(u"speedValueLabel")
        self.speedValueLabel.setMinimumSize(QSize(40, 0))
        self.speedValueLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.speedLayout.addWidget(self.speedValueLabel)


        self.controlsLayout.addLayout(self.speedLayout)


        self.mainLayout.addWidget(self.controlsGroup)

        self.sourceGroup = QGroupBox(StreamingPanel)
        self.sourceGroup.setObjectName(u"sourceGroup")
        self.sourceLayout = QFormLayout(self.sourceGroup)
        self.sourceLayout.setObjectName(u"sourceLayout")
        self.sourceLayout.setContentsMargins(8, 12, 8, 8)
        self.sourceTypeLabel = QLabel(self.sourceGroup)
        self.sourceTypeLabel.setObjectName(u"sourceTypeLabel")

        self.sourceLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.sourceTypeLabel)

        self.sourceTypeCombo = QComboBox(self.sourceGroup)
        self.sourceTypeCombo.addItem("")
        self.sourceTypeCombo.addItem("")
        self.sourceTypeCombo.addItem("")
        self.sourceTypeCombo.addItem("")
        self.sourceTypeCombo.addItem("")
        self.sourceTypeCombo.setObjectName(u"sourceTypeCombo")

        self.sourceLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.sourceTypeCombo)

        self.sourcePathLabel = QLabel(self.sourceGroup)
        self.sourcePathLabel.setObjectName(u"sourcePathLabel")

        self.sourceLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.sourcePathLabel)

        self.pathLayout = QHBoxLayout()
        self.pathLayout.setObjectName(u"pathLayout")
        self.sourcePathEdit = QLineEdit(self.sourceGroup)
        self.sourcePathEdit.setObjectName(u"sourcePathEdit")

        self.pathLayout.addWidget(self.sourcePathEdit)

        self.browseBtn = QPushButton(self.sourceGroup)
        self.browseBtn.setObjectName(u"browseBtn")
        self.browseBtn.setMaximumSize(QSize(30, 16777215))

        self.pathLayout.addWidget(self.browseBtn)


        self.sourceLayout.setLayout(1, QFormLayout.ItemRole.FieldRole, self.pathLayout)

        self.connectLayout = QHBoxLayout()
        self.connectLayout.setObjectName(u"connectLayout")
        self.connectBtn = QPushButton(self.sourceGroup)
        self.connectBtn.setObjectName(u"connectBtn")

        self.connectLayout.addWidget(self.connectBtn)

        self.disconnectBtn = QPushButton(self.sourceGroup)
        self.disconnectBtn.setObjectName(u"disconnectBtn")
        self.disconnectBtn.setEnabled(False)

        self.connectLayout.addWidget(self.disconnectBtn)


        self.sourceLayout.setLayout(2, QFormLayout.ItemRole.SpanningRole, self.connectLayout)


        self.mainLayout.addWidget(self.sourceGroup)

        self.settingsGroup = QGroupBox(StreamingPanel)
        self.settingsGroup.setObjectName(u"settingsGroup")
        self.settingsLayout = QFormLayout(self.settingsGroup)
        self.settingsLayout.setObjectName(u"settingsLayout")
        self.settingsLayout.setContentsMargins(8, 12, 8, 8)
        self.bufferSizeLabel = QLabel(self.settingsGroup)
        self.bufferSizeLabel.setObjectName(u"bufferSizeLabel")

        self.settingsLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.bufferSizeLabel)

        self.bufferSizeSpin = QSpinBox(self.settingsGroup)
        self.bufferSizeSpin.setObjectName(u"bufferSizeSpin")
        self.bufferSizeSpin.setMinimum(100)
        self.bufferSizeSpin.setMaximum(100000)
        self.bufferSizeSpin.setValue(10000)

        self.settingsLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.bufferSizeSpin)

        self.updateRateLabel = QLabel(self.settingsGroup)
        self.updateRateLabel.setObjectName(u"updateRateLabel")

        self.settingsLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.updateRateLabel)

        self.updateRateSpin = QSpinBox(self.settingsGroup)
        self.updateRateSpin.setObjectName(u"updateRateSpin")
        self.updateRateSpin.setMinimum(10)
        self.updateRateSpin.setMaximum(5000)
        self.updateRateSpin.setValue(100)

        self.settingsLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.updateRateSpin)

        self.autoScrollCheck = QCheckBox(self.settingsGroup)
        self.autoScrollCheck.setObjectName(u"autoScrollCheck")
        self.autoScrollCheck.setChecked(True)

        self.settingsLayout.setWidget(2, QFormLayout.ItemRole.SpanningRole, self.autoScrollCheck)

        self.recordCheck = QCheckBox(self.settingsGroup)
        self.recordCheck.setObjectName(u"recordCheck")

        self.settingsLayout.setWidget(3, QFormLayout.ItemRole.SpanningRole, self.recordCheck)


        self.mainLayout.addWidget(self.settingsGroup)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mainLayout.addItem(self.verticalSpacer)


        self.retranslateUi(StreamingPanel)

        QMetaObject.connectSlotsByName(StreamingPanel)
    # setupUi

    def retranslateUi(self, StreamingPanel):
        StreamingPanel.setWindowTitle(QCoreApplication.translate("StreamingPanel", u"Streaming Panel", None))
        self.headerLabel.setText(QCoreApplication.translate("StreamingPanel", u"\u25b6\ufe0f Streaming de Dados", None))
        self.headerLabel.setStyleSheet(QCoreApplication.translate("StreamingPanel", u"color: #198754; padding: 4px;", None))
        self.statusGroup.setTitle(QCoreApplication.translate("StreamingPanel", u"\ud83d\udce1 Status da Conex\u00e3o", None))
        self.statusIconLabel.setText(QCoreApplication.translate("StreamingPanel", u"\u26aa", None))
        self.statusTextLabel.setText(QCoreApplication.translate("StreamingPanel", u"Desconectado", None))
        self.rateLabel.setText(QCoreApplication.translate("StreamingPanel", u"Taxa:", None))
        self.rateValueLabel.setText(QCoreApplication.translate("StreamingPanel", u"0 pts/s", None))
        self.bufferLabel.setText(QCoreApplication.translate("StreamingPanel", u"Buffer:", None))
        self.bufferProgress.setFormat(QCoreApplication.translate("StreamingPanel", u"%p%", None))
        self.controlsGroup.setTitle(QCoreApplication.translate("StreamingPanel", u"\ud83c\udfae Controles de Playback", None))
        self.playBtn.setText(QCoreApplication.translate("StreamingPanel", u"\u25b6 Play", None))
#if QT_CONFIG(tooltip)
        self.playBtn.setToolTip(QCoreApplication.translate("StreamingPanel", u"Iniciar reprodu\u00e7\u00e3o do streaming", None))
#endif // QT_CONFIG(tooltip)
        self.pauseBtn.setText(QCoreApplication.translate("StreamingPanel", u"\u23f8 Pause", None))
#if QT_CONFIG(tooltip)
        self.pauseBtn.setToolTip(QCoreApplication.translate("StreamingPanel", u"Pausar reprodu\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.stopBtn.setText(QCoreApplication.translate("StreamingPanel", u"\u23f9 Stop", None))
#if QT_CONFIG(tooltip)
        self.stopBtn.setToolTip(QCoreApplication.translate("StreamingPanel", u"Parar reprodu\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.positionLabel.setText(QCoreApplication.translate("StreamingPanel", u"00:00", None))
        self.durationLabel.setText(QCoreApplication.translate("StreamingPanel", u"00:00", None))
        self.speedLabel.setText(QCoreApplication.translate("StreamingPanel", u"Velocidade:", None))
        self.speedValueLabel.setText(QCoreApplication.translate("StreamingPanel", u"1.0x", None))
        self.sourceGroup.setTitle(QCoreApplication.translate("StreamingPanel", u"\ud83d\udcc2 Fonte de Dados", None))
        self.sourceTypeLabel.setText(QCoreApplication.translate("StreamingPanel", u"Tipo:", None))
        self.sourceTypeCombo.setItemText(0, QCoreApplication.translate("StreamingPanel", u"Arquivo Local", None))
        self.sourceTypeCombo.setItemText(1, QCoreApplication.translate("StreamingPanel", u"Simula\u00e7\u00e3o", None))
        self.sourceTypeCombo.setItemText(2, QCoreApplication.translate("StreamingPanel", u"TCP/IP", None))
        self.sourceTypeCombo.setItemText(3, QCoreApplication.translate("StreamingPanel", u"Serial", None))
        self.sourceTypeCombo.setItemText(4, QCoreApplication.translate("StreamingPanel", u"OPC-UA", None))

#if QT_CONFIG(tooltip)
        self.sourceTypeCombo.setToolTip(QCoreApplication.translate("StreamingPanel", u"Tipo de fonte de dados", None))
#endif // QT_CONFIG(tooltip)
        self.sourcePathLabel.setText(QCoreApplication.translate("StreamingPanel", u"Endere\u00e7o:", None))
        self.sourcePathEdit.setPlaceholderText(QCoreApplication.translate("StreamingPanel", u"Caminho ou endere\u00e7o da fonte", None))
        self.browseBtn.setText(QCoreApplication.translate("StreamingPanel", u"...", None))
#if QT_CONFIG(tooltip)
        self.browseBtn.setToolTip(QCoreApplication.translate("StreamingPanel", u"Selecionar arquivo", None))
#endif // QT_CONFIG(tooltip)
        self.connectBtn.setText(QCoreApplication.translate("StreamingPanel", u"\ud83d\udd17 Conectar", None))
#if QT_CONFIG(tooltip)
        self.connectBtn.setToolTip(QCoreApplication.translate("StreamingPanel", u"Conectar \u00e0 fonte de dados", None))
#endif // QT_CONFIG(tooltip)
        self.disconnectBtn.setText(QCoreApplication.translate("StreamingPanel", u"\ud83d\udd0c Desconectar", None))
#if QT_CONFIG(tooltip)
        self.disconnectBtn.setToolTip(QCoreApplication.translate("StreamingPanel", u"Desconectar da fonte", None))
#endif // QT_CONFIG(tooltip)
        self.settingsGroup.setTitle(QCoreApplication.translate("StreamingPanel", u"\u2699\ufe0f Configura\u00e7\u00f5es", None))
        self.bufferSizeLabel.setText(QCoreApplication.translate("StreamingPanel", u"Buffer (pts):", None))
#if QT_CONFIG(tooltip)
        self.bufferSizeSpin.setToolTip(QCoreApplication.translate("StreamingPanel", u"Tamanho do buffer de dados", None))
#endif // QT_CONFIG(tooltip)
        self.updateRateLabel.setText(QCoreApplication.translate("StreamingPanel", u"Atualiza\u00e7\u00e3o (ms):", None))
#if QT_CONFIG(tooltip)
        self.updateRateSpin.setToolTip(QCoreApplication.translate("StreamingPanel", u"Taxa de atualiza\u00e7\u00e3o da visualiza\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.autoScrollCheck.setText(QCoreApplication.translate("StreamingPanel", u"Auto-scroll", None))
#if QT_CONFIG(tooltip)
        self.autoScrollCheck.setToolTip(QCoreApplication.translate("StreamingPanel", u"Rolar automaticamente para novos dados", None))
#endif // QT_CONFIG(tooltip)
        self.recordCheck.setText(QCoreApplication.translate("StreamingPanel", u"Gravar dados", None))
#if QT_CONFIG(tooltip)
        self.recordCheck.setToolTip(QCoreApplication.translate("StreamingPanel", u"Salvar dados recebidos em arquivo", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

