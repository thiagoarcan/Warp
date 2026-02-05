# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'selectionToolbar.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QWidget)

class Ui_SelectionToolbar(object):
    def setupUi(self, SelectionToolbar):
        if not SelectionToolbar.objectName():
            SelectionToolbar.setObjectName(u"SelectionToolbar")
        SelectionToolbar.resize(500, 40)
        SelectionToolbar.setMinimumHeight(36)
        SelectionToolbar.setMaximumHeight(48)
        self.mainLayout = QHBoxLayout(SelectionToolbar)
        self.mainLayout.setSpacing(4)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(4, 2, 4, 2)
        self.modeLabel = QLabel(SelectionToolbar)
        self.modeLabel.setObjectName(u"modeLabel")

        self.mainLayout.addWidget(self.modeLabel)

        self.singleBtn = QPushButton(SelectionToolbar)
        self.singleBtn.setObjectName(u"singleBtn")
        self.singleBtn.setCheckable(True)
        self.singleBtn.setChecked(True)

        self.mainLayout.addWidget(self.singleBtn)

        self.boxBtn = QPushButton(SelectionToolbar)
        self.boxBtn.setObjectName(u"boxBtn")
        self.boxBtn.setCheckable(True)

        self.mainLayout.addWidget(self.boxBtn)

        self.lassoBtn = QPushButton(SelectionToolbar)
        self.lassoBtn.setObjectName(u"lassoBtn")
        self.lassoBtn.setCheckable(True)

        self.mainLayout.addWidget(self.lassoBtn)

        self.rangeBtn = QPushButton(SelectionToolbar)
        self.rangeBtn.setObjectName(u"rangeBtn")
        self.rangeBtn.setCheckable(True)

        self.mainLayout.addWidget(self.rangeBtn)

        self.separator = QFrame(SelectionToolbar)
        self.separator.setObjectName(u"separator")
        self.separator.setFrameShape(QFrame.VLine)
        self.separator.setFrameShadow(QFrame.Sunken)

        self.mainLayout.addWidget(self.separator)

        self.selectAllBtn = QPushButton(SelectionToolbar)
        self.selectAllBtn.setObjectName(u"selectAllBtn")

        self.mainLayout.addWidget(self.selectAllBtn)

        self.invertBtn = QPushButton(SelectionToolbar)
        self.invertBtn.setObjectName(u"invertBtn")

        self.mainLayout.addWidget(self.invertBtn)

        self.clearBtn = QPushButton(SelectionToolbar)
        self.clearBtn.setObjectName(u"clearBtn")

        self.mainLayout.addWidget(self.clearBtn)

        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.mainLayout.addItem(self.horizontalSpacer)


        self.retranslateUi(SelectionToolbar)

        QMetaObject.connectSlotsByName(SelectionToolbar)
    # setupUi

    def retranslateUi(self, SelectionToolbar):
        self.modeLabel.setText(QCoreApplication.translate("SelectionToolbar", u"Mode:", None))
        self.singleBtn.setText(QCoreApplication.translate("SelectionToolbar", u"Single", None))
#if QT_CONFIG(tooltip)
        self.singleBtn.setToolTip(QCoreApplication.translate("SelectionToolbar", u"Select single points", None))
#endif // QT_CONFIG(tooltip)
        self.boxBtn.setText(QCoreApplication.translate("SelectionToolbar", u"Box", None))
#if QT_CONFIG(tooltip)
        self.boxBtn.setToolTip(QCoreApplication.translate("SelectionToolbar", u"Box selection", None))
#endif // QT_CONFIG(tooltip)
        self.lassoBtn.setText(QCoreApplication.translate("SelectionToolbar", u"Lasso", None))
#if QT_CONFIG(tooltip)
        self.lassoBtn.setToolTip(QCoreApplication.translate("SelectionToolbar", u"Freehand lasso selection", None))
#endif // QT_CONFIG(tooltip)
        self.rangeBtn.setText(QCoreApplication.translate("SelectionToolbar", u"Range", None))
#if QT_CONFIG(tooltip)
        self.rangeBtn.setToolTip(QCoreApplication.translate("SelectionToolbar", u"Range/time selection", None))
#endif // QT_CONFIG(tooltip)
        self.selectAllBtn.setText(QCoreApplication.translate("SelectionToolbar", u"All", None))
#if QT_CONFIG(tooltip)
        self.selectAllBtn.setToolTip(QCoreApplication.translate("SelectionToolbar", u"Select all points", None))
#endif // QT_CONFIG(tooltip)
        self.invertBtn.setText(QCoreApplication.translate("SelectionToolbar", u"Invert", None))
#if QT_CONFIG(tooltip)
        self.invertBtn.setToolTip(QCoreApplication.translate("SelectionToolbar", u"Invert selection", None))
#endif // QT_CONFIG(tooltip)
        self.clearBtn.setText(QCoreApplication.translate("SelectionToolbar", u"Clear", None))
#if QT_CONFIG(tooltip)
        self.clearBtn.setToolTip(QCoreApplication.translate("SelectionToolbar", u"Clear selection", None))
#endif // QT_CONFIG(tooltip)
        pass
    # retranslateUi

