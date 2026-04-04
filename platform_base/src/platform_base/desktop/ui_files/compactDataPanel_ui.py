# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'compactDataPanel.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFrame, QGroupBox,
    QHeaderView, QLabel, QPushButton, QSizePolicy,
    QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget)

class Ui_CompactDataPanel(object):
    def setupUi(self, CompactDataPanel):
        if not CompactDataPanel.objectName():
            CompactDataPanel.setObjectName(u"CompactDataPanel")
        CompactDataPanel.resize(400, 600)
        CompactDataPanel.setMinimumSize(QSize(150, 200))
        self.mainLayout = QVBoxLayout(CompactDataPanel)
        self.mainLayout.setSpacing(4)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(4, 4, 4, 4)
        self.arquivoFrame = QFrame(CompactDataPanel)
        self.arquivoFrame.setObjectName(u"arquivoFrame")
        self.arquivoFrame.setFrameShape(QFrame.StyledPanel)
        self.arquivoFrame.setFrameShadow(QFrame.Raised)
        self.arquivoLayout = QVBoxLayout(self.arquivoFrame)
        self.arquivoLayout.setSpacing(4)
        self.arquivoLayout.setObjectName(u"arquivoLayout")
        self.arquivoLayout.setContentsMargins(8, 8, 8, 8)
        self.carregarBtn = QPushButton(self.arquivoFrame)
        self.carregarBtn.setObjectName(u"carregarBtn")

        self.arquivoLayout.addWidget(self.carregarBtn)

        self.arquivoLabel = QLabel(self.arquivoFrame)
        self.arquivoLabel.setObjectName(u"arquivoLabel")
        self.arquivoLabel.setWordWrap(True)

        self.arquivoLayout.addWidget(self.arquivoLabel)

        self.infoLabel = QLabel(self.arquivoFrame)
        self.infoLabel.setObjectName(u"infoLabel")
        self.infoLabel.setWordWrap(True)

        self.arquivoLayout.addWidget(self.infoLabel)


        self.mainLayout.addWidget(self.arquivoFrame)

        self.seriesGroup = QGroupBox(CompactDataPanel)
        self.seriesGroup.setObjectName(u"seriesGroup")
        self.seriesLayout = QVBoxLayout(self.seriesGroup)
        self.seriesLayout.setSpacing(4)
        self.seriesLayout.setObjectName(u"seriesLayout")
        self.seriesTree = QTreeWidget(self.seriesGroup)
        self.seriesTree.setObjectName(u"seriesTree")
        self.seriesTree.setAlternatingRowColors(True)
        self.seriesTree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.seriesTree.setRootIsDecorated(True)
        self.seriesTree.setUniformRowHeights(True)

        self.seriesLayout.addWidget(self.seriesTree)


        self.mainLayout.addWidget(self.seriesGroup)

        self.dataGroup = QGroupBox(CompactDataPanel)
        self.dataGroup.setObjectName(u"dataGroup")
        self.dataLayout = QVBoxLayout(self.dataGroup)
        self.dataLayout.setSpacing(4)
        self.dataLayout.setObjectName(u"dataLayout")
        self.dataTable = QTableWidget(self.dataGroup)
        self.dataTable.setObjectName(u"dataTable")
        self.dataTable.setAlternatingRowColors(True)
        self.dataTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.dataTable.setGridStyle(Qt.SolidLine)
        self.dataTable.setSortingEnabled(True)

        self.dataLayout.addWidget(self.dataTable)


        self.mainLayout.addWidget(self.dataGroup)


        self.retranslateUi(CompactDataPanel)

        QMetaObject.connectSlotsByName(CompactDataPanel)
    # setupUi

    def retranslateUi(self, CompactDataPanel):
        CompactDataPanel.setWindowTitle(QCoreApplication.translate("CompactDataPanel", u"Dados", None))
        self.carregarBtn.setText(QCoreApplication.translate("CompactDataPanel", u"\ud83d\udcc2 Carregar Dados", None))
#if QT_CONFIG(tooltip)
        self.carregarBtn.setToolTip(QCoreApplication.translate("CompactDataPanel", u"Carregar arquivo de dados (CSV, Excel, Parquet, HDF5)", None))
#endif // QT_CONFIG(tooltip)
        self.arquivoLabel.setText(QCoreApplication.translate("CompactDataPanel", u"Nenhum arquivo carregado", None))
        self.arquivoLabel.setStyleSheet(QCoreApplication.translate("CompactDataPanel", u"color: gray; font-style: italic;", None))
        self.infoLabel.setText("")
        self.seriesGroup.setTitle(QCoreApplication.translate("CompactDataPanel", u"\ud83d\udcca S\u00e9ries de Dados", None))
        ___qtreewidgetitem = self.seriesTree.headerItem()
        ___qtreewidgetitem.setText(2, QCoreApplication.translate("CompactDataPanel", u"Pontos", None));
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("CompactDataPanel", u"Tipo", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("CompactDataPanel", u"Nome", None));
        self.dataGroup.setTitle(QCoreApplication.translate("CompactDataPanel", u"\ud83d\udccb Visualiza\u00e7\u00e3o de Dados", None))
    # retranslateUi

