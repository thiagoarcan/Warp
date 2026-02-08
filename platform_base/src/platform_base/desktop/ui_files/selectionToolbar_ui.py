
################################################################################
## Form generated from reading UI file 'selectionToolbar.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
)


class Ui_SelectionToolbar:
    def setupUi(self, SelectionToolbar):
        if not SelectionToolbar.objectName():
            SelectionToolbar.setObjectName("SelectionToolbar")
        SelectionToolbar.resize(500, 40)
        SelectionToolbar.setMinimumHeight(36)
        SelectionToolbar.setMaximumHeight(48)
        self.mainLayout = QHBoxLayout(SelectionToolbar)
        self.mainLayout.setSpacing(4)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(4, 2, 4, 2)
        self.modeLabel = QLabel(SelectionToolbar)
        self.modeLabel.setObjectName("modeLabel")

        self.mainLayout.addWidget(self.modeLabel)

        self.singleBtn = QPushButton(SelectionToolbar)
        self.singleBtn.setObjectName("singleBtn")
        self.singleBtn.setCheckable(True)
        self.singleBtn.setChecked(True)

        self.mainLayout.addWidget(self.singleBtn)

        self.boxBtn = QPushButton(SelectionToolbar)
        self.boxBtn.setObjectName("boxBtn")
        self.boxBtn.setCheckable(True)

        self.mainLayout.addWidget(self.boxBtn)

        self.lassoBtn = QPushButton(SelectionToolbar)
        self.lassoBtn.setObjectName("lassoBtn")
        self.lassoBtn.setCheckable(True)

        self.mainLayout.addWidget(self.lassoBtn)

        self.rangeBtn = QPushButton(SelectionToolbar)
        self.rangeBtn.setObjectName("rangeBtn")
        self.rangeBtn.setCheckable(True)

        self.mainLayout.addWidget(self.rangeBtn)

        self.separator = QFrame(SelectionToolbar)
        self.separator.setObjectName("separator")
        self.separator.setFrameShape(QFrame.VLine)
        self.separator.setFrameShadow(QFrame.Sunken)

        self.mainLayout.addWidget(self.separator)

        self.selectAllBtn = QPushButton(SelectionToolbar)
        self.selectAllBtn.setObjectName("selectAllBtn")

        self.mainLayout.addWidget(self.selectAllBtn)

        self.invertBtn = QPushButton(SelectionToolbar)
        self.invertBtn.setObjectName("invertBtn")

        self.mainLayout.addWidget(self.invertBtn)

        self.clearBtn = QPushButton(SelectionToolbar)
        self.clearBtn.setObjectName("clearBtn")

        self.mainLayout.addWidget(self.clearBtn)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.mainLayout.addItem(self.horizontalSpacer)


        self.retranslateUi(SelectionToolbar)

        QMetaObject.connectSlotsByName(SelectionToolbar)
    # setupUi

    def retranslateUi(self, SelectionToolbar):
        self.modeLabel.setText(QCoreApplication.translate("SelectionToolbar", "Mode:", None))
        self.singleBtn.setText(QCoreApplication.translate("SelectionToolbar", "Single", None))
#if QT_CONFIG(tooltip)
        self.singleBtn.setToolTip(QCoreApplication.translate("SelectionToolbar", "Select single points", None))
#endif // QT_CONFIG(tooltip)
        self.boxBtn.setText(QCoreApplication.translate("SelectionToolbar", "Box", None))
#if QT_CONFIG(tooltip)
        self.boxBtn.setToolTip(QCoreApplication.translate("SelectionToolbar", "Box selection", None))
#endif // QT_CONFIG(tooltip)
        self.lassoBtn.setText(QCoreApplication.translate("SelectionToolbar", "Lasso", None))
#if QT_CONFIG(tooltip)
        self.lassoBtn.setToolTip(QCoreApplication.translate("SelectionToolbar", "Freehand lasso selection", None))
#endif // QT_CONFIG(tooltip)
        self.rangeBtn.setText(QCoreApplication.translate("SelectionToolbar", "Range", None))
#if QT_CONFIG(tooltip)
        self.rangeBtn.setToolTip(QCoreApplication.translate("SelectionToolbar", "Range/time selection", None))
#endif // QT_CONFIG(tooltip)
        self.selectAllBtn.setText(QCoreApplication.translate("SelectionToolbar", "All", None))
#if QT_CONFIG(tooltip)
        self.selectAllBtn.setToolTip(QCoreApplication.translate("SelectionToolbar", "Select all points", None))
#endif // QT_CONFIG(tooltip)
        self.invertBtn.setText(QCoreApplication.translate("SelectionToolbar", "Invert", None))
#if QT_CONFIG(tooltip)
        self.invertBtn.setToolTip(QCoreApplication.translate("SelectionToolbar", "Invert selection", None))
#endif // QT_CONFIG(tooltip)
        self.clearBtn.setText(QCoreApplication.translate("SelectionToolbar", "Clear", None))
#if QT_CONFIG(tooltip)
        self.clearBtn.setToolTip(QCoreApplication.translate("SelectionToolbar", "Clear selection", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

