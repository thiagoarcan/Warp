# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'selectionSync.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QGroupBox,
    QLabel, QListWidget, QListWidgetItem, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_SelectionSync(object):
    def setupUi(self, SelectionSync):
        if not SelectionSync.objectName():
            SelectionSync.setObjectName(u"SelectionSync")
        SelectionSync.resize(300, 250)
        self.mainLayout = QVBoxLayout(SelectionSync)
        self.mainLayout.setSpacing(8)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.syncCheckbox = QCheckBox(SelectionSync)
        self.syncCheckbox.setObjectName(u"syncCheckbox")
        self.syncCheckbox.setChecked(True)

        self.mainLayout.addWidget(self.syncCheckbox)

        self.viewsGroup = QGroupBox(SelectionSync)
        self.viewsGroup.setObjectName(u"viewsGroup")
        self.viewsLayout = QVBoxLayout(self.viewsGroup)
        self.viewsLayout.setObjectName(u"viewsLayout")
        self.viewsList = QListWidget(self.viewsGroup)
        self.viewsList.setObjectName(u"viewsList")
        self.viewsList.setSelectionMode(QAbstractItemView.MultiSelection)

        self.viewsLayout.addWidget(self.viewsList)


        self.mainLayout.addWidget(self.viewsGroup)

        self.statusLabel = QLabel(SelectionSync)
        self.statusLabel.setObjectName(u"statusLabel")
        self.statusLabel.setAlignment(Qt.AlignCenter)

        self.mainLayout.addWidget(self.statusLabel)


        self.retranslateUi(SelectionSync)

        QMetaObject.connectSlotsByName(SelectionSync)
    # setupUi

    def retranslateUi(self, SelectionSync):
        self.syncCheckbox.setText(QCoreApplication.translate("SelectionSync", u"Enable Selection Sync", None))
        self.viewsGroup.setTitle(QCoreApplication.translate("SelectionSync", u"Synced Views", None))
        self.statusLabel.setText(QCoreApplication.translate("SelectionSync", u"Status: Ready", None))
        self.statusLabel.setStyleSheet(QCoreApplication.translate("SelectionSync", u"color: gray; font-style: italic;", None))
        pass
    # retranslateUi

