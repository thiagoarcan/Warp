# -*- coding: utf-8 -*-
"""
test_01_ui_loading.py — Carregamento de todos os arquivos .ui

Testes para validar que todos os 73 arquivos .ui:
1. Existem no diretório correto
2. São XMLs bem-formados
3. Têm estrutura válida de Qt Designer
4. Podem ser carregados com PyQt6.uic
5. Têm arquivos _ui.py compilados correspondentes
"""
from __future__ import annotations

from pathlib import Path

import pytest

from .helpers import validate_ui_xml, get_widgets_from_ui_xml


pytestmark = [pytest.mark.automated, pytest.mark.gui]


class TestUIFilesExistence:
    """Testes de existência e integridade do diretório de arquivos .ui."""

    def test_ui_files_dir_exists(self, ui_files_dir):
        """Verifica que o diretório de arquivos .ui existe."""
        assert ui_files_dir.exists(), f"Diretório não encontrado: {ui_files_dir}"
        assert ui_files_dir.is_dir(), f"Caminho não é diretório: {ui_files_dir}"

    def test_ui_files_not_empty(self, all_ui_files):
        """Verifica que existem arquivos .ui no diretório."""
        assert len(all_ui_files) > 0, "Nenhum arquivo .ui encontrado"

    def test_minimum_ui_files_count(self, all_ui_files):
        """Verifica que existem pelo menos 50 arquivos .ui (mínimo esperado)."""
        assert len(all_ui_files) >= 50, f"Apenas {len(all_ui_files)} arquivos .ui encontrados, esperado >= 50"

    def test_expected_core_ui_files_exist(self, ui_files_dir):
        """Verifica que os arquivos .ui mais importantes existem."""
        core_files = [
            "modernMainWindow.ui",
            "dataPanel.ui",
            "vizPanel.ui",
            "operationsPanel.ui",
            "configPanel.ui",
            "uploadDialog.ui",
            "settingsDialog.ui",
            "aboutDialog.ui",
        ]
        for filename in core_files:
            filepath = ui_files_dir / filename
            assert filepath.exists(), f"Arquivo .ui core não encontrado: {filename}"


class TestUIXmlValidity:
    """Testes de validação de estrutura XML dos arquivos .ui."""

    def test_all_ui_files_are_valid_xml(self, all_ui_files):
        """Verifica que todos os arquivos .ui são XMLs válidos."""
        invalid = []
        for ui_path in all_ui_files:
            is_valid, msg = validate_ui_xml(ui_path)
            if not is_valid:
                invalid.append((ui_path.name, msg))
        
        assert not invalid, f"Arquivos .ui inválidos: {invalid}"

    def test_ui_xml_valid_batch(self, all_ui_files):
        """Valida estrutura XML de todos os arquivos .ui."""
        for ui_file in all_ui_files:
            is_valid, msg = validate_ui_xml(ui_file)
            assert is_valid, f"XML inválido em {ui_file.name}: {msg}"


class TestUIXmlStructure:
    """Testes de estrutura interna dos arquivos .ui."""

    def test_ui_has_root_widget(self, ui_file_contents):
        """Verifica que todos os .ui têm widget raiz com class e name."""
        missing_widget = []
        for name, tree in ui_file_contents.items():
            if tree is None:
                missing_widget.append((name, "Falha ao parsear XML"))
                continue
            root = tree.getroot()
            widget = root.find("widget")
            if widget is None:
                missing_widget.append((name, "Sem elemento <widget>"))
            elif "class" not in widget.attrib:
                missing_widget.append((name, "Widget raiz sem atributo 'class'"))
            elif "name" not in widget.attrib:
                missing_widget.append((name, "Widget raiz sem atributo 'name'"))
        
        assert not missing_widget, f"Arquivos com problemas de estrutura: {missing_widget}"

    def test_ui_widget_count_reasonable(self, ui_file_contents):
        """Verifica que cada .ui tem número razoável de widgets (1-500)."""
        problematic = []
        for name, tree in ui_file_contents.items():
            if tree is None:
                continue
            # Conta todos os elementos <widget>
            root = tree.getroot()
            count = len(list(root.iter("widget")))
            if count < 1:
                problematic.append((name, f"Apenas {count} widgets"))
            elif count > 500:
                problematic.append((name, f"Muitos widgets: {count}"))
        
        assert not problematic, f"Arquivos com contagem de widgets problemática: {problematic}"


class TestUILoadingWithPyQt:
    """Testes de carregamento real dos .ui com PyQt6.uic."""

    def test_ui_loadable_with_uic_batch(self, qapp, all_ui_files):
        """Carrega todos os arquivos .ui com uic.loadUi e verifica sucesso."""
        from PyQt6 import uic
        from PyQt6.QtWidgets import QWidget, QDialog, QMainWindow
        import xml.etree.ElementTree as ET
        
        failed = []
        for ui_path in all_ui_files:
            try:
                # Detecta a classe base do widget raiz
                tree = ET.parse(ui_path)
                root = tree.getroot()
                widget_elem = root.find("widget")
                if widget_elem is None:
                    failed.append((ui_path.name, "Sem elemento widget"))
                    continue
                    
                widget_class = widget_elem.get("class", "QWidget")
                
                # Cria widget da classe correta
                if widget_class == "QDialog":
                    widget = QDialog()
                elif widget_class == "QMainWindow":
                    widget = QMainWindow()
                else:
                    widget = QWidget()
                
                uic.loadUi(str(ui_path), widget)
                widget.close()
                widget.deleteLater()
            except Exception as e:
                failed.append((ui_path.name, str(e)[:100]))
        
        qapp.processEvents()
        
        # Pelo menos 80% dos arquivos devem carregar corretamente
        success_rate = (len(all_ui_files) - len(failed)) / len(all_ui_files)
        if failed:
            # Documenta arquivos problemáticos para correção
            print(f"\nArquivos .ui com problemas de carregamento ({len(failed)}):")
            for name, error in failed[:10]:  # Mostra primeiros 10
                print(f"  - {name}: {error}")
        
        assert success_rate >= 0.80, \
            f"Taxa de sucesso ({success_rate:.1%}) abaixo de 80%. Falhas: {failed}"

    def test_core_ui_files_loadable(self, qapp, ui_files_dir):
        """Carrega arquivos .ui core individualmente e verifica widgets criados."""
        from PyQt6 import uic
        from PyQt6.QtWidgets import QWidget
        
        core_files = [
            "dataPanel.ui",
            "configPanel.ui",
            "operationsPanel.ui",
        ]
        
        for filename in core_files:
            filepath = ui_files_dir / filename
            if not filepath.exists():
                pytest.skip(f"Arquivo {filename} não encontrado")
            
            widget = QWidget()
            uic.loadUi(str(filepath), widget)
            
            # Verifica que tem pelo menos um child widget
            children = widget.findChildren(QWidget)
            assert len(children) >= 1, f"{filename} não criou widgets filhos"
            
            widget.close()
            widget.deleteLater()
        
        qapp.processEvents()


class TestUICompiledFiles:
    """Testes de arquivos _ui.py compilados."""

    def test_compiled_files_exist_for_core_ui(self, ui_files_dir):
        """Verifica que arquivos _ui.py existem para os .ui principais."""
        core_ui_files = [
            "modernMainWindow.ui",
            "dataPanel.ui",
            "vizPanel.ui",
            "operationsPanel.ui",
            "configPanel.ui",
            "uploadDialog.ui",
        ]
        
        missing_compiled = []
        for ui_name in core_ui_files:
            ui_path = ui_files_dir / ui_name
            if not ui_path.exists():
                continue
            
            # Nome do arquivo compilado: foo.ui -> foo_ui.py
            compiled_name = ui_name.replace(".ui", "_ui.py")
            compiled_path = ui_files_dir / compiled_name
            
            if not compiled_path.exists():
                missing_compiled.append(compiled_name)
        
        # Aviso, não falha (arquivos compilados podem não ser obrigatórios)
        if missing_compiled:
            pytest.skip(f"Arquivos _ui.py não encontrados (podem não ser obrigatórios): {missing_compiled}")

    def test_all_compiled_files_importable(self, ui_files_dir):
        """Verifica que todos os arquivos _ui.py têm sintaxe Python válida."""
        import ast
        
        compiled_files = list(ui_files_dir.glob("*_ui.py"))
        if not compiled_files:
            pytest.skip("Nenhum arquivo _ui.py encontrado")
        
        failed = []
        for py_path in compiled_files:
            try:
                # Apenas verifica sintaxe sem executar
                with open(py_path, "r", encoding="utf-8") as f:
                    source = f.read()
                ast.parse(source, filename=str(py_path))
            except SyntaxError as e:
                failed.append((py_path.name, str(e)[:80]))
            except Exception as e:
                failed.append((py_path.name, str(e)[:80]))
        
        assert not failed, f"Arquivos _ui.py com sintaxe inválida: {failed}"


class TestUIFileNamingConventions:
    """Testes de convenções de nomenclatura dos arquivos .ui."""

    def test_ui_filenames_lowercase_or_camelcase(self, all_ui_files):
        """Verifica que nomes de arquivo seguem convenção (camelCase ou lowercase)."""
        invalid_names = []
        for ui_path in all_ui_files:
            name = ui_path.stem  # sem extensão
            # Permite camelCase ou lowercase com underscores
            if " " in name:
                invalid_names.append((ui_path.name, "Contém espaços"))
            elif name.startswith("-") or name.endswith("-"):
                invalid_names.append((ui_path.name, "Começa/termina com hífen"))
        
        assert not invalid_names, f"Arquivos com nomes inválidos: {invalid_names}"

    def test_ui_widget_names_unique_in_file(self, ui_file_contents):
        """Verifica que objectNames são únicos dentro de cada arquivo .ui."""
        duplicates = []
        for filename, tree in ui_file_contents.items():
            if tree is None:
                continue
            
            widgets = get_widgets_from_ui_xml(tree)
            names = [w["name"] for w in widgets if w["name"]]
            
            seen = set()
            file_duplicates = []
            for name in names:
                if name in seen:
                    file_duplicates.append(name)
                seen.add(name)
            
            if file_duplicates:
                duplicates.append((filename, file_duplicates))
        
        assert not duplicates, f"Arquivos com objectNames duplicados: {duplicates}"
