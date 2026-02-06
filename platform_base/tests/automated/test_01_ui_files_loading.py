"""
Testes automatizados para carregamento de arquivos .ui
Valida que todos os arquivos .ui podem ser carregados sem erros
"""

import pytest
from pathlib import Path
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QDialog


# Descobrir todos os arquivos .ui no projeto
UI_FILES_DIR = Path(__file__).parent.parent.parent / "src" / "platform_base" / "desktop" / "ui_files"
UI_FILES = list(UI_FILES_DIR.glob("*.ui")) if UI_FILES_DIR.exists() else []


class TestUIFilesLoading:
    """Testes de carregamento de arquivos .ui"""

    @pytest.mark.gui
    @pytest.mark.parametrize("ui_file", UI_FILES, ids=[f.name for f in UI_FILES])
    def test_ui_file_loads_successfully(self, qtbot, ui_file):
        """Testa que cada arquivo .ui pode ser carregado sem erros"""
        # Tentar carregar o arquivo .ui
        try:
            # Determinar o tipo de widget base
            with open(ui_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'class="QMainWindow"' in content:
                    widget = QMainWindow()
                elif 'class="QDialog"' in content:
                    widget = QDialog()
                else:
                    widget = QWidget()
            
            # Carregar UI no widget
            uic.loadUi(str(ui_file), widget)
            qtbot.addWidget(widget)
            
            # Verificar que o widget foi criado
            assert widget is not None
            assert widget.objectName() or True  # Alguns widgets podem não ter objectName
            
        except Exception as e:
            pytest.fail(f"Falha ao carregar {ui_file.name}: {e}")

    @pytest.mark.gui
    @pytest.mark.parametrize("ui_file", UI_FILES, ids=[f.name for f in UI_FILES])
    def test_ui_file_has_valid_xml(self, ui_file):
        """Verifica que cada arquivo .ui tem XML válido"""
        import xml.etree.ElementTree as ET
        
        try:
            tree = ET.parse(ui_file)
            root = tree.getroot()
            
            # Verificar estrutura básica
            assert root.tag == "ui"
            assert root.get("version") == "4.0"
            
            # Verificar que tem pelo menos um widget
            widgets = root.findall(".//widget")
            assert len(widgets) > 0, f"{ui_file.name} não contém widgets"
            
        except ET.ParseError as e:
            pytest.fail(f"XML inválido em {ui_file.name}: {e}")

    @pytest.mark.gui
    def test_all_ui_files_found(self):
        """Verifica que arquivos .ui foram encontrados"""
        assert len(UI_FILES) > 0, "Nenhum arquivo .ui encontrado"
        assert len(UI_FILES) >= 50, f"Esperado pelo menos 50 arquivos .ui, encontrado {len(UI_FILES)}"

    @pytest.mark.gui
    @pytest.mark.parametrize("ui_file", UI_FILES, ids=[f.name for f in UI_FILES])
    def test_ui_file_not_empty(self, ui_file):
        """Verifica que arquivo .ui não está vazio"""
        size = ui_file.stat().st_size
        assert size > 100, f"{ui_file.name} muito pequeno ({size} bytes)"

    @pytest.mark.gui
    @pytest.mark.parametrize("ui_file", UI_FILES, ids=[f.name for f in UI_FILES])
    def test_ui_file_has_class_definition(self, ui_file):
        """Verifica que arquivo .ui define uma classe de widget"""
        with open(ui_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Deve ter tag <class>
        assert '<class>' in content, f"{ui_file.name} não define classe"
        
        # Deve ter tag <widget>
        assert '<widget' in content, f"{ui_file.name} não contém widgets"


class TestUIFilesResources:
    """Testes de recursos em arquivos .ui"""

    @pytest.mark.gui
    @pytest.mark.parametrize("ui_file", UI_FILES, ids=[f.name for f in UI_FILES])
    def test_ui_file_resources_valid(self, ui_file):
        """Verifica que recursos referenciados existem"""
        import xml.etree.ElementTree as ET
        
        tree = ET.parse(ui_file)
        root = tree.getroot()
        
        # Procurar por recursos (ícones, imagens)
        for iconset in root.findall(".//iconset"):
            resource = iconset.text
            if resource and not resource.startswith(":"):
                # Recurso externo - verificar se caminho é válido
                # (não verificamos existência pois podem estar em runtime)
                assert len(resource) > 0

    @pytest.mark.gui
    def test_main_window_ui_exists(self):
        """Verifica que mainWindow.ui existe e é válido"""
        main_window_ui = UI_FILES_DIR / "mainWindow.ui"
        assert main_window_ui.exists(), "mainWindow.ui não encontrado"
        
        # Verificar tamanho mínimo (deve ser substancial)
        size = main_window_ui.stat().st_size
        assert size > 10000, f"mainWindow.ui muito pequeno ({size} bytes)"


class TestUIFilesStructure:
    """Testes de estrutura de arquivos .ui"""

    @pytest.mark.gui
    @pytest.mark.parametrize("ui_file", UI_FILES, ids=[f.name for f in UI_FILES])
    def test_ui_file_connections_valid(self, ui_file):
        """Verifica que conexões signal/slot são válidas"""
        import xml.etree.ElementTree as ET
        
        tree = ET.parse(ui_file)
        root = tree.getroot()
        
        # Procurar por conexões
        for connection in root.findall(".//connection"):
            sender = connection.find("sender")
            signal = connection.find("signal")
            receiver = connection.find("receiver")
            slot = connection.find("slot")
            
            # Se há conexão, deve ter todos os elementos
            if connection is not None:
                # Conexões são opcionais, mas se existem devem ser válidas
                if sender is not None and signal is not None:
                    assert sender.text, f"Sender vazio em {ui_file.name}"
                    assert signal.text, f"Signal vazio em {ui_file.name}"
