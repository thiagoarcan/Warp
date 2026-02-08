
################################################################################
## Form generated from reading UI file 'selectionHistoryWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
)


class Ui_SelectionHistoryWidget:
    def setupUi(self, SelectionHistoryWidget):
        if not SelectionHistoryWidget.objectName():
            SelectionHistoryWidget.setObjectName("SelectionHistoryWidget")
        SelectionHistoryWidget.resize(300, 200)
        self.mainLayout = QVBoxLayout(SelectionHistoryWidget)
        self.mainLayout.setSpacing(4)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(4, 4, 4, 4)
        self.headerLayout = QHBoxLayout()
        self.headerLayout.setObjectName("headerLayout")
        self.titleLabel = QLabel(SelectionHistoryWidget)
        self.titleLabel.setObjectName("titleLabel")

        self.headerLayout.addWidget(self.titleLabel)

        self.headerSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.headerLayout.addItem(self.headerSpacer)

        self.clearBtn = QPushButton(SelectionHistoryWidget)
        self.clearBtn.setObjectName("clearBtn")
        self.clearBtn.setMaximumWidth(60)

        self.headerLayout.addWidget(self.clearBtn)


        self.mainLayout.addLayout(self.headerLayout)

        self.historyList = QListWidget(SelectionHistoryWidget)
        self.historyList.setObjectName("historyList")
        self.historyList.setAlternatingRowColors(True)
        self.historyList.setSelectionMode(QAbstractItemView.SingleSelection)

        self.mainLayout.addWidget(self.historyList)


        self.retranslateUi(SelectionHistoryWidget)

        QMetaObject.connectSlotsByName(SelectionHistoryWidget)
    # setupUi

    def retranslateUi(self, SelectionHistoryWidget):
        self.titleLabel.setText(QCoreApplication.translate("SelectionHistoryWidget", "\ud83d\udcdc Selection History", None))
        self.titleLabel.setStyleSheet(QCoreApplication.translate("SelectionHistoryWidget", "font-weight: bold;", None))
        self.clearBtn.setText(QCoreApplication.translate("SelectionHistoryWidget", "Clear", None))
    # retranslateUi

