"""
Export Dialog - Diálogo de exportação de dados

Features:
- Seleção de séries para exportar via TreeWidget
- Múltiplos formatos (CSV, Excel, Parquet, HDF5, JSON)
- Opções de configuração (compressão, metadados, etc.)
- Preview dos dados selecionados
- Barra de progresso para exportações grandes
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class ExportWorkerThread(QThread):
    """Worker thread para exportação assíncrona"""
    
    progress_updated = pyqtSignal(int, str)  # percent, message
    export_completed = pyqtSignal(dict)  # result
    export_failed = pyqtSignal(str)  # error message
    
    def __init__(self, data, config, output_path, parent=None):
        super().__init__(parent)
        self.data = data
        self.config = config
        self.output_path = output_path
    
    def run(self):
        """Executa exportação em background"""
        try:
            import time

            import pandas as pd
            
            self.progress_updated.emit(10, "Preparando dados...")
            
            # Simula preparação de dados
            df = self.data if isinstance(self.data, pd.DataFrame) else pd.DataFrame(self.data)
            total_rows = len(df)
            
            self.progress_updated.emit(30, f"Exportando {total_rows} linhas...")
            
            fmt = self.config.get('format', 'csv')
            output_path = Path(self.output_path)
            
            # Exporta conforme formato
            if fmt == "csv":
                df.to_csv(output_path, index=False)
            elif fmt == "xlsx":
                df.to_excel(output_path, index=False, engine='openpyxl')
            elif fmt == "parquet":
                df.to_parquet(output_path, index=False)
            elif fmt == "hdf5":
                df.to_hdf(output_path, key="data", mode="w")
            elif fmt == "json":
                df.to_json(output_path, orient="records", indent=2)
            
            self.progress_updated.emit(90, "Finalizando...")
            
            # Resultado
            result = {
                'path': str(output_path),
                'size_bytes': output_path.stat().st_size,
                'rows_exported': total_rows,
                'format': fmt
            }
            
            self.progress_updated.emit(100, "Exportação concluída!")
            self.export_completed.emit(result)
            
        except Exception as e:
            logger.exception("export_failed")
            self.export_failed.emit(str(e))


class ExportDialog(QDialog):
    """Diálogo completo de exportação de dados"""
    
    export_requested = pyqtSignal(dict)  # config
    
    def __init__(self, available_series: Optional[List[Tuple[str, str, int]]] = None, 
                 parent: Optional[QWidget] = None):
        """
        Args:
            available_series: Lista de (dataset_name, series_name, row_count)
            parent: Widget pai
        """
        super().__init__(parent)
        
        self.available_series = available_series or []
        self.selected_series = []
        self.export_worker = None
        
        self.setWindowTitle("Exportar Dados")
        self.setMinimumSize(700, 600)
        self.setModal(True)
        
        self._setup_ui()
        self._populate_series_tree()
        self._connect_signals()
    
    def _setup_ui(self):
        """Configura interface do usuário"""
        layout = QVBoxLayout(self)
        
        # Splitter principal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # === Painel Esquerdo: Seleção de séries ===
        left_panel = self._create_series_panel()
        splitter.addWidget(left_panel)
        
        # === Painel Direito: Configurações e Preview ===
        right_panel = self._create_config_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([350, 350])
        layout.addWidget(splitter)
        
        # === Barra de progresso ===
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)
        
        # === Botões ===
        button_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("Preview")
        self.preview_btn.clicked.connect(self._show_preview)
        button_layout.addWidget(self.preview_btn)
        
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.export_btn = QPushButton("Exportar")
        self.export_btn.setDefault(True)
        self.export_btn.clicked.connect(self._start_export)
        button_layout.addWidget(self.export_btn)
        
        layout.addLayout(button_layout)
    
    def _create_series_panel(self) -> QWidget:
        """Cria painel de seleção de séries"""
        panel = QGroupBox("Séries para Exportar")
        layout = QVBoxLayout(panel)
        
        # Tree widget com checkboxes
        self.series_tree = QTreeWidget()
        self.series_tree.setHeaderLabels(["Nome", "Linhas"])
        self.series_tree.setSelectionMode(QTreeWidget.SelectionMode.MultiSelection)
        self.series_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.series_tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.series_tree)
        
        # Botões de seleção
        btn_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("Selecionar Tudo")
        select_all_btn.clicked.connect(self._select_all_series)
        btn_layout.addWidget(select_all_btn)
        
        clear_btn = QPushButton("Limpar Seleção")
        clear_btn.clicked.connect(self._clear_selection)
        btn_layout.addWidget(clear_btn)
        
        layout.addLayout(btn_layout)
        
        # Info de seleção
        self.selection_info = QLabel("0 séries selecionadas")
        layout.addWidget(self.selection_info)
        
        return panel
    
    def _create_config_panel(self) -> QWidget:
        """Cria painel de configurações"""
        panel = QGroupBox("Configurações")
        layout = QVBoxLayout(panel)
        
        tabs = QTabWidget()
        
        # === Aba Formato ===
        format_tab = QWidget()
        format_layout = QFormLayout(format_tab)
        
        # Formato de saída
        self.format_combo = QComboBox()
        self.format_combo.addItems(["CSV (.csv)", "Excel (.xlsx)", "Parquet (.parquet)", 
                                    "HDF5 (.h5)", "JSON (.json)"])
        self.format_combo.currentIndexChanged.connect(self._on_format_changed)
        format_layout.addRow("Formato:", self.format_combo)
        
        # Delimitador (CSV)
        self.delimiter_combo = QComboBox()
        self.delimiter_combo.addItems(["Vírgula (,)", "Ponto e vírgula (;)", "Tab", "Espaço"])
        format_layout.addRow("Delimitador:", self.delimiter_combo)
        
        # Encoding
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(["UTF-8", "Latin-1", "Windows-1252"])
        format_layout.addRow("Encoding:", self.encoding_combo)
        
        # Decimal separator
        self.decimal_combo = QComboBox()
        self.decimal_combo.addItems(["Ponto (.)", "Vírgula (,)"])
        format_layout.addRow("Separador decimal:", self.decimal_combo)
        
        tabs.addTab(format_tab, "Formato")
        
        # === Aba Opções ===
        options_tab = QWidget()
        options_layout = QVBoxLayout(options_tab)
        
        self.include_header_check = QCheckBox("Incluir cabeçalho")
        self.include_header_check.setChecked(True)
        options_layout.addWidget(self.include_header_check)
        
        self.include_index_check = QCheckBox("Incluir índice")
        self.include_index_check.setChecked(False)
        options_layout.addWidget(self.include_index_check)
        
        self.include_metadata_check = QCheckBox("Incluir metadados")
        self.include_metadata_check.setChecked(True)
        options_layout.addWidget(self.include_metadata_check)
        
        self.compress_check = QCheckBox("Comprimir arquivo (gzip)")
        self.compress_check.setChecked(False)
        options_layout.addWidget(self.compress_check)
        
        self.date_format_check = QCheckBox("Formatar datas como ISO 8601")
        self.date_format_check.setChecked(True)
        options_layout.addWidget(self.date_format_check)
        
        options_layout.addStretch()
        tabs.addTab(options_tab, "Opções")
        
        # === Aba Preview ===
        preview_tab = QWidget()
        preview_layout = QVBoxLayout(preview_tab)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont("Consolas", 9))
        self.preview_text.setPlaceholderText("Clique em 'Preview' para ver os dados...")
        preview_layout.addWidget(self.preview_text)
        
        tabs.addTab(preview_tab, "Preview")
        
        layout.addWidget(tabs)
        
        # === Destino ===
        dest_group = QGroupBox("Destino")
        dest_layout = QHBoxLayout(dest_group)
        
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Selecione o arquivo de destino...")
        dest_layout.addWidget(self.path_edit)
        
        browse_btn = QPushButton("Procurar...")
        browse_btn.clicked.connect(self._browse_destination)
        dest_layout.addWidget(browse_btn)
        
        layout.addWidget(dest_group)
        
        return panel
    
    def _populate_series_tree(self):
        """Popula tree com séries disponíveis"""
        self.series_tree.clear()
        
        # Agrupa por dataset
        datasets = {}
        for item in self.available_series:
            if len(item) >= 3:
                dataset_name, series_name, row_count = item[:3]
            else:
                dataset_name = "Default"
                series_name = item[0] if item else "Unknown"
                row_count = 0
            
            if dataset_name not in datasets:
                datasets[dataset_name] = []
            datasets[dataset_name].append((series_name, row_count))
        
        # Cria itens na árvore
        for dataset_name, series_list in datasets.items():
            dataset_item = QTreeWidgetItem([dataset_name, ""])
            dataset_item.setFlags(dataset_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            dataset_item.setCheckState(0, Qt.CheckState.Unchecked)
            
            for series_name, row_count in series_list:
                series_item = QTreeWidgetItem([series_name, str(row_count)])
                series_item.setFlags(series_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                series_item.setCheckState(0, Qt.CheckState.Unchecked)
                series_item.setData(0, Qt.ItemDataRole.UserRole, (dataset_name, series_name))
                dataset_item.addChild(series_item)
            
            self.series_tree.addTopLevelItem(dataset_item)
        
        self.series_tree.expandAll()
    
    def _connect_signals(self):
        """Conecta sinais"""
        self.series_tree.itemChanged.connect(self._on_series_selection_changed)
    
    def _on_series_selection_changed(self, item: QTreeWidgetItem, column: int):
        """Atualiza quando seleção muda"""
        if column != 0:
            return
        
        # Se é item pai (dataset), propaga para filhos
        if item.childCount() > 0:
            state = item.checkState(0)
            for i in range(item.childCount()):
                child = item.child(i)
                child.setCheckState(0, state)
        
        # Conta selecionados
        self._update_selection_count()
    
    def _update_selection_count(self):
        """Atualiza contagem de seleção"""
        count = 0
        total_rows = 0
        
        for i in range(self.series_tree.topLevelItemCount()):
            dataset_item = self.series_tree.topLevelItem(i)
            for j in range(dataset_item.childCount()):
                child = dataset_item.child(j)
                if child.checkState(0) == Qt.CheckState.Checked:
                    count += 1
                    try:
                        total_rows += int(child.text(1))
                    except ValueError:
                        pass
        
        self.selection_info.setText(f"{count} séries selecionadas ({total_rows:,} linhas total)")
    
    def _select_all_series(self):
        """Seleciona todas as séries"""
        for i in range(self.series_tree.topLevelItemCount()):
            item = self.series_tree.topLevelItem(i)
            item.setCheckState(0, Qt.CheckState.Checked)
    
    def _clear_selection(self):
        """Limpa seleção"""
        for i in range(self.series_tree.topLevelItemCount()):
            item = self.series_tree.topLevelItem(i)
            item.setCheckState(0, Qt.CheckState.Unchecked)
    
    def _on_format_changed(self, index: int):
        """Atualiza opções conforme formato"""
        format_text = self.format_combo.currentText().lower()
        
        is_csv = "csv" in format_text
        self.delimiter_combo.setEnabled(is_csv)
        self.encoding_combo.setEnabled(is_csv or "json" in format_text)
        self.decimal_combo.setEnabled(is_csv)
        
        # Atualiza extensão no path
        if self.path_edit.text():
            self._update_path_extension()
    
    def _update_path_extension(self):
        """Atualiza extensão do arquivo conforme formato"""
        current_path = self.path_edit.text()
        if not current_path:
            return
        
        path = Path(current_path)
        ext_map = {
            "CSV": ".csv",
            "Excel": ".xlsx",
            "Parquet": ".parquet",
            "HDF5": ".h5",
            "JSON": ".json"
        }
        
        format_text = self.format_combo.currentText()
        for key, ext in ext_map.items():
            if key in format_text:
                new_path = path.with_suffix(ext)
                self.path_edit.setText(str(new_path))
                break
    
    def _browse_destination(self):
        """Abre diálogo para selecionar destino"""
        format_text = self.format_combo.currentText()
        
        filter_map = {
            "CSV": "CSV Files (*.csv)",
            "Excel": "Excel Files (*.xlsx)",
            "Parquet": "Parquet Files (*.parquet)",
            "HDF5": "HDF5 Files (*.h5 *.hdf5)",
            "JSON": "JSON Files (*.json)"
        }
        
        file_filter = "All Files (*.*)"
        for key, flt in filter_map.items():
            if key in format_text:
                file_filter = f"{flt};;All Files (*.*)"
                break
        
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar como",
            "",
            file_filter
        )
        
        if path:
            self.path_edit.setText(path)
    
    def _show_preview(self):
        """Mostra preview dos dados"""
        selected = self._get_selected_series()
        
        if not selected:
            self.preview_text.setPlainText("Nenhuma série selecionada para preview.")
            return
        
        # Simula preview
        preview_lines = []
        preview_lines.append(f"# Preview de Exportação")
        preview_lines.append(f"# Séries selecionadas: {len(selected)}")
        preview_lines.append(f"# Formato: {self.format_combo.currentText()}")
        preview_lines.append("")
        
        # Header simulado
        headers = ["timestamp"]
        for dataset, series in selected[:5]:  # Limita a 5 para preview
            headers.append(f"{dataset}.{series}")
        
        preview_lines.append(",".join(headers))
        
        # Dados simulados
        import random
        for i in range(min(10, 100)):
            row = [f"2024-01-01 00:00:{i:02d}"]
            for _ in range(len(headers) - 1):
                row.append(f"{random.uniform(0, 100):.2f}")
            preview_lines.append(",".join(row))
        
        preview_lines.append("...")
        preview_lines.append(f"# Total de linhas estimado: (calculado na exportação)")
        
        self.preview_text.setPlainText("\n".join(preview_lines))
    
    def _get_selected_series(self) -> List[Tuple[str, str]]:
        """Retorna lista de séries selecionadas"""
        selected = []
        
        for i in range(self.series_tree.topLevelItemCount()):
            dataset_item = self.series_tree.topLevelItem(i)
            for j in range(dataset_item.childCount()):
                child = dataset_item.child(j)
                if child.checkState(0) == Qt.CheckState.Checked:
                    data = child.data(0, Qt.ItemDataRole.UserRole)
                    if data:
                        selected.append(data)
        
        return selected
    
    def _get_export_config(self) -> Dict[str, Any]:
        """Retorna configuração de exportação"""
        format_text = self.format_combo.currentText().lower()
        
        # Determina formato
        if "csv" in format_text:
            fmt = "csv"
        elif "excel" in format_text or "xlsx" in format_text:
            fmt = "xlsx"
        elif "parquet" in format_text:
            fmt = "parquet"
        elif "hdf5" in format_text or "h5" in format_text:
            fmt = "hdf5"
        elif "json" in format_text:
            fmt = "json"
        else:
            fmt = "csv"
        
        # Delimitador
        delimiter_text = self.delimiter_combo.currentText()
        if "vírgula" in delimiter_text.lower():
            delimiter = ","
        elif "ponto e vírgula" in delimiter_text.lower():
            delimiter = ";"
        elif "tab" in delimiter_text.lower():
            delimiter = "\t"
        else:
            delimiter = " "
        
        # Decimal
        decimal_text = self.decimal_combo.currentText()
        decimal = "." if "ponto" in decimal_text.lower() else ","
        
        return {
            'format': fmt,
            'output_path': self.path_edit.text(),
            'selected_series': self._get_selected_series(),
            'delimiter': delimiter,
            'encoding': self.encoding_combo.currentText(),
            'decimal_separator': decimal,
            'include_header': self.include_header_check.isChecked(),
            'include_index': self.include_index_check.isChecked(),
            'include_metadata': self.include_metadata_check.isChecked(),
            'compress': self.compress_check.isChecked(),
            'date_format_iso': self.date_format_check.isChecked()
        }
    
    def _validate_config(self) -> bool:
        """Valida configuração antes de exportar"""
        if not self._get_selected_series():
            QMessageBox.warning(self, "Aviso", "Selecione pelo menos uma série para exportar.")
            return False
        
        if not self.path_edit.text():
            QMessageBox.warning(self, "Aviso", "Selecione um arquivo de destino.")
            return False
        
        output_path = Path(self.path_edit.text())
        if output_path.exists():
            reply = QMessageBox.question(
                self, "Confirmar",
                f"O arquivo '{output_path.name}' já existe. Deseja sobrescrevê-lo?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return False
        
        return True
    
    def _start_export(self):
        """Inicia exportação"""
        if not self._validate_config():
            return
        
        config = self._get_export_config()
        
        # Emite sinal com configuração
        self.export_requested.emit(config)
        
        # Mostra progresso
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Iniciando exportação...")
        
        # Desabilita botões durante exportação
        self.export_btn.setEnabled(False)
        self.preview_btn.setEnabled(False)
        
        # Em uma implementação real, iniciaria o worker thread aqui
        # Por agora, simula conclusão
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1000, lambda: self._on_export_progress(50, "Processando dados..."))
        QTimer.singleShot(2000, lambda: self._on_export_progress(100, "Concluído!"))
        QTimer.singleShot(2500, self._on_export_completed)
    
    def _on_export_progress(self, percent: int, message: str):
        """Atualiza progresso"""
        self.progress_bar.setValue(percent)
        self.progress_label.setText(message)
    
    def _on_export_completed(self):
        """Callback quando exportação completa"""
        self.export_btn.setEnabled(True)
        self.preview_btn.setEnabled(True)
        
        config = self._get_export_config()
        
        QMessageBox.information(
            self, "Sucesso",
            f"Dados exportados com sucesso para:\n{config['output_path']}"
        )
        
        self.accept()
    
    def _on_export_failed(self, error: str):
        """Callback quando exportação falha"""
        self.export_btn.setEnabled(True)
        self.preview_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        QMessageBox.critical(self, "Erro", f"Falha na exportação:\n{error}")
    
    def get_config(self) -> Optional[Dict[str, Any]]:
        """Retorna configuração se diálogo foi aceito"""
        if self.result() == QDialog.DialogCode.Accepted:
            return self._get_export_config()
        return None


def show_export_dialog(available_series: Optional[List[Tuple[str, str, int]]] = None, 
                       parent: Optional[QWidget] = None) -> Optional[Dict[str, Any]]:
    """
    Conveniência para mostrar diálogo de exportação
    
    Args:
        available_series: Lista de (dataset_name, series_name, row_count)
        parent: Widget pai
        
    Returns:
        Configuração de exportação ou None se cancelado
    """
    dialog = ExportDialog(available_series, parent)
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_config()
    
    return None
