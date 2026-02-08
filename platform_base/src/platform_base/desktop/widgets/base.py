"""
Base module for desktop widgets.

Re-exports UiLoaderMixin for convenience and maintains backward compatibility.
"""

from platform_base.ui.ui_loader_mixin import (
    UI_FILES_DIR,
    UiLoaderMixin,
    get_ui_files_directory,
)


__all__ = [
    "UI_FILES_DIR",
    "UiLoaderMixin",
    "get_ui_files_directory",
]
