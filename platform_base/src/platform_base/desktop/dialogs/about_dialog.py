"""
AboutDialog - About dialog for Platform Base v2.0

Shows application information, version, and credits.

Interface carregada de: desktop/ui_files/aboutDialog.ui
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from platform_base.ui.ui_loader_mixin import UiLoaderMixin
from platform_base.utils.i18n import tr
from platform_base.utils.logging import get_logger


logger = get_logger(__name__)


class AboutDialog(QDialog, UiLoaderMixin):
    """
    About dialog showing application information.

    Features:
    - Application version and build info
    - Credits and acknowledgments
    - System information
    - License information
    
    Interface carregada do arquivo .ui via UiLoaderMixin.
    """
    
    # Arquivo .ui que define a interface
    UI_FILE = "aboutDialog.ui"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Carrega interface do arquivo .ui
        if not self._load_ui():
            raise RuntimeError(f"Falha ao carregar arquivo UI: {self.UI_FILE}. Verifique se existe em desktop/ui_files/")
        self._setup_ui_from_file()

        logger.debug("about_dialog_initialized", ui_loaded=self._ui_loaded)

    def _setup_ui_from_file(self):
        """Configura widgets carregados do arquivo .ui"""
        # Encontra widgets do arquivo .ui
        self.tabs = self.findChild(QTabWidget, "tabs")
        self.logo_label = self.findChild(QLabel, "logoLabel")
        self.title_label = self.findChild(QLabel, "titleLabel")
        self.version_label = self.findChild(QLabel, "versionLabel")
        self.subtitle_label = self.findChild(QLabel, "subtitleLabel")
        self.about_text = self.findChild(QTextEdit, "aboutText")
        self.credits_text = self.findChild(QTextEdit, "creditsText")
        self.system_text = self.findChild(QTextEdit, "systemText")
        self.license_text = self.findChild(QTextEdit, "licenseText")
        self.close_btn = self.findChild(QPushButton, "closeBtn")
        
        # Configura logo
        if self.logo_label:
            self.logo_label.setStyleSheet("border: 1px solid gray; background: lightblue;")
        
        # Popula conteúdo das abas
        self._populate_about_tab()
        self._populate_credits_tab()
        self._populate_system_tab()
        self._populate_license_tab()
        
        logger.debug("about_dialog_ui_loaded_from_file")

    def _populate_about_tab(self):
        """Popula a aba About com conteúdo HTML"""
        if not self.about_text:
            return
        self.about_text.setHtml("""
        <h3>Platform Base v2.0</h3>
        <p><b>Desktop Time Series Analysis Tool</b></p>

        <p>Platform Base is a comprehensive desktop application for exploratory time series analysis
        of sensor data with irregular timestamps. Built with PyQt6, it provides native desktop
        performance with advanced visualization and processing capabilities.</p>

        <h4>Key Features:</h4>
        <ul>
        <li>Multi-format data loading (CSV, Excel, Parquet, HDF5)</li>
        <li>Advanced interpolation methods with provenance tracking</li>
        <li>2D and 3D visualization with pyqtgraph and PyVista</li>
        <li>Mathematical operations (derivatives, integrals, areas)</li>
        <li>Multi-series synchronization</li>
        <li>Temporal streaming and video export</li>
        <li>Plugin system for extensibility</li>
        <li>Session persistence and recovery</li>
        </ul>

        <p><b>Built for TRANSPETRO</b><br>
        Industrial time series data analysis and exploration.</p>
        """)

    def _populate_credits_tab(self):
        """Popula a aba Credits com conteúdo HTML"""
        if not self.credits_text:
            return
        self.credits_text.setHtml("""
        <h3>Credits and Acknowledgments</h3>

        <h4>Development Team:</h4>
        <p>Platform Base development team<br>
        <i>Time series analysis and desktop application development</i></p>

        <h4>Third-Party Libraries:</h4>
        <p><b>PyQt6</b> - Cross-platform GUI toolkit<br>
        Copyright © The Qt Company Ltd.</p>

        <p><b>pyqtgraph</b> - Scientific graphics and GUI library<br>
        Copyright © Luke Campagnola</p>

        <p><b>PyVista</b> - 3D plotting and mesh analysis<br>
        Copyright © PyVista developers</p>

        <p><b>NumPy</b> - Numerical computing library<br>
        Copyright © NumPy developers</p>

        <p><b>pandas</b> - Data analysis and manipulation<br>
        Copyright © pandas development team</p>

        <p><b>SciPy</b> - Scientific computing library<br>
        Copyright © SciPy developers</p>

        <p><b>pint</b> - Physical units library<br>
        Copyright © Hernan E. Grecco</p>

        <p><b>pydantic</b> - Data validation library<br>
        Copyright © Samuel Colvin</p>

        <h4>Special Thanks:</h4>
        <p>To the open source community for providing the foundational libraries
        that make this application possible.</p>
        """)

    def _populate_system_tab(self):
        """Popula a aba System com informações do sistema"""
        if not self.system_text:
            return
        
        import platform
        import sys

        from PyQt6.QtCore import PYQT_VERSION_STR, QT_VERSION_STR

        try:
            import numpy as np
            numpy_version = np.__version__
        except ImportError:
            numpy_version = "Not available"

        try:
            import pandas as pd
            pandas_version = pd.__version__
        except ImportError:
            pandas_version = "Not available"

        try:
            import pyqtgraph as pg
            pyqtgraph_version = pg.__version__
        except ImportError:
            pyqtgraph_version = "Not available"

        try:
            import pyvista as pv
            pyvista_version = pv.__version__
        except ImportError:
            pyvista_version = "Not available"

        system_info = f"""
        <h3>System Information</h3>

        <h4>Application:</h4>
        <table>
        <tr><td><b>Version:</b></td><td>2.0.0</td></tr>
        <tr><td><b>Build Date:</b></td><td>2024</td></tr>
        <tr><td><b>Architecture:</b></td><td>Desktop PyQt6</td></tr>
        </table>

        <h4>Python Environment:</h4>
        <table>
        <tr><td><b>Python:</b></td><td>{sys.version}</td></tr>
        <tr><td><b>Platform:</b></td><td>{platform.platform()}</td></tr>
        <tr><td><b>Processor:</b></td><td>{platform.processor()}</td></tr>
        </table>

        <h4>Qt/PyQt:</h4>
        <table>
        <tr><td><b>Qt Version:</b></td><td>{QT_VERSION_STR}</td></tr>
        <tr><td><b>PyQt6 Version:</b></td><td>{PYQT_VERSION_STR}</td></tr>
        </table>

        <h4>Key Dependencies:</h4>
        <table>
        <tr><td><b>NumPy:</b></td><td>{numpy_version}</td></tr>
        <tr><td><b>pandas:</b></td><td>{pandas_version}</td></tr>
        <tr><td><b>pyqtgraph:</b></td><td>{pyqtgraph_version}</td></tr>
        <tr><td><b>PyVista:</b></td><td>{pyvista_version}</td></tr>
        </table>
        """
        self.system_text.setHtml(system_info)

    def _populate_license_tab(self):
        """Popula a aba License com informações de licença"""
        if not self.license_text:
            return
        self.license_text.setPlainText("""
Platform Base v2.0
Copyright (c) 2024 TRANSPETRO

This software is provided for internal use at TRANSPETRO for time series
data analysis and exploration purposes.

The software is provided "AS IS", without warranty of any kind, express or
implied, including but not limited to the warranties of merchantability,
fitness for a particular purpose and noninfringement.

Third-party libraries used in this application are licensed under their
respective licenses. See the Credits tab for more information about
third-party components.

For support or questions about this software, please contact the
development team.
        """)
