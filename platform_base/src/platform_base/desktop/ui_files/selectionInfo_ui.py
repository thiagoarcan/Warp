# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'selectionInfo.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_SelectionInfo(object):
    def setupUi(self, SelectionInfo):
        if not SelectionInfo.objectName():
            SelectionInfo.setObjectName(u"SelectionInfo")
        SelectionInfo.resize(250, 150)
        self.mainLayout = QVBoxLayout(SelectionInfo)
        self.mainLayout.setSpacing(4)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.countLayout = QHBoxLayout()
        self.countLayout.setObjectName(u"countLayout")
        self.countLabel = QLabel(SelectionInfo)
        self.countLabel.setObjectName(u"countLabel")

        self.countLayout.addWidget(self.countLabel)

        self.countValue = QLabel(SelectionInfo)
        self.countValue.setObjectName(u"countValue")
        self.countValue.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.countLayout.addWidget(self.countValue)

        self.percentageLabel = QLabel(SelectionInfo)
        self.percentageLabel.setObjectName(u"percentageLabel")

        self.countLayout.addWidget(self.percentageLabel)


        self.mainLayout.addLayout(self.countLayout)

        self.statsGroup = QGroupBox(SelectionInfo)
        self.statsGroup.setObjectName(u"statsGroup")
        self.statsLayout = QFormLayout(self.statsGroup)
        self.statsLayout.setObjectName(u"statsLayout")
        self.minLabelTitle = QLabel(self.statsGroup)
        self.minLabelTitle.setObjectName(u"minLabelTitle")

        self.statsLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.minLabelTitle)

        self.minLabel = QLabel(self.statsGroup)
        self.minLabel.setObjectName(u"minLabel")
        self.minLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.statsLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.minLabel)

        self.maxLabelTitle = QLabel(self.statsGroup)
        self.maxLabelTitle.setObjectName(u"maxLabelTitle")

        self.statsLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.maxLabelTitle)

        self.maxLabel = QLabel(self.statsGroup)
        self.maxLabel.setObjectName(u"maxLabel")
        self.maxLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.statsLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.maxLabel)

        self.meanLabelTitle = QLabel(self.statsGroup)
        self.meanLabelTitle.setObjectName(u"meanLabelTitle")

        self.statsLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.meanLabelTitle)

        self.meanLabel = QLabel(self.statsGroup)
        self.meanLabel.setObjectName(u"meanLabel")
        self.meanLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.statsLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.meanLabel)

        self.stdLabelTitle = QLabel(self.statsGroup)
        self.stdLabelTitle.setObjectName(u"stdLabelTitle")

        self.statsLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.stdLabelTitle)

        self.stdLabel = QLabel(self.statsGroup)
        self.stdLabel.setObjectName(u"stdLabel")
        self.stdLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        self.statsLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.stdLabel)


        self.mainLayout.addWidget(self.statsGroup)

        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mainLayout.addItem(self.verticalSpacer)


        self.retranslateUi(SelectionInfo)

        QMetaObject.connectSlotsByName(SelectionInfo)
    # setupUi

    def retranslateUi(self, SelectionInfo):
        self.countLabel.setText(QCoreApplication.translate("SelectionInfo", u"Selected:", None))
        self.countValue.setText(QCoreApplication.translate("SelectionInfo", u"0 / 0 points", None))
        self.countValue.setStyleSheet(QCoreApplication.translate("SelectionInfo", u"font-weight: bold;", None))
        self.percentageLabel.setText(QCoreApplication.translate("SelectionInfo", u"(0%)", None))
        self.percentageLabel.setStyleSheet(QCoreApplication.translate("SelectionInfo", u"color: gray;", None))
        self.statsGroup.setTitle(QCoreApplication.translate("SelectionInfo", u"Statistics", None))
        self.minLabelTitle.setText(QCoreApplication.translate("SelectionInfo", u"Min:", None))
        self.minLabel.setText(QCoreApplication.translate("SelectionInfo", u"-", None))
        self.maxLabelTitle.setText(QCoreApplication.translate("SelectionInfo", u"Max:", None))
        self.maxLabel.setText(QCoreApplication.translate("SelectionInfo", u"-", None))
        self.meanLabelTitle.setText(QCoreApplication.translate("SelectionInfo", u"Mean:", None))
        self.meanLabel.setText(QCoreApplication.translate("SelectionInfo", u"-", None))
        self.stdLabelTitle.setText(QCoreApplication.translate("SelectionInfo", u"Std Dev:", None))
        self.stdLabel.setText(QCoreApplication.translate("SelectionInfo", u"-", None))
        pass
    # retranslateUi

