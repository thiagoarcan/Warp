#!/usr/bin/env python3
"""Teste ComboBox com MATPLOTLIB e SHORTCUTS como na aplicação real"""

import sys

# Importar matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

# Stylesheet EXATO do OperationsPanel
OPERATIONS_STYLE = """
    QWidget {
        background-color: #ffffff;
    }
    QGroupBox {
        font-weight: bold;
        border: 1px solid #e9ecef;
        border-radius: 6px;
        margin-top: 8px;
        padding-top: 8px;
        background-color: #f8f9fa;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 8px;
        padding: 2px 6px;
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 3px;
    }
    QPushButton {
        background-color: #0d6efd;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #0b5ed7;
    }
    QPushButton:disabled {
        background-color: #6c757d;
    }
    QSpinBox, QDoubleSpinBox {
        border: 1px solid #ced4da;
        border-radius: 4px;
        padding: 4px 8px;
        background-color: white;
        min-height: 24px;
    }
    QComboBox {
        border: 1px solid #ced4da;
        border-radius: 4px;
        padding: 4px 8px;
        background-color: white;
        min-height: 24px;
    }
    QTabWidget::pane {
        border: 1px solid #e9ecef;
        border-radius: 4px;
        background-color: white;
    }
    QTabBar::tab {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 6px 10px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        font-size: 11px;
    }
    QTabBar::tab:selected {
        background-color: white;
        border-bottom-color: white;
    }
"""

MAIN_WINDOW_STYLE = """
    QMainWindow {
        background-color: #f8f9fa;
    }
    QSplitter::handle {
        background-color: #e9ecef;
        width: 2px;
        height: 2px;
    }
    QSplitter::handle:hover {
        background-color: #0d6efd;
    }
"""


class StableComboBox(QComboBox):
    """Mesma classe do operations_panel"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(28)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMaxVisibleItems(15)


class FakeOperationsPanel(QWidget):
    """Replica EXATA da estrutura do OperationsPanel"""
    
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(200)
        self.setMaximumWidth(320)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # MESMO stylesheet
        self.setStyleSheet(OPERATIONS_STYLE)
        
        # Header - mesmo do OperationsPanel
        header = QLabel("⚙️ Operações")
        header.setFont(QFont("", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #0d6efd; padding: 4px;")
        layout.addWidget(header)
        
        # Seletor de série global - MESMO do OperationsPanel
        series_group = QGroupBox("🎯 Série para Operações")
        series_layout = QFormLayout(series_group)
        series_layout.setContentsMargins(6, 10, 6, 6)
        
        self.series_combo = StableComboBox()
        self.series_combo.setMinimumWidth(150)
        self.series_combo.setToolTip("Selecione a série para aplicar as operações")
        self.series_combo.addItem("(Nenhum dataset carregado)")
        self.series_combo.setEnabled(False)
        series_layout.addRow("Série:", self.series_combo)
        layout.addWidget(series_group)
        
        # Tab widget - MESMO do OperationsPanel
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.North)
        layout.addWidget(tabs, stretch=1)
        
        # Tab de interpolação - MESMA estrutura
        tab = QScrollArea()
        tab.setWidgetResizable(True)
        content = QWidget()
        tab_layout = QVBoxLayout(content)
        tab_layout.setSpacing(8)
        
        method_group = QGroupBox("📐 Método")
        method_layout = QFormLayout(method_group)
        
        self.interp_combo = StableComboBox()
        self.interp_combo.addItems([
            "linear", "cubic_spline", "smoothing_spline",
            "akima", "pchip", "polynomial",
            "mls", "gpr", "lomb_scargle", "resample_grid"
        ])
        self.interp_combo.setToolTip("Método de interpolação a utilizar")
        method_layout.addRow("Método:", self.interp_combo)
        
        tab_layout.addWidget(method_group)
        tab_layout.addStretch()
        tab.setWidget(content)
        tabs.addTab(tab, "📈")
        
        # Segunda tab com mais combos
        tab2 = QScrollArea()
        tab2.setWidgetResizable(True)
        content2 = QWidget()
        tab2_layout = QVBoxLayout(content2)
        
        deriv_group = QGroupBox("📉 Derivadas")
        deriv_layout = QFormLayout(deriv_group)
        
        self.deriv_order = StableComboBox()
        self.deriv_order.addItems(["1ª Derivada", "2ª Derivada", "3ª Derivada"])
        deriv_layout.addRow("Ordem:", self.deriv_order)
        
        self.deriv_method = StableComboBox()
        self.deriv_method.addItems(["central", "forward", "backward", "savgol"])
        deriv_layout.addRow("Método:", self.deriv_method)
        
        tab2_layout.addWidget(deriv_group)
        tab2_layout.addStretch()
        tab2.setWidget(content2)
        tabs.addTab(tab2, "📊")


class TestWindow(QMainWindow):
    """Replica a estrutura do ModernMainWindow"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Teste - Estrutura EXATA ModernMainWindow")
        self.resize(800, 600)
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(1)
        
        # Splitter horizontal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(True)
        splitter.setHandleWidth(3)
        main_layout.addWidget(splitter)
        
        # Left panel
        left_frame = QFrame()
        left_frame.setMaximumWidth(300)
        left_frame.setMinimumWidth(240)
        left_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e9ecef;
                border-radius: 8px;
            }
        """)
        left_layout = QVBoxLayout(left_frame)
        left_layout.addWidget(QLabel("Painel Esquerdo"))
        left_layout.addStretch()
        splitter.addWidget(left_frame)
        
        # Center panel - COM MATPLOTLIB CANVAS
        center_frame = QFrame()
        center_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e9ecef;
                border-radius: 8px;
            }
        """)
        center_layout = QVBoxLayout(center_frame)
        center_layout.addWidget(QLabel("Painel Central com Matplotlib"))
        
        # Adicionar matplotlib canvas como na aplicação real
        self.figure = Figure(figsize=(8, 6), dpi=100, tight_layout=True,
                            facecolor="white", edgecolor="none")
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setAcceptDrops(True)
        
        # Desenhar algo no gráfico
        ax = self.figure.add_subplot(111)
        ax.plot([1, 2, 3, 4, 5], [1, 4, 2, 3, 5], '-o', label="Teste")
        ax.set_title("Gráfico de Teste")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.legend()
        
        center_layout.addWidget(self.canvas)
        splitter.addWidget(center_frame)
        
        # Right panel - OperationsPanel
        right_frame = QFrame()
        right_frame.setMaximumWidth(320)
        right_frame.setMinimumWidth(200)
        right_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e9ecef;
                border-radius: 8px;
            }
        """)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(2, 2, 2, 2)
        
        self.ops_panel = FakeOperationsPanel()
        right_layout.addWidget(self.ops_panel)
        
        splitter.addWidget(right_frame)
        
        # Tamanhos
        splitter.setSizes([280, 400, 280])
        
        # === SHORTCUTS como na aplicação real ===
        self._setup_shortcuts()
    
    def _setup_shortcuts(self):
        """Configura shortcuts como na aplicação real"""
        # Escape - pode interferir com ComboBox popup
        escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        escape_shortcut.activated.connect(lambda: print("Escape pressed"))
        
        # Delete
        delete_shortcut = QShortcut(QKeySequence("Delete"), self)
        delete_shortcut.activated.connect(lambda: print("Delete pressed"))
        
        # F5
        refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        refresh_shortcut.activated.connect(lambda: print("F5 pressed"))
        
        # Ctrl+Z
        undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        undo_shortcut.activated.connect(lambda: print("Ctrl+Z pressed"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
