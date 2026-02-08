
################################################################################
## Form generated from reading UI file 'exportDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QVBoxLayout,
    QWidget,
)


class Ui_ExportDialog:
    def setupUi(self, ExportDialog):
        if not ExportDialog.objectName():
            ExportDialog.setObjectName("ExportDialog")
        ExportDialog.resize(800, 600)
        ExportDialog.setModal(True)
        self.mainLayout = QVBoxLayout(ExportDialog)
        self.mainLayout.setSpacing(12)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(16, 16, 16, 16)
        self.mainSplitter = QSplitter(ExportDialog)
        self.mainSplitter.setObjectName("mainSplitter")
        self.mainSplitter.setOrientation(Qt.Horizontal)
        self.seriesGroup = QGroupBox(self.mainSplitter)
        self.seriesGroup.setObjectName("seriesGroup")
        self.seriesLayout = QVBoxLayout(self.seriesGroup)
        self.seriesLayout.setObjectName("seriesLayout")
        self.seriesTree = QTreeWidget(self.seriesGroup)
        self.seriesTree.setObjectName("seriesTree")
        self.seriesTree.setSelectionMode(QAbstractItemView.MultiSelection)
        self.seriesTree.setAlternatingRowColors(True)

        self.seriesLayout.addWidget(self.seriesTree)

        self.selectionBtnLayout = QHBoxLayout()
        self.selectionBtnLayout.setObjectName("selectionBtnLayout")
        self.selectAllBtn = QPushButton(self.seriesGroup)
        self.selectAllBtn.setObjectName("selectAllBtn")

        self.selectionBtnLayout.addWidget(self.selectAllBtn)

        self.clearSelectionBtn = QPushButton(self.seriesGroup)
        self.clearSelectionBtn.setObjectName("clearSelectionBtn")

        self.selectionBtnLayout.addWidget(self.clearSelectionBtn)


        self.seriesLayout.addLayout(self.selectionBtnLayout)

        self.selectionInfoLabel = QLabel(self.seriesGroup)
        self.selectionInfoLabel.setObjectName("selectionInfoLabel")

        self.seriesLayout.addWidget(self.selectionInfoLabel)

        self.mainSplitter.addWidget(self.seriesGroup)
        self.configGroup = QGroupBox(self.mainSplitter)
        self.configGroup.setObjectName("configGroup")
        self.configLayout = QVBoxLayout(self.configGroup)
        self.configLayout.setObjectName("configLayout")
        self.configTabs = QTabWidget(self.configGroup)
        self.configTabs.setObjectName("configTabs")
        self.formatTab = QWidget()
        self.formatTab.setObjectName("formatTab")
        self.formatLayout = QFormLayout(self.formatTab)
        self.formatLayout.setObjectName("formatLayout")
        self.formatLabel = QLabel(self.formatTab)
        self.formatLabel.setObjectName("formatLabel")

        self.formatLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.formatLabel)

        self.formatCombo = QComboBox(self.formatTab)
        self.formatCombo.addItem("")
        self.formatCombo.addItem("")
        self.formatCombo.addItem("")
        self.formatCombo.addItem("")
        self.formatCombo.addItem("")
        self.formatCombo.setObjectName("formatCombo")

        self.formatLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.formatCombo)

        self.delimiterLabel = QLabel(self.formatTab)
        self.delimiterLabel.setObjectName("delimiterLabel")

        self.formatLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.delimiterLabel)

        self.delimiterCombo = QComboBox(self.formatTab)
        self.delimiterCombo.addItem("")
        self.delimiterCombo.addItem("")
        self.delimiterCombo.addItem("")
        self.delimiterCombo.addItem("")
        self.delimiterCombo.setObjectName("delimiterCombo")

        self.formatLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.delimiterCombo)

        self.encodingLabel = QLabel(self.formatTab)
        self.encodingLabel.setObjectName("encodingLabel")

        self.formatLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.encodingLabel)

        self.encodingCombo = QComboBox(self.formatTab)
        self.encodingCombo.addItem("")
        self.encodingCombo.addItem("")
        self.encodingCombo.addItem("")
        self.encodingCombo.setObjectName("encodingCombo")

        self.formatLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.encodingCombo)

        self.decimalLabel = QLabel(self.formatTab)
        self.decimalLabel.setObjectName("decimalLabel")

        self.formatLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.decimalLabel)

        self.decimalCombo = QComboBox(self.formatTab)
        self.decimalCombo.addItem("")
        self.decimalCombo.addItem("")
        self.decimalCombo.setObjectName("decimalCombo")

        self.formatLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.decimalCombo)

        self.configTabs.addTab(self.formatTab, "")
        self.optionsTab = QWidget()
        self.optionsTab.setObjectName("optionsTab")
        self.optionsLayout = QVBoxLayout(self.optionsTab)
        self.optionsLayout.setObjectName("optionsLayout")
        self.includeHeaderCheck = QCheckBox(self.optionsTab)
        self.includeHeaderCheck.setObjectName("includeHeaderCheck")
        self.includeHeaderCheck.setChecked(True)

        self.optionsLayout.addWidget(self.includeHeaderCheck)

        self.includeIndexCheck = QCheckBox(self.optionsTab)
        self.includeIndexCheck.setObjectName("includeIndexCheck")
        self.includeIndexCheck.setChecked(False)

        self.optionsLayout.addWidget(self.includeIndexCheck)

        self.includeMetadataCheck = QCheckBox(self.optionsTab)
        self.includeMetadataCheck.setObjectName("includeMetadataCheck")
        self.includeMetadataCheck.setChecked(True)

        self.optionsLayout.addWidget(self.includeMetadataCheck)

        self.compressCheck = QCheckBox(self.optionsTab)
        self.compressCheck.setObjectName("compressCheck")
        self.compressCheck.setChecked(False)

        self.optionsLayout.addWidget(self.compressCheck)

        self.dateFormatCheck = QCheckBox(self.optionsTab)
        self.dateFormatCheck.setObjectName("dateFormatCheck")
        self.dateFormatCheck.setChecked(True)

        self.optionsLayout.addWidget(self.dateFormatCheck)

        self.optionsSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.optionsLayout.addItem(self.optionsSpacer)

        self.configTabs.addTab(self.optionsTab, "")
        self.previewTab = QWidget()
        self.previewTab.setObjectName("previewTab")
        self.previewLayout = QVBoxLayout(self.previewTab)
        self.previewLayout.setObjectName("previewLayout")
        self.previewText = QTextEdit(self.previewTab)
        self.previewText.setObjectName("previewText")
        self.previewText.setReadOnly(True)
        font = QFont()
        font.setFamilies(["Consolas"])
        font.setPointSize(9)
        self.previewText.setFont(font)

        self.previewLayout.addWidget(self.previewText)

        self.configTabs.addTab(self.previewTab, "")

        self.configLayout.addWidget(self.configTabs)

        self.destGroup = QGroupBox(self.configGroup)
        self.destGroup.setObjectName("destGroup")
        self.destLayout = QHBoxLayout(self.destGroup)
        self.destLayout.setObjectName("destLayout")
        self.pathEdit = QLineEdit(self.destGroup)
        self.pathEdit.setObjectName("pathEdit")

        self.destLayout.addWidget(self.pathEdit)

        self.browseBtn = QPushButton(self.destGroup)
        self.browseBtn.setObjectName("browseBtn")

        self.destLayout.addWidget(self.browseBtn)


        self.configLayout.addWidget(self.destGroup)

        self.mainSplitter.addWidget(self.configGroup)

        self.mainLayout.addWidget(self.mainSplitter)

        self.progressBar = QProgressBar(ExportDialog)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setVisible(False)
        self.progressBar.setValue(0)

        self.mainLayout.addWidget(self.progressBar)

        self.progressLabel = QLabel(ExportDialog)
        self.progressLabel.setObjectName("progressLabel")
        self.progressLabel.setVisible(False)

        self.mainLayout.addWidget(self.progressLabel)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName("buttonLayout")
        self.previewBtn = QPushButton(ExportDialog)
        self.previewBtn.setObjectName("previewBtn")

        self.buttonLayout.addWidget(self.previewBtn)

        self.buttonSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.buttonSpacer)

        self.buttonBox = QDialogButtonBox(ExportDialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.buttonLayout.addWidget(self.buttonBox)


        self.mainLayout.addLayout(self.buttonLayout)


        self.retranslateUi(ExportDialog)
        self.buttonBox.accepted.connect(ExportDialog.accept)
        self.buttonBox.rejected.connect(ExportDialog.reject)

        self.configTabs.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(ExportDialog)
    # setupUi

    def retranslateUi(self, ExportDialog):
        ExportDialog.setWindowTitle(QCoreApplication.translate("ExportDialog", "\ud83d\udce4 Exportar Dados", None))
        self.seriesGroup.setTitle(QCoreApplication.translate("ExportDialog", "\ud83d\udcca S\u00e9ries para Exportar", None))
        ___qtreewidgetitem = self.seriesTree.headerItem()
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("ExportDialog", "Linhas", None))
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("ExportDialog", "Nome", None))
        self.selectAllBtn.setText(QCoreApplication.translate("ExportDialog", "Selecionar Tudo", None))
        self.clearSelectionBtn.setText(QCoreApplication.translate("ExportDialog", "Limpar Sele\u00e7\u00e3o", None))
        self.selectionInfoLabel.setText(QCoreApplication.translate("ExportDialog", "0 s\u00e9ries selecionadas", None))
        self.configGroup.setTitle(QCoreApplication.translate("ExportDialog", "\u2699\ufe0f Configura\u00e7\u00f5es", None))
        self.formatLabel.setText(QCoreApplication.translate("ExportDialog", "Formato:", None))
        self.formatCombo.setItemText(0, QCoreApplication.translate("ExportDialog", "CSV (.csv)", None))
        self.formatCombo.setItemText(1, QCoreApplication.translate("ExportDialog", "Excel (.xlsx)", None))
        self.formatCombo.setItemText(2, QCoreApplication.translate("ExportDialog", "Parquet (.parquet)", None))
        self.formatCombo.setItemText(3, QCoreApplication.translate("ExportDialog", "HDF5 (.h5)", None))
        self.formatCombo.setItemText(4, QCoreApplication.translate("ExportDialog", "JSON (.json)", None))

#if QT_CONFIG(tooltip)
        self.formatCombo.setToolTip(QCoreApplication.translate("ExportDialog", "Formato do arquivo de sa\u00edda", None))
#endif // QT_CONFIG(tooltip)
        self.delimiterLabel.setText(QCoreApplication.translate("ExportDialog", "Delimitador:", None))
        self.delimiterCombo.setItemText(0, QCoreApplication.translate("ExportDialog", "V\u00edrgula (,)", None))
        self.delimiterCombo.setItemText(1, QCoreApplication.translate("ExportDialog", "Ponto e v\u00edrgula (;)", None))
        self.delimiterCombo.setItemText(2, QCoreApplication.translate("ExportDialog", "Tab", None))
        self.delimiterCombo.setItemText(3, QCoreApplication.translate("ExportDialog", "Espa\u00e7o", None))

#if QT_CONFIG(tooltip)
        self.delimiterCombo.setToolTip(QCoreApplication.translate("ExportDialog", "Delimitador entre colunas (CSV)", None))
#endif // QT_CONFIG(tooltip)
        self.encodingLabel.setText(QCoreApplication.translate("ExportDialog", "Encoding:", None))
        self.encodingCombo.setItemText(0, QCoreApplication.translate("ExportDialog", "UTF-8", None))
        self.encodingCombo.setItemText(1, QCoreApplication.translate("ExportDialog", "Latin-1", None))
        self.encodingCombo.setItemText(2, QCoreApplication.translate("ExportDialog", "Windows-1252", None))

#if QT_CONFIG(tooltip)
        self.encodingCombo.setToolTip(QCoreApplication.translate("ExportDialog", "Codifica\u00e7\u00e3o de caracteres", None))
#endif // QT_CONFIG(tooltip)
        self.decimalLabel.setText(QCoreApplication.translate("ExportDialog", "Separador decimal:", None))
        self.decimalCombo.setItemText(0, QCoreApplication.translate("ExportDialog", "Ponto (.)", None))
        self.decimalCombo.setItemText(1, QCoreApplication.translate("ExportDialog", "V\u00edrgula (,)", None))

#if QT_CONFIG(tooltip)
        self.decimalCombo.setToolTip(QCoreApplication.translate("ExportDialog", "Separador decimal para n\u00fameros", None))
#endif // QT_CONFIG(tooltip)
        self.configTabs.setTabText(self.configTabs.indexOf(self.formatTab), QCoreApplication.translate("ExportDialog", "\ud83d\udcc4 Formato", None))
        self.includeHeaderCheck.setText(QCoreApplication.translate("ExportDialog", "Incluir cabe\u00e7alho", None))
#if QT_CONFIG(tooltip)
        self.includeHeaderCheck.setToolTip(QCoreApplication.translate("ExportDialog", "Incluir nomes das colunas na primeira linha", None))
#endif // QT_CONFIG(tooltip)
        self.includeIndexCheck.setText(QCoreApplication.translate("ExportDialog", "Incluir \u00edndice", None))
#if QT_CONFIG(tooltip)
        self.includeIndexCheck.setToolTip(QCoreApplication.translate("ExportDialog", "Incluir coluna de \u00edndice", None))
#endif // QT_CONFIG(tooltip)
        self.includeMetadataCheck.setText(QCoreApplication.translate("ExportDialog", "Incluir metadados", None))
#if QT_CONFIG(tooltip)
        self.includeMetadataCheck.setToolTip(QCoreApplication.translate("ExportDialog", "Incluir informa\u00e7\u00f5es sobre origem dos dados", None))
#endif // QT_CONFIG(tooltip)
        self.compressCheck.setText(QCoreApplication.translate("ExportDialog", "Comprimir arquivo (gzip)", None))
#if QT_CONFIG(tooltip)
        self.compressCheck.setToolTip(QCoreApplication.translate("ExportDialog", "Comprime o arquivo de sa\u00edda com gzip", None))
#endif // QT_CONFIG(tooltip)
        self.dateFormatCheck.setText(QCoreApplication.translate("ExportDialog", "Formatar datas como ISO 8601", None))
#if QT_CONFIG(tooltip)
        self.dateFormatCheck.setToolTip(QCoreApplication.translate("ExportDialog", "Usa formato YYYY-MM-DD HH:MM:SS para datas", None))
#endif // QT_CONFIG(tooltip)
        self.configTabs.setTabText(self.configTabs.indexOf(self.optionsTab), QCoreApplication.translate("ExportDialog", "\ud83d\udd27 Op\u00e7\u00f5es", None))
        self.previewText.setPlaceholderText(QCoreApplication.translate("ExportDialog", "Clique em 'Preview' para ver os dados...", None))
        self.configTabs.setTabText(self.configTabs.indexOf(self.previewTab), QCoreApplication.translate("ExportDialog", "\ud83d\udc41\ufe0f Preview", None))
        self.destGroup.setTitle(QCoreApplication.translate("ExportDialog", "\ud83d\udcc1 Destino", None))
        self.pathEdit.setPlaceholderText(QCoreApplication.translate("ExportDialog", "Selecione o arquivo de destino...", None))
        self.browseBtn.setText(QCoreApplication.translate("ExportDialog", "Procurar...", None))
        self.progressLabel.setText("")
        self.previewBtn.setText(QCoreApplication.translate("ExportDialog", "\ud83d\udc41\ufe0f Preview", None))
#if QT_CONFIG(tooltip)
        self.previewBtn.setToolTip(QCoreApplication.translate("ExportDialog", "Visualizar dados antes de exportar", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

