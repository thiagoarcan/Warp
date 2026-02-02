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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QFormLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QTabWidget,
    QVBoxLayout, QWidget)

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        if not SettingsDialog.objectName():
            SettingsDialog.setObjectName(u"SettingsDialog")
        SettingsDialog.resize(700, 500)
        SettingsDialog.setModal(True)
        self.mainLayout = QVBoxLayout(SettingsDialog)
        self.mainLayout.setObjectName(u"mainLayout")
        self.settingsTabs = QTabWidget(SettingsDialog)
        self.settingsTabs.setObjectName(u"settingsTabs")
        self.generalTab = QWidget()
        self.generalTab.setObjectName(u"generalTab")
        self.generalTabLayout = QVBoxLayout(self.generalTab)
        self.generalTabLayout.setObjectName(u"generalTabLayout")
        self.appearanceGroup = QGroupBox(self.generalTab)
        self.appearanceGroup.setObjectName(u"appearanceGroup")
        self.appearanceLayout = QFormLayout(self.appearanceGroup)
        self.appearanceLayout.setObjectName(u"appearanceLayout")
        self.themeLabel = QLabel(self.appearanceGroup)
        self.themeLabel.setObjectName(u"themeLabel")

        self.appearanceLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.themeLabel)

        self.themeCombo = QComboBox(self.appearanceGroup)
        self.themeCombo.addItem("")
        self.themeCombo.addItem("")
        self.themeCombo.addItem("")
        self.themeCombo.setObjectName(u"themeCombo")

        self.appearanceLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.themeCombo)

        self.fontSizeLabel = QLabel(self.appearanceGroup)
        self.fontSizeLabel.setObjectName(u"fontSizeLabel")

        self.appearanceLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.fontSizeLabel)

        self.fontSizeSpin = QSpinBox(self.appearanceGroup)
        self.fontSizeSpin.setObjectName(u"fontSizeSpin")
        self.fontSizeSpin.setMinimum(8)
        self.fontSizeSpin.setMaximum(20)
        self.fontSizeSpin.setValue(9)

        self.appearanceLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.fontSizeSpin)

        self.displayLabel = QLabel(self.appearanceGroup)
        self.displayLabel.setObjectName(u"displayLabel")

        self.appearanceLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.displayLabel)

        self.dpiCheck = QCheckBox(self.appearanceGroup)
        self.dpiCheck.setObjectName(u"dpiCheck")

        self.appearanceLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.dpiCheck)


        self.generalTabLayout.addWidget(self.appearanceGroup)

        self.behaviorGroup = QGroupBox(self.generalTab)
        self.behaviorGroup.setObjectName(u"behaviorGroup")
        self.behaviorLayout = QFormLayout(self.behaviorGroup)
        self.behaviorLayout.setObjectName(u"behaviorLayout")
        self.autosaveLabel = QLabel(self.behaviorGroup)
        self.autosaveLabel.setObjectName(u"autosaveLabel")

        self.behaviorLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.autosaveLabel)

        self.autosaveSpin = QSpinBox(self.behaviorGroup)
        self.autosaveSpin.setObjectName(u"autosaveSpin")
        self.autosaveSpin.setMinimum(1)
        self.autosaveSpin.setMaximum(60)
        self.autosaveSpin.setValue(5)

        self.behaviorLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.autosaveSpin)

        self.exitLabel = QLabel(self.behaviorGroup)
        self.exitLabel.setObjectName(u"exitLabel")

        self.behaviorLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.exitLabel)

        self.confirmExitCheck = QCheckBox(self.behaviorGroup)
        self.confirmExitCheck.setObjectName(u"confirmExitCheck")

        self.behaviorLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.confirmExitCheck)

        self.windowLabel = QLabel(self.behaviorGroup)
        self.windowLabel.setObjectName(u"windowLabel")

        self.behaviorLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.windowLabel)

        self.rememberWindowCheck = QCheckBox(self.behaviorGroup)
        self.rememberWindowCheck.setObjectName(u"rememberWindowCheck")

        self.behaviorLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.rememberWindowCheck)


        self.generalTabLayout.addWidget(self.behaviorGroup)

        self.generalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.generalTabLayout.addItem(self.generalSpacer)

        self.settingsTabs.addTab(self.generalTab, "")
        self.performanceTab = QWidget()
        self.performanceTab.setObjectName(u"performanceTab")
        self.performanceTabLayout = QVBoxLayout(self.performanceTab)
        self.performanceTabLayout.setObjectName(u"performanceTabLayout")
        self.memoryGroup = QGroupBox(self.performanceTab)
        self.memoryGroup.setObjectName(u"memoryGroup")
        self.memoryLayout = QFormLayout(self.memoryGroup)
        self.memoryLayout.setObjectName(u"memoryLayout")
        self.cacheSizeLabel = QLabel(self.memoryGroup)
        self.cacheSizeLabel.setObjectName(u"cacheSizeLabel")

        self.memoryLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.cacheSizeLabel)

        self.cacheSizeSpin = QSpinBox(self.memoryGroup)
        self.cacheSizeSpin.setObjectName(u"cacheSizeSpin")
        self.cacheSizeSpin.setMinimum(100)
        self.cacheSizeSpin.setMaximum(4000)
        self.cacheSizeSpin.setValue(500)

        self.memoryLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.cacheSizeSpin)


        self.performanceTabLayout.addWidget(self.memoryGroup)

        self.renderingGroup = QGroupBox(self.performanceTab)
        self.renderingGroup.setObjectName(u"renderingGroup")
        self.renderingLayout = QFormLayout(self.renderingGroup)
        self.renderingLayout.setObjectName(u"renderingLayout")
        self.decimationLabel = QLabel(self.renderingGroup)
        self.decimationLabel.setObjectName(u"decimationLabel")

        self.renderingLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.decimationLabel)

        self.decimationSpin = QSpinBox(self.renderingGroup)
        self.decimationSpin.setObjectName(u"decimationSpin")
        self.decimationSpin.setMinimum(1000)
        self.decimationSpin.setMaximum(100000)
        self.decimationSpin.setValue(10000)

        self.renderingLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.decimationSpin)


        self.performanceTabLayout.addWidget(self.renderingGroup)

        self.performanceSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.performanceTabLayout.addItem(self.performanceSpacer)

        self.settingsTabs.addTab(self.performanceTab, "")
        self.loggingTab = QWidget()
        self.loggingTab.setObjectName(u"loggingTab")
        self.loggingTabLayout = QVBoxLayout(self.loggingTab)
        self.loggingTabLayout.setObjectName(u"loggingTabLayout")
        self.loggingGroup = QGroupBox(self.loggingTab)
        self.loggingGroup.setObjectName(u"loggingGroup")
        self.loggingLayout = QFormLayout(self.loggingGroup)
        self.loggingLayout.setObjectName(u"loggingLayout")
        self.logLevelLabel = QLabel(self.loggingGroup)
        self.logLevelLabel.setObjectName(u"logLevelLabel")

        self.loggingLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.logLevelLabel)

        self.logLevelCombo = QComboBox(self.loggingGroup)
        self.logLevelCombo.addItem("")
        self.logLevelCombo.addItem("")
        self.logLevelCombo.addItem("")
        self.logLevelCombo.addItem("")
        self.logLevelCombo.setObjectName(u"logLevelCombo")

        self.loggingLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.logLevelCombo)

        self.logPathLabel = QLabel(self.loggingGroup)
        self.logPathLabel.setObjectName(u"logPathLabel")

        self.loggingLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.logPathLabel)

        self.logPathLayout = QHBoxLayout()
        self.logPathLayout.setObjectName(u"logPathLayout")
        self.logPathEdit = QLineEdit(self.loggingGroup)
        self.logPathEdit.setObjectName(u"logPathEdit")

        self.logPathLayout.addWidget(self.logPathEdit)

        self.logPathBrowseBtn = QPushButton(self.loggingGroup)
        self.logPathBrowseBtn.setObjectName(u"logPathBrowseBtn")

        self.logPathLayout.addWidget(self.logPathBrowseBtn)


        self.loggingLayout.setLayout(1, QFormLayout.ItemRole.FieldRole, self.logPathLayout)


        self.loggingTabLayout.addWidget(self.loggingGroup)

        self.loggingSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.loggingTabLayout.addItem(self.loggingSpacer)

        self.settingsTabs.addTab(self.loggingTab, "")

        self.mainLayout.addWidget(self.settingsTabs)

        self.buttonBox = QDialogButtonBox(SettingsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Apply|QDialogButtonBox.Cancel|QDialogButtonBox.Ok|QDialogButtonBox.RestoreDefaults)

        self.mainLayout.addWidget(self.buttonBox)


        self.retranslateUi(SettingsDialog)
        self.buttonBox.accepted.connect(SettingsDialog.accept)
        self.buttonBox.rejected.connect(SettingsDialog.reject)

        self.settingsTabs.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(SettingsDialog)
    # setupUi

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(QCoreApplication.translate("SettingsDialog", u"Settings", None))
        self.appearanceGroup.setTitle(QCoreApplication.translate("SettingsDialog", u"Appearance", None))
        self.themeLabel.setText(QCoreApplication.translate("SettingsDialog", u"Theme:", None))
        self.themeCombo.setItemText(0, QCoreApplication.translate("SettingsDialog", u"Auto", None))
        self.themeCombo.setItemText(1, QCoreApplication.translate("SettingsDialog", u"Light", None))
        self.themeCombo.setItemText(2, QCoreApplication.translate("SettingsDialog", u"Dark", None))

        self.fontSizeLabel.setText(QCoreApplication.translate("SettingsDialog", u"Font Size:", None))
        self.displayLabel.setText(QCoreApplication.translate("SettingsDialog", u"Display:", None))
        self.dpiCheck.setText(QCoreApplication.translate("SettingsDialog", u"Enable high DPI scaling", None))
        self.behaviorGroup.setTitle(QCoreApplication.translate("SettingsDialog", u"Behavior", None))
        self.autosaveLabel.setText(QCoreApplication.translate("SettingsDialog", u"Auto-save interval:", None))
        self.autosaveSpin.setSuffix(QCoreApplication.translate("SettingsDialog", u" minutes", None))
        self.exitLabel.setText(QCoreApplication.translate("SettingsDialog", u"Exit:", None))
        self.confirmExitCheck.setText(QCoreApplication.translate("SettingsDialog", u"Confirm before exiting", None))
        self.windowLabel.setText(QCoreApplication.translate("SettingsDialog", u"Window:", None))
        self.rememberWindowCheck.setText(QCoreApplication.translate("SettingsDialog", u"Remember window position and size", None))
        self.settingsTabs.setTabText(self.settingsTabs.indexOf(self.generalTab), QCoreApplication.translate("SettingsDialog", u"General", None))
        self.memoryGroup.setTitle(QCoreApplication.translate("SettingsDialog", u"Memory", None))
        self.cacheSizeLabel.setText(QCoreApplication.translate("SettingsDialog", u"Cache Size (MB):", None))
        self.renderingGroup.setTitle(QCoreApplication.translate("SettingsDialog", u"Rendering", None))
        self.decimationLabel.setText(QCoreApplication.translate("SettingsDialog", u"Decimation Threshold:", None))
        self.settingsTabs.setTabText(self.settingsTabs.indexOf(self.performanceTab), QCoreApplication.translate("SettingsDialog", u"Performance", None))
        self.loggingGroup.setTitle(QCoreApplication.translate("SettingsDialog", u"Logging Settings", None))
        self.logLevelLabel.setText(QCoreApplication.translate("SettingsDialog", u"Log Level:", None))
        self.logLevelCombo.setItemText(0, QCoreApplication.translate("SettingsDialog", u"DEBUG", None))
        self.logLevelCombo.setItemText(1, QCoreApplication.translate("SettingsDialog", u"INFO", None))
        self.logLevelCombo.setItemText(2, QCoreApplication.translate("SettingsDialog", u"WARNING", None))
        self.logLevelCombo.setItemText(3, QCoreApplication.translate("SettingsDialog", u"ERROR", None))

        self.logPathLabel.setText(QCoreApplication.translate("SettingsDialog", u"Log Path:", None))
        self.logPathBrowseBtn.setText(QCoreApplication.translate("SettingsDialog", u"Browse...", None))
        self.settingsTabs.setTabText(self.settingsTabs.indexOf(self.loggingTab), QCoreApplication.translate("SettingsDialog", u"Logging", None))
    # retranslateUi

