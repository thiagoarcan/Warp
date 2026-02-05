"""
DataTablesPanel - Painel de tabelas de dados

Exibe diferentes visões dos dados: brutos, interpolados, sincronizados, calculados
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHeaderView,
    QLabel,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QMessageBox,
    QFileDialog,
)
import pandas as pd
import numpy as np


class DataTableView(QWidget):
    """View única para uma tabela de dados"""
    
    export_requested = pyqtSignal(str)  # Tipo de dados a exportar
    
    def __init__(self, table_name: str, parent=None):
        super().__init__(parent)
        self.table_name = table_name
        self._data = None
        self._init_ui()
    
    def _init_ui(self):
        """Inicializa a interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header com informações e botões
        header_layout = QHBoxLayout()
        
        self.info_label = QLabel("Sem dados")
        header_layout.addWidget(self.info_label)
        
        header_layout.addStretch()
        
        # Botão de exportar
        export_btn = QPushButton("💾 Exportar")
        export_btn.setToolTip(f"Exportar dados {self.table_name}")
        export_btn.clicked.connect(lambda: self.export_requested.emit(self.table_name))
        header_layout.addWidget(export_btn)
        
        # Botão de copiar
        copy_btn = QPushButton("📋 Copiar")
        copy_btn.setToolTip("Copiar dados para área de transferência")
        copy_btn.clicked.connect(self._copy_to_clipboard)
        header_layout.addWidget(copy_btn)
        
        layout.addLayout(header_layout)
        
        # Tabela
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
    
    def set_data(self, data: pd.DataFrame):
        """Define os dados a serem exibidos"""
        self._data = data
        
        if data is None or data.empty:
            self.info_label.setText("Sem dados")
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return
        
        # Atualiza info
        rows, cols = data.shape
        self.info_label.setText(f"📊 {rows:,} linhas × {cols} colunas")
        
        # Preenche tabela
        self.table.setRowCount(rows)
        self.table.setColumnCount(cols)
        self.table.setHorizontalHeaderLabels([str(col) for col in data.columns])
        
        for i in range(rows):
            for j in range(cols):
                value = data.iloc[i, j]
                
                # Formata valor baseado no tipo
                if pd.isna(value):
                    text = "NaN"
                elif isinstance(value, (int, np.integer)):
                    text = f"{value:,}"
                elif isinstance(value, (float, np.floating)):
                    text = f"{value:.6g}"
                elif isinstance(value, pd.Timestamp):
                    text = str(value)
                else:
                    text = str(value)
                
                item = QTableWidgetItem(text)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Read-only
                self.table.setItem(i, j, item)
        
        # Ajusta largura das colunas
        self.table.resizeColumnsToContents()
    
    def _copy_to_clipboard(self):
        """Copia dados selecionados para área de transferência"""
        if self._data is None or self._data.empty:
            return
        
        from PyQt6.QtWidgets import QApplication
        
        # Se houver seleção, copia apenas seleção
        selected_ranges = self.table.selectedRanges()
        if selected_ranges:
            selected_data = []
            for sel_range in selected_ranges:
                for row in range(sel_range.topRow(), sel_range.bottomRow() + 1):
                    row_data = []
                    for col in range(sel_range.leftColumn(), sel_range.rightColumn() + 1):
                        item = self.table.item(row, col)
                        row_data.append(item.text() if item else "")
                    selected_data.append("\t".join(row_data))
            
            clipboard_text = "\n".join(selected_data)
        else:
            # Copia todos os dados
            clipboard_text = self._data.to_csv(sep="\t", index=False)
        
        QApplication.clipboard().setText(clipboard_text)
        
        # Feedback visual
        QMessageBox.information(
            self,
            "Copiado",
            "Dados copiados para área de transferência"
        )
    
    def get_data(self) -> pd.DataFrame | None:
        """Retorna os dados atuais"""
        return self._data


class DataTablesPanel(QWidget):
    """
    Painel de tabelas de dados com abas.
    
    Exibe:
    - Dados brutos (raw)
    - Dados interpolados (interpolated)
    - Dados sincronizados (synchronized)
    - Dados calculados (calculated)
    - Resultados de operações (results)
    """
    
    export_requested = pyqtSignal(str, str)  # (tipo, filepath)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._views = {}
    
    def _init_ui(self):
        """Inicializa a interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget para diferentes visões
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        layout.addWidget(self.tabs)
        
        # Cria abas
        self._create_tab("raw", "📄 Dados Brutos")
        self._create_tab("interpolated", "📈 Interpolados")
        self._create_tab("synchronized", "🔄 Sincronizados")
        self._create_tab("calculated", "🧮 Calculados")
        self._create_tab("results", "📊 Resultados")
    
    def _create_tab(self, key: str, title: str):
        """Cria uma aba com tabela"""
        view = DataTableView(title)
        view.export_requested.connect(self._on_export_requested)
        self.tabs.addTab(view, title)
        self._views[key] = view
    
    def set_raw_data(self, data: pd.DataFrame):
        """Define dados brutos"""
        self._views["raw"].set_data(data)
    
    def set_interpolated_data(self, data: pd.DataFrame):
        """Define dados interpolados"""
        self._views["interpolated"].set_data(data)
    
    def set_synchronized_data(self, data: pd.DataFrame):
        """Define dados sincronizados"""
        self._views["synchronized"].set_data(data)
    
    def set_calculated_data(self, data: pd.DataFrame):
        """Define dados calculados"""
        self._views["calculated"].set_data(data)
    
    def set_results_data(self, data: pd.DataFrame):
        """Define resultados"""
        self._views["results"].set_data(data)
    
    def _on_export_requested(self, table_name: str):
        """Handler para exportação de dados"""
        # Determina qual view requisitou a exportação
        view = None
        data_type = None
        for key, v in self._views.items():
            if v.table_name == table_name:
                view = v
                data_type = key
                break
        
        if not view or view.get_data() is None:
            QMessageBox.warning(
                self,
                "Sem dados",
                "Não há dados para exportar nesta tabela"
            )
            return
        
        # Diálogo de salvar arquivo
        filepath, selected_filter = QFileDialog.getSaveFileName(
            self,
            f"Exportar {table_name}",
            f"dados_{data_type}.csv",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;All Files (*)"
        )
        
        if not filepath:
            return
        
        try:
            data = view.get_data()
            
            if filepath.endswith('.xlsx'):
                data.to_excel(filepath, index=False)
            else:
                data.to_csv(filepath, index=False)
            
            QMessageBox.information(
                self,
                "Exportado",
                f"Dados exportados para:\n{filepath}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao exportar dados:\n{str(e)}"
            )
    
    def clear_all(self):
        """Limpa todas as tabelas"""
        for view in self._views.values():
            view.set_data(None)
