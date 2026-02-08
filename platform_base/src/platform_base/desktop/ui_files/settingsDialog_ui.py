
################################################################################
## Form generated from reading UI file 'settingsDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFontComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class Ui_SettingsDialog:
    def setupUi(self, SettingsDialog):
        if not SettingsDialog.objectName():
            SettingsDialog.setObjectName("SettingsDialog")
        SettingsDialog.resize(700, 550)
        SettingsDialog.setMinimumSize(QSize(700, 550))
        SettingsDialog.setModal(True)
        self.mainLayout = QVBoxLayout(SettingsDialog)
        self.mainLayout.setSpacing(12)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(16, 16, 16, 16)
        self.settingsTabs = QTabWidget(SettingsDialog)
        self.settingsTabs.setObjectName("settingsTabs")
        self.appearanceTab = QWidget()
        self.appearanceTab.setObjectName("appearanceTab")
        self.appearanceTabLayout = QVBoxLayout(self.appearanceTab)
        self.appearanceTabLayout.setSpacing(16)
        self.appearanceTabLayout.setObjectName("appearanceTabLayout")
        self.themeGroup = QGroupBox(self.appearanceTab)
        self.themeGroup.setObjectName("themeGroup")
        self.themeLayout = QFormLayout(self.themeGroup)
        self.themeLayout.setObjectName("themeLayout")
        self.themeLabel = QLabel(self.themeGroup)
        self.themeLabel.setObjectName("themeLabel")

        self.themeLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.themeLabel)

        self.themeCombo = QComboBox(self.themeGroup)
        self.themeCombo.addItem("")
        self.themeCombo.addItem("")
        self.themeCombo.addItem("")
        self.themeCombo.setObjectName("themeCombo")

        self.themeLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.themeCombo)

        self.accentColorLabel = QLabel(self.themeGroup)
        self.accentColorLabel.setObjectName("accentColorLabel")

        self.themeLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.accentColorLabel)

        self.accentColorBtn = QPushButton(self.themeGroup)
        self.accentColorBtn.setObjectName("accentColorBtn")
        self.accentColorBtn.setMinimumSize(QSize(100, 30))
        self.accentColorBtn.setMaximumSize(QSize(100, 30))

        self.themeLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.accentColorBtn)


        self.appearanceTabLayout.addWidget(self.themeGroup)

        self.fontGroup = QGroupBox(self.appearanceTab)
        self.fontGroup.setObjectName("fontGroup")
        self.fontLayout = QFormLayout(self.fontGroup)
        self.fontLayout.setObjectName("fontLayout")
        self.fontFamilyLabel = QLabel(self.fontGroup)
        self.fontFamilyLabel.setObjectName("fontFamilyLabel")

        self.fontLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.fontFamilyLabel)

        self.fontCombo = QFontComboBox(self.fontGroup)
        self.fontCombo.setObjectName("fontCombo")

        self.fontLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.fontCombo)

        self.fontSizeLabel = QLabel(self.fontGroup)
        self.fontSizeLabel.setObjectName("fontSizeLabel")

        self.fontLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.fontSizeLabel)

        self.fontSizeSpin = QSpinBox(self.fontGroup)
        self.fontSizeSpin.setObjectName("fontSizeSpin")
        self.fontSizeSpin.setMinimum(8)
        self.fontSizeSpin.setMaximum(18)
        self.fontSizeSpin.setValue(10)

        self.fontLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.fontSizeSpin)


        self.appearanceTabLayout.addWidget(self.fontGroup)

        self.appearanceSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.appearanceTabLayout.addItem(self.appearanceSpacer)

        self.settingsTabs.addTab(self.appearanceTab, "")
        self.visualizationTab = QWidget()
        self.visualizationTab.setObjectName("visualizationTab")
        self.visualizationTabLayout = QVBoxLayout(self.visualizationTab)
        self.visualizationTabLayout.setSpacing(16)
        self.visualizationTabLayout.setObjectName("visualizationTabLayout")
        self.plotDefaultsGroup = QGroupBox(self.visualizationTab)
        self.plotDefaultsGroup.setObjectName("plotDefaultsGroup")
        self.plotDefaultsLayout = QVBoxLayout(self.plotDefaultsGroup)
        self.plotDefaultsLayout.setObjectName("plotDefaultsLayout")
        self.gridCheck = QCheckBox(self.plotDefaultsGroup)
        self.gridCheck.setObjectName("gridCheck")

        self.plotDefaultsLayout.addWidget(self.gridCheck)

        self.legendCheck = QCheckBox(self.plotDefaultsGroup)
        self.legendCheck.setObjectName("legendCheck")

        self.plotDefaultsLayout.addWidget(self.legendCheck)

        self.crosshairCheck = QCheckBox(self.plotDefaultsGroup)
        self.crosshairCheck.setObjectName("crosshairCheck")

        self.plotDefaultsLayout.addWidget(self.crosshairCheck)

        self.autozoomCheck = QCheckBox(self.plotDefaultsGroup)
        self.autozoomCheck.setObjectName("autozoomCheck")

        self.plotDefaultsLayout.addWidget(self.autozoomCheck)


        self.visualizationTabLayout.addWidget(self.plotDefaultsGroup)

        self.lineStyleGroup = QGroupBox(self.visualizationTab)
        self.lineStyleGroup.setObjectName("lineStyleGroup")
        self.lineStyleLayout = QFormLayout(self.lineStyleGroup)
        self.lineStyleLayout.setObjectName("lineStyleLayout")
        self.lineWidthLabel = QLabel(self.lineStyleGroup)
        self.lineWidthLabel.setObjectName("lineWidthLabel")

        self.lineStyleLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lineWidthLabel)

        self.lineWidthSpin = QDoubleSpinBox(self.lineStyleGroup)
        self.lineWidthSpin.setObjectName("lineWidthSpin")
        self.lineWidthSpin.setDecimals(1)
        self.lineWidthSpin.setMinimum(0.500000000000000)
        self.lineWidthSpin.setMaximum(5.000000000000000)
        self.lineWidthSpin.setSingleStep(0.500000000000000)
        self.lineWidthSpin.setValue(2.000000000000000)

        self.lineStyleLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineWidthSpin)

        self.markerSizeLabel = QLabel(self.lineStyleGroup)
        self.markerSizeLabel.setObjectName("markerSizeLabel")

        self.lineStyleLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.markerSizeLabel)

        self.markerSizeSpin = QSpinBox(self.lineStyleGroup)
        self.markerSizeSpin.setObjectName("markerSizeSpin")
        self.markerSizeSpin.setMinimum(1)
        self.markerSizeSpin.setMaximum(10)
        self.markerSizeSpin.setValue(3)

        self.lineStyleLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.markerSizeSpin)


        self.visualizationTabLayout.addWidget(self.lineStyleGroup)

        self.visualizationSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.visualizationTabLayout.addItem(self.visualizationSpacer)

        self.settingsTabs.addTab(self.visualizationTab, "")
        self.performanceTab = QWidget()
        self.performanceTab.setObjectName("performanceTab")
        self.performanceTabLayout = QVBoxLayout(self.performanceTab)
        self.performanceTabLayout.setSpacing(16)
        self.performanceTabLayout.setObjectName("performanceTabLayout")
        self.downsamplingGroup = QGroupBox(self.performanceTab)
        self.downsamplingGroup.setObjectName("downsamplingGroup")
        self.downsamplingLayout = QFormLayout(self.downsamplingGroup)
        self.downsamplingLayout.setObjectName("downsamplingLayout")
        self.lttbLabel = QLabel(self.downsamplingGroup)
        self.lttbLabel.setObjectName("lttbLabel")

        self.downsamplingLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lttbLabel)

        self.lttbSpin = QSpinBox(self.downsamplingGroup)
        self.lttbSpin.setObjectName("lttbSpin")
        self.lttbSpin.setMinimum(1000)
        self.lttbSpin.setMaximum(1000000)
        self.lttbSpin.setSingleStep(5000)
        self.lttbSpin.setValue(10000)

        self.downsamplingLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lttbSpin)

        self.maxPointsLabel = QLabel(self.downsamplingGroup)
        self.maxPointsLabel.setObjectName("maxPointsLabel")

        self.downsamplingLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.maxPointsLabel)

        self.maxPointsSpin = QSpinBox(self.downsamplingGroup)
        self.maxPointsSpin.setObjectName("maxPointsSpin")
        self.maxPointsSpin.setMinimum(10000)
        self.maxPointsSpin.setMaximum(10000000)
        self.maxPointsSpin.setSingleStep(10000)
        self.maxPointsSpin.setValue(100000)

        self.downsamplingLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.maxPointsSpin)


        self.performanceTabLayout.addWidget(self.downsamplingGroup)

        self.memoryGroup = QGroupBox(self.performanceTab)
        self.memoryGroup.setObjectName("memoryGroup")
        self.memoryLayout = QFormLayout(self.memoryGroup)
        self.memoryLayout.setObjectName("memoryLayout")
        self.bufferLabel = QLabel(self.memoryGroup)
        self.bufferLabel.setObjectName("bufferLabel")

        self.memoryLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.bufferLabel)

        self.bufferSpin = QSpinBox(self.memoryGroup)
        self.bufferSpin.setObjectName("bufferSpin")
        self.bufferSpin.setMinimum(128)
        self.bufferSpin.setMaximum(4096)
        self.bufferSpin.setSingleStep(128)
        self.bufferSpin.setValue(512)

        self.memoryLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.bufferSpin)


        self.performanceTabLayout.addWidget(self.memoryGroup)

        self.accelerationGroup = QGroupBox(self.performanceTab)
        self.accelerationGroup.setObjectName("accelerationGroup")
        self.accelerationLayout = QVBoxLayout(self.accelerationGroup)
        self.accelerationLayout.setObjectName("accelerationLayout")
        self.openglCheck = QCheckBox(self.accelerationGroup)
        self.openglCheck.setObjectName("openglCheck")

        self.accelerationLayout.addWidget(self.openglCheck)

        self.openglWarningLabel = QLabel(self.accelerationGroup)
        self.openglWarningLabel.setObjectName("openglWarningLabel")

        self.accelerationLayout.addWidget(self.openglWarningLabel)


        self.performanceTabLayout.addWidget(self.accelerationGroup)

        self.performanceSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.performanceTabLayout.addItem(self.performanceSpacer)

        self.settingsTabs.addTab(self.performanceTab, "")
        self.pathsTab = QWidget()
        self.pathsTab.setObjectName("pathsTab")
        self.pathsTabLayout = QVBoxLayout(self.pathsTab)
        self.pathsTabLayout.setSpacing(16)
        self.pathsTabLayout.setObjectName("pathsTabLayout")
        self.directoriesGroup = QGroupBox(self.pathsTab)
        self.directoriesGroup.setObjectName("directoriesGroup")
        self.directoriesLayout = QFormLayout(self.directoriesGroup)
        self.directoriesLayout.setObjectName("directoriesLayout")
        self.dataDirLabel = QLabel(self.directoriesGroup)
        self.dataDirLabel.setObjectName("dataDirLabel")

        self.directoriesLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.dataDirLabel)

        self.dataDirLayout = QHBoxLayout()
        self.dataDirLayout.setObjectName("dataDirLayout")
        self.dataDirEdit = QLineEdit(self.directoriesGroup)
        self.dataDirEdit.setObjectName("dataDirEdit")
        self.dataDirEdit.setReadOnly(True)

        self.dataDirLayout.addWidget(self.dataDirEdit)

        self.dataDirBtn = QPushButton(self.directoriesGroup)
        self.dataDirBtn.setObjectName("dataDirBtn")
        self.dataDirBtn.setMinimumSize(QSize(40, 0))
        self.dataDirBtn.setMaximumSize(QSize(40, 16777215))

        self.dataDirLayout.addWidget(self.dataDirBtn)


        self.directoriesLayout.setLayout(0, QFormLayout.ItemRole.FieldRole, self.dataDirLayout)

        self.exportDirLabel = QLabel(self.directoriesGroup)
        self.exportDirLabel.setObjectName("exportDirLabel")

        self.directoriesLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.exportDirLabel)

        self.exportDirLayout = QHBoxLayout()
        self.exportDirLayout.setObjectName("exportDirLayout")
        self.exportDirEdit = QLineEdit(self.directoriesGroup)
        self.exportDirEdit.setObjectName("exportDirEdit")
        self.exportDirEdit.setReadOnly(True)

        self.exportDirLayout.addWidget(self.exportDirEdit)

        self.exportDirBtn = QPushButton(self.directoriesGroup)
        self.exportDirBtn.setObjectName("exportDirBtn")
        self.exportDirBtn.setMinimumSize(QSize(40, 0))
        self.exportDirBtn.setMaximumSize(QSize(40, 16777215))

        self.exportDirLayout.addWidget(self.exportDirBtn)


        self.directoriesLayout.setLayout(1, QFormLayout.ItemRole.FieldRole, self.exportDirLayout)


        self.pathsTabLayout.addWidget(self.directoriesGroup)

        self.recentFilesGroup = QGroupBox(self.pathsTab)
        self.recentFilesGroup.setObjectName("recentFilesGroup")
        self.recentFilesLayout = QFormLayout(self.recentFilesGroup)
        self.recentFilesLayout.setObjectName("recentFilesLayout")
        self.recentMaxLabel = QLabel(self.recentFilesGroup)
        self.recentMaxLabel.setObjectName("recentMaxLabel")

        self.recentFilesLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.recentMaxLabel)

        self.recentMaxSpin = QSpinBox(self.recentFilesGroup)
        self.recentMaxSpin.setObjectName("recentMaxSpin")
        self.recentMaxSpin.setMinimum(5)
        self.recentMaxSpin.setMaximum(50)
        self.recentMaxSpin.setValue(10)

        self.recentFilesLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.recentMaxSpin)

        self.clearRecentLabel = QLabel(self.recentFilesGroup)
        self.clearRecentLabel.setObjectName("clearRecentLabel")

        self.recentFilesLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.clearRecentLabel)

        self.clearRecentBtn = QPushButton(self.recentFilesGroup)
        self.clearRecentBtn.setObjectName("clearRecentBtn")

        self.recentFilesLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.clearRecentBtn)


        self.pathsTabLayout.addWidget(self.recentFilesGroup)

        self.pathsSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.pathsTabLayout.addItem(self.pathsSpacer)

        self.settingsTabs.addTab(self.pathsTab, "")
        self.behaviorTab = QWidget()
        self.behaviorTab.setObjectName("behaviorTab")
        self.behaviorTabLayout = QVBoxLayout(self.behaviorTab)
        self.behaviorTabLayout.setSpacing(16)
        self.behaviorTabLayout.setObjectName("behaviorTabLayout")
        self.applicationGroup = QGroupBox(self.behaviorTab)
        self.applicationGroup.setObjectName("applicationGroup")
        self.applicationLayout = QVBoxLayout(self.applicationGroup)
        self.applicationLayout.setObjectName("applicationLayout")
        self.confirmExitCheck = QCheckBox(self.applicationGroup)
        self.confirmExitCheck.setObjectName("confirmExitCheck")

        self.applicationLayout.addWidget(self.confirmExitCheck)

        self.autoSaveLayoutCheck = QCheckBox(self.applicationGroup)
        self.autoSaveLayoutCheck.setObjectName("autoSaveLayoutCheck")

        self.applicationLayout.addWidget(self.autoSaveLayoutCheck)

        self.rememberSizeCheck = QCheckBox(self.applicationGroup)
        self.rememberSizeCheck.setObjectName("rememberSizeCheck")

        self.applicationLayout.addWidget(self.rememberSizeCheck)

        self.checkUpdatesCheck = QCheckBox(self.applicationGroup)
        self.checkUpdatesCheck.setObjectName("checkUpdatesCheck")

        self.applicationLayout.addWidget(self.checkUpdatesCheck)


        self.behaviorTabLayout.addWidget(self.applicationGroup)

        self.streamingGroup = QGroupBox(self.behaviorTab)
        self.streamingGroup.setObjectName("streamingGroup")
        self.streamingLayout = QFormLayout(self.streamingGroup)
        self.streamingLayout.setObjectName("streamingLayout")
        self.fpsLabel = QLabel(self.streamingGroup)
        self.fpsLabel.setObjectName("fpsLabel")

        self.streamingLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.fpsLabel)

        self.fpsSpin = QSpinBox(self.streamingGroup)
        self.fpsSpin.setObjectName("fpsSpin")
        self.fpsSpin.setMinimum(1)
        self.fpsSpin.setMaximum(60)
        self.fpsSpin.setValue(30)

        self.streamingLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.fpsSpin)

        self.windowSizeLabel = QLabel(self.streamingGroup)
        self.windowSizeLabel.setObjectName("windowSizeLabel")

        self.streamingLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.windowSizeLabel)

        self.windowSizeSpin = QSpinBox(self.streamingGroup)
        self.windowSizeSpin.setObjectName("windowSizeSpin")
        self.windowSizeSpin.setMinimum(100)
        self.windowSizeSpin.setMaximum(10000)
        self.windowSizeSpin.setSingleStep(100)
        self.windowSizeSpin.setValue(1000)

        self.streamingLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.windowSizeSpin)


        self.behaviorTabLayout.addWidget(self.streamingGroup)

        self.behaviorSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.behaviorTabLayout.addItem(self.behaviorSpacer)

        self.settingsTabs.addTab(self.behaviorTab, "")

        self.mainLayout.addWidget(self.settingsTabs)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName("buttonLayout")
        self.resetBtn = QPushButton(SettingsDialog)
        self.resetBtn.setObjectName("resetBtn")

        self.buttonLayout.addWidget(self.resetBtn)

        self.buttonSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.buttonSpacer)

        self.cancelBtn = QPushButton(SettingsDialog)
        self.cancelBtn.setObjectName("cancelBtn")

        self.buttonLayout.addWidget(self.cancelBtn)

        self.applyBtn = QPushButton(SettingsDialog)
        self.applyBtn.setObjectName("applyBtn")

        self.buttonLayout.addWidget(self.applyBtn)

        self.okBtn = QPushButton(SettingsDialog)
        self.okBtn.setObjectName("okBtn")

        self.buttonLayout.addWidget(self.okBtn)


        self.mainLayout.addLayout(self.buttonLayout)


        self.retranslateUi(SettingsDialog)
        self.cancelBtn.clicked.connect(SettingsDialog.reject)

        self.settingsTabs.setCurrentIndex(0)
        self.okBtn.setDefault(True)


        QMetaObject.connectSlotsByName(SettingsDialog)
    # setupUi

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(QCoreApplication.translate("SettingsDialog", "\u2699\ufe0f Configura\u00e7\u00f5es", None))
        self.themeGroup.setTitle(QCoreApplication.translate("SettingsDialog", "\ud83c\udf17 Tema", None))
        self.themeLabel.setText(QCoreApplication.translate("SettingsDialog", "Tema:", None))
        self.themeCombo.setItemText(0, QCoreApplication.translate("SettingsDialog", "Claro (Light)", None))
        self.themeCombo.setItemText(1, QCoreApplication.translate("SettingsDialog", "Escuro (Dark)", None))
        self.themeCombo.setItemText(2, QCoreApplication.translate("SettingsDialog", "Sistema", None))

#if QT_CONFIG(tooltip)
        self.themeCombo.setToolTip(QCoreApplication.translate("SettingsDialog", "Selecione o tema visual da aplica\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.accentColorLabel.setText(QCoreApplication.translate("SettingsDialog", "Cor de Destaque:", None))
#if QT_CONFIG(tooltip)
        self.accentColorBtn.setToolTip(QCoreApplication.translate("SettingsDialog", "Clique para escolher a cor de destaque", None))
#endif // QT_CONFIG(tooltip)
        self.accentColorBtn.setText("")
        self.fontGroup.setTitle(QCoreApplication.translate("SettingsDialog", "\ud83d\udd24 Fonte", None))
        self.fontFamilyLabel.setText(QCoreApplication.translate("SettingsDialog", "Fam\u00edlia:", None))
#if QT_CONFIG(tooltip)
        self.fontCombo.setToolTip(QCoreApplication.translate("SettingsDialog", "Fonte da interface", None))
#endif // QT_CONFIG(tooltip)
        self.fontSizeLabel.setText(QCoreApplication.translate("SettingsDialog", "Tamanho:", None))
#if QT_CONFIG(tooltip)
        self.fontSizeSpin.setToolTip(QCoreApplication.translate("SettingsDialog", "Tamanho da fonte (8-18 pt)", None))
#endif // QT_CONFIG(tooltip)
        self.fontSizeSpin.setSuffix(QCoreApplication.translate("SettingsDialog", " pt", None))
        self.settingsTabs.setTabText(self.settingsTabs.indexOf(self.appearanceTab), QCoreApplication.translate("SettingsDialog", "\ud83c\udfa8 Apar\u00eancia", None))
        self.plotDefaultsGroup.setTitle(QCoreApplication.translate("SettingsDialog", "\ud83d\udcc8 Padr\u00f5es de Gr\u00e1fico", None))
#if QT_CONFIG(tooltip)
        self.gridCheck.setToolTip(QCoreApplication.translate("SettingsDialog", "Exibir linhas de grade nos gr\u00e1ficos automaticamente", None))
#endif // QT_CONFIG(tooltip)
        self.gridCheck.setText(QCoreApplication.translate("SettingsDialog", "Mostrar grid por padr\u00e3o", None))
#if QT_CONFIG(tooltip)
        self.legendCheck.setToolTip(QCoreApplication.translate("SettingsDialog", "Exibir legenda nos gr\u00e1ficos automaticamente", None))
#endif // QT_CONFIG(tooltip)
        self.legendCheck.setText(QCoreApplication.translate("SettingsDialog", "Mostrar legenda por padr\u00e3o", None))
#if QT_CONFIG(tooltip)
        self.crosshairCheck.setToolTip(QCoreApplication.translate("SettingsDialog", "Ativar cursor em cruz com coordenadas automaticamente", None))
#endif // QT_CONFIG(tooltip)
        self.crosshairCheck.setText(QCoreApplication.translate("SettingsDialog", "Crosshair ativo por padr\u00e3o", None))
#if QT_CONFIG(tooltip)
        self.autozoomCheck.setToolTip(QCoreApplication.translate("SettingsDialog", "Ajustar automaticamente o zoom para mostrar todos os dados", None))
#endif // QT_CONFIG(tooltip)
        self.autozoomCheck.setText(QCoreApplication.translate("SettingsDialog", "Auto-ajustar zoom ao carregar", None))
        self.lineStyleGroup.setTitle(QCoreApplication.translate("SettingsDialog", "\u270f\ufe0f Estilo de Linha", None))
        self.lineWidthLabel.setText(QCoreApplication.translate("SettingsDialog", "Largura da linha:", None))
#if QT_CONFIG(tooltip)
        self.lineWidthSpin.setToolTip(QCoreApplication.translate("SettingsDialog", "Espessura das linhas nos gr\u00e1ficos", None))
#endif // QT_CONFIG(tooltip)
        self.lineWidthSpin.setSuffix(QCoreApplication.translate("SettingsDialog", " px", None))
        self.markerSizeLabel.setText(QCoreApplication.translate("SettingsDialog", "Tamanho do marcador:", None))
#if QT_CONFIG(tooltip)
        self.markerSizeSpin.setToolTip(QCoreApplication.translate("SettingsDialog", "Tamanho dos marcadores de pontos", None))
#endif // QT_CONFIG(tooltip)
        self.markerSizeSpin.setSuffix(QCoreApplication.translate("SettingsDialog", " px", None))
        self.settingsTabs.setTabText(self.settingsTabs.indexOf(self.visualizationTab), QCoreApplication.translate("SettingsDialog", "\ud83d\udcca Visualiza\u00e7\u00e3o", None))
        self.downsamplingGroup.setTitle(QCoreApplication.translate("SettingsDialog", "\ud83d\udcc9 Downsampling (LTTB)", None))
        self.lttbLabel.setText(QCoreApplication.translate("SettingsDialog", "Limite para LTTB:", None))
#if QT_CONFIG(tooltip)
        self.lttbSpin.setToolTip(QCoreApplication.translate("SettingsDialog", "N\u00famero de pontos a partir do qual o LTTB \u00e9 ativado", None))
#endif // QT_CONFIG(tooltip)
        self.lttbSpin.setSuffix(QCoreApplication.translate("SettingsDialog", " pontos", None))
        self.maxPointsLabel.setText(QCoreApplication.translate("SettingsDialog", "M\u00e1x. pontos render:", None))
#if QT_CONFIG(tooltip)
        self.maxPointsSpin.setToolTip(QCoreApplication.translate("SettingsDialog", "M\u00e1ximo de pontos renderizados por s\u00e9rie", None))
#endif // QT_CONFIG(tooltip)
        self.maxPointsSpin.setSuffix(QCoreApplication.translate("SettingsDialog", " pontos", None))
        self.memoryGroup.setTitle(QCoreApplication.translate("SettingsDialog", "\ud83d\udcbe Mem\u00f3ria", None))
        self.bufferLabel.setText(QCoreApplication.translate("SettingsDialog", "Buffer de dados:", None))
#if QT_CONFIG(tooltip)
        self.bufferSpin.setToolTip(QCoreApplication.translate("SettingsDialog", "Tamanho do buffer de dados em mem\u00f3ria", None))
#endif // QT_CONFIG(tooltip)
        self.bufferSpin.setSuffix(QCoreApplication.translate("SettingsDialog", " MB", None))
        self.accelerationGroup.setTitle(QCoreApplication.translate("SettingsDialog", "\ud83d\ude80 Acelera\u00e7\u00e3o", None))
#if QT_CONFIG(tooltip)
        self.openglCheck.setToolTip(QCoreApplication.translate("SettingsDialog", "Habilitar renderiza\u00e7\u00e3o por GPU (pode melhorar performance)", None))
#endif // QT_CONFIG(tooltip)
        self.openglCheck.setText(QCoreApplication.translate("SettingsDialog", "Usar acelera\u00e7\u00e3o OpenGL (experimental)", None))
        self.openglWarningLabel.setText(QCoreApplication.translate("SettingsDialog", "\u26a0\ufe0f OpenGL pode causar instabilidade em alguns sistemas", None))
        self.openglWarningLabel.setStyleSheet(QCoreApplication.translate("SettingsDialog", "color: #fd7e14; font-size: 11px;", None))
        self.settingsTabs.setTabText(self.settingsTabs.indexOf(self.performanceTab), QCoreApplication.translate("SettingsDialog", "\u26a1 Performance", None))
        self.directoriesGroup.setTitle(QCoreApplication.translate("SettingsDialog", "\ud83d\udcc2 Diret\u00f3rios Padr\u00e3o", None))
        self.dataDirLabel.setText(QCoreApplication.translate("SettingsDialog", "Dados:", None))
        self.dataDirEdit.setPlaceholderText(QCoreApplication.translate("SettingsDialog", "Diret\u00f3rio padr\u00e3o para abrir arquivos", None))
        self.dataDirBtn.setText(QCoreApplication.translate("SettingsDialog", "\ud83d\udcc1", None))
        self.exportDirLabel.setText(QCoreApplication.translate("SettingsDialog", "Exporta\u00e7\u00e3o:", None))
        self.exportDirEdit.setPlaceholderText(QCoreApplication.translate("SettingsDialog", "Diret\u00f3rio padr\u00e3o para exportar arquivos", None))
        self.exportDirBtn.setText(QCoreApplication.translate("SettingsDialog", "\ud83d\udcc1", None))
        self.recentFilesGroup.setTitle(QCoreApplication.translate("SettingsDialog", "\ud83d\udccb Arquivos Recentes", None))
        self.recentMaxLabel.setText(QCoreApplication.translate("SettingsDialog", "M\u00e1ximo de recentes:", None))
#if QT_CONFIG(tooltip)
        self.recentMaxSpin.setToolTip(QCoreApplication.translate("SettingsDialog", "N\u00famero m\u00e1ximo de arquivos recentes a lembrar", None))
#endif // QT_CONFIG(tooltip)
        self.clearRecentLabel.setText("")
        self.clearRecentBtn.setText(QCoreApplication.translate("SettingsDialog", "\ud83d\uddd1\ufe0f Limpar Recentes", None))
        self.settingsTabs.setTabText(self.settingsTabs.indexOf(self.pathsTab), QCoreApplication.translate("SettingsDialog", "\ud83d\udcc1 Caminhos", None))
        self.applicationGroup.setTitle(QCoreApplication.translate("SettingsDialog", "\ud83d\udda5\ufe0f Aplica\u00e7\u00e3o", None))
#if QT_CONFIG(tooltip)
        self.confirmExitCheck.setToolTip(QCoreApplication.translate("SettingsDialog", "Exibir confirma\u00e7\u00e3o ao fechar a aplica\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.confirmExitCheck.setText(QCoreApplication.translate("SettingsDialog", "Confirmar antes de sair", None))
#if QT_CONFIG(tooltip)
        self.autoSaveLayoutCheck.setToolTip(QCoreApplication.translate("SettingsDialog", "Restaurar posi\u00e7\u00e3o e tamanho dos pain\u00e9is ao reabrir", None))
#endif // QT_CONFIG(tooltip)
        self.autoSaveLayoutCheck.setText(QCoreApplication.translate("SettingsDialog", "Salvar layout automaticamente", None))
#if QT_CONFIG(tooltip)
        self.rememberSizeCheck.setToolTip(QCoreApplication.translate("SettingsDialog", "Restaurar tamanho da janela ao reabrir", None))
#endif // QT_CONFIG(tooltip)
        self.rememberSizeCheck.setText(QCoreApplication.translate("SettingsDialog", "Lembrar tamanho da janela", None))
#if QT_CONFIG(tooltip)
        self.checkUpdatesCheck.setToolTip(QCoreApplication.translate("SettingsDialog", "Verificar novas vers\u00f5es automaticamente", None))
#endif // QT_CONFIG(tooltip)
        self.checkUpdatesCheck.setText(QCoreApplication.translate("SettingsDialog", "Verificar atualiza\u00e7\u00f5es ao iniciar", None))
        self.streamingGroup.setTitle(QCoreApplication.translate("SettingsDialog", "\u25b6\ufe0f Streaming", None))
        self.fpsLabel.setText(QCoreApplication.translate("SettingsDialog", "FPS padr\u00e3o:", None))
#if QT_CONFIG(tooltip)
        self.fpsSpin.setToolTip(QCoreApplication.translate("SettingsDialog", "Taxa de quadros padr\u00e3o para streaming", None))
#endif // QT_CONFIG(tooltip)
        self.fpsSpin.setSuffix(QCoreApplication.translate("SettingsDialog", " fps", None))
        self.windowSizeLabel.setText(QCoreApplication.translate("SettingsDialog", "Janela padr\u00e3o:", None))
#if QT_CONFIG(tooltip)
        self.windowSizeSpin.setToolTip(QCoreApplication.translate("SettingsDialog", "Janela de visualiza\u00e7\u00e3o padr\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.windowSizeSpin.setSuffix(QCoreApplication.translate("SettingsDialog", " pontos", None))
        self.settingsTabs.setTabText(self.settingsTabs.indexOf(self.behaviorTab), QCoreApplication.translate("SettingsDialog", "\ud83d\udd27 Comportamento", None))
        self.resetBtn.setText(QCoreApplication.translate("SettingsDialog", "\ud83d\udd04 Restaurar Padr\u00f5es", None))
#if QT_CONFIG(tooltip)
        self.resetBtn.setToolTip(QCoreApplication.translate("SettingsDialog", "Restaurar todas as configura\u00e7\u00f5es para valores padr\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.cancelBtn.setText(QCoreApplication.translate("SettingsDialog", "\u274c Cancelar", None))
        self.applyBtn.setText(QCoreApplication.translate("SettingsDialog", "\u2713 Aplicar", None))
        self.okBtn.setText(QCoreApplication.translate("SettingsDialog", "\u2713 OK", None))
    # retranslateUi

