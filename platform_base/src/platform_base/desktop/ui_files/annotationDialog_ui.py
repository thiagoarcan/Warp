# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'annotationDialog.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QDoubleSpinBox, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_AnnotationDialog(object):
    def setupUi(self, AnnotationDialog):
        if not AnnotationDialog.objectName():
            AnnotationDialog.setObjectName(u"AnnotationDialog")
        AnnotationDialog.resize(400, 300)
        AnnotationDialog.setMinimumWidth(400)
        AnnotationDialog.setModal(True)
        self.mainLayout = QVBoxLayout(AnnotationDialog)
        self.mainLayout.setSpacing(12)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(16, 16, 16, 16)
        self.positionGroup = QGroupBox(AnnotationDialog)
        self.positionGroup.setObjectName(u"positionGroup")
        self.positionLayout = QFormLayout(self.positionGroup)
        self.positionLayout.setObjectName(u"positionLayout")
        self.xLabel = QLabel(self.positionGroup)
        self.xLabel.setObjectName(u"xLabel")

        self.positionLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.xLabel)

        self.xSpin = QDoubleSpinBox(self.positionGroup)
        self.xSpin.setObjectName(u"xSpin")
        self.xSpin.setDecimals(6)
        self.xSpin.setMinimum(-1000000.000000000000000)
        self.xSpin.setMaximum(1000000.000000000000000)

        self.positionLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.xSpin)

        self.yLabel = QLabel(self.positionGroup)
        self.yLabel.setObjectName(u"yLabel")

        self.positionLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.yLabel)

        self.ySpin = QDoubleSpinBox(self.positionGroup)
        self.ySpin.setObjectName(u"ySpin")
        self.ySpin.setDecimals(6)
        self.ySpin.setMinimum(-1000000.000000000000000)
        self.ySpin.setMaximum(1000000.000000000000000)

        self.positionLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.ySpin)


        self.mainLayout.addWidget(self.positionGroup)

        self.textGroup = QGroupBox(AnnotationDialog)
        self.textGroup.setObjectName(u"textGroup")
        self.textLayout = QVBoxLayout(self.textGroup)
        self.textLayout.setObjectName(u"textLayout")
        self.textEdit = QTextEdit(self.textGroup)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setMaximumHeight(80)

        self.textLayout.addWidget(self.textEdit)


        self.mainLayout.addWidget(self.textGroup)

        self.styleGroup = QGroupBox(AnnotationDialog)
        self.styleGroup.setObjectName(u"styleGroup")
        self.styleLayout = QFormLayout(self.styleGroup)
        self.styleLayout.setObjectName(u"styleLayout")
        self.arrowCheck = QCheckBox(self.styleGroup)
        self.arrowCheck.setObjectName(u"arrowCheck")
        self.arrowCheck.setChecked(True)

        self.styleLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.arrowCheck)

        self.colorLabel = QLabel(self.styleGroup)
        self.colorLabel.setObjectName(u"colorLabel")

        self.styleLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.colorLabel)

        self.colorCombo = QComboBox(self.styleGroup)
        self.colorCombo.addItem("")
        self.colorCombo.addItem("")
        self.colorCombo.addItem("")
        self.colorCombo.addItem("")
        self.colorCombo.addItem("")
        self.colorCombo.setObjectName(u"colorCombo")

        self.styleLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.colorCombo)


        self.mainLayout.addWidget(self.styleGroup)

        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mainLayout.addItem(self.verticalSpacer)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.buttonSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.buttonSpacer)

        self.cancelBtn = QPushButton(AnnotationDialog)
        self.cancelBtn.setObjectName(u"cancelBtn")

        self.buttonLayout.addWidget(self.cancelBtn)

        self.addBtn = QPushButton(AnnotationDialog)
        self.addBtn.setObjectName(u"addBtn")

        self.buttonLayout.addWidget(self.addBtn)


        self.mainLayout.addLayout(self.buttonLayout)


        self.retranslateUi(AnnotationDialog)

        self.addBtn.setDefault(True)


        QMetaObject.connectSlotsByName(AnnotationDialog)
    # setupUi

    def retranslateUi(self, AnnotationDialog):
        AnnotationDialog.setWindowTitle(QCoreApplication.translate("AnnotationDialog", u"Adicionar Anota\u00e7\u00e3o", None))
        self.positionGroup.setTitle(QCoreApplication.translate("AnnotationDialog", u"\ud83d\udccd Posi\u00e7\u00e3o", None))
        self.xLabel.setText(QCoreApplication.translate("AnnotationDialog", u"X:", None))
        self.yLabel.setText(QCoreApplication.translate("AnnotationDialog", u"Y:", None))
        self.textGroup.setTitle(QCoreApplication.translate("AnnotationDialog", u"\ud83d\udcdd Texto", None))
        self.textEdit.setPlaceholderText(QCoreApplication.translate("AnnotationDialog", u"Digite o texto da anota\u00e7\u00e3o...", None))
        self.styleGroup.setTitle(QCoreApplication.translate("AnnotationDialog", u"\ud83c\udfa8 Estilo", None))
        self.arrowCheck.setText(QCoreApplication.translate("AnnotationDialog", u"Mostrar seta", None))
        self.colorLabel.setText(QCoreApplication.translate("AnnotationDialog", u"Cor:", None))
        self.colorCombo.setItemText(0, QCoreApplication.translate("AnnotationDialog", u"Vermelho", None))
        self.colorCombo.setItemText(1, QCoreApplication.translate("AnnotationDialog", u"Azul", None))
        self.colorCombo.setItemText(2, QCoreApplication.translate("AnnotationDialog", u"Verde", None))
        self.colorCombo.setItemText(3, QCoreApplication.translate("AnnotationDialog", u"Preto", None))
        self.colorCombo.setItemText(4, QCoreApplication.translate("AnnotationDialog", u"Laranja", None))

        self.cancelBtn.setText(QCoreApplication.translate("AnnotationDialog", u"Cancelar", None))
        self.addBtn.setText(QCoreApplication.translate("AnnotationDialog", u"Adicionar", None))
    # retranslateUi

