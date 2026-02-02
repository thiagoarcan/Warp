# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'uploadDialog.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QFormLayout,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QProgressBar, QPushButton, QSizePolicy,
    QSpacerItem, QTabWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)

class Ui_UploadDialog(object):
    def setupUi(self, UploadDialog):
        if not UploadDialog.objectName():
            UploadDialog.setObjectName(u"UploadDialog")
        UploadDialog.resize(900, 700)
        UploadDialog.setModal(True)
        self.mainLayout = QVBoxLayout(UploadDialog)
        self.mainLayout.setObjectName(u"mainLayout")
        self.fileGroup = QGroupBox(UploadDialog)
        self.fileGroup.setObjectName(u"fileGroup")
        self.fileGroupLayout = QVBoxLayout(self.fileGroup)
        self.fileGroupLayout.setObjectName(u"fileGroupLayout")
        self.pathLayout = QHBoxLayout()
        self.pathLayout.setObjectName(u"pathLayout")
        self.filePathEdit = QLineEdit(self.fileGroup)
        self.filePathEdit.setObjectName(u"filePathEdit")

        self.pathLayout.addWidget(self.filePathEdit)

        self.browseBtn = QPushButton(self.fileGroup)
        self.browseBtn.setObjectName(u"browseBtn")

        self.pathLayout.addWidget(self.browseBtn)

        self.browseMultiBtn = QPushButton(self.fileGroup)
        self.browseMultiBtn.setObjectName(u"browseMultiBtn")

        self.pathLayout.addWidget(self.browseMultiBtn)


        self.fileGroupLayout.addLayout(self.pathLayout)

        self.filesListLabel = QLabel(self.fileGroup)
        self.filesListLabel.setObjectName(u"filesListLabel")
        self.filesListLabel.setWordWrap(True)

        self.fileGroupLayout.addWidget(self.filesListLabel)

        self.formatLabel = QLabel(self.fileGroup)
        self.formatLabel.setObjectName(u"formatLabel")

        self.fileGroupLayout.addWidget(self.formatLabel)


        self.mainLayout.addWidget(self.fileGroup)

        self.tabs = QTabWidget(UploadDialog)
        self.tabs.setObjectName(u"tabs")
        self.configTab = QWidget()
        self.configTab.setObjectName(u"configTab")
        self.configTabLayout = QVBoxLayout(self.configTab)
        self.configTabLayout.setObjectName(u"configTabLayout")
        self.generalGroup = QGroupBox(self.configTab)
        self.generalGroup.setObjectName(u"generalGroup")
        self.generalLayout = QFormLayout(self.generalGroup)
        self.generalLayout.setObjectName(u"generalLayout")
        self.encodingLabel = QLabel(self.generalGroup)
        self.encodingLabel.setObjectName(u"encodingLabel")

        self.generalLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.encodingLabel)

        self.encodingCombo = QComboBox(self.generalGroup)
        self.encodingCombo.addItem("")
        self.encodingCombo.addItem("")
        self.encodingCombo.addItem("")
        self.encodingCombo.addItem("")
        self.encodingCombo.setObjectName(u"encodingCombo")

        self.generalLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.encodingCombo)

        self.delimiterLabel = QLabel(self.generalGroup)
        self.delimiterLabel.setObjectName(u"delimiterLabel")

        self.generalLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.delimiterLabel)

        self.delimiterCombo = QComboBox(self.generalGroup)
        self.delimiterCombo.addItem("")
        self.delimiterCombo.addItem("")
        self.delimiterCombo.addItem("")
        self.delimiterCombo.addItem("")
        self.delimiterCombo.setObjectName(u"delimiterCombo")
        self.delimiterCombo.setEditable(True)

        self.generalLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.delimiterCombo)

        self.timestampLabel = QLabel(self.generalGroup)
        self.timestampLabel.setObjectName(u"timestampLabel")

        self.generalLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.timestampLabel)

        self.timestampCombo = QComboBox(self.generalGroup)
        self.timestampCombo.setObjectName(u"timestampCombo")
        self.timestampCombo.setEditable(True)

        self.generalLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.timestampCombo)


        self.configTabLayout.addWidget(self.generalGroup)

        self.excelGroup = QGroupBox(self.configTab)
        self.excelGroup.setObjectName(u"excelGroup")
        self.excelLayout = QFormLayout(self.excelGroup)
        self.excelLayout.setObjectName(u"excelLayout")
        self.sheetLabel = QLabel(self.excelGroup)
        self.sheetLabel.setObjectName(u"sheetLabel")

        self.excelLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.sheetLabel)

        self.sheetCombo = QComboBox(self.excelGroup)
        self.sheetCombo.setObjectName(u"sheetCombo")

        self.excelLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.sheetCombo)


        self.configTabLayout.addWidget(self.excelGroup)

        self.hdf5Group = QGroupBox(self.configTab)
        self.hdf5Group.setObjectName(u"hdf5Group")
        self.hdf5Layout = QFormLayout(self.hdf5Group)
        self.hdf5Layout.setObjectName(u"hdf5Layout")
        self.hdf5KeyLabel = QLabel(self.hdf5Group)
        self.hdf5KeyLabel.setObjectName(u"hdf5KeyLabel")

        self.hdf5Layout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.hdf5KeyLabel)

        self.hdf5KeyCombo = QComboBox(self.hdf5Group)
        self.hdf5KeyCombo.setObjectName(u"hdf5KeyCombo")
        self.hdf5KeyCombo.setEditable(True)

        self.hdf5Layout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.hdf5KeyCombo)


        self.configTabLayout.addWidget(self.hdf5Group)

        self.configSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.configTabLayout.addItem(self.configSpacer)

        self.tabs.addTab(self.configTab, "")
        self.previewTab = QWidget()
        self.previewTab.setObjectName(u"previewTab")
        self.previewTabLayout = QVBoxLayout(self.previewTab)
        self.previewTabLayout.setObjectName(u"previewTabLayout")
        self.previewTable = QTableWidget(self.previewTab)
        self.previewTable.setObjectName(u"previewTable")
        self.previewTable.setAlternatingRowColors(True)

        self.previewTabLayout.addWidget(self.previewTable)

        self.previewInfoLabel = QLabel(self.previewTab)
        self.previewInfoLabel.setObjectName(u"previewInfoLabel")

        self.previewTabLayout.addWidget(self.previewInfoLabel)

        self.tabs.addTab(self.previewTab, "")

        self.mainLayout.addWidget(self.tabs)

        self.progressGroup = QGroupBox(UploadDialog)
        self.progressGroup.setObjectName(u"progressGroup")
        self.progressLayout = QVBoxLayout(self.progressGroup)
        self.progressLayout.setObjectName(u"progressLayout")
        self.progressBar = QProgressBar(self.progressGroup)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setVisible(False)

        self.progressLayout.addWidget(self.progressBar)

        self.statusLabel = QLabel(self.progressGroup)
        self.statusLabel.setObjectName(u"statusLabel")

        self.progressLayout.addWidget(self.statusLabel)


        self.mainLayout.addWidget(self.progressGroup)

        self.loadedFilesLabel = QLabel(UploadDialog)
        self.loadedFilesLabel.setObjectName(u"loadedFilesLabel")
        self.loadedFilesLabel.setWordWrap(True)

        self.mainLayout.addWidget(self.loadedFilesLabel)

        self.buttonsLayout = QHBoxLayout()
        self.buttonsLayout.setObjectName(u"buttonsLayout")
        self.previewBtn = QPushButton(UploadDialog)
        self.previewBtn.setObjectName(u"previewBtn")
        self.previewBtn.setEnabled(False)

        self.buttonsLayout.addWidget(self.previewBtn)

        self.buttonsSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonsLayout.addItem(self.buttonsSpacer)

        self.cancelBtn = QPushButton(UploadDialog)
        self.cancelBtn.setObjectName(u"cancelBtn")

        self.buttonsLayout.addWidget(self.cancelBtn)

        self.loadAllBtn = QPushButton(UploadDialog)
        self.loadAllBtn.setObjectName(u"loadAllBtn")
        self.loadAllBtn.setEnabled(False)

        self.buttonsLayout.addWidget(self.loadAllBtn)

        self.loadBtn = QPushButton(UploadDialog)
        self.loadBtn.setObjectName(u"loadBtn")
        self.loadBtn.setEnabled(False)

        self.buttonsLayout.addWidget(self.loadBtn)


        self.mainLayout.addLayout(self.buttonsLayout)


        self.retranslateUi(UploadDialog)

        self.tabs.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(UploadDialog)
    # setupUi

    def retranslateUi(self, UploadDialog):
        UploadDialog.setWindowTitle(QCoreApplication.translate("UploadDialog", u"Load Data Files", None))
        self.fileGroup.setTitle(QCoreApplication.translate("UploadDialog", u"File Selection", None))
        self.filePathEdit.setPlaceholderText(QCoreApplication.translate("UploadDialog", u"Select file(s) to load...", None))
        self.browseBtn.setText(QCoreApplication.translate("UploadDialog", u"Browse...", None))
#if QT_CONFIG(tooltip)
        self.browseBtn.setToolTip(QCoreApplication.translate("UploadDialog", u"Select a single file", None))
#endif // QT_CONFIG(tooltip)
        self.browseMultiBtn.setText(QCoreApplication.translate("UploadDialog", u"Select Multiple...", None))
#if QT_CONFIG(tooltip)
        self.browseMultiBtn.setToolTip(QCoreApplication.translate("UploadDialog", u"Select multiple files at once", None))
#endif // QT_CONFIG(tooltip)
        self.filesListLabel.setText(QCoreApplication.translate("UploadDialog", u"No files selected", None))
        self.formatLabel.setText(QCoreApplication.translate("UploadDialog", u"Format: Not detected", None))
        self.generalGroup.setTitle(QCoreApplication.translate("UploadDialog", u"General Settings", None))
        self.encodingLabel.setText(QCoreApplication.translate("UploadDialog", u"Encoding:", None))
        self.encodingCombo.setItemText(0, QCoreApplication.translate("UploadDialog", u"utf-8", None))
        self.encodingCombo.setItemText(1, QCoreApplication.translate("UploadDialog", u"latin-1", None))
        self.encodingCombo.setItemText(2, QCoreApplication.translate("UploadDialog", u"cp1252", None))
        self.encodingCombo.setItemText(3, QCoreApplication.translate("UploadDialog", u"ascii", None))

        self.delimiterLabel.setText(QCoreApplication.translate("UploadDialog", u"Delimiter:", None))
        self.delimiterCombo.setItemText(0, QCoreApplication.translate("UploadDialog", u",", None))
        self.delimiterCombo.setItemText(1, QCoreApplication.translate("UploadDialog", u";", None))
        self.delimiterCombo.setItemText(2, QCoreApplication.translate("UploadDialog", u"\\t", None))
        self.delimiterCombo.setItemText(3, QCoreApplication.translate("UploadDialog", u"|", None))

        self.timestampLabel.setText(QCoreApplication.translate("UploadDialog", u"Timestamp Column:", None))
        self.excelGroup.setTitle(QCoreApplication.translate("UploadDialog", u"Excel Settings", None))
        self.sheetLabel.setText(QCoreApplication.translate("UploadDialog", u"Sheet:", None))
        self.hdf5Group.setTitle(QCoreApplication.translate("UploadDialog", u"HDF5 Settings", None))
        self.hdf5KeyLabel.setText(QCoreApplication.translate("UploadDialog", u"Dataset Key:", None))
        self.tabs.setTabText(self.tabs.indexOf(self.configTab), QCoreApplication.translate("UploadDialog", u"Configuration", None))
        self.previewInfoLabel.setText(QCoreApplication.translate("UploadDialog", u"Generate preview to see data", None))
        self.tabs.setTabText(self.tabs.indexOf(self.previewTab), QCoreApplication.translate("UploadDialog", u"Preview", None))
        self.progressGroup.setTitle(QCoreApplication.translate("UploadDialog", u"Progress", None))
        self.statusLabel.setText(QCoreApplication.translate("UploadDialog", u"Select a file to begin", None))
        self.loadedFilesLabel.setStyleSheet(QCoreApplication.translate("UploadDialog", u"color: green; font-weight: bold;", None))
        self.previewBtn.setText(QCoreApplication.translate("UploadDialog", u"Generate Preview", None))
        self.cancelBtn.setText(QCoreApplication.translate("UploadDialog", u"Close", None))
        self.loadAllBtn.setStyleSheet(QCoreApplication.translate("UploadDialog", u"font-weight: bold;", None))
        self.loadAllBtn.setText(QCoreApplication.translate("UploadDialog", u"Load All Selected", None))
#if QT_CONFIG(tooltip)
        self.loadAllBtn.setToolTip(QCoreApplication.translate("UploadDialog", u"Load all selected files simultaneously", None))
#endif // QT_CONFIG(tooltip)
        self.loadBtn.setText(QCoreApplication.translate("UploadDialog", u"Load && Close", None))
#if QT_CONFIG(tooltip)
        self.loadBtn.setToolTip(QCoreApplication.translate("UploadDialog", u"Load single file and close dialog", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

