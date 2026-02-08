
################################################################################
## Form generated from reading UI file 'videoExportDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QVBoxLayout,
)


class Ui_VideoExportDialog:
    def setupUi(self, VideoExportDialog):
        if not VideoExportDialog.objectName():
            VideoExportDialog.setObjectName("VideoExportDialog")
        VideoExportDialog.resize(550, 500)
        VideoExportDialog.setModal(True)
        self.mainLayout = QVBoxLayout(VideoExportDialog)
        self.mainLayout.setSpacing(12)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(16, 16, 16, 16)
        self.outputGroup = QGroupBox(VideoExportDialog)
        self.outputGroup.setObjectName("outputGroup")
        self.outputLayout = QFormLayout(self.outputGroup)
        self.outputLayout.setObjectName("outputLayout")
        self.pathLabel = QLabel(self.outputGroup)
        self.pathLabel.setObjectName("pathLabel")

        self.outputLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.pathLabel)

        self.pathRowLayout = QHBoxLayout()
        self.pathRowLayout.setObjectName("pathRowLayout")
        self.pathEdit = QLabel(self.outputGroup)
        self.pathEdit.setObjectName("pathEdit")
        self.pathEdit.setWordWrap(True)

        self.pathRowLayout.addWidget(self.pathEdit)

        self.browseBtn = QPushButton(self.outputGroup)
        self.browseBtn.setObjectName("browseBtn")

        self.pathRowLayout.addWidget(self.browseBtn)


        self.outputLayout.setLayout(0, QFormLayout.ItemRole.FieldRole, self.pathRowLayout)

        self.formatLabelText = QLabel(self.outputGroup)
        self.formatLabelText.setObjectName("formatLabelText")

        self.outputLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.formatLabelText)

        self.formatCombo = QComboBox(self.outputGroup)
        self.formatCombo.addItem("")
        self.formatCombo.addItem("")
        self.formatCombo.addItem("")
        self.formatCombo.addItem("")
        self.formatCombo.addItem("")
        self.formatCombo.setObjectName("formatCombo")

        self.outputLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.formatCombo)


        self.mainLayout.addWidget(self.outputGroup)

        self.qualityGroup = QGroupBox(VideoExportDialog)
        self.qualityGroup.setObjectName("qualityGroup")
        self.qualityLayout = QFormLayout(self.qualityGroup)
        self.qualityLayout.setObjectName("qualityLayout")
        self.qualityLabel = QLabel(self.qualityGroup)
        self.qualityLabel.setObjectName("qualityLabel")

        self.qualityLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.qualityLabel)

        self.qualityCombo = QComboBox(self.qualityGroup)
        self.qualityCombo.addItem("")
        self.qualityCombo.addItem("")
        self.qualityCombo.addItem("")
        self.qualityCombo.addItem("")
        self.qualityCombo.addItem("")
        self.qualityCombo.setObjectName("qualityCombo")

        self.qualityLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.qualityCombo)

        self.resolutionLabel = QLabel(self.qualityGroup)
        self.resolutionLabel.setObjectName("resolutionLabel")

        self.qualityLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.resolutionLabel)

        self.resolutionLayout = QHBoxLayout()
        self.resolutionLayout.setObjectName("resolutionLayout")
        self.widthSpinbox = QSpinBox(self.qualityGroup)
        self.widthSpinbox.setObjectName("widthSpinbox")
        self.widthSpinbox.setMinimum(320)
        self.widthSpinbox.setMaximum(7680)
        self.widthSpinbox.setValue(1920)

        self.resolutionLayout.addWidget(self.widthSpinbox)

        self.resolutionSeparator = QLabel(self.qualityGroup)
        self.resolutionSeparator.setObjectName("resolutionSeparator")

        self.resolutionLayout.addWidget(self.resolutionSeparator)

        self.heightSpinbox = QSpinBox(self.qualityGroup)
        self.heightSpinbox.setObjectName("heightSpinbox")
        self.heightSpinbox.setMinimum(240)
        self.heightSpinbox.setMaximum(4320)
        self.heightSpinbox.setValue(1080)

        self.resolutionLayout.addWidget(self.heightSpinbox)


        self.qualityLayout.setLayout(1, QFormLayout.ItemRole.FieldRole, self.resolutionLayout)

        self.fpsLabel = QLabel(self.qualityGroup)
        self.fpsLabel.setObjectName("fpsLabel")

        self.qualityLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.fpsLabel)

        self.fpsSpinbox = QSpinBox(self.qualityGroup)
        self.fpsSpinbox.setObjectName("fpsSpinbox")
        self.fpsSpinbox.setMinimum(1)
        self.fpsSpinbox.setMaximum(120)
        self.fpsSpinbox.setValue(30)

        self.qualityLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.fpsSpinbox)


        self.mainLayout.addWidget(self.qualityGroup)

        self.durationGroup = QGroupBox(VideoExportDialog)
        self.durationGroup.setObjectName("durationGroup")
        self.durationLayout = QFormLayout(self.durationGroup)
        self.durationLayout.setObjectName("durationLayout")
        self.fullDurationCheckbox = QCheckBox(self.durationGroup)
        self.fullDurationCheckbox.setObjectName("fullDurationCheckbox")
        self.fullDurationCheckbox.setChecked(True)

        self.durationLayout.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.fullDurationCheckbox)

        self.customDurationLabel = QLabel(self.durationGroup)
        self.customDurationLabel.setObjectName("customDurationLabel")

        self.durationLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.customDurationLabel)

        self.customDurationSpinbox = QSpinBox(self.durationGroup)
        self.customDurationSpinbox.setObjectName("customDurationSpinbox")
        self.customDurationSpinbox.setEnabled(False)
        self.customDurationSpinbox.setMinimum(1)
        self.customDurationSpinbox.setMaximum(3600)
        self.customDurationSpinbox.setValue(60)

        self.durationLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.customDurationSpinbox)


        self.mainLayout.addWidget(self.durationGroup)

        self.viewGroup = QGroupBox(VideoExportDialog)
        self.viewGroup.setObjectName("viewGroup")
        self.viewLayout = QFormLayout(self.viewGroup)
        self.viewLayout.setObjectName("viewLayout")
        self.layoutLabel = QLabel(self.viewGroup)
        self.layoutLabel.setObjectName("layoutLabel")

        self.viewLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.layoutLabel)

        self.layoutCombo = QComboBox(self.viewGroup)
        self.layoutCombo.addItem("")
        self.layoutCombo.addItem("")
        self.layoutCombo.addItem("")
        self.layoutCombo.setObjectName("layoutCombo")

        self.viewLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.layoutCombo)

        self.includeAllViewsCheckbox = QCheckBox(self.viewGroup)
        self.includeAllViewsCheckbox.setObjectName("includeAllViewsCheckbox")
        self.includeAllViewsCheckbox.setChecked(True)

        self.viewLayout.setWidget(1, QFormLayout.ItemRole.SpanningRole, self.includeAllViewsCheckbox)


        self.mainLayout.addWidget(self.viewGroup)

        self.verticalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mainLayout.addItem(self.verticalSpacer)

        self.progressBar = QProgressBar(VideoExportDialog)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setVisible(False)
        self.progressBar.setValue(0)

        self.mainLayout.addWidget(self.progressBar)

        self.statusLabel = QLabel(VideoExportDialog)
        self.statusLabel.setObjectName("statusLabel")
        self.statusLabel.setVisible(False)

        self.mainLayout.addWidget(self.statusLabel)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName("buttonLayout")
        self.buttonSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.buttonSpacer)

        self.cancelBtn = QPushButton(VideoExportDialog)
        self.cancelBtn.setObjectName("cancelBtn")

        self.buttonLayout.addWidget(self.cancelBtn)

        self.exportBtn = QPushButton(VideoExportDialog)
        self.exportBtn.setObjectName("exportBtn")

        self.buttonLayout.addWidget(self.exportBtn)


        self.mainLayout.addLayout(self.buttonLayout)


        self.retranslateUi(VideoExportDialog)

        self.exportBtn.setDefault(True)


        QMetaObject.connectSlotsByName(VideoExportDialog)
    # setupUi

    def retranslateUi(self, VideoExportDialog):
        VideoExportDialog.setWindowTitle(QCoreApplication.translate("VideoExportDialog", "\ud83c\udfac Exportar V\u00eddeo", None))
        self.outputGroup.setTitle(QCoreApplication.translate("VideoExportDialog", "\ud83d\udcc1 Arquivo de Sa\u00edda", None))
        self.pathLabel.setText(QCoreApplication.translate("VideoExportDialog", "Destino:", None))
        self.pathEdit.setText(QCoreApplication.translate("VideoExportDialog", "Nenhum arquivo selecionado", None))
        self.pathEdit.setStyleSheet(QCoreApplication.translate("VideoExportDialog", "color: gray; font-style: italic;", None))
        self.browseBtn.setText(QCoreApplication.translate("VideoExportDialog", "Procurar...", None))
        self.formatLabelText.setText(QCoreApplication.translate("VideoExportDialog", "Formato:", None))
        self.formatCombo.setItemText(0, QCoreApplication.translate("VideoExportDialog", "MP4 (H.264)", None))
        self.formatCombo.setItemText(1, QCoreApplication.translate("VideoExportDialog", "AVI", None))
        self.formatCombo.setItemText(2, QCoreApplication.translate("VideoExportDialog", "MOV", None))
        self.formatCombo.setItemText(3, QCoreApplication.translate("VideoExportDialog", "WebM", None))
        self.formatCombo.setItemText(4, QCoreApplication.translate("VideoExportDialog", "GIF", None))

#if QT_CONFIG(tooltip)
        self.formatCombo.setToolTip(QCoreApplication.translate("VideoExportDialog", "Formato do arquivo de v\u00eddeo", None))
#endif // QT_CONFIG(tooltip)
        self.qualityGroup.setTitle(QCoreApplication.translate("VideoExportDialog", "\ud83d\udcca Qualidade", None))
        self.qualityLabel.setText(QCoreApplication.translate("VideoExportDialog", "Preset:", None))
        self.qualityCombo.setItemText(0, QCoreApplication.translate("VideoExportDialog", "Low (720p, 15fps)", None))
        self.qualityCombo.setItemText(1, QCoreApplication.translate("VideoExportDialog", "Medium (1080p, 30fps)", None))
        self.qualityCombo.setItemText(2, QCoreApplication.translate("VideoExportDialog", "High (1080p, 60fps)", None))
        self.qualityCombo.setItemText(3, QCoreApplication.translate("VideoExportDialog", "Ultra (4K, 30fps)", None))
        self.qualityCombo.setItemText(4, QCoreApplication.translate("VideoExportDialog", "Custom", None))

#if QT_CONFIG(tooltip)
        self.qualityCombo.setToolTip(QCoreApplication.translate("VideoExportDialog", "Preset de qualidade (define resolu\u00e7\u00e3o e FPS)", None))
#endif // QT_CONFIG(tooltip)
        self.resolutionLabel.setText(QCoreApplication.translate("VideoExportDialog", "Resolu\u00e7\u00e3o:", None))
        self.widthSpinbox.setSuffix(QCoreApplication.translate("VideoExportDialog", " px", None))
#if QT_CONFIG(tooltip)
        self.widthSpinbox.setToolTip(QCoreApplication.translate("VideoExportDialog", "Largura do v\u00eddeo", None))
#endif // QT_CONFIG(tooltip)
        self.resolutionSeparator.setText(QCoreApplication.translate("VideoExportDialog", "\u00d7", None))
        self.heightSpinbox.setSuffix(QCoreApplication.translate("VideoExportDialog", " px", None))
#if QT_CONFIG(tooltip)
        self.heightSpinbox.setToolTip(QCoreApplication.translate("VideoExportDialog", "Altura do v\u00eddeo", None))
#endif // QT_CONFIG(tooltip)
        self.fpsLabel.setText(QCoreApplication.translate("VideoExportDialog", "FPS:", None))
        self.fpsSpinbox.setSuffix(QCoreApplication.translate("VideoExportDialog", " fps", None))
#if QT_CONFIG(tooltip)
        self.fpsSpinbox.setToolTip(QCoreApplication.translate("VideoExportDialog", "Quadros por segundo", None))
#endif // QT_CONFIG(tooltip)
        self.durationGroup.setTitle(QCoreApplication.translate("VideoExportDialog", "\u23f1\ufe0f Dura\u00e7\u00e3o", None))
        self.fullDurationCheckbox.setText(QCoreApplication.translate("VideoExportDialog", "Usar dura\u00e7\u00e3o completa dos dados", None))
#if QT_CONFIG(tooltip)
        self.fullDurationCheckbox.setToolTip(QCoreApplication.translate("VideoExportDialog", "Exporta toda a linha do tempo dos dados", None))
#endif // QT_CONFIG(tooltip)
        self.customDurationLabel.setText(QCoreApplication.translate("VideoExportDialog", "Dura\u00e7\u00e3o personalizada:", None))
        self.customDurationSpinbox.setSuffix(QCoreApplication.translate("VideoExportDialog", " segundos", None))
#if QT_CONFIG(tooltip)
        self.customDurationSpinbox.setToolTip(QCoreApplication.translate("VideoExportDialog", "Dura\u00e7\u00e3o do v\u00eddeo em segundos", None))
#endif // QT_CONFIG(tooltip)
        self.viewGroup.setTitle(QCoreApplication.translate("VideoExportDialog", "\ud83d\uddbc\ufe0f Layout das Views", None))
        self.layoutLabel.setText(QCoreApplication.translate("VideoExportDialog", "Layout:", None))
        self.layoutCombo.setItemText(0, QCoreApplication.translate("VideoExportDialog", "Single View (visualiza\u00e7\u00e3o \u00fanica)", None))
        self.layoutCombo.setItemText(1, QCoreApplication.translate("VideoExportDialog", "Grid (grade)", None))
        self.layoutCombo.setItemText(2, QCoreApplication.translate("VideoExportDialog", "Split (dividido)", None))

#if QT_CONFIG(tooltip)
        self.layoutCombo.setToolTip(QCoreApplication.translate("VideoExportDialog", "Modo de layout das visualiza\u00e7\u00f5es", None))
#endif // QT_CONFIG(tooltip)
        self.includeAllViewsCheckbox.setText(QCoreApplication.translate("VideoExportDialog", "Incluir todas as views vis\u00edveis", None))
#if QT_CONFIG(tooltip)
        self.includeAllViewsCheckbox.setToolTip(QCoreApplication.translate("VideoExportDialog", "Inclui todas as views ativas no v\u00eddeo", None))
#endif // QT_CONFIG(tooltip)
        self.statusLabel.setText("")
        self.cancelBtn.setText(QCoreApplication.translate("VideoExportDialog", "Cancelar", None))
        self.exportBtn.setText(QCoreApplication.translate("VideoExportDialog", "\ud83c\udfac Exportar", None))
        self.exportBtn.setStyleSheet(QCoreApplication.translate("VideoExportDialog", "font-weight: bold;", None))
    # retranslateUi

