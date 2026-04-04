# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settingsDialog.ui'
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
    QDoubleSpinBox, QFontComboBox, QFormLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QTabWidget,
    QVBoxLayout, QWidget)

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        if not SettingsDialog.objectName():
            SettingsDialog.setObjectName(u"SettingsDialog")
        SettingsDialog.resize(700, 550)
        SettingsDialog.setMinimumSize(QSize(700, 550))
        SettingsDialog.setModal(True)
        self.mainLayout = QVBoxLayout(SettingsDialog)
        self.mainLayout.setSpacing(12)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(16, 16, 16, 16)
        self.settingsTabs = QTabWidget(SettingsDialog)
        self.settingsTabs.setObjectName(u"settingsTabs")
        self.appearanceTab = QWidget()
        self.appearanceTab.setObjectName(u"appearanceTab")
        self.appearanceTabLayout = QVBoxLayout(self.appearanceTab)
        self.appearanceTabLayout.setSpacing(16)
        self.appearanceTabLayout.setObjectName(u"appearanceTabLayout")
        self.themeGroup = QGroupBox(self.appearanceTab)
        self.themeGroup.setObjectName(u"themeGroup")
        self.themeLayout = QFormLayout(self.themeGroup)
        self.themeLayout.setObjectName(u"themeLayout")
        self.themeLabel = QLabel(self.themeGroup)
        self.themeLabel.setObjectName(u"themeLabel")

        self.themeLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.themeLabel)

        self.themeCombo = QComboBox(self.themeGroup)
        self.themeCombo.addItem("")
        self.themeCombo.addItem("")
        self.themeCombo.addItem("")
        self.themeCombo.setObjectName(u"themeCombo")

        self.themeLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.themeCombo)

        self.accentColorLabel = QLabel(self.themeGroup)
        self.accentColorLabel.setObjectName(u"accentColorLabel")

        self.themeLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.accentColorLabel)

        self.accentColorBtn = QPushButton(self.themeGroup)
        self.accentColorBtn.setObjectName(u"accentColorBtn")
        self.accentColorBtn.setMinimumSize(QSize(100, 30))
        self.accentColorBtn.setMaximumSize(QSize(100, 30))

        self.themeLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.accentColorBtn)


        self.appearanceTabLayout.addWidget(self.themeGroup)

        self.fontGroup = QGroupBox(self.appearanceTab)
        self.fontGroup.setObjectName(u"fontGroup")
        self.fontLayout = QFormLayout(self.fontGroup)
        self.fontLayout.setObjectName(u"fontLayout")
        self.fontFamilyLabel = QLabel(self.fontGroup)
        self.fontFamilyLabel.setObjectName(u"fontFamilyLabel")

        self.fontLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.fontFamilyLabel)

        self.fontCombo = QFontComboBox(self.fontGroup)
        self.fontCombo.setObjectName(u"fontCombo")

        self.fontLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.fontCombo)

        self.fontSizeLabel = QLabel(self.fontGroup)
        self.fontSizeLabel.setObjectName(u"fontSizeLabel")

        self.fontLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.fontSizeLabel)

        self.fontSizeSpin = QSpinBox(self.fontGroup)
        self.fontSizeSpin.setObjectName(u"fontSizeSpin")
        self.fontSizeSpin.setMinimum(8)
        self.fontSizeSpin.setMaximum(18)
        self.fontSizeSpin.setValue(10)

        self.fontLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.fontSizeSpin)


        self.appearanceTabLayout.addWidget(self.fontGroup)

        self.appearanceSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.appearanceTabLayout.addItem(self.appearanceSpacer)

        self.settingsTabs.addTab(self.appearanceTab, "")
        self.visualizationTab = QWidget()
        self.visualizationTab.setObjectName(u"visualizationTab")
        self.visualizationTabLayout = QVBoxLayout(self.visualizationTab)
        self.visualizationTabLayout.setSpacing(16)
        self.visualizationTabLayout.setObjectName(u"visualizationTabLayout")
        self.plotDefaultsGroup = QGroupBox(self.visualizationTab)
        self.plotDefaultsGroup.setObjectName(u"plotDefaultsGroup")
        self.plotDefaultsLayout = QVBoxLayout(self.plotDefaultsGroup)
        self.plotDefaultsLayout.setObjectName(u"plotDefaultsLayout")
        self.gridCheck = QCheckBox(self.plotDefaultsGroup)
        self.gridCheck.setObjectName(u"gridCheck")

        self.plotDefaultsLayout.addWidget(self.gridCheck)

        self.legendCheck = QCheckBox(self.plotDefaultsGroup)
        self.legendCheck.setObjectName(u"legendCheck")

        self.plotDefaultsLayout.addWidget(self.legendCheck)

        self.crosshairCheck = QCheckBox(self.plotDefaultsGroup)
        self.crosshairCheck.setObjectName(u"crosshairCheck")

        self.plotDefaultsLayout.addWidget(self.crosshairCheck)

        self.autozoomCheck = QCheckBox(self.plotDefaultsGroup)
        self.autozoomCheck.setObjectName(u"autozoomCheck")

        self.plotDefaultsLayout.addWidget(self.autozoomCheck)


        self.visualizationTabLayout.addWidget(self.plotDefaultsGroup)

        self.lineStyleGroup = QGroupBox(self.visualizationTab)
        self.lineStyleGroup.setObjectName(u"lineStyleGroup")
        self.lineStyleLayout = QFormLayout(self.lineStyleGroup)
        self.lineStyleLayout.setObjectName(u"lineStyleLayout")
        self.lineWidthLabel = QLabel(self.lineStyleGroup)
        self.lineWidthLabel.setObjectName(u"lineWidthLabel")

        self.lineStyleLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lineWidthLabel)

        self.lineWidthSpin = QDoubleSpinBox(self.lineStyleGroup)
        self.lineWidthSpin.setObjectName(u"lineWidthSpin")
        self.lineWidthSpin.setDecimals(1)
        self.lineWidthSpin.setMinimum(0.500000000000000)
        self.lineWidthSpin.setMaximum(5.000000000000000)
        self.lineWidthSpin.setSingleStep(0.500000000000000)
        self.lineWidthSpin.setValue(2.000000000000000)

        self.lineStyleLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineWidthSpin)

        self.markerSizeLabel = QLabel(self.lineStyleGroup)
        self.markerSizeLabel.setObjectName(u"markerSizeLabel")

        self.lineStyleLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.markerSizeLabel)

        self.markerSizeSpin = QSpinBox(self.lineStyleGroup)
        self.markerSizeSpin.setObjectName(u"markerSizeSpin")
        self.markerSizeSpin.setMinimum(1)
        self.markerSizeSpin.setMaximum(10)
        self.markerSizeSpin.setValue(3)

        self.lineStyleLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.markerSizeSpin)


        self.visualizationTabLayout.addWidget(self.lineStyleGroup)

        self.visualizationSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.visualizationTabLayout.addItem(self.visualizationSpacer)

        self.settingsTabs.addTab(self.visualizationTab, "")
        self.performanceTab = QWidget()
        self.performanceTab.setObjectName(u"performanceTab")
        self.performanceTabLayout = QVBoxLayout(self.performanceTab)
        self.performanceTabLayout.setSpacing(16)
        self.performanceTabLayout.setObjectName(u"performanceTabLayout")
        self.downsamplingGroup = QGroupBox(self.performanceTab)
        self.downsamplingGroup.setObjectName(u"downsamplingGroup")
        self.downsamplingLayout = QFormLayout(self.downsamplingGroup)
        self.downsamplingLayout.setObjectName(u"downsamplingLayout")
        self.lttbLabel = QLabel(self.downsamplingGroup)
        self.lttbLabel.setObjectName(u"lttbLabel")

        self.downsamplingLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lttbLabel)

        self.lttbSpin = QSpinBox(self.downsamplingGroup)
        self.lttbSpin.setObjectName(u"lttbSpin")
        self.lttbSpin.setMinimum(1000)
        self.lttbSpin.setMaximum(1000000)
        self.lttbSpin.setSingleStep(5000)
        self.lttbSpin.setValue(10000)

        self.downsamplingLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lttbSpin)

        self.maxPointsLabel = QLabel(self.downsamplingGroup)
        self.maxPointsLabel.setObjectName(u"maxPointsLabel")

        self.downsamplingLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.maxPointsLabel)

        self.maxPointsSpin = QSpinBox(self.downsamplingGroup)
        self.maxPointsSpin.setObjectName(u"maxPointsSpin")
        self.maxPointsSpin.setMinimum(10000)
        self.maxPointsSpin.setMaximum(10000000)
        self.maxPointsSpin.setSingleStep(10000)
        self.maxPointsSpin.setValue(100000)

        self.downsamplingLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.maxPointsSpin)


        self.performanceTabLayout.addWidget(self.downsamplingGroup)

        self.memoryGroup = QGroupBox(self.performanceTab)
        self.memoryGroup.setObjectName(u"memoryGroup")
        self.memoryLayout = QFormLayout(self.memoryGroup)
        self.memoryLayout.setObjectName(u"memoryLayout")
        self.bufferLabel = QLabel(self.memoryGroup)
        self.bufferLabel.setObjectName(u"bufferLabel")

        self.memoryLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.bufferLabel)

        self.bufferSpin = QSpinBox(self.memoryGroup)
        self.bufferSpin.setObjectName(u"bufferSpin")
        self.bufferSpin.setMinimum(128)
        self.bufferSpin.setMaximum(4096)
        self.bufferSpin.setSingleStep(128)
        self.bufferSpin.setValue(512)

        self.memoryLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.bufferSpin)


        self.performanceTabLayout.addWidget(self.memoryGroup)

        self.accelerationGroup = QGroupBox(self.performanceTab)
        self.accelerationGroup.setObjectName(u"accelerationGroup")
        self.accelerationLayout = QVBoxLayout(self.accelerationGroup)
        self.accelerationLayout.setObjectName(u"accelerationLayout")
        self.openglCheck = QCheckBox(self.accelerationGroup)
        self.openglCheck.setObjectName(u"openglCheck")

        self.accelerationLayout.addWidget(self.openglCheck)

        self.openglWarningLabel = QLabel(self.accelerationGroup)
        self.openglWarningLabel.setObjectName(u"openglWarningLabel")

        self.accelerationLayout.addWidget(self.openglWarningLabel)


        self.performanceTabLayout.addWidget(self.accelerationGroup)

        self.performanceSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.performanceTabLayout.addItem(self.performanceSpacer)

        self.settingsTabs.addTab(self.performanceTab, "")
        self.pathsTab = QWidget()
        self.pathsTab.setObjectName(u"pathsTab")
        self.pathsTabLayout = QVBoxLayout(self.pathsTab)
        self.pathsTabLayout.setSpacing(16)
        self.pathsTabLayout.setObjectName(u"pathsTabLayout")
        self.directoriesGroup = QGroupBox(self.pathsTab)
        self.directoriesGroup.setObjectName(u"directoriesGroup")
        self.directoriesLayout = QFormLayout(self.directoriesGroup)
        self.directoriesLayout.setObjectName(u"directoriesLayout")
        self.dataDirLabel = QLabel(self.directoriesGroup)
        self.dataDirLabel.setObjectName(u"dataDirLabel")

        self.directoriesLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.dataDirLabel)

        self.dataDirLayout = QHBoxLayout()
        self.dataDirLayout.setObjectName(u"dataDirLayout")
        self.dataDirEdit = QLineEdit(self.directoriesGroup)
        self.dataDirEdit.setObjectName(u"dataDirEdit")
        self.dataDirEdit.setReadOnly(True)

        self.dataDirLayout.addWidget(self.dataDirEdit)

        self.dataDirBtn = QPushButton(self.directoriesGroup)
        self.dataDirBtn.setObjectName(u"dataDirBtn")
        self.dataDirBtn.setMinimumSize(QSize(40, 0))
        self.dataDirBtn.setMaximumSize(QSize(40, 16777215))

        self.dataDirLayout.addWidget(self.dataDirBtn)


        self.directoriesLayout.setLayout(0, QFormLayout.ItemRole.FieldRole, self.dataDirLayout)

        self.exportDirLabel = QLabel(self.directoriesGroup)
        self.exportDirLabel.setObjectName(u"exportDirLabel")

        self.directoriesLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.exportDirLabel)

        self.exportDirLayout = QHBoxLayout()
        self.exportDirLayout.setObjectName(u"exportDirLayout")
        self.exportDirEdit = QLineEdit(self.directoriesGroup)
        self.exportDirEdit.setObjectName(u"exportDirEdit")
        self.exportDirEdit.setReadOnly(True)

        self.exportDirLayout.addWidget(self.exportDirEdit)

        self.exportDirBtn = QPushButton(self.directoriesGroup)
        self.exportDirBtn.setObjectName(u"exportDirBtn")
        self.exportDirBtn.setMinimumSize(QSize(40, 0))
        self.exportDirBtn.setMaximumSize(QSize(40, 16777215))

        self.exportDirLayout.addWidget(self.exportDirBtn)


        self.directoriesLayout.setLayout(1, QFormLayout.ItemRole.FieldRole, self.exportDirLayout)


        self.pathsTabLayout.addWidget(self.directoriesGroup)

        self.recentFilesGroup = QGroupBox(self.pathsTab)
        self.recentFilesGroup.setObjectName(u"recentFilesGroup")
        self.recentFilesLayout = QFormLayout(self.recentFilesGroup)
        self.recentFilesLayout.setObjectName(u"recentFilesLayout")
        self.recentMaxLabel = QLabel(self.recentFilesGroup)
        self.recentMaxLabel.setObjectName(u"recentMaxLabel")

        self.recentFilesLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.recentMaxLabel)

        self.recentMaxSpin = QSpinBox(self.recentFilesGroup)
        self.recentMaxSpin.setObjectName(u"recentMaxSpin")
        self.recentMaxSpin.setMinimum(5)
        self.recentMaxSpin.setMaximum(50)
        self.recentMaxSpin.setValue(10)

        self.recentFilesLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.recentMaxSpin)

        self.clearRecentLabel = QLabel(self.recentFilesGroup)
        self.clearRecentLabel.setObjectName(u"clearRecentLabel")

        self.recentFilesLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.clearRecentLabel)

        self.clearRecentBtn = QPushButton(self.recentFilesGroup)
        self.clearRecentBtn.setObjectName(u"clearRecentBtn")

        self.recentFilesLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.clearRecentBtn)


        self.pathsTabLayout.addWidget(self.recentFilesGroup)

        self.pathsSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.pathsTabLayout.addItem(self.pathsSpacer)

        self.settingsTabs.addTab(self.pathsTab, "")
        self.behaviorTab = QWidget()
        self.behaviorTab.setObjectName(u"behaviorTab")
        self.behaviorTabLayout = QVBoxLayout(self.behaviorTab)
        self.behaviorTabLayout.setSpacing(16)
        self.behaviorTabLayout.setObjectName(u"behaviorTabLayout")
        self.applicationGroup = QGroupBox(self.behaviorTab)
        self.applicationGroup.setObjectName(u"applicationGroup")
        self.applicationLayout = QVBoxLayout(self.applicationGroup)
        self.applicationLayout.setObjectName(u"applicationLayout")
        self.confirmExitCheck = QCheckBox(self.applicationGroup)
        self.confirmExitCheck.setObjectName(u"confirmExitCheck")

        self.applicationLayout.addWidget(self.confirmExitCheck)

        self.autoSaveLayoutCheck = QCheckBox(self.applicationGroup)
        self.autoSaveLayoutCheck.setObjectName(u"autoSaveLayoutCheck")

        self.applicationLayout.addWidget(self.autoSaveLayoutCheck)

        self.rememberSizeCheck = QCheckBox(self.applicationGroup)
        self.rememberSizeCheck.setObjectName(u"rememberSizeCheck")

        self.applicationLayout.addWidget(self.rememberSizeCheck)

        self.checkUpdatesCheck = QCheckBox(self.applicationGroup)
        self.checkUpdatesCheck.setObjectName(u"checkUpdatesCheck")

        self.applicationLayout.addWidget(self.checkUpdatesCheck)


        self.behaviorTabLayout.addWidget(self.applicationGroup)

        self.streamingGroup = QGroupBox(self.behaviorTab)
        self.streamingGroup.setObjectName(u"streamingGroup")
        self.streamingLayout = QFormLayout(self.streamingGroup)
        self.streamingLayout.setObjectName(u"streamingLayout")
        self.fpsLabel = QLabel(self.streamingGroup)
        self.fpsLabel.setObjectName(u"fpsLabel")

        self.streamingLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.fpsLabel)

        self.fpsSpin = QSpinBox(self.streamingGroup)
        self.fpsSpin.setObjectName(u"fpsSpin")
        self.fpsSpin.setMinimum(1)
        self.fpsSpin.setMaximum(60)
        self.fpsSpin.setValue(30)

        self.streamingLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.fpsSpin)

        self.windowSizeLabel = QLabel(self.streamingGroup)
        self.windowSizeLabel.setObjectName(u"windowSizeLabel")

        self.streamingLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.windowSizeLabel)

        self.windowSizeSpin = QSpinBox(self.streamingGroup)
        self.windowSizeSpin.setObjectName(u"windowSizeSpin")
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
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.resetBtn = QPushButton(SettingsDialog)
        self.resetBtn.setObjectName(u"resetBtn")

        self.buttonLayout.addWidget(self.resetBtn)

        self.buttonSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.buttonSpacer)

        self.cancelBtn = QPushButton(SettingsDialog)
        self.cancelBtn.setObjectName(u"cancelBtn")

        self.buttonLayout.addWidget(self.cancelBtn)

        self.applyBtn = QPushButton(SettingsDialog)
        self.applyBtn.setObjectName(u"applyBtn")

        self.buttonLayout.addWidget(self.applyBtn)

        self.okBtn = QPushButton(SettingsDialog)
        self.okBtn.setObjectName(u"okBtn")

        self.buttonLayout.addWidget(self.okBtn)


        self.mainLayout.addLayout(self.buttonLayout)


        self.retranslateUi(SettingsDialog)
        self.cancelBtn.clicked.connect(SettingsDialog.reject)

        self.settingsTabs.setCurrentIndex(0)
        self.okBtn.setDefault(True)


        QMetaObject.connectSlotsByName(SettingsDialog)
    # setupUi

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(QCoreApplication.translate("SettingsDialog", u"\u2699\ufe0f Configura\u00e7\u00f5es", None))
        self.themeGroup.setTitle(QCoreApplication.translate("SettingsDialog", u"\ud83c\udf17 Tema", None))
        self.themeLabel.setText(QCoreApplication.translate("SettingsDialog", u"Tema:", None))
        self.themeCombo.setItemText(0, QCoreApplication.translate("SettingsDialog", u"Claro (Light)", None))
        self.themeCombo.setItemText(1, QCoreApplication.translate("SettingsDialog", u"Escuro (Dark)", None))
        self.themeCombo.setItemText(2, QCoreApplication.translate("SettingsDialog", u"Sistema", None))

#if QT_CONFIG(tooltip)
        self.themeCombo.setToolTip(QCoreApplication.translate("SettingsDialog", u"Selecione o tema visual da aplica\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.accentColorLabel.setText(QCoreApplication.translate("SettingsDialog", u"Cor de Destaque:", None))
#if QT_CONFIG(tooltip)
        self.accentColorBtn.setToolTip(QCoreApplication.translate("SettingsDialog", u"Clique para escolher a cor de destaque", None))
#endif // QT_CONFIG(tooltip)
        self.accentColorBtn.setText("")
        self.fontGroup.setTitle(QCoreApplication.translate("SettingsDialog", u"\ud83d\udd24 Fonte", None))
        self.fontFamilyLabel.setText(QCoreApplication.translate("SettingsDialog", u"Fam\u00edlia:", None))
#if QT_CONFIG(tooltip)
        self.fontCombo.setToolTip(QCoreApplication.translate("SettingsDialog", u"Fonte da interface", None))
#endif // QT_CONFIG(tooltip)
        self.fontSizeLabel.setText(QCoreApplication.translate("SettingsDialog", u"Tamanho:", None))
#if QT_CONFIG(tooltip)
        self.fontSizeSpin.setToolTip(QCoreApplication.translate("SettingsDialog", u"Tamanho da fonte (8-18 pt)", None))
#endif // QT_CONFIG(tooltip)
        self.fontSizeSpin.setSuffix(QCoreApplication.translate("SettingsDialog", u" pt", None))
        self.settingsTabs.setTabText(self.settingsTabs.indexOf(self.appearanceTab), QCoreApplication.translate("SettingsDialog", u"\ud83c\udfa8 Apar\u00eancia", None))
        self.plotDefaultsGroup.setTitle(QCoreApplication.translate("SettingsDialog", u"\ud83d\udcc8 Padr\u00f5es de Gr\u00e1fico", None))
#if QT_CONFIG(tooltip)
        self.gridCheck.setToolTip(QCoreApplication.translate("SettingsDialog", u"Exibir linhas de grade nos gr\u00e1ficos automaticamente", None))
#endif // QT_CONFIG(tooltip)
        self.gridCheck.setText(QCoreApplication.translate("SettingsDialog", u"Mostrar grid por padr\u00e3o", None))
#if QT_CONFIG(tooltip)
        self.legendCheck.setToolTip(QCoreApplication.translate("SettingsDialog", u"Exibir legenda nos gr\u00e1ficos automaticamente", None))
#endif // QT_CONFIG(tooltip)
        self.legendCheck.setText(QCoreApplication.translate("SettingsDialog", u"Mostrar legenda por padr\u00e3o", None))
#if QT_CONFIG(tooltip)
        self.crosshairCheck.setToolTip(QCoreApplication.translate("SettingsDialog", u"Ativar cursor em cruz com coordenadas automaticamente", None))
#endif // QT_CONFIG(tooltip)
        self.crosshairCheck.setText(QCoreApplication.translate("SettingsDialog", u"Crosshair ativo por padr\u00e3o", None))
#if QT_CONFIG(tooltip)
        self.autozoomCheck.setToolTip(QCoreApplication.translate("SettingsDialog", u"Ajustar automaticamente o zoom para mostrar todos os dados", None))
#endif // QT_CONFIG(tooltip)
        self.autozoomCheck.setText(QCoreApplication.translate("SettingsDialog", u"Auto-ajustar zoom ao carregar", None))
        self.lineStyleGroup.setTitle(QCoreApplication.translate("SettingsDialog", u"\u270f\ufe0f Estilo de Linha", None))
        self.lineWidthLabel.setText(QCoreApplication.translate("SettingsDialog", u"Largura da linha:", None))
#if QT_CONFIG(tooltip)
        self.lineWidthSpin.setToolTip(QCoreApplication.translate("SettingsDialog", u"Espessura das linhas nos gr\u00e1ficos", None))
#endif // QT_CONFIG(tooltip)
        self.lineWidthSpin.setSuffix(QCoreApplication.translate("SettingsDialog", u" px", None))
        self.markerSizeLabel.setText(QCoreApplication.translate("SettingsDialog", u"Tamanho do marcador:", None))
#if QT_CONFIG(tooltip)
        self.markerSizeSpin.setToolTip(QCoreApplication.translate("SettingsDialog", u"Tamanho dos marcadores de pontos", None))
#endif // QT_CONFIG(tooltip)
        self.markerSizeSpin.setSuffix(QCoreApplication.translate("SettingsDialog", u" px", None))
        self.settingsTabs.setTabText(self.settingsTabs.indexOf(self.visualizationTab), QCoreApplication.translate("SettingsDialog", u"\ud83d\udcca Visualiza\u00e7\u00e3o", None))
        self.downsamplingGroup.setTitle(QCoreApplication.translate("SettingsDialog", u"\ud83d\udcc9 Downsampling (LTTB)", None))
        self.lttbLabel.setText(QCoreApplication.translate("SettingsDialog", u"Limite para LTTB:", None))
#if QT_CONFIG(tooltip)
        self.lttbSpin.setToolTip(QCoreApplication.translate("SettingsDialog", u"N\u00famero de pontos a partir do qual o LTTB \u00e9 ativado", None))
#endif // QT_CONFIG(tooltip)
        self.lttbSpin.setSuffix(QCoreApplication.translate("SettingsDialog", u" pontos", None))
        self.maxPointsLabel.setText(QCoreApplication.translate("SettingsDialog", u"M\u00e1x. pontos render:", None))
#if QT_CONFIG(tooltip)
        self.maxPointsSpin.setToolTip(QCoreApplication.translate("SettingsDialog", u"M\u00e1ximo de pontos renderizados por s\u00e9rie", None))
#endif // QT_CONFIG(tooltip)
        self.maxPointsSpin.setSuffix(QCoreApplication.translate("SettingsDialog", u" pontos", None))
        self.memoryGroup.setTitle(QCoreApplication.translate("SettingsDialog", u"\ud83d\udcbe Mem\u00f3ria", None))
        self.bufferLabel.setText(QCoreApplication.translate("SettingsDialog", u"Buffer de dados:", None))
#if QT_CONFIG(tooltip)
        self.bufferSpin.setToolTip(QCoreApplication.translate("SettingsDialog", u"Tamanho do buffer de dados em mem\u00f3ria", None))
#endif // QT_CONFIG(tooltip)
        self.bufferSpin.setSuffix(QCoreApplication.translate("SettingsDialog", u" MB", None))
        self.accelerationGroup.setTitle(QCoreApplication.translate("SettingsDialog", u"\ud83d\ude80 Acelera\u00e7\u00e3o", None))
#if QT_CONFIG(tooltip)
        self.openglCheck.setToolTip(QCoreApplication.translate("SettingsDialog", u"Habilitar renderiza\u00e7\u00e3o por GPU (pode melhorar performance)", None))
#endif // QT_CONFIG(tooltip)
        self.openglCheck.setText(QCoreApplication.translate("SettingsDialog", u"Usar acelera\u00e7\u00e3o OpenGL (experimental)", None))
        self.openglWarningLabel.setText(QCoreApplication.translate("SettingsDialog", u"\u26a0\ufe0f OpenGL pode causar instabilidade em alguns sistemas", None))
        self.openglWarningLabel.setStyleSheet(QCoreApplication.translate("SettingsDialog", u"color: #fd7e14; font-size: 11px;", None))
        self.settingsTabs.setTabText(self.settingsTabs.indexOf(self.performanceTab), QCoreApplication.translate("SettingsDialog", u"\u26a1 Performance", None))
        self.directoriesGroup.setTitle(QCoreApplication.translate("SettingsDialog", u"\ud83d\udcc2 Diret\u00f3rios Padr\u00e3o", None))
        self.dataDirLabel.setText(QCoreApplication.translate("SettingsDialog", u"Dados:", None))
        self.dataDirEdit.setPlaceholderText(QCoreApplication.translate("SettingsDialog", u"Diret\u00f3rio padr\u00e3o para abrir arquivos", None))
        self.dataDirBtn.setText(QCoreApplication.translate("SettingsDialog", u"\ud83d\udcc1", None))
        self.exportDirLabel.setText(QCoreApplication.translate("SettingsDialog", u"Exporta\u00e7\u00e3o:", None))
        self.exportDirEdit.setPlaceholderText(QCoreApplication.translate("SettingsDialog", u"Diret\u00f3rio padr\u00e3o para exportar arquivos", None))
        self.exportDirBtn.setText(QCoreApplication.translate("SettingsDialog", u"\ud83d\udcc1", None))
        self.recentFilesGroup.setTitle(QCoreApplication.translate("SettingsDialog", u"\ud83d\udccb Arquivos Recentes", None))
        self.recentMaxLabel.setText(QCoreApplication.translate("SettingsDialog", u"M\u00e1ximo de recentes:", None))
#if QT_CONFIG(tooltip)
        self.recentMaxSpin.setToolTip(QCoreApplication.translate("SettingsDialog", u"N\u00famero m\u00e1ximo de arquivos recentes a lembrar", None))
#endif // QT_CONFIG(tooltip)
        self.clearRecentLabel.setText("")
        self.clearRecentBtn.setText(QCoreApplication.translate("SettingsDialog", u"\ud83d\uddd1\ufe0f Limpar Recentes", None))
        self.settingsTabs.setTabText(self.settingsTabs.indexOf(self.pathsTab), QCoreApplication.translate("SettingsDialog", u"\ud83d\udcc1 Caminhos", None))
        self.applicationGroup.setTitle(QCoreApplication.translate("SettingsDialog", u"\ud83d\udda5\ufe0f Aplica\u00e7\u00e3o", None))
#if QT_CONFIG(tooltip)
        self.confirmExitCheck.setToolTip(QCoreApplication.translate("SettingsDialog", u"Exibir confirma\u00e7\u00e3o ao fechar a aplica\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.confirmExitCheck.setText(QCoreApplication.translate("SettingsDialog", u"Confirmar antes de sair", None))
#if QT_CONFIG(tooltip)
        self.autoSaveLayoutCheck.setToolTip(QCoreApplication.translate("SettingsDialog", u"Restaurar posi\u00e7\u00e3o e tamanho dos pain\u00e9is ao reabrir", None))
#endif // QT_CONFIG(tooltip)
        self.autoSaveLayoutCheck.setText(QCoreApplication.translate("SettingsDialog", u"Salvar layout automaticamente", None))
#if QT_CONFIG(tooltip)
        self.rememberSizeCheck.setToolTip(QCoreApplication.translate("SettingsDialog", u"Restaurar tamanho da janela ao reabrir", None))
#endif // QT_CONFIG(tooltip)
        self.rememberSizeCheck.setText(QCoreApplication.translate("SettingsDialog", u"Lembrar tamanho da janela", None))
#if QT_CONFIG(tooltip)
        self.checkUpdatesCheck.setToolTip(QCoreApplication.translate("SettingsDialog", u"Verificar novas vers\u00f5es automaticamente", None))
#endif // QT_CONFIG(tooltip)
        self.checkUpdatesCheck.setText(QCoreApplication.translate("SettingsDialog", u"Verificar atualiza\u00e7\u00f5es ao iniciar", None))
        self.streamingGroup.setTitle(QCoreApplication.translate("SettingsDialog", u"\u25b6\ufe0f Streaming", None))
        self.fpsLabel.setText(QCoreApplication.translate("SettingsDialog", u"FPS padr\u00e3o:", None))
#if QT_CONFIG(tooltip)
        self.fpsSpin.setToolTip(QCoreApplication.translate("SettingsDialog", u"Taxa de quadros padr\u00e3o para streaming", None))
#endif // QT_CONFIG(tooltip)
        self.fpsSpin.setSuffix(QCoreApplication.translate("SettingsDialog", u" fps", None))
        self.windowSizeLabel.setText(QCoreApplication.translate("SettingsDialog", u"Janela padr\u00e3o:", None))
#if QT_CONFIG(tooltip)
        self.windowSizeSpin.setToolTip(QCoreApplication.translate("SettingsDialog", u"Janela de visualiza\u00e7\u00e3o padr\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.windowSizeSpin.setSuffix(QCoreApplication.translate("SettingsDialog", u" pontos", None))
        self.settingsTabs.setTabText(self.settingsTabs.indexOf(self.behaviorTab), QCoreApplication.translate("SettingsDialog", u"\ud83d\udd27 Comportamento", None))
        self.resetBtn.setText(QCoreApplication.translate("SettingsDialog", u"\ud83d\udd04 Restaurar Padr\u00f5es", None))
#if QT_CONFIG(tooltip)
        self.resetBtn.setToolTip(QCoreApplication.translate("SettingsDialog", u"Restaurar todas as configura\u00e7\u00f5es para valores padr\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.cancelBtn.setText(QCoreApplication.translate("SettingsDialog", u"\u274c Cancelar", None))
        self.applyBtn.setText(QCoreApplication.translate("SettingsDialog", u"\u2713 Aplicar", None))
        self.okBtn.setText(QCoreApplication.translate("SettingsDialog", u"\u2713 OK", None))
    # retranslateUi

