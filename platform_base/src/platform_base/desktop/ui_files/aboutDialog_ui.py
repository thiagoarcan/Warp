
################################################################################
## Form generated from reading UI file 'aboutDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class Ui_AboutDialog:
    def setupUi(self, AboutDialog):
        if not AboutDialog.objectName():
            AboutDialog.setObjectName("AboutDialog")
        AboutDialog.resize(500, 400)
        AboutDialog.setModal(True)
        self.mainLayout = QVBoxLayout(AboutDialog)
        self.mainLayout.setObjectName("mainLayout")
        self.headerLayout = QHBoxLayout()
        self.headerLayout.setObjectName("headerLayout")
        self.logoLabel = QLabel(AboutDialog)
        self.logoLabel.setObjectName("logoLabel")
        self.logoLabel.setMinimumSize(QSize(64, 64))
        self.logoLabel.setMaximumSize(QSize(64, 64))
        self.logoLabel.setAlignment(Qt.AlignCenter)

        self.headerLayout.addWidget(self.logoLabel)

        self.titleLayout = QVBoxLayout()
        self.titleLayout.setObjectName("titleLayout")
        self.titleLabel = QLabel(AboutDialog)
        self.titleLabel.setObjectName("titleLabel")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.titleLabel.setFont(font)

        self.titleLayout.addWidget(self.titleLabel)

        self.versionLabel = QLabel(AboutDialog)
        self.versionLabel.setObjectName("versionLabel")

        self.titleLayout.addWidget(self.versionLabel)

        self.subtitleLabel = QLabel(AboutDialog)
        self.subtitleLabel.setObjectName("subtitleLabel")

        self.titleLayout.addWidget(self.subtitleLabel)

        self.titleSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.titleLayout.addItem(self.titleSpacer)


        self.headerLayout.addLayout(self.titleLayout)

        self.headerSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.headerLayout.addItem(self.headerSpacer)


        self.mainLayout.addLayout(self.headerLayout)

        self.tabs = QTabWidget(AboutDialog)
        self.tabs.setObjectName("tabs")
        self.aboutTab = QWidget()
        self.aboutTab.setObjectName("aboutTab")
        self.aboutTabLayout = QVBoxLayout(self.aboutTab)
        self.aboutTabLayout.setObjectName("aboutTabLayout")
        self.aboutText = QTextEdit(self.aboutTab)
        self.aboutText.setObjectName("aboutText")
        self.aboutText.setReadOnly(True)

        self.aboutTabLayout.addWidget(self.aboutText)

        self.tabs.addTab(self.aboutTab, "")
        self.creditsTab = QWidget()
        self.creditsTab.setObjectName("creditsTab")
        self.creditsTabLayout = QVBoxLayout(self.creditsTab)
        self.creditsTabLayout.setObjectName("creditsTabLayout")
        self.creditsText = QTextEdit(self.creditsTab)
        self.creditsText.setObjectName("creditsText")
        self.creditsText.setReadOnly(True)

        self.creditsTabLayout.addWidget(self.creditsText)

        self.tabs.addTab(self.creditsTab, "")
        self.systemTab = QWidget()
        self.systemTab.setObjectName("systemTab")
        self.systemTabLayout = QVBoxLayout(self.systemTab)
        self.systemTabLayout.setObjectName("systemTabLayout")
        self.systemText = QTextEdit(self.systemTab)
        self.systemText.setObjectName("systemText")
        self.systemText.setReadOnly(True)

        self.systemTabLayout.addWidget(self.systemText)

        self.tabs.addTab(self.systemTab, "")
        self.licenseTab = QWidget()
        self.licenseTab.setObjectName("licenseTab")
        self.licenseTabLayout = QVBoxLayout(self.licenseTab)
        self.licenseTabLayout.setObjectName("licenseTabLayout")
        self.licenseText = QTextEdit(self.licenseTab)
        self.licenseText.setObjectName("licenseText")
        self.licenseText.setReadOnly(True)

        self.licenseTabLayout.addWidget(self.licenseText)

        self.tabs.addTab(self.licenseTab, "")

        self.mainLayout.addWidget(self.tabs)

        self.buttonsLayout = QHBoxLayout()
        self.buttonsLayout.setObjectName("buttonsLayout")
        self.buttonsSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonsLayout.addItem(self.buttonsSpacer)

        self.closeBtn = QPushButton(AboutDialog)
        self.closeBtn.setObjectName("closeBtn")

        self.buttonsLayout.addWidget(self.closeBtn)


        self.mainLayout.addLayout(self.buttonsLayout)


        self.retranslateUi(AboutDialog)
        self.closeBtn.clicked.connect(AboutDialog.accept)

        self.tabs.setCurrentIndex(0)
        self.closeBtn.setDefault(True)


        QMetaObject.connectSlotsByName(AboutDialog)
    # setupUi

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(QCoreApplication.translate("AboutDialog", "About Platform Base", None))
        self.logoLabel.setText(QCoreApplication.translate("AboutDialog", "Logo", None))
        self.titleLabel.setText(QCoreApplication.translate("AboutDialog", "Platform Base", None))
        self.versionLabel.setText(QCoreApplication.translate("AboutDialog", "Version 2.0.0", None))
        self.versionLabel.setStyleSheet(QCoreApplication.translate("AboutDialog", "color: gray;", None))
        self.subtitleLabel.setText(QCoreApplication.translate("AboutDialog", "Time Series Analysis Tool", None))
        self.tabs.setTabText(self.tabs.indexOf(self.aboutTab), QCoreApplication.translate("AboutDialog", "About", None))
        self.tabs.setTabText(self.tabs.indexOf(self.creditsTab), QCoreApplication.translate("AboutDialog", "Credits", None))
        self.tabs.setTabText(self.tabs.indexOf(self.systemTab), QCoreApplication.translate("AboutDialog", "System", None))
        self.tabs.setTabText(self.tabs.indexOf(self.licenseTab), QCoreApplication.translate("AboutDialog", "License", None))
        self.closeBtn.setText(QCoreApplication.translate("AboutDialog", "Close", None))
    # retranslateUi

