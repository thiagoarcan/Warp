"""
ResultsPanel - Results and logging panel for Platform Base v2.0

Displays operation results, logs, and data quality metrics.
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


class ResultsPanel(QWidget):
    """
    Results and logging panel.

    Features:
    - Operation results table
    - Real-time logging display
    - Data quality metrics
    - Export capabilities
    """

    def __init__(self, session_state: SessionState, signal_hub: SignalHub,
                 parent: QWidget | None = None):
        super().__init__(parent)

        self.session_state = session_state
        self.signal_hub = signal_hub

        self._setup_ui()
        self._connect_signals()

        # Start log polling timer
        self._setup_log_polling()

        logger.debug("results_panel_initialized")

    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)

        # Tab widget for different views
        self.tabs = QTabWidget()

        # Results tab
        self.results_tab = self._create_results_tab()
        self.tabs.addTab(self.results_tab, "Results")

        # Logs tab
        self.logs_tab = self._create_logs_tab()
        self.tabs.addTab(self.logs_tab, "Logs")

        # Quality tab
        self.quality_tab = self._create_quality_tab()
        self.tabs.addTab(self.quality_tab, "Quality")

        layout.addWidget(self.tabs)

        # Control buttons
        buttons_layout = QHBoxLayout()

        self.clear_results_btn = QPushButton("Clear Results")
        self.clear_results_btn.clicked.connect(self._clear_results)
        buttons_layout.addWidget(self.clear_results_btn)

        self.export_results_btn = QPushButton("Export Results")
        self.export_results_btn.clicked.connect(self._export_results)
        buttons_layout.addWidget(self.export_results_btn)

        buttons_layout.addStretch()

        self.auto_show_check = QCheckBox("Auto-show on results")
        self.auto_show_check.setChecked(True)
        buttons_layout.addWidget(self.auto_show_check)

        layout.addLayout(buttons_layout)

    def _create_results_tab(self) -> QWidget:
        """Create results tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Results table
        self.results_table = ResultsTable()
        layout.addWidget(self.results_table)

        # Result details
        details_group = QGroupBox("Result Details")
        details_layout = QVBoxLayout(details_group)

        self.result_details = QTextEdit()
        self.result_details.setMaximumHeight(150)
        self.result_details.setReadOnly(True)
        details_layout.addWidget(self.result_details)

        layout.addWidget(details_group)

        # Connect selection
        self.results_table.itemSelectionChanged.connect(self._on_result_selected)

        return widget

    def _create_logs_tab(self) -> QWidget:
        """Create logs tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Log controls
        controls_layout = QHBoxLayout()

        controls_layout.addWidget(QLabel("Level:"))
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["all", "debug", "info", "warning", "error"])
        self.log_level_combo.currentTextChanged.connect(self._on_log_level_changed)
        controls_layout.addWidget(self.log_level_combo)

        controls_layout.addWidget(QLabel("Filter:"))
        self.log_filter_edit = QLineEdit()
        self.log_filter_edit.setPlaceholderText("Search logs...")
        self.log_filter_edit.textChanged.connect(self._on_log_filter_changed)
        controls_layout.addWidget(self.log_filter_edit)

        self.clear_logs_btn = QPushButton("Clear")
        self.clear_logs_btn.clicked.connect(self._clear_logs)
        controls_layout.addWidget(self.clear_logs_btn)

        layout.addLayout(controls_layout)

        # Log display
        self.log_widget = LogWidget()
        layout.addWidget(self.log_widget)

        return widget

    def _create_quality_tab(self) -> QWidget:
        """Create quality metrics tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Quality summary
        summary_group = QGroupBox("Data Quality Summary")
        summary_layout = QVBoxLayout(summary_group)

        self.quality_summary = QTextEdit()
        self.quality_summary.setMaximumHeight(100)
        self.quality_summary.setReadOnly(True)
        summary_layout.addWidget(self.quality_summary)

        layout.addWidget(summary_group)

        # Quality metrics tree
        metrics_group = QGroupBox("Quality Metrics")
        metrics_layout = QVBoxLayout(metrics_group)

        self.quality_tree = QTreeWidget()
        self.quality_tree.setHeaderLabels(["Metric", "Value", "Status"])
        metrics_layout.addWidget(self.quality_tree)

        layout.addWidget(metrics_group)

        return widget

    def _setup_log_polling(self):
        """Setup log polling timer"""
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self._poll_logs)
        self.log_timer.start(1000)  # Poll every second

    def _connect_signals(self):
        """Connect signals"""
        # Listen to operation events
        self.signal_hub.operation_started.connect(self._on_operation_started)
        self.signal_hub.operation_progress.connect(self._on_operation_progress)
        self.signal_hub.operation_completed.connect(self._on_operation_completed)
        self.signal_hub.operation_failed.connect(self._on_operation_failed)

        # Listen to errors
        self.signal_hub.error_occurred.connect(self._on_error_occurred)
        self.signal_hub.status_updated.connect(self._on_status_updated)

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
    def _clear_logs(self):
        """Clear log display"""
        self.log_widget.clear_logs()

    @pyqtSlot()
    def _export_results(self):
        """Export results to file"""
        logger.info("results_export_requested")
        # Export functionality to be implemented

    def _poll_logs(self):
        """Poll for new log entries"""
        # This would integrate with the logging system
        # For now, just a placeholder

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
