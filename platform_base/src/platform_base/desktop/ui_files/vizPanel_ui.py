# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'vizPanel.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGroupBox, QHBoxLayout,
    QLabel, QSizePolicy, QSpacerItem, QSpinBox,
    QSplitter, QTabWidget, QToolBar, QVBoxLayout,
    QWidget)

class Ui_VizPanel(object):
    def setupUi(self, VizPanel):
        if not VizPanel.objectName():
            VizPanel.setObjectName(u"VizPanel")
        VizPanel.resize(900, 600)
        VizPanel.setMinimumSize(QSize(400, 300))
        self.mainLayout = QVBoxLayout(VizPanel)
        self.mainLayout.setSpacing(4)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(4, 4, 4, 4)
        self.toolbar = QToolBar(VizPanel)
        self.toolbar.setObjectName(u"toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)

        self.mainLayout.addWidget(self.toolbar)

        self.mainSplitter = QSplitter(VizPanel)
        self.mainSplitter.setObjectName(u"mainSplitter")
        self.mainSplitter.setOrientation(Qt.Horizontal)
        self.plotTabs = QTabWidget(self.mainSplitter)
        self.plotTabs.setObjectName(u"plotTabs")
        self.plotTabs.setTabsClosable(True)
        self.plotTabs.setMovable(True)
        self.mainSplitter.addWidget(self.plotTabs)
        self.controlsWidget = QWidget(self.mainSplitter)
        self.controlsWidget.setObjectName(u"controlsWidget")
        self.controlsWidget.setMinimumSize(QSize(180, 0))
        self.controlsWidget.setMaximumSize(QSize(300, 16777215))
        self.controlsLayout = QVBoxLayout(self.controlsWidget)
        self.controlsLayout.setObjectName(u"controlsLayout")
        self.controlsLayout.setContentsMargins(0, 0, 0, 0)
        self.settingsGroup = QGroupBox(self.controlsWidget)
        self.settingsGroup.setObjectName(u"settingsGroup")
        self.settingsLayout = QVBoxLayout(self.settingsGroup)
        self.settingsLayout.setObjectName(u"settingsLayout")
        self.widthLayout = QHBoxLayout()
        self.widthLayout.setObjectName(u"widthLayout")
        self.widthLabel = QLabel(self.settingsGroup)
        self.widthLabel.setObjectName(u"widthLabel")

        self.widthLayout.addWidget(self.widthLabel)

        self.lineWidthSpin = QSpinBox(self.settingsGroup)
        self.lineWidthSpin.setObjectName(u"lineWidthSpin")
        self.lineWidthSpin.setMinimum(1)
        self.lineWidthSpin.setMaximum(10)
        self.lineWidthSpin.setValue(2)

        self.widthLayout.addWidget(self.lineWidthSpin)


        self.settingsLayout.addLayout(self.widthLayout)

        self.gridCheck = QCheckBox(self.settingsGroup)
        self.gridCheck.setObjectName(u"gridCheck")
        self.gridCheck.setChecked(True)

        self.settingsLayout.addWidget(self.gridCheck)

        self.legendCheck = QCheckBox(self.settingsGroup)
        self.legendCheck.setObjectName(u"legendCheck")
        self.legendCheck.setChecked(True)

        self.settingsLayout.addWidget(self.legendCheck)


        self.controlsLayout.addWidget(self.settingsGroup)

        self.seriesGroup = QGroupBox(self.controlsWidget)
        self.seriesGroup.setObjectName(u"seriesGroup")
        self.seriesGroupLayout = QVBoxLayout(self.seriesGroup)
        self.seriesGroupLayout.setObjectName(u"seriesGroupLayout")
        self.seriesList = QWidget(self.seriesGroup)
        self.seriesList.setObjectName(u"seriesList")
        self.seriesListLayout = QVBoxLayout(self.seriesList)
        self.seriesListLayout.setObjectName(u"seriesListLayout")
        self.seriesListLayout.setContentsMargins(0, 0, 0, 0)

        self.seriesGroupLayout.addWidget(self.seriesList)


        self.controlsLayout.addWidget(self.seriesGroup)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.controlsLayout.addItem(self.verticalSpacer)

        self.mainSplitter.addWidget(self.controlsWidget)

        self.mainLayout.addWidget(self.mainSplitter)


        self.retranslateUi(VizPanel)

        QMetaObject.connectSlotsByName(VizPanel)
    # setupUi

    def retranslateUi(self, VizPanel):
        VizPanel.setWindowTitle(QCoreApplication.translate("VizPanel", u"Visualization Panel", None))
        self.settingsGroup.setTitle(QCoreApplication.translate("VizPanel", u"Plot Settings", None))
        self.widthLabel.setText(QCoreApplication.translate("VizPanel", u"Line Width:", None))
        self.gridCheck.setText(QCoreApplication.translate("VizPanel", u"Show Grid", None))
        self.legendCheck.setText(QCoreApplication.translate("VizPanel", u"Show Legend", None))
        self.seriesGroup.setTitle(QCoreApplication.translate("VizPanel", u"Active Series", None))
    # retranslateUi

