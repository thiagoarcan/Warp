
################################################################################
## Form generated from reading UI file 'selectionSync.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QGroupBox,
    QLabel,
    QListWidget,
    QVBoxLayout,
)


class Ui_SelectionSync:
    def setupUi(self, SelectionSync):
        if not SelectionSync.objectName():
            SelectionSync.setObjectName("SelectionSync")
        SelectionSync.resize(300, 250)
        self.mainLayout = QVBoxLayout(SelectionSync)
        self.mainLayout.setSpacing(8)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.syncCheckbox = QCheckBox(SelectionSync)
        self.syncCheckbox.setObjectName("syncCheckbox")
        self.syncCheckbox.setChecked(True)

        self.mainLayout.addWidget(self.syncCheckbox)

        self.viewsGroup = QGroupBox(SelectionSync)
        self.viewsGroup.setObjectName("viewsGroup")
        self.viewsLayout = QVBoxLayout(self.viewsGroup)
        self.viewsLayout.setObjectName("viewsLayout")
        self.viewsList = QListWidget(self.viewsGroup)
        self.viewsList.setObjectName("viewsList")
        self.viewsList.setSelectionMode(QAbstractItemView.MultiSelection)

        self.viewsLayout.addWidget(self.viewsList)


        self.mainLayout.addWidget(self.viewsGroup)

        self.statusLabel = QLabel(SelectionSync)
        self.statusLabel.setObjectName("statusLabel")
        self.statusLabel.setAlignment(Qt.AlignCenter)

        self.mainLayout.addWidget(self.statusLabel)


        self.retranslateUi(SelectionSync)

        QMetaObject.connectSlotsByName(SelectionSync)
    # setupUi

    def retranslateUi(self, SelectionSync):
        self.syncCheckbox.setText(QCoreApplication.translate("SelectionSync", "Enable Selection Sync", None))
        self.viewsGroup.setTitle(QCoreApplication.translate("SelectionSync", "Synced Views", None))
        self.statusLabel.setText(QCoreApplication.translate("SelectionSync", "Status: Ready", None))
        self.statusLabel.setStyleSheet(QCoreApplication.translate("SelectionSync", "color: gray; font-style: italic;", None))
    # retranslateUi

