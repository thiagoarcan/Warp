# Examples Directory

This directory contains example implementations demonstrating the Qt Designer UI migration pattern.

## Files

### data_panel_refactored_example.py

Demonstrates how a complex panel (DataPanel) is refactored from programmatic UI code to use Qt Designer `.ui` files.

**Key Points:**
- Shows before/after code comparison
- Demonstrates the UiLoaderMixin pattern
- Illustrates 86% reduction in UI setup code
- Separates UI definition from business logic

**Usage Pattern:**
```python
class MyPanel(QWidget, UiLoaderMixin):
    UI_FILE = "panels/my_panel"  # Points to designer/panels/my_panel.ui
    
    def __init__(self, session_state):
        super().__init__()
        self._load_ui()  # Loads the .ui file
        self._configure_widgets()  # Configure what can't be in .ui
        self._setup_connections()  # Connect signals
```

## Notes

- These are EXAMPLES only - not part of the actual codebase
- The actual refactoring will be done in Phase 4 of the migration
- Examples show the intended pattern and benefits
