#!/usr/bin/env python3
"""Teste usando os painéis REAIS da aplicação"""

import sys
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

# Importar componentes reais
from platform_base.core.dataset_store import DatasetStore
from platform_base.ui.panels.data_panel import DataPanel
from platform_base.ui.panels.operations_panel import OperationsPanel
from platform_base.ui.panels.viz_panel import VizPanel
from platform_base.ui.state import SessionState


class TestWindow(QMainWindow):
    """Janela de teste com TODOS os painéis REAIS"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Teste - TODOS os painéis REAIS")
        self.resize(1200, 800)
        
        # Criar session state real
        self.dataset_store = DatasetStore()
        self.session_state = SessionState(self.dataset_store)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(1)
        
        # Splitter horizontal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - DataPanel REAL
        left_frame = QFrame()
        left_frame.setMinimumWidth(200)
        left_frame.setMaximumWidth(300)
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(2, 2, 2, 2)
        self.data_panel = DataPanel(self.session_state)
        left_layout.addWidget(self.data_panel)
        splitter.addWidget(left_frame)
        
        # Center panel - VizPanel REAL
        center_frame = QFrame()
        center_layout = QVBoxLayout(center_frame)
        center_layout.setContentsMargins(2, 2, 2, 2)
        self.viz_panel = VizPanel(self.session_state)
        center_layout.addWidget(self.viz_panel)
        splitter.addWidget(center_frame)
        
        # Right panel - OperationsPanel REAL
        right_frame = QFrame()
        right_frame.setMaximumWidth(320)
        right_frame.setMinimumWidth(200)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(2, 2, 2, 2)
        self.ops_panel = OperationsPanel(self.session_state)
        right_layout.addWidget(self.ops_panel)
        splitter.addWidget(right_frame)
        
        splitter.setSizes([280, 600, 280])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
