"""
AboutDialog - About dialog for Platform Base v2.0

Shows application information, version, and credits.
"""

from __future__ import annotations

from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTextEdit, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap

from platform_base.utils.logging import get_logger
from platform_base.utils.i18n import tr

logger = get_logger(__name__)


class AboutDialog(QDialog):
    """
    About dialog showing application information.
    
    Features:
    - Application version and build info
    - Credits and acknowledgments
    - System information
    - License information
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._setup_ui()
        
        logger.debug("about_dialog_initialized")
    
    def _setup_ui(self):
        """Setup user interface"""
        self.setWindowTitle(tr("About Platform Base"))
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Header with logo and title
        header_layout = QHBoxLayout()
        
        # Logo placeholder (would load from resources)
        logo_label = QLabel()
        logo_label.setFixedSize(64, 64)
        logo_label.setStyleSheet("border: 1px solid gray; background: lightblue;")
        logo_label.setText(tr("Logo"))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(logo_label)
        
        # Title and version
        title_layout = QVBoxLayout()
        
        title_label = QLabel(tr("Platform Base"))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)
        
        version_label = QLabel(tr("Version 2.0.0"))
        version_label.setStyleSheet("color: gray;")
        title_layout.addWidget(version_label)
        
        subtitle_label = QLabel(tr("Time Series Analysis Tool"))
        title_layout.addWidget(subtitle_label)
        
        title_layout.addStretch()
        header_layout.addLayout(title_layout)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Information tabs
        self.tabs = QTabWidget()
        
        # About tab
        about_tab = self._create_about_tab()
        self.tabs.addTab(about_tab, tr("About"))
        
        # Credits tab
        credits_tab = self._create_credits_tab()
        self.tabs.addTab(credits_tab, tr("Credits"))
        
        # System info tab
        system_tab = self._create_system_tab()
        self.tabs.addTab(system_tab, tr("System"))
        
        # License tab
        license_tab = self._create_license_tab()
        self.tabs.addTab(license_tab, tr("License"))
        
        layout.addWidget(self.tabs)
        
        # Close button
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        close_btn = QPushButton(tr("Close"))
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
    
    def _create_about_tab(self) -> QWidget:
        """Create about tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setHtml("""
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
        layout.addWidget(about_text)
        
        return widget
    
    def _create_credits_tab(self) -> QWidget:
        """Create credits tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        credits_text = QTextEdit()
        credits_text.setReadOnly(True)
        credits_text.setHtml("""
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
        layout.addWidget(credits_text)
        
        return widget
    
    def _create_system_tab(self) -> QWidget:
        """Create system information tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        system_text = QTextEdit()
        system_text.setReadOnly(True)
        
        # Gather system information
        import sys
        import platform
        from PyQt6.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
        
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
        
        system_text.setHtml(system_info)
        layout.addWidget(system_text)
        
        return widget
    
    def _create_license_tab(self) -> QWidget:
        """Create license information tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        license_text = QTextEdit()
        license_text.setReadOnly(True)
        license_text.setPlainText("""
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
        layout.addWidget(license_text)
        
        return widget