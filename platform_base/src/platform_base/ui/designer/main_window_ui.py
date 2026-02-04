# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QMainWindow,
    QMenu, QMenuBar, QSizePolicy, QSplitter,
    QStatusBar, QToolBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1800, 1100)
        MainWindow.setMinimumSize(QSize(1400, 900))
        MainWindow.setStyleSheet(u"QMainWindow {\n"
"    background-color: #f8f9fa;\n"
"}\n"
"QToolBar {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #e9ecef;\n"
"    border-radius: 6px;\n"
"    padding: 4px;\n"
"    margin: 2px;\n"
"}\n"
"QToolBar QToolButton {\n"
"    background-color: transparent;\n"
"    border: 1px solid transparent;\n"
"    border-radius: 4px;\n"
"    padding: 8px;\n"
"    margin: 2px;\n"
"    min-width: 32px;\n"
"    min-height: 32px;\n"
"}\n"
"QToolBar QToolButton:hover {\n"
"    background-color: #e9ecef;\n"
"    border: 1px solid #ced4da;\n"
"}\n"
"QToolBar QToolButton:pressed {\n"
"    background-color: #dee2e6;\n"
"}\n"
"QStatusBar {\n"
"    background-color: #ffffff;\n"
"    border-top: 1px solid #e9ecef;\n"
"    padding: 4px 8px;\n"
"}\n"
"QSplitter::handle {\n"
"    background-color: #e9ecef;\n"
"    width: 2px;\n"
"    height: 2px;\n"
"}\n"
"QSplitter::handle:hover {\n"
"    background-color: #0d6efd;\n"
"}")
        self.action_open_dataset = QAction(MainWindow)
        self.action_open_dataset.setObjectName(u"action_open_dataset")
        self.action_save_session = QAction(MainWindow)
        self.action_save_session.setObjectName(u"action_save_session")
        self.action_load_session = QAction(MainWindow)
        self.action_load_session.setObjectName(u"action_load_session")
        self.action_export_data = QAction(MainWindow)
        self.action_export_data.setObjectName(u"action_export_data")
        self.action_exit = QAction(MainWindow)
        self.action_exit.setObjectName(u"action_exit")
        self.action_new_2d_plot = QAction(MainWindow)
        self.action_new_2d_plot.setObjectName(u"action_new_2d_plot")
        self.action_new_3d_plot = QAction(MainWindow)
        self.action_new_3d_plot.setObjectName(u"action_new_3d_plot")
        self.action_reset_layout = QAction(MainWindow)
        self.action_reset_layout.setObjectName(u"action_reset_layout")
        self.action_interpolate = QAction(MainWindow)
        self.action_interpolate.setObjectName(u"action_interpolate")
        self.action_derivative = QAction(MainWindow)
        self.action_derivative.setObjectName(u"action_derivative")
        self.action_integral = QAction(MainWindow)
        self.action_integral.setObjectName(u"action_integral")
        self.action_clear_cache = QAction(MainWindow)
        self.action_clear_cache.setObjectName(u"action_clear_cache")
        self.action_settings = QAction(MainWindow)
        self.action_settings.setObjectName(u"action_settings")
        self.action_about = QAction(MainWindow)
        self.action_about.setObjectName(u"action_about")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(1)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(2, 2, 2, 2)
        self.main_splitter = QSplitter(self.centralwidget)
        self.main_splitter.setObjectName(u"main_splitter")
        self.main_splitter.setOrientation(Qt.Horizontal)
        self.main_splitter.setHandleWidth(3)
        self.main_splitter.setChildrenCollapsible(True)
        self.main_splitter.setStyleSheet(u"QSplitter::handle {\n"
"    background-color: #dee2e6;\n"
"    border: 1px solid #ced4da;\n"
"}\n"
"QSplitter::handle:hover {\n"
"    background-color: #0d6efd;\n"
"}\n"
"QSplitter::handle:horizontal {\n"
"    width: 3px;\n"
"}")
        self.left_frame = QFrame(self.main_splitter)
        self.left_frame.setObjectName(u"left_frame")
        self.left_frame.setMinimumSize(QSize(240, 0))
        self.left_frame.setMaximumSize(QSize(300, 16777215))
        self.left_frame.setFrameShape(QFrame.StyledPanel)
        self.left_frame.setFrameShadow(QFrame.Raised)
        self.left_frame.setStyleSheet(u"QFrame {\n"
"    border: 1px solid #e9ecef;\n"
"    border-radius: 4px;\n"
"    background-color: #fafafa;\n"
"}")
        self.left_layout = QVBoxLayout(self.left_frame)
        self.left_layout.setSpacing(2)
        self.left_layout.setObjectName(u"left_layout")
        self.left_layout.setContentsMargins(2, 2, 2, 2)
        self.data_panel_placeholder = QWidget(self.left_frame)
        self.data_panel_placeholder.setObjectName(u"data_panel_placeholder")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.data_panel_placeholder.sizePolicy().hasHeightForWidth())
        self.data_panel_placeholder.setSizePolicy(sizePolicy)

        self.left_layout.addWidget(self.data_panel_placeholder)

        self.main_splitter.addWidget(self.left_frame)
        self.center_frame = QFrame(self.main_splitter)
        self.center_frame.setObjectName(u"center_frame")
        self.center_frame.setFrameShape(QFrame.StyledPanel)
        self.center_frame.setFrameShadow(QFrame.Raised)
        self.center_frame.setStyleSheet(u"QFrame {\n"
"    border: 1px solid #e9ecef;\n"
"    border-radius: 4px;\n"
"    background-color: #ffffff;\n"
"}")
        self.center_layout = QVBoxLayout(self.center_frame)
        self.center_layout.setSpacing(2)
        self.center_layout.setObjectName(u"center_layout")
        self.center_layout.setContentsMargins(2, 2, 2, 2)
        self.viz_panel_placeholder = QWidget(self.center_frame)
        self.viz_panel_placeholder.setObjectName(u"viz_panel_placeholder")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.viz_panel_placeholder.sizePolicy().hasHeightForWidth())
        self.viz_panel_placeholder.setSizePolicy(sizePolicy1)

        self.center_layout.addWidget(self.viz_panel_placeholder)

        self.main_splitter.addWidget(self.center_frame)
        self.right_frame = QFrame(self.main_splitter)
        self.right_frame.setObjectName(u"right_frame")
        self.right_frame.setMinimumSize(QSize(200, 0))
        self.right_frame.setMaximumSize(QSize(280, 16777215))
        self.right_frame.setFrameShape(QFrame.StyledPanel)
        self.right_frame.setFrameShadow(QFrame.Raised)
        self.right_frame.setStyleSheet(u"QFrame {\n"
"    border: 1px solid #e9ecef;\n"
"    border-radius: 4px;\n"
"    background-color: #fafafa;\n"
"}")
        self.right_layout = QVBoxLayout(self.right_frame)
        self.right_layout.setSpacing(2)
        self.right_layout.setObjectName(u"right_layout")
        self.right_layout.setContentsMargins(2, 2, 2, 2)
        self.operations_panel_placeholder = QWidget(self.right_frame)
        self.operations_panel_placeholder.setObjectName(u"operations_panel_placeholder")
        sizePolicy.setHeightForWidth(self.operations_panel_placeholder.sizePolicy().hasHeightForWidth())
        self.operations_panel_placeholder.setSizePolicy(sizePolicy)

        self.right_layout.addWidget(self.operations_panel_placeholder)

        self.main_splitter.addWidget(self.right_frame)

        self.horizontalLayout.addWidget(self.main_splitter)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1800, 30))
        self.menubar.setStyleSheet(u"QMenuBar {\n"
"    background-color: #ffffff;\n"
"    border-bottom: 1px solid #e9ecef;\n"
"    padding: 4px;\n"
"}\n"
"QMenuBar::item {\n"
"    background: transparent;\n"
"    padding: 6px 12px;\n"
"    border-radius: 4px;\n"
"}\n"
"QMenuBar::item:selected {\n"
"    background-color: #e9ecef;\n"
"}\n"
"QMenu {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #e9ecef;\n"
"    border-radius: 6px;\n"
"    padding: 4px;\n"
"}\n"
"QMenu::item {\n"
"    padding: 8px 24px;\n"
"    border-radius: 4px;\n"
"}\n"
"QMenu::item:selected {\n"
"    background-color: #0d6efd;\n"
"    color: white;\n"
"}")
        self.menu_file = QMenu(self.menubar)
        self.menu_file.setObjectName(u"menu_file")
        self.menu_view = QMenu(self.menubar)
        self.menu_view.setObjectName(u"menu_view")
        self.menu_operations = QMenu(self.menubar)
        self.menu_operations.setObjectName(u"menu_operations")
        self.menu_tools = QMenu(self.menubar)
        self.menu_tools.setObjectName(u"menu_tools")
        self.menu_help = QMenu(self.menubar)
        self.menu_help.setObjectName(u"menu_help")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        self.statusbar.setStyleSheet(u"QStatusBar {\n"
"    background-color: #ffffff;\n"
"    border-top: 1px solid #e9ecef;\n"
"    padding: 4px 8px;\n"
"}")
        MainWindow.setStatusBar(self.statusbar)
        self.toolbar = QToolBar(MainWindow)
        self.toolbar.setObjectName(u"toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(24, 24))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        self.menubar.addAction(self.menu_file.menuAction())
        self.menubar.addAction(self.menu_view.menuAction())
        self.menubar.addAction(self.menu_operations.menuAction())
        self.menubar.addAction(self.menu_tools.menuAction())
        self.menubar.addAction(self.menu_help.menuAction())
        self.menu_file.addAction(self.action_open_dataset)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_save_session)
        self.menu_file.addAction(self.action_load_session)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_export_data)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_exit)
        self.menu_view.addAction(self.action_new_2d_plot)
        self.menu_view.addAction(self.action_new_3d_plot)
        self.menu_view.addSeparator()
        self.menu_view.addAction(self.action_reset_layout)
        self.menu_operations.addAction(self.action_interpolate)
        self.menu_operations.addAction(self.action_derivative)
        self.menu_operations.addAction(self.action_integral)
        self.menu_tools.addAction(self.action_clear_cache)
        self.menu_tools.addAction(self.action_settings)
        self.menu_help.addAction(self.action_about)
        self.toolbar.addAction(self.action_open_dataset)
        self.toolbar.addAction(self.action_save_session)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.action_new_2d_plot)
        self.toolbar.addAction(self.action_new_3d_plot)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.action_interpolate)
        self.toolbar.addAction(self.action_derivative)
        self.toolbar.addAction(self.action_integral)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.action_export_data)
        self.toolbar.addAction(self.action_settings)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Platform Base v2.0 - An\u00e1lise de S\u00e9ries Temporais", None))
        self.action_open_dataset.setText(QCoreApplication.translate("MainWindow", u"Abrir", None))
        self.action_open_dataset.setIconText(QCoreApplication.translate("MainWindow", u"\ud83d\udcc1 Abrir", None))
#if QT_CONFIG(tooltip)
        self.action_open_dataset.setToolTip(QCoreApplication.translate("MainWindow", u"Abrir dataset (Ctrl+O)", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.action_open_dataset.setStatusTip(QCoreApplication.translate("MainWindow", u"Abrir arquivo de dados (CSV, Excel, Parquet, HDF5)", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
        self.action_open_dataset.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.action_save_session.setText(QCoreApplication.translate("MainWindow", u"\ud83d\udcbe &Salvar Sess\u00e3o...", None))
        self.action_save_session.setIconText(QCoreApplication.translate("MainWindow", u"\ud83d\udcbe Salvar", None))
#if QT_CONFIG(tooltip)
        self.action_save_session.setToolTip(QCoreApplication.translate("MainWindow", u"Salvar sess\u00e3o (Ctrl+S)", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.action_save_session.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.action_load_session.setText(QCoreApplication.translate("MainWindow", u"\ud83d\udcc2 &Carregar Sess\u00e3o...", None))
        self.action_export_data.setText(QCoreApplication.translate("MainWindow", u"\ud83d\udce4 &Exportar Dados...", None))
        self.action_export_data.setIconText(QCoreApplication.translate("MainWindow", u"\ud83d\udce4 Exportar", None))
#if QT_CONFIG(tooltip)
        self.action_export_data.setToolTip(QCoreApplication.translate("MainWindow", u"Exportar dados processados", None))
#endif // QT_CONFIG(tooltip)
        self.action_exit.setText(QCoreApplication.translate("MainWindow", u"\ud83d\udeaa &Sair", None))
#if QT_CONFIG(shortcut)
        self.action_exit.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Q", None))
#endif // QT_CONFIG(shortcut)
        self.action_new_2d_plot.setText(QCoreApplication.translate("MainWindow", u"\ud83d\udcca Novo Gr\u00e1fico &2D", None))
        self.action_new_2d_plot.setIconText(QCoreApplication.translate("MainWindow", u"\ud83d\udcca Gr\u00e1fico 2D", None))
#if QT_CONFIG(tooltip)
        self.action_new_2d_plot.setToolTip(QCoreApplication.translate("MainWindow", u"Criar gr\u00e1fico 2D", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.action_new_2d_plot.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+2", None))
#endif // QT_CONFIG(shortcut)
        self.action_new_3d_plot.setText(QCoreApplication.translate("MainWindow", u"\ud83d\udcc8 Novo Gr\u00e1fico &3D", None))
        self.action_new_3d_plot.setIconText(QCoreApplication.translate("MainWindow", u"\ud83d\udcc8 Gr\u00e1fico 3D", None))
#if QT_CONFIG(tooltip)
        self.action_new_3d_plot.setToolTip(QCoreApplication.translate("MainWindow", u"Criar gr\u00e1fico 3D", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.action_new_3d_plot.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+3", None))
#endif // QT_CONFIG(shortcut)
        self.action_reset_layout.setText(QCoreApplication.translate("MainWindow", u"\ud83d\udd04 &Resetar Layout", None))
        self.action_interpolate.setText(QCoreApplication.translate("MainWindow", u"\ud83d\udd17 &Interpolar S\u00e9rie...", None))
        self.action_interpolate.setIconText(QCoreApplication.translate("MainWindow", u"\u26a1 Interpolar", None))
#if QT_CONFIG(tooltip)
        self.action_interpolate.setToolTip(QCoreApplication.translate("MainWindow", u"Interpolar s\u00e9rie selecionada", None))
#endif // QT_CONFIG(tooltip)
        self.action_derivative.setText(QCoreApplication.translate("MainWindow", u"\ud83d\udcd0 &Derivada...", None))
        self.action_derivative.setIconText(QCoreApplication.translate("MainWindow", u"\ud83d\udcd0 Derivada", None))
#if QT_CONFIG(tooltip)
        self.action_derivative.setToolTip(QCoreApplication.translate("MainWindow", u"Calcular derivada", None))
#endif // QT_CONFIG(tooltip)
        self.action_integral.setText(QCoreApplication.translate("MainWindow", u"\u222b &Integral...", None))
        self.action_integral.setIconText(QCoreApplication.translate("MainWindow", u"\u222b Integral", None))
#if QT_CONFIG(tooltip)
        self.action_integral.setToolTip(QCoreApplication.translate("MainWindow", u"Calcular integral", None))
#endif // QT_CONFIG(tooltip)
        self.action_clear_cache.setText(QCoreApplication.translate("MainWindow", u"\ud83d\uddd1\ufe0f Limpar &Cache", None))
        self.action_settings.setText(QCoreApplication.translate("MainWindow", u"\u2699\ufe0f &Configura\u00e7\u00f5es...", None))
        self.action_settings.setIconText(QCoreApplication.translate("MainWindow", u"\u2699\ufe0f Config", None))
#if QT_CONFIG(tooltip)
        self.action_settings.setToolTip(QCoreApplication.translate("MainWindow", u"Configura\u00e7\u00f5es da aplica\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.action_about.setText(QCoreApplication.translate("MainWindow", u"\u2139\ufe0f &Sobre...", None))
        self.menu_file.setTitle(QCoreApplication.translate("MainWindow", u"\ud83d\udcc1 &Arquivo", None))
        self.menu_view.setTitle(QCoreApplication.translate("MainWindow", u"\ud83d\udc41\ufe0f &Visualizar", None))
        self.menu_operations.setTitle(QCoreApplication.translate("MainWindow", u"\u26a1 &Opera\u00e7\u00f5es", None))
        self.menu_tools.setTitle(QCoreApplication.translate("MainWindow", u"\ud83d\udd27 &Ferramentas", None))
        self.menu_help.setTitle(QCoreApplication.translate("MainWindow", u"\u2753 &Ajuda", None))
        self.toolbar.setWindowTitle(QCoreApplication.translate("MainWindow", u"Ferramentas", None))
    # retranslateUi

