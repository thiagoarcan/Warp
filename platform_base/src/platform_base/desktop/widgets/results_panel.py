"""
ResultsPanel - Results and logging panel for Platform Base v2.0

Displays operation results, logs, and data quality metrics.

Interface carregada de: desktop/ui_files/resultsPanel.ui
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from platform_base.ui.ui_loader_mixin import UiLoaderMixin
from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from platform_base.desktop.session_state import SessionState
    from platform_base.desktop.signal_hub import SignalHub


logger = get_logger(__name__)


class LogWidget(QTextEdit):
    """Enhanced text widget for displaying logs with filtering"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Configure text display
        self.setReadOnly(True)
        font = QFont("Consolas", 9)  # Monospace font
        self.setFont(font)

        # Log storage
        self.log_entries: list[dict[str, Any]] = []
        self.filtered_entries: list[dict[str, Any]] = []

        # Filters
        self.level_filter = "all"
        self.text_filter = ""

        # Auto-scroll
        self.auto_scroll = True

    def add_log_entry(self, level: str, message: str, timestamp: datetime | None = None, **kwargs):
        """Add log entry"""
        if timestamp is None:
            timestamp = datetime.now()

        entry = {
            "level": level,
            "message": message,
            "timestamp": timestamp,
            "extra": kwargs,
        }

        self.log_entries.append(entry)
        self._update_filtered_entries()
        self._update_display()

    def set_level_filter(self, level: str):
        """Set log level filter"""
        self.level_filter = level
        self._update_filtered_entries()
        self._update_display()

    def set_text_filter(self, text: str):
        """Set text filter"""
        self.text_filter = text.lower()
        self._update_filtered_entries()
        self._update_display()

    def _update_filtered_entries(self):
        """Update filtered entries based on current filters"""
        self.filtered_entries = []

        for entry in self.log_entries:
            # Level filter
            if self.level_filter != "all" and entry["level"] != self.level_filter:
                continue

            # Text filter
            if self.text_filter and self.text_filter not in entry["message"].lower():
                continue

            self.filtered_entries.append(entry)

    def _update_display(self):
        """Update text display"""
        # Save current scroll position
        scrollbar = self.verticalScrollBar()
        at_bottom = scrollbar.value() == scrollbar.maximum()

        # Clear and rebuild
        self.clear()

        for entry in self.filtered_entries[-1000:]:  # Show last 1000 entries
            timestamp_str = entry["timestamp"].strftime("%H:%M:%S.%f")[:-3]
            level = entry["level"].upper()
            message = entry["message"]

            # Color by level
            if level == "ERROR":
                color = "#ff4444"
            elif level == "WARNING":
                color = "#ffaa00"
            elif level == "INFO":
                color = "#0066cc"
            else:  # DEBUG
                color = "#666666"

            line = f'<font color="{color}">[{timestamp_str}] {level}: {message}</font>'
            self.append(line)

        # Maintain scroll position
        if self.auto_scroll and at_bottom:
            scrollbar.setValue(scrollbar.maximum())

    def clear_logs(self):
        """Clear all log entries"""
        self.log_entries.clear()
        self.filtered_entries.clear()
        self.clear()


class ResultsTable(QTableWidget):
    """Table widget for displaying operation results"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Configure table
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSortingEnabled(True)

        # Setup columns
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels([
            "Operation", "Series", "Status", "Duration", "Points", "Quality", "Created",
        ])

        # Resize columns
        header = self.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

    def add_result(self, operation_id: str, result_data: dict[str, Any]):
        """Add operation result to table"""
        row = self.rowCount()
        self.insertRow(row)

        # Extract data from result
        operation_type = result_data.get("operation", "Unknown")
        series_name = result_data.get("series_name", "N/A")
        status = "Success" if result_data.get("success", True) else "Failed"
        duration = f"{result_data.get('duration_ms', 0):.1f} ms"
        n_points = result_data.get("n_points", 0)
        quality = f"{result_data.get('quality_score', 0):.2%}" if result_data.get("quality_score") else "N/A"
        created = result_data.get("timestamp", datetime.now()).strftime("%H:%M:%S")

        # Set items
        self.setItem(row, 0, QTableWidgetItem(operation_type))
        self.setItem(row, 1, QTableWidgetItem(series_name))

        # Status with color
        status_item = QTableWidgetItem(status)
        if status == "Success":
            status_item.setBackground(Qt.GlobalColor.lightGreen)
        else:
            status_item.setBackground(Qt.GlobalColor.lightGray)
        self.setItem(row, 2, status_item)

        self.setItem(row, 3, QTableWidgetItem(duration))
        self.setItem(row, 4, QTableWidgetItem(str(n_points)))
        self.setItem(row, 5, QTableWidgetItem(quality))
        self.setItem(row, 6, QTableWidgetItem(created))

        # Store full data in first item
        self.item(row, 0).setData(Qt.ItemDataRole.UserRole, result_data)

        # Auto-scroll to new item
        self.scrollToItem(self.item(row, 0))


class ResultsPanel(QWidget, UiLoaderMixin):
    """
    Results and logging panel.

    Features:
    - Operation results table
    - Real-time logging display
    - Data quality metrics
    - Export capabilities
    
    Interface carregada do arquivo .ui via UiLoaderMixin.
    """
    
    # Arquivo .ui que define a interface
    UI_FILE = "resultsPanel.ui"

    def __init__(self, session_state: SessionState, signal_hub: SignalHub,
                 parent: QWidget | None = None):
        super().__init__(parent)

        self.session_state = session_state
        self.signal_hub = signal_hub

        # Carregar interface do arquivo .ui
        if not self._load_ui():
            raise RuntimeError(f"Falha ao carregar arquivo UI: {self.UI_FILE}. Verifique se existe em desktop/ui_files/")
        self._setup_ui_from_file()

        self._connect_signals()

        # Start log polling timer
        self._setup_log_polling()

        logger.debug("results_panel_initialized")

    def _setup_ui_from_file(self):
        """Configura widgets carregados do arquivo .ui"""
        # Obter widgets do arquivo .ui (nomes do .ui)
        self.tabs = self.findChild(QTabWidget, "tabs")
        self.results_table = self.findChild(QTableWidget, "resultsTable")
        self.result_details = self.findChild(QTextEdit, "resultDetails")
        self.log_widget = self.findChild(QTextEdit, "logWidget")
        self.level_filter = self.findChild(QComboBox, "levelFilter")
        self.text_filter = self.findChild(QLineEdit, "textFilter")
        self.clear_logs_btn = self.findChild(QPushButton, "clearLogsBtn")
        self.quality_tree = self.findChild(QTreeWidget, "qualityTree")
        
        # Conectar sinais
        if self.results_table:
            self.results_table.itemSelectionChanged.connect(self._on_result_selected)
        
        if self.level_filter:
            self.level_filter.currentTextChanged.connect(self._filter_logs)
        
        if self.text_filter:
            self.text_filter.textChanged.connect(self._filter_logs)
        
        if self.clear_logs_btn:
            self.clear_logs_btn.clicked.connect(self._clear_logs)
            
        logger.debug("results_panel_ui_loaded_from_file")

    def _setup_log_polling(self):
        """Setup log polling timer"""
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self._poll_logs)
        self.log_timer.start(1000)  # Poll every second

    def _connect_signals(self):
        """Connect signals"""
        # Listen to operation events
        if self.signal_hub is not None:
            self.signal_hub.operation_started.connect(self._on_operation_started)
            self.signal_hub.operation_progress.connect(self._on_operation_progress)
            self.signal_hub.operation_completed.connect(self._on_operation_completed)
            self.signal_hub.operation_failed.connect(self._on_operation_failed)

            # Listen to errors
            self.signal_hub.error_occurred.connect(self._on_error_occurred)
            self.signal_hub.status_updated.connect(self._on_status_updated)
        else:
            logger.warning("ResultsPanel initialized without signal_hub - operation tracking disabled")

    @pyqtSlot(str, str)
    def _on_operation_started(self, operation_type: str, operation_id: str):
        """Handle operation started"""
        self.log_widget.add_log_entry("info", f"Operation started: {operation_type} ({operation_id})")

        # Show panel if auto-show enabled
        if self.auto_show_check.isChecked():
            self.parent().show()  # Show dock widget

    @pyqtSlot(str, int)
    def _on_operation_progress(self, operation_id: str, progress: int):
        """Handle operation progress"""
        if progress % 10 == 0:  # Log every 10%
            self.log_widget.add_log_entry("debug", f"Operation {operation_id}: {progress}% complete")

    @pyqtSlot(str, object)
    def _on_operation_completed(self, operation_id: str, result):
        """Handle operation completed"""
        self.log_widget.add_log_entry("info", f"Operation completed: {operation_id}")

        # Add to results table
        if isinstance(result, dict):
            result["operation_id"] = operation_id
            result["success"] = True
            result["timestamp"] = datetime.now()
            self.results_table.add_result(operation_id, result)

        # Update quality metrics
        self._update_quality_metrics()

        # Switch to results tab
        self.tabs.setCurrentIndex(0)

    @pyqtSlot(str, str)
    def _on_operation_failed(self, operation_id: str, error_message: str):
        """Handle operation failed"""
        self.log_widget.add_log_entry("error", f"Operation failed: {operation_id} - {error_message}")

        # Add to results table
        result_data = {
            "operation_id": operation_id,
            "operation": "failed",
            "success": False,
            "error": error_message,
            "timestamp": datetime.now(),
        }
        self.results_table.add_result(operation_id, result_data)

    @pyqtSlot(str, str)
    def _on_error_occurred(self, error_type: str, error_message: str):
        """Handle general errors"""
        self.log_widget.add_log_entry("error", f"{error_type}: {error_message}")

    @pyqtSlot(str)
    def _on_status_updated(self, message: str):
        """Handle status updates"""
        self.log_widget.add_log_entry("debug", f"Status: {message}")

    @pyqtSlot()
    def _on_result_selected(self):
        """Handle result selection"""
        current_row = self.results_table.currentRow()
        if current_row >= 0:
            item = self.results_table.item(current_row, 0)
            result_data = item.data(Qt.ItemDataRole.UserRole)

            if result_data:
                # Show detailed information
                details = []
                details.append(f"Operation ID: {result_data.get('operation_id', 'N/A')}")
                details.append(f"Operation Type: {result_data.get('operation', 'N/A')}")
                details.append(f"Success: {result_data.get('success', False)}")
                details.append(f"Duration: {result_data.get('duration_ms', 0):.2f} ms")
                details.append(f"Timestamp: {result_data.get('timestamp', 'N/A')}")

                if "error" in result_data:
                    details.append(f"Error: {result_data['error']}")

                if "parameters" in result_data:
                    details.append("\\nParameters:")
                    for key, value in result_data["parameters"].items():
                        details.append(f"  {key}: {value}")

                self.result_details.setPlainText("\\n".join(details))

    @pyqtSlot(str)
    def _on_log_level_changed(self, level: str):
        """Handle log level filter change"""
        self.log_widget.set_level_filter(level)

    @pyqtSlot(str)
    def _on_log_filter_changed(self, text: str):
        """Handle log text filter change"""
        self.log_widget.set_text_filter(text)

    @pyqtSlot()
    def _clear_results(self):
        """Clear results table"""
        self.results_table.setRowCount(0)
        self.result_details.clear()
        self.quality_summary.clear()
        self.quality_tree.clear()

    @pyqtSlot()
    def _filter_logs(self):
        """Aplica filtros aos logs exibidos."""
        if not hasattr(self, 'log_widget') or self.log_widget is None:
            return

        # Obter valores dos filtros
        level = ""
        text = ""

        if hasattr(self, 'level_filter') and self.level_filter:
            level = self.level_filter.currentText().lower()

        if hasattr(self, 'text_filter') and self.text_filter:
            text = self.text_filter.text().lower()

        # Aplicar filtros no widget de log
        if hasattr(self.log_widget, 'set_level_filter'):
            self.log_widget.set_level_filter(level)

        if hasattr(self.log_widget, 'set_text_filter'):
            self.log_widget.set_text_filter(text)

        logger.debug("logs_filtered", level=level, text=text)

    @pyqtSlot()
    def _clear_logs(self):
        """Clear log display"""
        self.log_widget.clear_logs()

    @pyqtSlot()
    def _export_results(self):
        """Export results to file"""
        logger.info("results_export_requested")

        import csv
        import json
        from pathlib import Path

        from PyQt6.QtWidgets import QFileDialog

        # Ask for file type
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Results",
            "",
            "CSV Files (*.csv);;JSON Files (*.json);;All Files (*.*)"
        )

        if not file_path:
            return

        try:
            # Collect all results from table
            results = []
            for row in range(self.results_table.rowCount()):
                item = self.results_table.item(row, 0)
                result_data = item.data(Qt.ItemDataRole.UserRole)
                if result_data:
                    # Convert datetime to string for serialization
                    result_copy = result_data.copy()
                    if "timestamp" in result_copy and isinstance(result_copy["timestamp"], datetime):
                        result_copy["timestamp"] = result_copy["timestamp"].isoformat()
                    results.append(result_copy)

            # Export based on file extension
            file_path_obj = Path(file_path)

            if file_path_obj.suffix == '.json' or "JSON" in selected_filter:
                # Export as JSON
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, default=str)
                logger.info("results_exported_json", path=file_path, count=len(results))

            else:  # CSV by default
                # Export as CSV
                if not results:
                    logger.warning("no_results_to_export")
                    return

                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    # Get all keys from all results
                    all_keys = set()
                    for result in results:
                        all_keys.update(result.keys())

                    fieldnames = sorted(all_keys)
                    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')

                    writer.writeheader()
                    for result in results:
                        # Convert non-string values to strings
                        row_data = {k: str(v) if not isinstance(v, (str, int, float)) else v 
                                   for k, v in result.items()}
                        writer.writerow(row_data)

                logger.info("results_exported_csv", path=file_path, count=len(results))

            self.log_widget.add_log_entry(
                "info", 
                f"Results exported to {file_path_obj.name} ({len(results)} entries)"
            )

        except Exception as e:
            logger.exception("results_export_failed", error=str(e))
            self.log_widget.add_log_entry("error", f"Export failed: {str(e)}")

    def _poll_logs(self):
        """Poll for new log entries from the logging system"""
        # This integrates with the centralized logging system
        # For production, this could connect to a log aggregator or file

        # Logs são adicionados em tempo real via signals dos workers
        try:
            # Verificar se há novos logs no buffer
            log_buffer = getattr(self.session_state, '_log_buffer', [])
            if log_buffer:
                for log_entry in log_buffer:
                    self.log_widget.add_log_entry(
                        log_entry.get('level', 'info'),
                        log_entry.get('message', ''),
                        timestamp=log_entry.get('timestamp')
                    )
                self.session_state._log_buffer = []
        except Exception as e:
            logger.exception(f"Error polling logs: {e}")

    def _update_quality_metrics(self):
        """Update quality metrics display"""
        # Calculate quality metrics from current data
        selection = self.session_state.selection
        if not selection.dataset_id:
            return

        try:
            dataset = self.session_state.dataset_store.get_dataset(selection.dataset_id)

            # Calculate overall metrics
            total_points = len(dataset.t_seconds)
            total_series = len(dataset.series)

            metrics_text = f"""
Total Points: {total_points:,}
Total Series: {total_series}
Time Range: {dataset.t_seconds[-1] - dataset.t_seconds[0]:.2f} seconds
Validation Warnings: {len(dataset.metadata.validation_warnings)}
Validation Errors: {len(dataset.metadata.validation_errors)}
"""

            self.quality_summary.setPlainText(metrics_text.strip())

            # Update quality tree
            self.quality_tree.clear()

            # Add dataset-level metrics
            dataset_item = QTreeWidgetItem(["Dataset Quality", "", ""])
            self.quality_tree.addTopLevelItem(dataset_item)

            # Schema confidence
            confidence_item = QTreeWidgetItem([
                "Schema Confidence",
                f"{dataset.metadata.schema_confidence:.2%}",
                "Good" if dataset.metadata.schema_confidence > 0.8 else "Warning",
            ])
            dataset_item.addChild(confidence_item)

            # Add series-level metrics
            for series in dataset.series.values():
                series_item = QTreeWidgetItem([f"Series: {series.name}", "", ""])
                self.quality_tree.addTopLevelItem(series_item)

                # NaN ratio
                nan_ratio = sum(1 for x in series.values if str(x) == "nan") / len(series.values)
                nan_item = QTreeWidgetItem([
                    "NaN Ratio",
                    f"{nan_ratio:.2%}",
                    "Good" if nan_ratio < 0.05 else "Warning",
                ])
                series_item.addChild(nan_item)

                # Interpolation info if available
                if series.interpolation_info:
                    interp_ratio = sum(series.interpolation_info.is_interpolated) / len(series.interpolation_info.is_interpolated)
                    interp_item = QTreeWidgetItem([
                        "Interpolated Ratio",
                        f"{interp_ratio:.2%}",
                        "Info",
                    ])
                    series_item.addChild(interp_item)

            # Expand all items
            self.quality_tree.expandAll()

        except Exception as e:
            logger.exception("failed_to_update_quality_metrics", error=str(e))
            self.quality_summary.setPlainText(f"Error calculating metrics: {e}")
