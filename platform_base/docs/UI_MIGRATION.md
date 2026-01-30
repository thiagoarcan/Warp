# UI Migration to Qt Designer Files

This document describes the migration of the Platform Base UI from programmatic Python code to Qt Designer `.ui` files.

## 📁 Directory Structure

```
src/platform_base/ui/
├── designer/                    # Qt Designer .ui files
│   ├── main_window.ui          # Main application window
│   ├── panels/                 # Panel UI files
│   │   └── data_panel.ui       # Data management panel
│   ├── dialogs/                # Dialog UI files (to be created)
│   ├── tabs/                   # Tab UI files (to be created)
│   └── components/             # Component UI files (to be created)
├── loader.py                   # UI loading utilities
├── mixins.py                   # Mixin classes for UI loading
└── [existing Python files]     # Existing UI implementation

```

## 🔧 Using the UI Loader

### Loading UI Files

The `loader.py` module provides three main functions:

#### 1. `load_ui(ui_name, widget)`

Loads a `.ui` file into an existing widget:

```python
from PyQt6.QtWidgets import QWidget
from platform_base.ui.loader import load_ui

class MyPanel(QWidget):
    def __init__(self):
        super().__init__()
        load_ui("panels/data_panel", self)
        # Now you can access widgets from the .ui file
        self.load_button.clicked.connect(self.on_load)
```

#### 2. `get_ui_class(ui_name)`

Returns a class generated from a `.ui` file:

```python
from platform_base.ui.loader import get_ui_class

DataPanelUI = get_ui_class("panels/data_panel")

class DataPanel(DataPanelUI):
    def __init__(self):
        super().__init__()
        self._setup_connections()
```

#### 3. `validate_ui_file(ui_name)`

Checks if a `.ui` file exists:

```python
from platform_base.ui.loader import validate_ui_file

if validate_ui_file("panels/data_panel"):
    print("UI file found!")
```

### Using the UiLoaderMixin

The `UiLoaderMixin` class provides a convenient way to load UI files:

```python
from PyQt6.QtWidgets import QWidget
from platform_base.ui.mixins import UiLoaderMixin
from platform_base.ui.state import SessionState

class DataPanel(QWidget, UiLoaderMixin):
    UI_FILE = "panels/data_panel"
    
    def __init__(self, session_state: SessionState):
        super().__init__()
        self.session_state = session_state
        self._load_ui()  # Loads panels/data_panel.ui
        self._connect_signals()
    
    def _connect_signals(self):
        # Connect widgets from the .ui file
        self.load_button.clicked.connect(self._on_load_clicked)
        self.series_tree.itemClicked.connect(self._on_series_selected)
```

### Using the DialogLoaderMixin

For dialogs, use `DialogLoaderMixin` which includes additional dialog-specific features:

```python
from PyQt6.QtWidgets import QDialog
from platform_base.ui.mixins import DialogLoaderMixin

class SettingsDialog(QDialog, DialogLoaderMixin):
    UI_FILE = "dialogs/settings_dialog"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._load_ui()
        self._setup_dialog_buttons()  # Auto-connects OK/Cancel buttons
```

## 📝 Creating UI Files

### Using Qt Designer

1. Open Qt Designer (or use XML editor for small changes)
2. Create a new widget/dialog/mainwindow
3. Design the interface visually
4. Save to `src/platform_base/ui/designer/` with appropriate subdirectory
5. Use naming convention: `component_name.ui`

### Widget Naming Convention

When creating UI files, follow these naming conventions for programmatic access:

- **Buttons**: `action_name_button` (e.g., `load_button`, `save_button`)
- **Labels**: `description_label` (e.g., `title_label`, `status_label`)
- **Trees**: `content_tree` (e.g., `series_tree`, `datasets_tree`)
- **Tables**: `content_table` (e.g., `data_table`, `results_table`)
- **Combos**: `option_combo` (e.g., `preview_rows_combo`, `format_combo`)
- **Groups**: `purpose_group` (e.g., `datasets_group`, `series_group`)

### Placeholder Widgets

For dynamic widgets that cannot be fully defined in Qt Designer (e.g., Matplotlib, VTK widgets):

1. Add a `QWidget` placeholder in the `.ui` file
2. Name it with `_placeholder` suffix (e.g., `plot_placeholder`)
3. Replace it programmatically in Python:

```python
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

def _setup_plot_widget(self):
    # Remove placeholder
    old_widget = self.plot_placeholder
    parent = old_widget.parent()
    layout = parent.layout()
    
    # Create real widget
    self.plot_canvas = FigureCanvasQTAgg(self.figure)
    
    # Replace in layout
    index = layout.indexOf(old_widget)
    layout.removeWidget(old_widget)
    layout.insertWidget(index, self.plot_canvas)
    old_widget.deleteLater()
```

## ✅ Migration Checklist

### Phase 1: Infrastructure ✅
- [x] Create `ui/designer/` directory structure
- [x] Implement `ui/loader.py` with loading functions
- [x] Create `ui/mixins.py` with mixin classes

### Phase 2: Main Window ✅
- [x] Create `main_window.ui`
  - Menu bar with 5 menus (File, View, Operations, Tools, Help)
  - Toolbar with actions
  - Status bar
  - 3-panel layout with splitters
  - Placeholders for dynamic panels

### Phase 3: Panels
- [x] Create `panels/data_panel.ui`
- [ ] Create `panels/viz_panel.ui`
- [ ] Create `panels/operations_panel.ui`
- [ ] Create `panels/config_panel.ui`
- [ ] Create `panels/results_panel.ui`
- [ ] Create `panels/streaming_panel.ui`
- [ ] Create `panels/selection_panel.ui`

### Phase 4: Python Refactoring
- [ ] Refactor `main_window.py` to use `.ui` file
- [ ] Refactor panel classes to use `.ui` files
- [ ] Update signal connections
- [ ] Replace placeholder widgets

## 🎨 Styling

Styles are currently embedded in the `.ui` files using Qt StyleSheets. Key design elements:

- **Colors**:
  - Primary: `#0d6efd` (blue)
  - Background: `#f8f9fa` (light gray)
  - Borders: `#e9ecef` (gray)
  - Text: `#212529` (dark gray)

- **Spacing**:
  - Margins: 2-6px (compact)
  - Border radius: 4-6px
  - Padding: 4-8px

## 🧪 Testing

To validate UI files without Qt GUI:

```python
import xml.etree.ElementTree as ET
from pathlib import Path

ui_path = Path('src/platform_base/ui/designer/main_window.ui')
tree = ET.parse(str(ui_path))
root = tree.getroot()
assert root.tag == 'ui'
assert root.get('version') == '4.0'
```

## 📚 References

- [PyQt6 uic module](https://www.riverbankcomputing.com/static/Docs/PyQt6/api/uic/uic-module.html)
- [Qt Designer Manual](https://doc.qt.io/qt-6/qtdesigner-manual.html)
- [Using .ui files with PyQt](https://realpython.com/qt-designer-python/)
