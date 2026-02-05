# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'selectionHistoryWidget.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_SelectionHistoryWidget(object):
    def setupUi(self, SelectionHistoryWidget):
        if not SelectionHistoryWidget.objectName():
            SelectionHistoryWidget.setObjectName(u"SelectionHistoryWidget")
        SelectionHistoryWidget.resize(300, 200)
        self.mainLayout = QVBoxLayout(SelectionHistoryWidget)
        self.mainLayout.setSpacing(4)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(4, 4, 4, 4)
        self.headerLayout = QHBoxLayout()
        self.headerLayout.setObjectName(u"headerLayout")
        self.titleLabel = QLabel(SelectionHistoryWidget)
        self.titleLabel.setObjectName(u"titleLabel")

        self.headerLayout.addWidget(self.titleLabel)

        self.headerSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.headerLayout.addItem(self.headerSpacer)

        self.clearBtn = QPushButton(SelectionHistoryWidget)
        self.clearBtn.setObjectName(u"clearBtn")
        self.clearBtn.setMaximumWidth(60)

        self.headerLayout.addWidget(self.clearBtn)


        self.mainLayout.addLayout(self.headerLayout)

        self.historyList = QListWidget(SelectionHistoryWidget)
        self.historyList.setObjectName(u"historyList")
        self.historyList.setAlternatingRowColors(True)
        self.historyList.setSelectionMode(QAbstractItemView.SingleSelection)

        self.mainLayout.addWidget(self.historyList)


        self.retranslateUi(SelectionHistoryWidget)

        QMetaObject.connectSlotsByName(SelectionHistoryWidget)
    # setupUi

    def retranslateUi(self, SelectionHistoryWidget):
        self.titleLabel.setText(QCoreApplication.translate("SelectionHistoryWidget", u"\ud83d\udcdc Selection History", None))
        self.titleLabel.setStyleSheet(QCoreApplication.translate("SelectionHistoryWidget", u"font-weight: bold;", None))
        self.clearBtn.setText(QCoreApplication.translate("SelectionHistoryWidget", u"Clear", None))
        pass
    # retranslateUi

