"""
Export Dialog - Diálogo de exportação de dados

Features:
- Seleção de séries para exportar via TreeWidget
- Múltiplos formatos (CSV, Excel, Parquet, HDF5, JSON)
- Opções de configuração (compressão, metadados, etc.)
- Preview dos dados selecionados
- Barra de progresso para exportações grandes

Interface carregada de: desktop/ui_files/exportDialog.ui
Todos os widgets são definidos no arquivo .ui - NENHUMA CRIAÇÃO PROGRAMÁTICA.
"""

from __future__ import annotations

import contextlib
from pathlib import Path
from typing import Any

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)

from platform_base.ui.ui_loader_mixin import UiLoaderMixin
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
            import pandas as pd

            self.progress_updated.emit(10, "Preparando dados...")

            df = self.data if isinstance(self.data, pd.DataFrame) else pd.DataFrame(self.data)
            total_rows = len(df)

            self.progress_updated.emit(30, f"Exportando {total_rows} linhas...")

            fmt = self.config.get("format", "csv")
            output_path = Path(self.output_path)

            if fmt == "csv":
                df.to_csv(output_path, index=False)
            elif fmt == "xlsx":
                df.to_excel(output_path, index=False, engine="openpyxl")
            elif fmt == "parquet":
                df.to_parquet(output_path, index=False)
            elif fmt == "hdf5":
                df.to_hdf(output_path, key="data", mode="w")
            elif fmt == "json":
                df.to_json(output_path, orient="records", indent=2)

            self.progress_updated.emit(90, "Finalizando...")

            result = {
                "path": str(output_path),
                "size_bytes": output_path.stat().st_size,
                "rows_exported": total_rows,
                "format": fmt,
            }

            self.progress_updated.emit(100, "Exportação concluída!")
            self.export_completed.emit(result)

        except Exception as e:
            logger.exception("export_failed")
            self.export_failed.emit(str(e))


class ExportDialog(QDialog, UiLoaderMixin):
    """
    Diálogo completo de exportação de dados
    
    Interface 100% carregada do arquivo .ui via UiLoaderMixin.
    Nenhum widget é criado programaticamente.
    """
    
    UI_FILE = "exportDialog.ui"

    export_requested = pyqtSignal(dict)  # config

    def __init__(self, available_series: list[tuple[str, str, int]] | None = None,
                 parent: QWidget | None = None):
        """
        Args:
            available_series: Lista de (dataset_name, series_name, row_count)
            parent: Widget pai
        """
        super().__init__(parent)

        self.available_series = available_series or []
        self.selected_series = []
        self.export_worker = None

        if not self._load_ui():
            raise RuntimeError(
                f"Falha ao carregar arquivo UI: {self.UI_FILE}. "
                "Verifique se existe em desktop/ui_files/"
            )
        
        self._setup_ui_from_file()
        self._populate_series_tree()
        self._setup_connections()
        self._initialize_widget_states()
        
        logger.debug("export_dialog_initialized", ui_loaded=self._ui_loaded)

    def _setup_ui_from_file(self):
        """Busca referências a todos os widgets definidos no arquivo .ui"""
        
        # === Widgets principais ===
        self._main_splitter = self.findChild(QSplitter, "mainSplitter")
        self._button_box = self.findChild(QDialogButtonBox, "buttonBox")
        
        # === Painel de seleção de séries ===
        self._series_tree = self.findChild(QTreeWidget, "seriesTree")
        self._select_all_btn = self.findChild(QPushButton, "selectAllBtn")
        self._clear_selection_btn = self.findChild(QPushButton, "clearSelectionBtn")
        self._selection_info = self.findChild(QLabel, "selectionInfoLabel")
        
        # === Tabs de configuração ===
        self._config_tabs = self.findChild(QTabWidget, "configTabs")
        
        # === Aba Formato ===
        self._format_combo = self.findChild(QComboBox, "formatCombo")
        self._delimiter_combo = self.findChild(QComboBox, "delimiterCombo")
        self._encoding_combo = self.findChild(QComboBox, "encodingCombo")
        self._decimal_combo = self.findChild(QComboBox, "decimalCombo")
        
        # === Aba Opções ===
        self._include_header_check = self.findChild(QCheckBox, "includeHeaderCheck")
        self._include_index_check = self.findChild(QCheckBox, "includeIndexCheck")
        self._include_metadata_check = self.findChild(QCheckBox, "includeMetadataCheck")
        self._compress_check = self.findChild(QCheckBox, "compressCheck")
        self._date_format_check = self.findChild(QCheckBox, "dateFormatCheck")
        
        # === Aba Preview ===
        self._preview_text = self.findChild(QTextEdit, "previewText")
        
        # === Destino ===
        self._path_edit = self.findChild(QLineEdit, "pathEdit")
        self._browse_btn = self.findChild(QPushButton, "browseBtn")
        
        # === Progresso ===
        self._progress_bar = self.findChild(QProgressBar, "progressBar")
        self._progress_label = self.findChild(QLabel, "progressLabel")
        
        # === Botão Preview ===
        self._preview_btn = self.findChild(QPushButton, "previewBtn")
        
        # Validação
        self._validate_widgets()
        
        logger.debug("export_dialog_ui_widgets_loaded")

    def _validate_widgets(self):
        """Valida que todos os widgets essenciais foram encontrados no .ui"""
        required_widgets = {
            "seriesTree": self._series_tree,
            "formatCombo": self._format_combo,
            "delimiterCombo": self._delimiter_combo,
            "encodingCombo": self._encoding_combo,
            "decimalCombo": self._decimal_combo,
            "includeHeaderCheck": self._include_header_check,
            "includeIndexCheck": self._include_index_check,
            "includeMetadataCheck": self._include_metadata_check,
            "compressCheck": self._compress_check,
            "dateFormatCheck": self._date_format_check,
            "previewText": self._preview_text,
            "pathEdit": self._path_edit,
            "browseBtn": self._browse_btn,
            "progressBar": self._progress_bar,
            "buttonBox": self._button_box,
        }
        
        missing = [name for name, widget in required_widgets.items() if widget is None]
        
        if missing:
            raise RuntimeError(
                f"Widgets ausentes no arquivo .ui: {', '.join(missing)}. "
                f"Verifique se {self.UI_FILE} está completo."
            )

    def _setup_connections(self):
        """Configura conexões de sinais entre widgets"""
        # Seleção de séries
        if self._select_all_btn:
            self._select_all_btn.clicked.connect(self._select_all_series)
        if self._clear_selection_btn:
            self._clear_selection_btn.clicked.connect(self._clear_selection)
        self._series_tree.itemChanged.connect(self._on_series_selection_changed)
        
        # Formato
        self._format_combo.currentIndexChanged.connect(self._on_format_changed)
        
        # Navegação
        self._browse_btn.clicked.connect(self._browse_destination)
        
        # Preview
        if self._preview_btn:
            self._preview_btn.clicked.connect(self._show_preview)
        
        # Botões
        if self._button_box:
            self._button_box.accepted.connect(self._start_export)
            self._button_box.rejected.connect(self.reject)

    def _initialize_widget_states(self):
        """Inicializa estados dos widgets"""
        self._on_format_changed(0)

    def _populate_series_tree(self):
        """Popula tree com séries disponíveis"""
        self._series_tree.clear()

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

            self._series_tree.addTopLevelItem(dataset_item)

        self._series_tree.expandAll()

    def _on_series_selection_changed(self, item: QTreeWidgetItem, column: int):
        """Atualiza quando seleção muda"""
        if column != 0:
            return

        if item.childCount() > 0:
            state = item.checkState(0)
            for i in range(item.childCount()):
                child = item.child(i)
                child.setCheckState(0, state)

        self._update_selection_count()

    def _update_selection_count(self):
        """Atualiza contagem de seleção"""
        count = 0
        total_rows = 0

        for i in range(self._series_tree.topLevelItemCount()):
            dataset_item = self._series_tree.topLevelItem(i)
            for j in range(dataset_item.childCount()):
                child = dataset_item.child(j)
                if child.checkState(0) == Qt.CheckState.Checked:
                    count += 1
                    with contextlib.suppress(ValueError):
                        total_rows += int(child.text(1))

        if self._selection_info:
            self._selection_info.setText(f"{count} séries selecionadas ({total_rows:,} linhas total)")

    def _select_all_series(self):
        """Seleciona todas as séries"""
        for i in range(self._series_tree.topLevelItemCount()):
            item = self._series_tree.topLevelItem(i)
            item.setCheckState(0, Qt.CheckState.Checked)

    def _clear_selection(self):
        """Limpa seleção"""
        for i in range(self._series_tree.topLevelItemCount()):
            item = self._series_tree.topLevelItem(i)
            item.setCheckState(0, Qt.CheckState.Unchecked)

    def _on_format_changed(self, index: int):
        """Atualiza opções conforme formato"""
        format_text = self._format_combo.currentText().lower()

        is_csv = "csv" in format_text
        self._delimiter_combo.setEnabled(is_csv)
        self._encoding_combo.setEnabled(is_csv or "json" in format_text)
        self._decimal_combo.setEnabled(is_csv)

        if self._path_edit.text():
            self._update_path_extension()

    def _update_path_extension(self):
        """Atualiza extensão do arquivo conforme formato"""
        current_path = self._path_edit.text()
        if not current_path:
            return

        path = Path(current_path)
        ext_map = {
            "CSV": ".csv",
            "Excel": ".xlsx",
            "Parquet": ".parquet",
            "HDF5": ".h5",
            "JSON": ".json",
        }

        format_text = self._format_combo.currentText()
        for key, ext in ext_map.items():
            if key in format_text:
                new_path = path.with_suffix(ext)
                self._path_edit.setText(str(new_path))
                break

    def _browse_destination(self):
        """Abre diálogo para selecionar destino"""
        format_text = self._format_combo.currentText()

        filter_map = {
            "CSV": "CSV Files (*.csv)",
            "Excel": "Excel Files (*.xlsx)",
            "Parquet": "Parquet Files (*.parquet)",
            "HDF5": "HDF5 Files (*.h5 *.hdf5)",
            "JSON": "JSON Files (*.json)",
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
            file_filter,
        )

        if path:
            self._path_edit.setText(path)

    def _show_preview(self):
        """Mostra preview dos dados"""
        selected = self._get_selected_series()

        if not selected:
            self._preview_text.setPlainText("Nenhuma série selecionada para preview.")
            return

        preview_lines = [
            "# Preview de Exportação",
            f"# Séries selecionadas: {len(selected)}",
            f"# Formato: {self._format_combo.currentText()}",
            "",
        ]

        headers = ["timestamp"]
        for dataset, series in selected[:5]:
            headers.append(f"{dataset}.{series}")

        preview_lines.append(",".join(headers))

        import random
        for i in range(10):
            row = [f"2024-01-01 00:00:{i:02d}"]
            for _ in range(len(headers) - 1):
                row.append(f"{random.uniform(0, 100):.2f}")
            preview_lines.append(",".join(row))

        preview_lines.extend(["...", "# Total de linhas estimado: (calculado na exportação)"])
        self._preview_text.setPlainText("\n".join(preview_lines))

    def _get_selected_series(self) -> list[tuple[str, str]]:
        """Retorna lista de séries selecionadas"""
        selected = []

        for i in range(self._series_tree.topLevelItemCount()):
            dataset_item = self._series_tree.topLevelItem(i)
            for j in range(dataset_item.childCount()):
                child = dataset_item.child(j)
                if child.checkState(0) == Qt.CheckState.Checked:
                    data = child.data(0, Qt.ItemDataRole.UserRole)
                    if data:
                        selected.append(data)

        return selected

    def _get_export_config(self) -> dict[str, Any]:
        """Retorna configuração de exportação"""
        format_text = self._format_combo.currentText().lower()

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

        delimiter_text = self._delimiter_combo.currentText()
        if "vírgula" in delimiter_text.lower():
            delimiter = ","
        elif "ponto e vírgula" in delimiter_text.lower():
            delimiter = ";"
        elif "tab" in delimiter_text.lower():
            delimiter = "\t"
        else:
            delimiter = " "

        decimal_text = self._decimal_combo.currentText()
        decimal = "." if "ponto" in decimal_text.lower() else ","

        return {
            "format": fmt,
            "output_path": self._path_edit.text(),
            "selected_series": self._get_selected_series(),
            "delimiter": delimiter,
            "encoding": self._encoding_combo.currentText(),
            "decimal_separator": decimal,
            "include_header": self._include_header_check.isChecked(),
            "include_index": self._include_index_check.isChecked(),
            "include_metadata": self._include_metadata_check.isChecked(),
            "compress": self._compress_check.isChecked(),
            "date_format_iso": self._date_format_check.isChecked(),
        }

    def _start_export(self):
        """Inicia exportação"""
        if not self._path_edit.text():
            QMessageBox.warning(self, "Atenção", "Selecione um destino para o arquivo.")
            return
        
        selected = self._get_selected_series()
        if not selected:
            QMessageBox.warning(self, "Atenção", "Selecione ao menos uma série para exportar.")
            return
        
        config = self._get_export_config()
        self.export_requested.emit(config)
        self.accept()

    def get_config(self) -> dict[str, Any] | None:
        """Retorna configuração se diálogo foi aceito"""
        if self.result() == QDialog.DialogCode.Accepted:
            return self._get_export_config()
        return None


def show_export_dialog(available_series: list[tuple[str, str, int]] | None = None,
                       parent: QWidget | None = None) -> dict[str, Any] | None:
    """
    Função de conveniência para mostrar o diálogo de exportação

    Args:
        available_series: Lista de (dataset_name, series_name, row_count)
        parent: Widget pai
        
    Returns:
        Dicionário com configuração ou None se cancelado
    """
    dialog = ExportDialog(available_series, parent)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_config()

    return None
