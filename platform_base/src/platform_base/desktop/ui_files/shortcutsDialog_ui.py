
################################################################################
## Form generated from reading UI file 'shortcutsDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


class Ui_ShortcutsDialog:
    def setupUi(self, ShortcutsDialog):
        if not ShortcutsDialog.objectName():
            ShortcutsDialog.setObjectName("ShortcutsDialog")
        ShortcutsDialog.resize(700, 500)
        ShortcutsDialog.setMinimumSize(QSize(600, 400))
        self.mainLayout = QVBoxLayout(ShortcutsDialog)
        self.mainLayout.setSpacing(8)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(12, 12, 12, 12)
        self.searchLayout = QHBoxLayout()
        self.searchLayout.setObjectName("searchLayout")
        self.searchLabel = QLabel(ShortcutsDialog)
        self.searchLabel.setObjectName("searchLabel")

        self.searchLayout.addWidget(self.searchLabel)

        self.searchEdit = QLineEdit(ShortcutsDialog)
        self.searchEdit.setObjectName("searchEdit")
        self.searchEdit.setClearButtonEnabled(True)

        self.searchLayout.addWidget(self.searchEdit)


        self.mainLayout.addLayout(self.searchLayout)

        self.shortcutsTable = QTableWidget(ShortcutsDialog)
        if (self.shortcutsTable.columnCount() < 4):
            self.shortcutsTable.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.shortcutsTable.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.shortcutsTable.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.shortcutsTable.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.shortcutsTable.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        self.shortcutsTable.setObjectName("shortcutsTable")
        self.shortcutsTable.setAlternatingRowColors(True)
        self.shortcutsTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.shortcutsTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.shortcutsTable.setSortingEnabled(True)

        self.mainLayout.addWidget(self.shortcutsTable)

        self.actionLayout = QHBoxLayout()
        self.actionLayout.setObjectName("actionLayout")
        self.resetBtn = QPushButton(ShortcutsDialog)
        self.resetBtn.setObjectName("resetBtn")

        self.actionLayout.addWidget(self.resetBtn)

        self.resetAllBtn = QPushButton(ShortcutsDialog)
        self.resetAllBtn.setObjectName("resetAllBtn")

        self.actionLayout.addWidget(self.resetAllBtn)

        self.actionSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.actionLayout.addItem(self.actionSpacer)


        self.mainLayout.addLayout(self.actionLayout)

        self.buttonBox = QDialogButtonBox(ShortcutsDialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Apply|QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.mainLayout.addWidget(self.buttonBox)


        self.retranslateUi(ShortcutsDialog)

        QMetaObject.connectSlotsByName(ShortcutsDialog)
    # setupUi

    def retranslateUi(self, ShortcutsDialog):
        ShortcutsDialog.setWindowTitle(QCoreApplication.translate("ShortcutsDialog", "Keyboard Shortcuts", None))
        self.searchLabel.setText(QCoreApplication.translate("ShortcutsDialog", "\ud83d\udd0d Search:", None))
        self.searchEdit.setPlaceholderText(QCoreApplication.translate("ShortcutsDialog", "Filter shortcuts by name or key...", None))
        ___qtablewidgetitem = self.shortcutsTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("ShortcutsDialog", "Action ID", None))
        ___qtablewidgetitem1 = self.shortcutsTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("ShortcutsDialog", "Description", None))
        ___qtablewidgetitem2 = self.shortcutsTable.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("ShortcutsDialog", "Shortcut", None))
        ___qtablewidgetitem3 = self.shortcutsTable.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("ShortcutsDialog", "Default", None))
        self.resetBtn.setText(QCoreApplication.translate("ShortcutsDialog", "Reset Selected", None))
#if QT_CONFIG(tooltip)
        self.resetBtn.setToolTip(QCoreApplication.translate("ShortcutsDialog", "Reset selected shortcut to default", None))
#endif // QT_CONFIG(tooltip)
        self.resetAllBtn.setText(QCoreApplication.translate("ShortcutsDialog", "Reset All", None))
#if QT_CONFIG(tooltip)
        self.resetAllBtn.setToolTip(QCoreApplication.translate("ShortcutsDialog", "Reset all shortcuts to defaults", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

