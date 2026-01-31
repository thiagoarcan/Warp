"""
Accessibility helper utilities.

Provides utility functions for common accessibility tasks.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

from PyQt6.QtCore import Qt, QObject
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QToolButton,
    QCheckBox,
    QRadioButton,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QLineEdit,
    QTextEdit,
    QPlainTextEdit,
    QSlider,
    QProgressBar,
    QGroupBox,
    QTabWidget,
    QTreeView,
    QTableView,
    QListView,
    QMenu,
    QToolBar,
    QStatusBar,
    QDockWidget,
    QDialog,
    QMessageBox,
    QAbstractButton,
    QAbstractSpinBox,
    QAbstractSlider,
)

logger = logging.getLogger(__name__)


def set_accessible_name(widget: QWidget, name: str) -> None:
    """
    Set the accessible name for a widget.
    
    The accessible name is the primary identifier read by screen readers.
    
    Args:
        widget: Widget to configure
        name: Accessible name (should be concise and descriptive)
    """
    widget.setAccessibleName(name)
    logger.debug(f"Set accessible name '{name}' for {widget.__class__.__name__}")


def set_accessible_description(widget: QWidget, description: str) -> None:
    """
    Set the accessible description for a widget.
    
    The description provides additional context beyond the name.
    
    Args:
        widget: Widget to configure
        description: Detailed description
    """
    widget.setAccessibleDescription(description)


def set_accessible_properties(
    widget: QWidget,
    name: str,
    description: str = "",
    tooltip: str = "",
) -> None:
    """
    Set all accessible properties for a widget.
    
    Args:
        widget: Widget to configure
        name: Accessible name
        description: Accessible description
        tooltip: Tooltip text (also helps sighted users)
    """
    widget.setAccessibleName(name)
    if description:
        widget.setAccessibleDescription(description)
    if tooltip:
        widget.setToolTip(tooltip)


def add_shortcut_to_tooltip(widget: QWidget, shortcut: str) -> None:
    """
    Add shortcut information to a widget's tooltip.
    
    Args:
        widget: Widget to update
        shortcut: Shortcut key sequence (e.g., "Ctrl+S")
    """
    current_tooltip = widget.toolTip()
    if current_tooltip:
        widget.setToolTip(f"{current_tooltip} ({shortcut})")
    else:
        widget.setToolTip(f"({shortcut})")


def make_button_accessible(
    button: QAbstractButton,
    name: str,
    description: str = "",
    shortcut: str = "",
) -> None:
    """
    Configure accessibility for a button.
    
    Args:
        button: Button widget
        name: Accessible name
        description: What the button does
        shortcut: Associated keyboard shortcut
    """
    button.setAccessibleName(name)
    
    tooltip_parts = []
    if description:
        tooltip_parts.append(description)
        button.setAccessibleDescription(description)
    if shortcut:
        tooltip_parts.append(f"({shortcut})")
    
    if tooltip_parts:
        button.setToolTip(" ".join(tooltip_parts))


def make_input_accessible(
    widget: QWidget,
    label: str,
    description: str = "",
    required: bool = False,
) -> None:
    """
    Configure accessibility for an input widget.
    
    Args:
        widget: Input widget (QLineEdit, QComboBox, etc.)
        label: Field label
        description: Help text
        required: Whether the field is required
    """
    name = label
    if required:
        name = f"{label} (obrigatório)"
    
    widget.setAccessibleName(name)
    if description:
        widget.setAccessibleDescription(description)
        widget.setToolTip(description)


def associate_label_with_input(label: QLabel, input_widget: QWidget) -> None:
    """
    Associate a label with its input widget for accessibility.
    
    This helps screen readers understand the relationship.
    
    Args:
        label: Label widget
        input_widget: Associated input widget
    """
    label.setBuddy(input_widget)
    
    # Transfer label text to accessible name if not set
    if not input_widget.accessibleName():
        input_widget.setAccessibleName(label.text().replace("&", "").replace(":", ""))


def setup_logical_tab_order(widgets: Sequence[QWidget]) -> None:
    """
    Setup logical tab order for a sequence of widgets.
    
    Args:
        widgets: Widgets in the desired tab order
    """
    for i in range(len(widgets) - 1):
        QWidget.setTabOrder(widgets[i], widgets[i + 1])
    
    logger.debug(f"Set tab order for {len(widgets)} widgets")


def make_group_accessible(
    group: QGroupBox,
    widgets: Sequence[QWidget],
) -> None:
    """
    Configure accessibility for a group of related widgets.
    
    Args:
        group: Group box container
        widgets: Widgets in the group
    """
    # Group title becomes accessible name
    group.setAccessibleName(group.title())
    
    # Setup tab order within group
    if widgets:
        setup_logical_tab_order(widgets)


def make_table_accessible(
    table: Union[QTableView, QTreeView, QListView],
    name: str,
    description: str = "",
    row_count: int = 0,
    column_count: int = 0,
) -> None:
    """
    Configure accessibility for a table or list view.
    
    Args:
        table: Table/tree/list view widget
        name: Accessible name
        description: Description of table contents
        row_count: Number of rows (for description)
        column_count: Number of columns (for description)
    """
    table.setAccessibleName(name)
    
    desc_parts = [description] if description else []
    if row_count:
        desc_parts.append(f"{row_count} linhas")
    if column_count:
        desc_parts.append(f"{column_count} colunas")
    
    if desc_parts:
        table.setAccessibleDescription(". ".join(desc_parts))


def make_slider_accessible(
    slider: QAbstractSlider,
    name: str,
    value_format: str = "{value}",
    min_label: str = "",
    max_label: str = "",
) -> None:
    """
    Configure accessibility for a slider.
    
    Args:
        slider: Slider widget
        name: Accessible name
        value_format: Format string for value (e.g., "{value}%")
        min_label: Label for minimum value
        max_label: Label for maximum value
    """
    min_val = slider.minimum()
    max_val = slider.maximum()
    
    description = f"De {min_label or min_val} a {max_label or max_val}"
    
    slider.setAccessibleName(name)
    slider.setAccessibleDescription(description)
    
    # Update accessible value on change
    def update_value(value: int) -> None:
        formatted = value_format.format(value=value)
        slider.setAccessibleName(f"{name}: {formatted}")
    
    slider.valueChanged.connect(update_value)


def make_progress_accessible(
    progress: QProgressBar,
    name: str,
    task_description: str = "",
) -> None:
    """
    Configure accessibility for a progress bar.
    
    Args:
        progress: Progress bar widget
        name: Accessible name
        task_description: Description of what's being processed
    """
    progress.setAccessibleName(name)
    if task_description:
        progress.setAccessibleDescription(task_description)
    
    # Update accessible value on change
    def update_value(value: int) -> None:
        max_val = progress.maximum()
        if max_val > 0:
            percent = int(value / max_val * 100)
            progress.setAccessibleName(f"{name}: {percent}%")
    
    progress.valueChanged.connect(update_value)


def make_tab_widget_accessible(
    tab_widget: QTabWidget,
    name: str,
) -> None:
    """
    Configure accessibility for a tab widget.
    
    Args:
        tab_widget: Tab widget
        name: Accessible name for the tab bar
    """
    tab_widget.setAccessibleName(name)
    
    # Update description when tab changes
    def update_tab(index: int) -> None:
        tab_name = tab_widget.tabText(index)
        count = tab_widget.count()
        tab_widget.setAccessibleDescription(
            f"Aba {tab_name} selecionada. {index + 1} de {count} abas."
        )
    
    tab_widget.currentChanged.connect(update_tab)
    
    # Initial update
    if tab_widget.count() > 0:
        update_tab(tab_widget.currentIndex())


def make_dialog_accessible(
    dialog: QDialog,
    title: str,
    purpose: str,
) -> None:
    """
    Configure accessibility for a dialog.
    
    Args:
        dialog: Dialog widget
        title: Dialog title
        purpose: What the dialog is for
    """
    dialog.setWindowTitle(title)
    dialog.setAccessibleName(title)
    dialog.setAccessibleDescription(purpose)


def make_status_bar_accessible(status_bar: QStatusBar) -> None:
    """
    Configure accessibility for a status bar.
    
    Args:
        status_bar: Status bar widget
    """
    status_bar.setAccessibleName("Barra de status")
    status_bar.setAccessibleDescription("Exibe informações sobre o estado atual da aplicação")


def make_toolbar_accessible(
    toolbar: QToolBar,
    name: str = "",
) -> None:
    """
    Configure accessibility for a toolbar.
    
    Args:
        toolbar: Toolbar widget
        name: Toolbar name
    """
    toolbar_name = name or toolbar.windowTitle() or "Barra de ferramentas"
    toolbar.setAccessibleName(toolbar_name)
    
    action_count = len(toolbar.actions())
    toolbar.setAccessibleDescription(f"{action_count} ações disponíveis")


def make_dock_accessible(
    dock: QDockWidget,
    purpose: str = "",
) -> None:
    """
    Configure accessibility for a dock widget.
    
    Args:
        dock: Dock widget
        purpose: Purpose of the dock panel
    """
    name = dock.windowTitle() or "Painel"
    dock.setAccessibleName(name)
    if purpose:
        dock.setAccessibleDescription(purpose)


def announce_to_screen_reader(message: str) -> None:
    """
    Announce a message to screen readers.
    
    This is a placeholder - actual implementation depends on platform.
    
    Args:
        message: Message to announce
    """
    logger.info(f"Screen reader announcement: {message}")
    # Note: PyQt6 doesn't have direct live region support
    # For real screen reader support, use platform-specific APIs
    # or implement via accessibility bridge


def format_number_for_speech(
    value: float,
    unit: str = "",
    precision: int = 2,
) -> str:
    """
    Format a number for text-to-speech readability.
    
    Args:
        value: Numeric value
        unit: Unit of measurement
        precision: Decimal places
        
    Returns:
        Speech-friendly formatted string
    """
    if value == int(value):
        formatted = str(int(value))
    else:
        formatted = f"{value:.{precision}f}"
    
    if unit:
        return f"{formatted} {unit}"
    return formatted


def format_range_for_speech(
    start: float,
    end: float,
    unit: str = "",
) -> str:
    """
    Format a range for text-to-speech.
    
    Args:
        start: Start value
        end: End value
        unit: Unit of measurement
        
    Returns:
        Speech-friendly range description
    """
    start_str = format_number_for_speech(start)
    end_str = format_number_for_speech(end)
    
    if unit:
        return f"de {start_str} a {end_str} {unit}"
    return f"de {start_str} a {end_str}"


def format_percentage_for_speech(value: float) -> str:
    """
    Format a percentage for text-to-speech.
    
    Args:
        value: Percentage value (0-100)
        
    Returns:
        Speech-friendly percentage
    """
    if value == int(value):
        return f"{int(value)} por cento"
    return f"{value:.1f} por cento"


def get_widget_state_description(widget: QWidget) -> str:
    """
    Get a description of a widget's current state.
    
    Args:
        widget: Widget to describe
        
    Returns:
        State description
    """
    states = []
    
    if not widget.isEnabled():
        states.append("desabilitado")
    if not widget.isVisible():
        states.append("oculto")
    if widget.hasFocus():
        states.append("em foco")
    
    if isinstance(widget, QAbstractButton):
        if widget.isChecked():
            states.append("marcado" if isinstance(widget, QCheckBox) else "selecionado")
    
    if isinstance(widget, QLineEdit):
        if widget.isReadOnly():
            states.append("somente leitura")
        if not widget.text():
            states.append("vazio")
    
    return ", ".join(states) if states else "normal"


def validate_contrast_ratio(
    foreground: str,
    background: str,
    min_ratio: float = 4.5,
) -> Tuple[bool, float]:
    """
    Validate contrast ratio between two colors.
    
    Args:
        foreground: Foreground color (hex)
        background: Background color (hex)
        min_ratio: Minimum required ratio (WCAG AA = 4.5, AAA = 7.0)
        
    Returns:
        (passes, actual_ratio)
    """
    def luminance(hex_color: str) -> float:
        """Calculate relative luminance of a color."""
        hex_color = hex_color.lstrip("#")
        r, g, b = [int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4)]
        
        def adjust(c: float) -> float:
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        
        return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)
    
    l1 = luminance(foreground)
    l2 = luminance(background)
    
    lighter = max(l1, l2)
    darker = min(l1, l2)
    
    ratio = (lighter + 0.05) / (darker + 0.05)
    
    return ratio >= min_ratio, ratio


__all__ = [
    "add_shortcut_to_tooltip",
    "announce_to_screen_reader",
    "associate_label_with_input",
    "format_number_for_speech",
    "format_percentage_for_speech",
    "format_range_for_speech",
    "get_widget_state_description",
    "make_button_accessible",
    "make_dialog_accessible",
    "make_dock_accessible",
    "make_group_accessible",
    "make_input_accessible",
    "make_progress_accessible",
    "make_slider_accessible",
    "make_status_bar_accessible",
    "make_tab_widget_accessible",
    "make_table_accessible",
    "make_toolbar_accessible",
    "set_accessible_description",
    "set_accessible_name",
    "set_accessible_properties",
    "setup_logical_tab_order",
    "validate_contrast_ratio",
]
