# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'axesConfigDialog.ui'
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
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QVBoxLayout, QWidget)

class Ui_AxesConfigDialog(object):
    def setupUi(self, AxesConfigDialog):
        if not AxesConfigDialog.objectName():
            AxesConfigDialog.setObjectName(u"AxesConfigDialog")
        AxesConfigDialog.resize(400, 500)
        AxesConfigDialog.setModal(True)
        self.verticalLayout = QVBoxLayout(AxesConfigDialog)
        self.verticalLayout.setSpacing(12)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(16, 16, 16, 16)
        self.title_group = QGroupBox(AxesConfigDialog)
        self.title_group.setObjectName(u"title_group")
        self.formLayout = QFormLayout(self.title_group)
        self.formLayout.setObjectName(u"formLayout")
        self.label_title = QLabel(self.title_group)
        self.label_title.setObjectName(u"label_title")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_title)

        self.title_edit = QLineEdit(self.title_group)
        self.title_edit.setObjectName(u"title_edit")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.title_edit)

        self.label_title_size = QLabel(self.title_group)
        self.label_title_size.setObjectName(u"label_title_size")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_title_size)

        self.title_size_spin = QSpinBox(self.title_group)
        self.title_size_spin.setObjectName(u"title_size_spin")
        self.title_size_spin.setMinimum(8)
        self.title_size_spin.setMaximum(24)
        self.title_size_spin.setValue(14)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.title_size_spin)


        self.verticalLayout.addWidget(self.title_group)

        self.labels_group = QGroupBox(AxesConfigDialog)
        self.labels_group.setObjectName(u"labels_group")
        self.formLayout_2 = QFormLayout(self.labels_group)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_xlabel = QLabel(self.labels_group)
        self.label_xlabel.setObjectName(u"label_xlabel")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_xlabel)

        self.xlabel_edit = QLineEdit(self.labels_group)
        self.xlabel_edit.setObjectName(u"xlabel_edit")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.xlabel_edit)

        self.label_ylabel = QLabel(self.labels_group)
        self.label_ylabel.setObjectName(u"label_ylabel")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_ylabel)

        self.ylabel_edit = QLineEdit(self.labels_group)
        self.ylabel_edit.setObjectName(u"ylabel_edit")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.ylabel_edit)

        self.label_label_size = QLabel(self.labels_group)
        self.label_label_size.setObjectName(u"label_label_size")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_label_size)

        self.label_size_spin = QSpinBox(self.labels_group)
        self.label_size_spin.setObjectName(u"label_size_spin")
        self.label_size_spin.setMinimum(8)
        self.label_size_spin.setMaximum(18)
        self.label_size_spin.setValue(12)

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.FieldRole, self.label_size_spin)


        self.verticalLayout.addWidget(self.labels_group)

        self.xlim_group = QGroupBox(AxesConfigDialog)
        self.xlim_group.setObjectName(u"xlim_group")
        self.verticalLayout_2 = QVBoxLayout(self.xlim_group)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.xlim_auto_check = QCheckBox(self.xlim_group)
        self.xlim_auto_check.setObjectName(u"xlim_auto_check")
        self.xlim_auto_check.setChecked(True)

        self.verticalLayout_2.addWidget(self.xlim_auto_check)

        self.horizontalLayout_xlim = QHBoxLayout()
        self.horizontalLayout_xlim.setObjectName(u"horizontalLayout_xlim")
        self.label_xmin = QLabel(self.xlim_group)
        self.label_xmin.setObjectName(u"label_xmin")

        self.horizontalLayout_xlim.addWidget(self.label_xmin)

        self.xmin_spin = QDoubleSpinBox(self.xlim_group)
        self.xmin_spin.setObjectName(u"xmin_spin")
        self.xmin_spin.setEnabled(False)
        self.xmin_spin.setDecimals(4)
        self.xmin_spin.setMinimum(-10000000000.000000000000000)
        self.xmin_spin.setMaximum(10000000000.000000000000000)

        self.horizontalLayout_xlim.addWidget(self.xmin_spin)

        self.label_xmax = QLabel(self.xlim_group)
        self.label_xmax.setObjectName(u"label_xmax")

        self.horizontalLayout_xlim.addWidget(self.label_xmax)

        self.xmax_spin = QDoubleSpinBox(self.xlim_group)
        self.xmax_spin.setObjectName(u"xmax_spin")
        self.xmax_spin.setEnabled(False)
        self.xmax_spin.setDecimals(4)
        self.xmax_spin.setMinimum(-10000000000.000000000000000)
        self.xmax_spin.setMaximum(10000000000.000000000000000)

        self.horizontalLayout_xlim.addWidget(self.xmax_spin)


        self.verticalLayout_2.addLayout(self.horizontalLayout_xlim)


        self.verticalLayout.addWidget(self.xlim_group)

        self.ylim_group = QGroupBox(AxesConfigDialog)
        self.ylim_group.setObjectName(u"ylim_group")
        self.verticalLayout_3 = QVBoxLayout(self.ylim_group)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.ylim_auto_check = QCheckBox(self.ylim_group)
        self.ylim_auto_check.setObjectName(u"ylim_auto_check")
        self.ylim_auto_check.setChecked(True)

        self.verticalLayout_3.addWidget(self.ylim_auto_check)

        self.horizontalLayout_ylim = QHBoxLayout()
        self.horizontalLayout_ylim.setObjectName(u"horizontalLayout_ylim")
        self.label_ymin = QLabel(self.ylim_group)
        self.label_ymin.setObjectName(u"label_ymin")

        self.horizontalLayout_ylim.addWidget(self.label_ymin)

        self.ymin_spin = QDoubleSpinBox(self.ylim_group)
        self.ymin_spin.setObjectName(u"ymin_spin")
        self.ymin_spin.setEnabled(False)
        self.ymin_spin.setDecimals(4)
        self.ymin_spin.setMinimum(-10000000000.000000000000000)
        self.ymin_spin.setMaximum(10000000000.000000000000000)

        self.horizontalLayout_ylim.addWidget(self.ymin_spin)

        self.label_ymax = QLabel(self.ylim_group)
        self.label_ymax.setObjectName(u"label_ymax")

        self.horizontalLayout_ylim.addWidget(self.label_ymax)

        self.ymax_spin = QDoubleSpinBox(self.ylim_group)
        self.ymax_spin.setObjectName(u"ymax_spin")
        self.ymax_spin.setEnabled(False)
        self.ymax_spin.setDecimals(4)
        self.ymax_spin.setMinimum(-10000000000.000000000000000)
        self.ymax_spin.setMaximum(10000000000.000000000000000)

        self.horizontalLayout_ylim.addWidget(self.ymax_spin)


        self.verticalLayout_3.addLayout(self.horizontalLayout_ylim)


        self.verticalLayout.addWidget(self.ylim_group)

        self.scale_group = QGroupBox(AxesConfigDialog)
        self.scale_group.setObjectName(u"scale_group")
        self.formLayout_3 = QFormLayout(self.scale_group)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.label_xscale = QLabel(self.scale_group)
        self.label_xscale.setObjectName(u"label_xscale")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_xscale)

        self.xscale_combo = QComboBox(self.scale_group)
        self.xscale_combo.addItem("")
        self.xscale_combo.addItem("")
        self.xscale_combo.addItem("")
        self.xscale_combo.setObjectName(u"xscale_combo")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.FieldRole, self.xscale_combo)

        self.label_yscale = QLabel(self.scale_group)
        self.label_yscale.setObjectName(u"label_yscale")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_yscale)

        self.yscale_combo = QComboBox(self.scale_group)
        self.yscale_combo.addItem("")
        self.yscale_combo.addItem("")
        self.yscale_combo.addItem("")
        self.yscale_combo.setObjectName(u"yscale_combo")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.FieldRole, self.yscale_combo)


        self.verticalLayout.addWidget(self.scale_group)

        self.grid_group = QGroupBox(AxesConfigDialog)
        self.grid_group.setObjectName(u"grid_group")
        self.formLayout_4 = QFormLayout(self.grid_group)
        self.formLayout_4.setObjectName(u"formLayout_4")
        self.grid_check = QCheckBox(self.grid_group)
        self.grid_check.setObjectName(u"grid_check")
        self.grid_check.setChecked(True)

        self.formLayout_4.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.grid_check)

        self.label_grid_alpha = QLabel(self.grid_group)
        self.label_grid_alpha.setObjectName(u"label_grid_alpha")

        self.formLayout_4.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_grid_alpha)

        self.grid_alpha_spin = QDoubleSpinBox(self.grid_group)
        self.grid_alpha_spin.setObjectName(u"grid_alpha_spin")
        self.grid_alpha_spin.setDecimals(2)
        self.grid_alpha_spin.setMinimum(0.000000000000000)
        self.grid_alpha_spin.setMaximum(1.000000000000000)
        self.grid_alpha_spin.setSingleStep(0.100000000000000)
        self.grid_alpha_spin.setValue(0.300000000000000)

        self.formLayout_4.setWidget(1, QFormLayout.ItemRole.FieldRole, self.grid_alpha_spin)


        self.verticalLayout.addWidget(self.grid_group)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.horizontalLayout_buttons = QHBoxLayout()
        self.horizontalLayout_buttons.setObjectName(u"horizontalLayout_buttons")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_buttons.addItem(self.horizontalSpacer)

        self.cancel_btn = QPushButton(AxesConfigDialog)
        self.cancel_btn.setObjectName(u"cancel_btn")

        self.horizontalLayout_buttons.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton(AxesConfigDialog)
        self.ok_btn.setObjectName(u"ok_btn")

        self.horizontalLayout_buttons.addWidget(self.ok_btn)


        self.verticalLayout.addLayout(self.horizontalLayout_buttons)


        self.retranslateUi(AxesConfigDialog)

        self.ok_btn.setDefault(True)


        QMetaObject.connectSlotsByName(AxesConfigDialog)
    # setupUi

    def retranslateUi(self, AxesConfigDialog):
        AxesConfigDialog.setWindowTitle(QCoreApplication.translate("AxesConfigDialog", u"\u2699\ufe0f Configurar Eixos", None))
        self.title_group.setTitle(QCoreApplication.translate("AxesConfigDialog", u"\ud83d\udcdd T\u00edtulo", None))
        self.label_title.setText(QCoreApplication.translate("AxesConfigDialog", u"T\u00edtulo:", None))
        self.title_edit.setPlaceholderText(QCoreApplication.translate("AxesConfigDialog", u"T\u00edtulo do gr\u00e1fico", None))
        self.label_title_size.setText(QCoreApplication.translate("AxesConfigDialog", u"Tamanho:", None))
        self.labels_group.setTitle(QCoreApplication.translate("AxesConfigDialog", u"\ud83c\udff7\ufe0f Labels", None))
        self.label_xlabel.setText(QCoreApplication.translate("AxesConfigDialog", u"Eixo X:", None))
        self.xlabel_edit.setPlaceholderText(QCoreApplication.translate("AxesConfigDialog", u"Label do eixo X", None))
        self.label_ylabel.setText(QCoreApplication.translate("AxesConfigDialog", u"Eixo Y:", None))
        self.ylabel_edit.setPlaceholderText(QCoreApplication.translate("AxesConfigDialog", u"Label do eixo Y", None))
        self.label_label_size.setText(QCoreApplication.translate("AxesConfigDialog", u"Tamanho:", None))
        self.xlim_group.setTitle(QCoreApplication.translate("AxesConfigDialog", u"\u2194\ufe0f Limites X", None))
        self.xlim_auto_check.setText(QCoreApplication.translate("AxesConfigDialog", u"Auto-ajustar", None))
        self.label_xmin.setText(QCoreApplication.translate("AxesConfigDialog", u"Min:", None))
        self.label_xmax.setText(QCoreApplication.translate("AxesConfigDialog", u"Max:", None))
        self.ylim_group.setTitle(QCoreApplication.translate("AxesConfigDialog", u"\u2195\ufe0f Limites Y", None))
        self.ylim_auto_check.setText(QCoreApplication.translate("AxesConfigDialog", u"Auto-ajustar", None))
        self.label_ymin.setText(QCoreApplication.translate("AxesConfigDialog", u"Min:", None))
        self.label_ymax.setText(QCoreApplication.translate("AxesConfigDialog", u"Max:", None))
        self.scale_group.setTitle(QCoreApplication.translate("AxesConfigDialog", u"\ud83d\udccf Escala", None))
        self.label_xscale.setText(QCoreApplication.translate("AxesConfigDialog", u"Escala X:", None))
        self.xscale_combo.setItemText(0, QCoreApplication.translate("AxesConfigDialog", u"linear", None))
        self.xscale_combo.setItemText(1, QCoreApplication.translate("AxesConfigDialog", u"log", None))
        self.xscale_combo.setItemText(2, QCoreApplication.translate("AxesConfigDialog", u"symlog", None))

        self.label_yscale.setText(QCoreApplication.translate("AxesConfigDialog", u"Escala Y:", None))
        self.yscale_combo.setItemText(0, QCoreApplication.translate("AxesConfigDialog", u"linear", None))
        self.yscale_combo.setItemText(1, QCoreApplication.translate("AxesConfigDialog", u"log", None))
        self.yscale_combo.setItemText(2, QCoreApplication.translate("AxesConfigDialog", u"symlog", None))

        self.grid_group.setTitle(QCoreApplication.translate("AxesConfigDialog", u"\u268f Grid", None))
        self.grid_check.setText(QCoreApplication.translate("AxesConfigDialog", u"Mostrar grid", None))
        self.label_grid_alpha.setText(QCoreApplication.translate("AxesConfigDialog", u"Transpar\u00eancia:", None))
        self.cancel_btn.setText(QCoreApplication.translate("AxesConfigDialog", u"\u274c Cancelar", None))
        self.ok_btn.setText(QCoreApplication.translate("AxesConfigDialog", u"\u2713 Aplicar", None))
    # retranslateUi

