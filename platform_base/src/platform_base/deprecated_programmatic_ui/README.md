# Deprecated Programmatic UI Code

**⚠️ THIS FOLDER CONTAINS DEPRECATED CODE - DO NOT USE ⚠️**

## Purpose

This folder isolates all programmatic UI creation code that has been **replaced by .ui files**.

All interface components should now be loaded exclusively from Qt Designer `.ui` files located in:
- `platform_base/src/platform_base/desktop/ui_files/`

## Contents

### 1. `main_window_unified.py`
- **Original:** `platform_base/ui/main_window_unified.py`
- **Status:** Deprecated - replaced by `desktop/main_window.py` with `mainWindow.ui`
- **Reason:** Was attempting to load from `modernMainWindow.ui` (26-line stub)
- **Replacement:** Use `desktop/main_window.py` which loads from `mainWindow.ui` (497 lines)

### 2. `main_window_old.py`
- **Original:** `platform_base/ui/main_window_old.py`
- **Status:** Deprecated - older version of main window
- **Reason:** Superseded by current implementation
- **Replacement:** Use `desktop/main_window.py`

### 3. `main_window_programmatic_fallbacks.py.txt`
- **Original:** Methods from `desktop/main_window.py` (lines 314-625)
- **Status:** Deprecated - programmatic UI fallbacks no longer used
- **Methods Included:**
  - `_setup_window()` - Programmatic window configuration
  - `_create_dockable_panels()` - Programmatic panel creation
  - `_create_menu_bar()` - Programmatic menu bar creation
  - `_create_tool_bar()` - Programmatic toolbar creation
  - `_create_status_bar()` - Programmatic status bar creation
- **Reason:** Violated custom instruction #3: "Não são admitidos fallbacks para interfaces"
- **Replacement:** All UI elements defined in `mainWindow.ui`

## Architecture Change

### Before (Deprecated)
```python
if self._load_ui():
    self._setup_ui_from_file()
else:
    # DEPRECATED: Programmatic fallback
    self._setup_window()
    self._create_dockable_panels()
    self._create_menu_bar()
    self._create_tool_bar()
    self._create_status_bar()
```

### After (Current)
```python
# Fail fast - no fallbacks allowed
if not self._load_ui():
    raise RuntimeError(
        "Interface deve ser carregada exclusivamente de arquivos .ui"
    )
self._setup_ui_from_file()
```

## Why This Code Was Deprecated

1. **Custom Instruction #3:** "Não são admitidos fallbacks para interfaces; todas devem ser carregadas de arquivos `.ui`"
2. **Code Duplication:** Multiple implementations caused confusion
3. **Incomplete Stub:** `modernMainWindow.ui` was only 26 lines (vs 497 in working version)
4. **Architecture Violation:** Programmatic UI contradicted exclusive .ui-based loading requirement

## Migration Path

If you need UI functionality:

1. ✅ **DO:** Use `desktop/main_window.py` which loads from `mainWindow.ui`
2. ✅ **DO:** Edit `mainWindow.ui` in Qt Designer for UI changes
3. ❌ **DON'T:** Use programmatic UI creation methods
4. ❌ **DON'T:** Create fallback implementations

## Historical Context

These files were part of PR: "Consolidate MainWindow to single .ui-based implementation"
- **Date:** 2026-02-05
- **Branch:** copilot/update-local-repository
- **Commits:** 5ee52b2, dab3f5a, 8ad6f43, 496db63

## Removal Schedule

This folder and its contents will be **permanently removed** in a future release once:
1. All team members are aware of the architecture change
2. No references remain in active code
3. Sufficient time has passed for reference purposes (estimated: 2-3 months)

---

**Last Updated:** 2026-02-06
**Status:** Archived for reference only
