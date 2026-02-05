# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'syncSettingsWidget.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QFormLayout,
    QLabel, QSizePolicy, QWidget)

class Ui_SyncSettingsWidget(object):
    def setupUi(self, SyncSettingsWidget):
        if not SyncSettingsWidget.objectName():
            SyncSettingsWidget.setObjectName(u"SyncSettingsWidget")
        SyncSettingsWidget.resize(300, 150)
        self.formLayout = QFormLayout(SyncSettingsWidget)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(10, 10, 10, 10)
        self.methodLabel = QLabel(SyncSettingsWidget)
        self.methodLabel.setObjectName(u"methodLabel")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.methodLabel)

        self.syncMethodCombo = QComboBox(SyncSettingsWidget)
        self.syncMethodCombo.addItem("")
        self.syncMethodCombo.addItem("")
        self.syncMethodCombo.addItem("")
        self.syncMethodCombo.setObjectName(u"syncMethodCombo")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.syncMethodCombo)

        self.freqLabel = QLabel(SyncSettingsWidget)
        self.freqLabel.setObjectName(u"freqLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.freqLabel)

        self.targetFreqSpin = QDoubleSpinBox(SyncSettingsWidget)
        self.targetFreqSpin.setObjectName(u"targetFreqSpin")
        self.targetFreqSpin.setDecimals(3)
        self.targetFreqSpin.setMinimum(0.001000000000000)
        self.targetFreqSpin.setMaximum(1000.000000000000000)
        self.targetFreqSpin.setValue(1.000000000000000)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.targetFreqSpin)

        self.resampleLabel = QLabel(SyncSettingsWidget)
        self.resampleLabel.setObjectName(u"resampleLabel")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.resampleLabel)

        self.resampleMethodCombo = QComboBox(SyncSettingsWidget)
        self.resampleMethodCombo.addItem("")
        self.resampleMethodCombo.addItem("")
        self.resampleMethodCombo.addItem("")
        self.resampleMethodCombo.setObjectName(u"resampleMethodCombo")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.resampleMethodCombo)


        self.retranslateUi(SyncSettingsWidget)

        QMetaObject.connectSlotsByName(SyncSettingsWidget)
    # setupUi

    def retranslateUi(self, SyncSettingsWidget):
        SyncSettingsWidget.setWindowTitle(QCoreApplication.translate("SyncSettingsWidget", u"Synchronization Settings", None))
        self.methodLabel.setText(QCoreApplication.translate("SyncSettingsWidget", u"Method:", None))
        self.syncMethodCombo.setItemText(0, QCoreApplication.translate("SyncSettingsWidget", u"common_grid_interpolate", None))
        self.syncMethodCombo.setItemText(1, QCoreApplication.translate("SyncSettingsWidget", u"kalman_align", None))
        self.syncMethodCombo.setItemText(2, QCoreApplication.translate("SyncSettingsWidget", u"dtw_align", None))

#if QT_CONFIG(tooltip)
        self.syncMethodCombo.setToolTip(QCoreApplication.translate("SyncSettingsWidget", u"Select synchronization method", None))
#endif // QT_CONFIG(tooltip)
        self.freqLabel.setText(QCoreApplication.translate("SyncSettingsWidget", u"Target Frequency:", None))
#if QT_CONFIG(tooltip)
        self.targetFreqSpin.setToolTip(QCoreApplication.translate("SyncSettingsWidget", u"Target sampling frequency in Hz", None))
#endif // QT_CONFIG(tooltip)
        self.targetFreqSpin.setSuffix(QCoreApplication.translate("SyncSettingsWidget", u" Hz", None))
        self.resampleLabel.setText(QCoreApplication.translate("SyncSettingsWidget", u"Resample Method:", None))
        self.resampleMethodCombo.setItemText(0, QCoreApplication.translate("SyncSettingsWidget", u"linear", None))
        self.resampleMethodCombo.setItemText(1, QCoreApplication.translate("SyncSettingsWidget", u"cubic", None))
        self.resampleMethodCombo.setItemText(2, QCoreApplication.translate("SyncSettingsWidget", u"nearest", None))

#if QT_CONFIG(tooltip)
        self.resampleMethodCombo.setToolTip(QCoreApplication.translate("SyncSettingsWidget", u"Interpolation method for resampling", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

