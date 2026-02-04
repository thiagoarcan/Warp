#!/usr/bin/env python3
"""
Teste completo de todas as funcionalidades implementadas:
1. DateTime axis
2. Coordinate tooltip
3. Context menu calculations  
4. Secondary Y axis
5. Draggable legends
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime

import numpy as np
from pint import Unit
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


def test_matplotlib_widget():
    """Testa o MatplotlibWidget com datetime axis"""
    from platform_base.core.models import Series, SeriesMetadata
    from platform_base.ui.panels.viz_panel import MatplotlibWidget
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Criar dados de teste com datetime
    n_points = 100
    t_seconds = np.linspace(0, 3600, n_points)  # 1 hora de dados
    values = np.sin(2 * np.pi * t_seconds / 3600) * 100 + np.random.randn(n_points) * 10
    
    # Criar datetime array
    base_time = np.datetime64('2024-01-15T10:00:00')
    t_datetime = base_time + (t_seconds * 1e9).astype('timedelta64[ns]')
    
    # Criar série com todos os campos obrigatórios
    series = Series(
        series_id="test_series_001",
        name="Pressão",
        unit=Unit("bar"),
        values=values,
        metadata=SeriesMetadata(
            original_name="Pressão",
            source_column="pressure"
        )
    )
    
    # Criar widget
    widget = MatplotlibWidget(
        series=series,
        plot_type="line",
        dataset_name="Teste Dataset",
        t_datetime=t_datetime,
        t_seconds=t_seconds
    )
    
    # Janela principal
    window = QMainWindow()
    window.setWindowTitle("Teste Datetime Axis e Tooltip")
    window.setCentralWidget(widget)
    window.resize(1200, 800)
    window.show()
    
    print("=" * 60)
    print("TESTE DE FUNCIONALIDADES")
    print("=" * 60)
    print("1. Mova o mouse sobre o gráfico para ver coordenadas")
    print("2. Clique com botão direito para menu de contexto")
    print("3. Verifique se o eixo X mostra datetime")
    print("4. Teste arrastar a legenda")
    print("=" * 60)
    
    return app.exec()


def test_full_application():
    """Testa a aplicação completa"""
    from platform_base.main_window import MainWindow
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    print("=" * 60)
    print("APLICAÇÃO COMPLETA")
    print("=" * 60)
    print("1. Carregue um arquivo JSON com dados")
    print("2. Selecione um dataset e plote uma série")
    print("3. Verifique datetime no eixo X")
    print("4. Mova o mouse para ver coordenadas")
    print("5. Clique direito para cálculos")
    print("=" * 60)
    
    return app.exec()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Teste de funcionalidades")
    parser.add_argument("--full", action="store_true", help="Testar aplicação completa")
    parser.add_argument("--widget", action="store_true", help="Testar apenas widget matplotlib")
    args = parser.parse_args()
    
    if args.widget:
        sys.exit(test_matplotlib_widget())
    else:
        sys.exit(test_full_application())
