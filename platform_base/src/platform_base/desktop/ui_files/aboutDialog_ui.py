# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'aboutDialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QTabWidget,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        if not AboutDialog.objectName():
            AboutDialog.setObjectName(u"AboutDialog")
        AboutDialog.resize(500, 400)
        AboutDialog.setModal(True)
        self.mainLayout = QVBoxLayout(AboutDialog)
        self.mainLayout.setObjectName(u"mainLayout")
        self.headerLayout = QHBoxLayout()
        self.headerLayout.setObjectName(u"headerLayout")
        self.logoLabel = QLabel(AboutDialog)
        self.logoLabel.setObjectName(u"logoLabel")
        self.logoLabel.setMinimumSize(QSize(64, 64))
        self.logoLabel.setMaximumSize(QSize(64, 64))
        self.logoLabel.setAlignment(Qt.AlignCenter)

        self.headerLayout.addWidget(self.logoLabel)

        self.titleLayout = QVBoxLayout()
        self.titleLayout.setObjectName(u"titleLayout")
        self.titleLabel = QLabel(AboutDialog)
        self.titleLabel.setObjectName(u"titleLabel")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.titleLabel.setFont(font)

        self.titleLayout.addWidget(self.titleLabel)

        self.versionLabel = QLabel(AboutDialog)
        self.versionLabel.setObjectName(u"versionLabel")

        self.titleLayout.addWidget(self.versionLabel)

        self.subtitleLabel = QLabel(AboutDialog)
        self.subtitleLabel.setObjectName(u"subtitleLabel")

        self.titleLayout.addWidget(self.subtitleLabel)

        self.titleSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.titleLayout.addItem(self.titleSpacer)


        self.headerLayout.addLayout(self.titleLayout)

        self.headerSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.headerLayout.addItem(self.headerSpacer)


        self.mainLayout.addLayout(self.headerLayout)

        self.tabs = QTabWidget(AboutDialog)
        self.tabs.setObjectName(u"tabs")
        self.aboutTab = QWidget()
        self.aboutTab.setObjectName(u"aboutTab")
        self.aboutTabLayout = QVBoxLayout(self.aboutTab)
        self.aboutTabLayout.setObjectName(u"aboutTabLayout")
        self.aboutText = QTextEdit(self.aboutTab)
        self.aboutText.setObjectName(u"aboutText")
        self.aboutText.setReadOnly(True)

        self.aboutTabLayout.addWidget(self.aboutText)

        self.tabs.addTab(self.aboutTab, "")
        self.creditsTab = QWidget()
        self.creditsTab.setObjectName(u"creditsTab")
        self.creditsTabLayout = QVBoxLayout(self.creditsTab)
        self.creditsTabLayout.setObjectName(u"creditsTabLayout")
        self.creditsText = QTextEdit(self.creditsTab)
        self.creditsText.setObjectName(u"creditsText")
        self.creditsText.setReadOnly(True)

        self.creditsTabLayout.addWidget(self.creditsText)

        self.tabs.addTab(self.creditsTab, "")
        self.systemTab = QWidget()
        self.systemTab.setObjectName(u"systemTab")
        self.systemTabLayout = QVBoxLayout(self.systemTab)
        self.systemTabLayout.setObjectName(u"systemTabLayout")
        self.systemText = QTextEdit(self.systemTab)
        self.systemText.setObjectName(u"systemText")
        self.systemText.setReadOnly(True)

        self.systemTabLayout.addWidget(self.systemText)

        self.tabs.addTab(self.systemTab, "")
        self.licenseTab = QWidget()
        self.licenseTab.setObjectName(u"licenseTab")
        self.licenseTabLayout = QVBoxLayout(self.licenseTab)
        self.licenseTabLayout.setObjectName(u"licenseTabLayout")
        self.licenseText = QTextEdit(self.licenseTab)
        self.licenseText.setObjectName(u"licenseText")
        self.licenseText.setReadOnly(True)

        self.licenseTabLayout.addWidget(self.licenseText)

        self.tabs.addTab(self.licenseTab, "")

        self.mainLayout.addWidget(self.tabs)

        self.buttonsLayout = QHBoxLayout()
        self.buttonsLayout.setObjectName(u"buttonsLayout")
        self.buttonsSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonsLayout.addItem(self.buttonsSpacer)

        self.closeBtn = QPushButton(AboutDialog)
        self.closeBtn.setObjectName(u"closeBtn")

        self.buttonsLayout.addWidget(self.closeBtn)


        self.mainLayout.addLayout(self.buttonsLayout)


        self.retranslateUi(AboutDialog)
        self.closeBtn.clicked.connect(AboutDialog.accept)

        self.tabs.setCurrentIndex(0)
        self.closeBtn.setDefault(True)


        QMetaObject.connectSlotsByName(AboutDialog)
    # setupUi

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(QCoreApplication.translate("AboutDialog", u"About Platform Base", None))
        self.logoLabel.setText(QCoreApplication.translate("AboutDialog", u"Logo", None))
        self.titleLabel.setText(QCoreApplication.translate("AboutDialog", u"Platform Base", None))
        self.versionLabel.setText(QCoreApplication.translate("AboutDialog", u"Version 2.0.0", None))
        self.versionLabel.setStyleSheet(QCoreApplication.translate("AboutDialog", u"color: gray;", None))
        self.subtitleLabel.setText(QCoreApplication.translate("AboutDialog", u"Time Series Analysis Tool", None))
        self.tabs.setTabText(self.tabs.indexOf(self.aboutTab), QCoreApplication.translate("AboutDialog", u"About", None))
        self.tabs.setTabText(self.tabs.indexOf(self.creditsTab), QCoreApplication.translate("AboutDialog", u"Credits", None))
        self.tabs.setTabText(self.tabs.indexOf(self.systemTab), QCoreApplication.translate("AboutDialog", u"System", None))
        self.tabs.setTabText(self.tabs.indexOf(self.licenseTab), QCoreApplication.translate("AboutDialog", u"License", None))
        self.closeBtn.setText(QCoreApplication.translate("AboutDialog", u"Close", None))
    # retranslateUi

