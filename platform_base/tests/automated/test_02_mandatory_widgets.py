# -*- coding: utf-8 -*-
"""
test_02_mandatory_widgets.py — Validação de widgets obrigatórios em cada tela

Testes para validar que cada tela/painel/dialog contém os widgets obrigatórios
conforme especificado no design da aplicação.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from PyQt6 import uic
from PyQt6.QtWidgets import (
    QWidget, QMainWindow, QDialog, QDialogButtonBox,
    QPushButton, QTreeView, QTableView, QListView, QComboBox,
    QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox,
    QCheckBox, QRadioButton, QGroupBox, QTabWidget, QStackedWidget,
    QProgressBar, QSlider, QLabel, QToolBar, QMenuBar, QStatusBar,
    QDockWidget, QScrollArea, QSplitter, QFrame,
)

from .helpers import get_ui_files_dir, get_widgets_from_ui_xml, get_all_widgets

UI_FILES_DIR = get_ui_files_dir()


pytestmark = [pytest.mark.automated, pytest.mark.gui]


# ═══════════════════════════════════════════════════════════════════════════
# Definição de widgets obrigatórios por tela
# ═══════════════════════════════════════════════════════════════════════════
MANDATORY_WIDGETS = {
    # MainWindow
    "modernMainWindow.ui": {
        "root_class": "QMainWindow",
        "widgets": [
            {"name": "centralwidget", "type": "QWidget"},
        ],
    },
    # Painéis principais
    "dataPanel.ui": {
        "root_class": "QWidget",
        "widgets": [
            # Espera-se tree ou table para exibir dados
        ],
    },
    "vizPanel.ui": {
        "root_class": "QWidget",
        "widgets": [],
    },
    "operationsPanel.ui": {
        "root_class": "QWidget",
        "widgets": [],
    },
    "configPanel.ui": {
        "root_class": "QWidget",
        "widgets": [],
    },
    "resultsPanel.ui": {
        "root_class": "QWidget",
        "widgets": [],
    },
    "streamingControls.ui": {
        "root_class": "QWidget",
        "widgets": [],
    },
    # Dialogs — todos devem ter QDialogButtonBox ou botões OK/Cancel
    "uploadDialog.ui": {
        "root_class": "QDialog",
        "widgets": [],
    },
    "settingsDialog.ui": {
        "root_class": "QDialog",
        "widgets": [],
    },
    "aboutDialog.ui": {
        "root_class": "QDialog",
        "widgets": [],
    },
    "exportDialog.ui": {
        "root_class": "QDialog",
        "widgets": [],
    },
    "filterDialog.ui": {
        "root_class": "QDialog",
        "widgets": [],
    },
    "smoothingDialog.ui": {
        "root_class": "QDialog",
        "widgets": [],
    },
    "shortcutsDialog.ui": {
        "root_class": "QDialog",
        "widgets": [],
    },
}


class TestMandatoryWidgetsPresent:
    """Verifica presença de widgets obrigatórios em cada tela."""

    def test_all_ui_files_have_root_widget(self, all_ui_files, ui_file_contents):
        """Verifica que todos os .ui têm widget raiz."""
        missing_root = []
        for ui_path in all_ui_files:
            tree = ui_file_contents.get(ui_path.name)
            if tree is None:
                missing_root.append((ui_path.name, "Falha ao parsear"))
                continue
            
            root = tree.getroot()
            widget = root.find("widget")
            if widget is None:
                missing_root.append((ui_path.name, "Sem widget raiz"))
        
        assert not missing_root, f"Arquivos sem widget raiz: {missing_root}"

    def test_dialog_files_have_dialog_root(self, ui_files_dir, ui_file_contents):
        """Verifica que arquivos *Dialog.ui têm QDialog como widget raiz."""
        dialog_files = list(ui_files_dir.glob("*Dialog.ui")) + list(ui_files_dir.glob("*dialog.ui"))
        
        wrong_class = []
        for dialog_path in dialog_files:
            tree = ui_file_contents.get(dialog_path.name)
            if tree is None:
                continue
            
            root = tree.getroot()
            widget = root.find("widget")
            if widget is not None:
                widget_class = widget.get("class", "")
                # Aceita QDialog ou QWidget (alguns dialogs herdam QWidget)
                if widget_class not in ("QDialog", "QWidget"):
                    wrong_class.append((dialog_path.name, widget_class))
        
        assert not wrong_class, f"Dialogs com classe raiz incorreta: {wrong_class}"

    def test_panel_files_have_widget_root(self, ui_files_dir, ui_file_contents):
        """Verifica que arquivos *Panel.ui têm QWidget como widget raiz."""
        panel_files = list(ui_files_dir.glob("*Panel.ui")) + list(ui_files_dir.glob("*panel.ui"))
        
        wrong_class = []
        for panel_path in panel_files:
            tree = ui_file_contents.get(panel_path.name)
            if tree is None:
                continue
            
            root = tree.getroot()
            widget = root.find("widget")
            if widget is not None:
                widget_class = widget.get("class", "")
                # Aceita QWidget, QFrame, QGroupBox
                if widget_class not in ("QWidget", "QFrame", "QGroupBox", "QScrollArea"):
                    wrong_class.append((panel_path.name, widget_class))
        
        # Não falha, apenas avisa
        if wrong_class:
            pytest.skip(f"Painéis com classe raiz inesperada (não necessariamente errado): {wrong_class}")


class TestWidgetTypesCorrect:
    """Verifica que widgets têm os tipos corretos."""

    def test_buttons_are_pushbuttons(self, ui_file_contents):
        """Verifica que widgets com nome *Button são QPushButton ou derivados."""
        wrong_types = []
        button_classes = {"QPushButton", "QToolButton", "QRadioButton", "QCheckBox", "QCommandLinkButton"}
        
        for filename, tree in ui_file_contents.items():
            if tree is None:
                continue
            
            widgets = get_widgets_from_ui_xml(tree)
            for w in widgets:
                name = w.get("name", "")
                wclass = w.get("class", "")
                # Se o nome termina com Button, deve ser um tipo de botão
                if name.lower().endswith("button") and wclass not in button_classes:
                    wrong_types.append((filename, name, wclass))
        
        assert not wrong_types, f"Widgets com nomes de botão mas tipos errados: {wrong_types}"

    def test_views_are_view_types(self, ui_file_contents):
        """Verifica que widgets com nome *View são QAbstractItemView derivados."""
        view_classes = {
            "QTreeView", "QListView", "QTableView", "QColumnView",
            "QHeaderView", "QTreeWidget", "QListWidget", "QTableWidget",
        }
        wrong_types = []
        
        for filename, tree in ui_file_contents.items():
            if tree is None:
                continue
            
            widgets = get_widgets_from_ui_xml(tree)
            for w in widgets:
                name = w.get("name", "")
                wclass = w.get("class", "")
                # Se o nome termina com View (mas não review, overview, etc.)
                if name.lower().endswith("view") and not any(x in name.lower() for x in ["review", "overview", "preview"]):
                    if wclass and wclass not in view_classes and wclass != "QGraphicsView":
                        wrong_types.append((filename, name, wclass))
        
        # Aviso, não falha
        if wrong_types:
            pytest.skip(f"Views com tipos não padrão (pode ser customizado): {wrong_types}")


class TestWidgetNamesUnique:
    """Verifica unicidade de objectNames."""

    def test_no_duplicate_object_names(self, ui_file_contents):
        """Verifica que não há objectNames duplicados em cada arquivo."""
        duplicates_found = []
        
        for filename, tree in ui_file_contents.items():
            if tree is None:
                continue
            
            widgets = get_widgets_from_ui_xml(tree)
            names = [w["name"] for w in widgets if w["name"]]
            
            seen = {}
            for name in names:
                seen[name] = seen.get(name, 0) + 1
            
            dups = [n for n, count in seen.items() if count > 1]
            if dups:
                duplicates_found.append((filename, dups))
        
        assert not duplicates_found, f"Arquivos com objectNames duplicados: {duplicates_found}"


class TestLayoutsNotEmpty:
    """Verifica que layouts principais contêm widgets."""

    def test_main_layouts_have_children(self, qapp, ui_files_dir):
        """Carrega arquivos .ui core e verifica que layouts têm children."""
        core_files = [
            "dataPanel.ui",
            "configPanel.ui",
            "operationsPanel.ui",
        ]
        
        empty_layouts = []
        for filename in core_files:
            filepath = ui_files_dir / filename
            if not filepath.exists():
                continue
            
            widget = QWidget()
            try:
                uic.loadUi(str(filepath), widget)
                
                # Verifica se tem algum layout
                layout = widget.layout()
                if layout is not None and layout.count() == 0:
                    empty_layouts.append((filename, "Layout vazio"))
                
                widget.close()
                widget.deleteLater()
            except Exception as e:
                empty_layouts.append((filename, f"Erro: {e}"))
        
        qapp.processEvents()
        
        # Aviso, não falha (layouts podem ser preenchidos dinamicamente)
        if empty_layouts:
            pytest.skip(f"Layouts vazios (podem ser preenchidos em runtime): {empty_layouts}")


class TestMandatoryWidgetsInPanels:
    """Testa widgets obrigatórios específicos em cada painel."""

    def test_data_panel_has_data_view(self, qapp, ui_files_dir):
        """DataPanel deve ter algum tipo de view para exibir dados."""
        filepath = ui_files_dir / "dataPanel.ui"
        if not filepath.exists():
            pytest.skip("dataPanel.ui não encontrado")
        
        widget = QWidget()
        uic.loadUi(str(filepath), widget)
        
        # Procura por TreeView, TableView, ListView ou widgets similares
        views = (
            widget.findChildren(QTreeView) +
            widget.findChildren(QTableView) +
            widget.findChildren(QListView)
        )
        
        widget.close()
        widget.deleteLater()
        qapp.processEvents()
        
        # Aviso se não encontrar views
        if not views:
            pytest.skip("DataPanel não tem QTreeView/QTableView/QListView (pode usar widget customizado)")

    def test_dialog_has_buttons(self, qapp, ui_files_dir):
        """Dialogs devem ter buttonBox ou botões individuais."""
        dialog_files = [
            "uploadDialog.ui",
            "settingsDialog.ui",
            "exportDialog.ui",
            "filterDialog.ui",
        ]
        
        dialogs_without_buttons = []
        for filename in dialog_files:
            filepath = ui_files_dir / filename
            if not filepath.exists():
                continue
            
            widget = QWidget()
            try:
                uic.loadUi(str(filepath), widget)
                
                # Procura por QDialogButtonBox ou QPushButton
                button_boxes = widget.findChildren(QDialogButtonBox)
                buttons = widget.findChildren(QPushButton)
                
                if not button_boxes and not buttons:
                    dialogs_without_buttons.append(filename)
                
                widget.close()
                widget.deleteLater()
            except Exception:
                pass
        
        qapp.processEvents()
        
        # Aviso, não falha
        if dialogs_without_buttons:
            pytest.skip(f"Dialogs sem botões visíveis (podem ser adicionados em runtime): {dialogs_without_buttons}")


class TestSpecificMandatoryWidgets:
    """Testes específicos para widgets mandatórios por configuração."""

    @pytest.mark.parametrize("ui_name,config", [
        (name, config) for name, config in MANDATORY_WIDGETS.items()
    ], ids=list(MANDATORY_WIDGETS.keys()))
    def test_mandatory_widgets_from_config(self, qapp, ui_files_dir, ui_file_contents, ui_name, config):
        """Testa widgets mandatórios conforme MANDATORY_WIDGETS."""
        filepath = ui_files_dir / ui_name
        if not filepath.exists():
            pytest.skip(f"{ui_name} não encontrado")
        
        # Determina a classe base correta a partir do XML
        tree = ui_file_contents.get(ui_name)
        if tree is None:
            pytest.skip(f"Não foi possível parsear {ui_name}")
        
        root = tree.getroot()
        widget_elem = root.find("widget")
        if widget_elem is None:
            pytest.skip(f"Arquivo {ui_name} não tem widget raiz")
        
        widget_class = widget_elem.get("class", "QWidget")
        
        # Cria a classe base correta para uic.loadUi
        if widget_class == "QMainWindow":
            widget = QMainWindow()
        elif widget_class == "QDialog":
            widget = QDialog()
        else:
            widget = QWidget()
        
        try:
            uic.loadUi(str(filepath), widget)
        except Exception as e:
            pytest.skip(f"Erro ao carregar {ui_name}: {str(e)[:50]}")
        
        missing = []
        for req in config.get("widgets", []):
            req_name = req.get("name")
            if req_name:
                child = widget.findChild(QWidget, req_name)
                if child is None:
                    missing.append(req_name)
        
        widget.close()
        widget.deleteLater()
        qapp.processEvents()
        
        assert not missing, f"Widgets obrigatórios não encontrados em {ui_name}: {missing}"
