# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'selectionPanel.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_SelectionPanel(object):
    def setupUi(self, SelectionPanel):
        if not SelectionPanel.objectName():
            SelectionPanel.setObjectName(u"SelectionPanel")
        SelectionPanel.resize(280, 400)
        SelectionPanel.setMinimumSize(QSize(200, 300))
        self.mainLayout = QVBoxLayout(SelectionPanel)
        self.mainLayout.setSpacing(4)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(4, 4, 4, 4)
        self.toolbarContainer = QFrame(SelectionPanel)
        self.toolbarContainer.setObjectName(u"toolbarContainer")
        self.toolbarContainer.setFrameShape(QFrame.NoFrame)
        self.toolbarContainer.setMinimumHeight(40)
        self.toolbarLayout = QVBoxLayout(self.toolbarContainer)
        self.toolbarLayout.setSpacing(0)
        self.toolbarLayout.setContentsMargins(0, 0, 0, 0)
        self.toolbarLayout.setObjectName(u"toolbarLayout")

        self.mainLayout.addWidget(self.toolbarContainer)

        self.statsContainer = QFrame(SelectionPanel)
        self.statsContainer.setObjectName(u"statsContainer")
        self.statsContainer.setFrameShape(QFrame.NoFrame)
        self.statsContainerLayout = QVBoxLayout(self.statsContainer)
        self.statsContainerLayout.setSpacing(0)
        self.statsContainerLayout.setContentsMargins(0, 0, 0, 0)
        self.statsContainerLayout.setObjectName(u"statsContainerLayout")

        self.mainLayout.addWidget(self.statsContainer)

        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mainLayout.addItem(self.verticalSpacer)


        self.retranslateUi(SelectionPanel)

        QMetaObject.connectSlotsByName(SelectionPanel)
    # setupUi

    def retranslateUi(self, SelectionPanel):
        pass
    # retranslateUi

