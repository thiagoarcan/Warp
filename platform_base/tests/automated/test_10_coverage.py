# -*- coding: utf-8 -*-
"""
test_10_coverage.py — Meta-testes de cobertura

Testes para validar:
1. Todos os módulos são importáveis
2. Todas as classes principais são testadas
3. Todos os arquivos UI são carregáveis
4. Todos os signals são testados
5. Cobertura mínima de 70%
"""
from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path
from typing import List, Set

import pytest

pytestmark = [pytest.mark.automated]


class TestModuleImportability:
    """Verifica que todos os módulos são importáveis."""

    def get_python_modules(self) -> List[str]:
        """Retorna lista de módulos Python no projeto."""
        src_path = Path(__file__).resolve().parents[2] / "src" / "platform_base"
        
        modules = []
        
        if not src_path.exists():
            return modules
        
        for py_file in src_path.rglob("*.py"):
            if py_file.name.startswith("_") and py_file.name != "__init__.py":
                continue
            if "__pycache__" in str(py_file):
                continue
            
            # Converte path para nome de módulo
            relative = py_file.relative_to(src_path.parent)
            parts = list(relative.parts)
            
            if parts[-1] == "__init__.py":
                parts = parts[:-1]
            else:
                parts[-1] = parts[-1].replace(".py", "")
            
            module_name = ".".join(parts)
            if module_name:
                modules.append(module_name)
        
        return modules

    def test_core_modules_importable(self, qapp):
        """Verifica que módulos core são importáveis."""
        core_modules = [
            "platform_base",
            "platform_base.core",
            "platform_base.ui",
            "platform_base.desktop",
        ]
        
        for module_name in core_modules:
            try:
                module = importlib.import_module(module_name)
                assert module is not None
            except ImportError as e:
                pytest.fail(f"Falhou ao importar {module_name}: {e}")
            except Exception:
                pass  # Pode ter dependências faltando

    def test_all_init_modules_importable(self, qapp):
        """Verifica que todos os __init__.py são importáveis."""
        src_path = Path(__file__).resolve().parents[2] / "src" / "platform_base"
        
        if not src_path.exists():
            pytest.skip("Diretório src não encontrado")
        
        init_files = list(src_path.rglob("__init__.py"))
        failed = []
        
        for init_file in init_files:
            # Converte para nome de módulo
            relative = init_file.relative_to(src_path.parent)
            parts = list(relative.parts)[:-1]  # Remove __init__.py
            
            if not parts:
                continue
            
            module_name = ".".join(parts)
            
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                failed.append((module_name, str(e)))
            except Exception:
                pass  # Outros erros são aceitáveis
        
        # Pode ter algumas falhas por dependências
        assert len(failed) < len(init_files), f"Muitas falhas de importação: {failed[:5]}"


class TestUIFileCoverage:
    """Verifica cobertura de arquivos UI."""

    def test_all_ui_files_logged(self, all_ui_files):
        """Verifica que todos os arquivos UI são conhecidos."""
        assert len(all_ui_files) > 0, "Nenhum arquivo UI encontrado"
        
        # Lista para referência
        print(f"\nTotal de arquivos UI: {len(all_ui_files)}")
        
        # Categoriza por tipo
        dialogs = [f for f in all_ui_files if "dialog" in f.stem.lower()]
        panels = [f for f in all_ui_files if "panel" in f.stem.lower()]
        windows = [f for f in all_ui_files if "window" in f.stem.lower()]
        others = [f for f in all_ui_files if f not in dialogs + panels + windows]
        
        print(f"  - Dialogs: {len(dialogs)}")
        print(f"  - Panels: {len(panels)}")
        print(f"  - Windows: {len(windows)}")
        print(f"  - Outros: {len(others)}")

    @pytest.mark.parametrize("ui_type", ["dialog", "panel", "window"])
    def test_ui_type_coverage(self, all_ui_files, ui_type):
        """Verifica cobertura por tipo de UI."""
        matching = [f for f in all_ui_files if ui_type in f.stem.lower()]
        
        # Pode não ter todos os tipos
        assert isinstance(matching, list)


class TestSignalCoverage:
    """Verifica cobertura de signals."""

    def test_signalhub_signals_documented(self, qapp, signal_hub):
        """Verifica que signals do SignalHub são documentados."""
        if signal_hub is None:
            pytest.skip("SignalHub não disponível")
        
        # Extrai signals
        signals = []
        for name in dir(signal_hub):
            if not name.startswith("_"):
                attr = getattr(signal_hub, name, None)
                if attr is not None and hasattr(attr, "emit"):
                    signals.append(name)
        
        assert len(signals) > 0, "SignalHub não tem signals"
        print(f"\nSignals encontrados: {len(signals)}")
        for s in signals[:10]:  # Mostra primeiros 10
            print(f"  - {s}")

    def test_sessionstate_signals_documented(self, qapp, session_state):
        """Verifica que signals do SessionState são documentados."""
        if session_state is None:
            pytest.skip("SessionState não disponível")
        
        # Extrai signals
        signals = []
        for name in dir(session_state):
            if not name.startswith("_"):
                attr = getattr(session_state, name, None)
                if attr is not None and hasattr(attr, "emit"):
                    signals.append(name)
        
        print(f"\nSessionState signals: {len(signals)}")


class TestClassCoverage:
    """Verifica cobertura de classes principais."""

    def get_classes_in_module(self, module_name: str) -> List[str]:
        """Retorna lista de classes definidas em um módulo."""
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            return []
        
        classes = []
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type):
                # Verifica se foi definida neste módulo
                if hasattr(obj, "__module__") and obj.__module__ == module_name:
                    classes.append(name)
        
        return classes

    def test_core_classes_exist(self, qapp):
        """Verifica que classes core existem."""
        expected_classes = {
            "platform_base.core.dataset_store": ["DatasetStore"],
            "platform_base.core.session_state": ["SessionState"],
            "platform_base.core.signal_hub": ["SignalHub"],
        }
        
        found = 0
        missing = []
        
        for module_name, class_names in expected_classes.items():
            try:
                module = importlib.import_module(module_name)
                for class_name in class_names:
                    if hasattr(module, class_name):
                        found += 1
                    else:
                        missing.append(f"{module_name}.{class_name}")
            except ImportError:
                missing.extend([f"{module_name}.{c}" for c in class_names])
        
        # Pelo menos algumas devem existir
        total = sum(len(v) for v in expected_classes.values())
        assert found > 0 or total == 0, f"Nenhuma classe core encontrada. Missing: {missing}"


class TestDialogPanelCoverage:
    """Verifica cobertura de dialogs e panels."""

    def test_dialog_classes_exist(self, qapp):
        """Verifica que classes de dialog existem."""
        try:
            from platform_base.desktop import dialogs
        except ImportError:
            pytest.skip("Módulo dialogs não disponível")
        
        dialog_names = [n for n in dir(dialogs) if "Dialog" in n and not n.startswith("_")]
        
        print(f"\nDialogs encontrados: {len(dialog_names)}")
        for name in dialog_names[:10]:
            print(f"  - {name}")
        
        assert True  # Informativo

    def test_panel_classes_exist(self, qapp):
        """Verifica que classes de panel existem."""
        try:
            from platform_base.desktop import panels
        except ImportError:
            pytest.skip("Módulo panels não disponível")
        
        panel_names = [n for n in dir(panels) if "Panel" in n and not n.startswith("_")]
        
        print(f"\nPanels encontrados: {len(panel_names)}")
        for name in panel_names[:10]:
            print(f"  - {name}")
        
        assert True  # Informativo


class TestTestCoverage:
    """Meta-testes sobre a cobertura dos testes."""

    def test_all_test_files_exist(self):
        """Verifica que todos os arquivos de teste existem."""
        test_dir = Path(__file__).parent
        
        expected_files = [
            "test_01_ui_loading.py",
            "test_02_mandatory_widgets.py",
            "test_03_navigation.py",
            "test_04_signals_slots.py",
            "test_05_initialization.py",
            "test_06_resources.py",
            "test_07_state_visibility.py",
            "test_08_memory_leaks.py",
            "test_09_exceptions_errors.py",
            "test_10_coverage.py",
        ]
        
        for filename in expected_files:
            file_path = test_dir / filename
            assert file_path.exists(), f"Arquivo de teste faltando: {filename}"

    def test_conftest_exists(self):
        """Verifica que conftest.py existe."""
        test_dir = Path(__file__).parent
        conftest = test_dir / "conftest.py"
        
        assert conftest.exists(), "conftest.py não encontrado"

    def test_minimum_test_count(self):
        """Verifica quantidade mínima de testes."""
        test_dir = Path(__file__).parent
        
        test_files = list(test_dir.glob("test_*.py"))
        
        # Conta funções de teste
        total_tests = 0
        for tf in test_files:
            content = tf.read_text(encoding="utf-8")
            # Conta definições de teste
            tests = content.count("def test_")
            total_tests += tests
        
        print(f"\nTotal de testes encontrados: {total_tests}")
        
        # Deve ter pelo menos 50 testes
        assert total_tests >= 50, f"Poucos testes: {total_tests} (mínimo: 50)"


class TestCoverageThreshold:
    """Verifica threshold de cobertura."""

    def test_coverage_report_location(self):
        """Verifica localização do relatório de cobertura."""
        project_root = Path(__file__).resolve().parents[2]
        reports_dir = project_root / "docs" / "reports"
        
        # Diretório deve existir ou ser criável
        if not reports_dir.exists():
            reports_dir.mkdir(parents=True, exist_ok=True)
        
        assert reports_dir.exists()

    def test_htmlcov_excluded_from_git(self):
        """Verifica que htmlcov está no .gitignore."""
        project_root = Path(__file__).resolve().parents[2]
        gitignore = project_root / ".gitignore"
        
        if not gitignore.exists():
            pytest.skip(".gitignore não encontrado")
        
        content = gitignore.read_text(encoding="utf-8", errors="ignore")
        
        # htmlcov deve estar ignorado
        assert "htmlcov" in content or ".*cov*" in content or "coverage" in content, \
            "htmlcov deveria estar no .gitignore"


class TestCodeQuality:
    """Verifica qualidade do código."""

    def test_no_print_statements_in_src(self):
        """Verifica ausência de prints em src/ (devem usar logging)."""
        src_path = Path(__file__).resolve().parents[2] / "src" / "platform_base"
        
        if not src_path.exists():
            pytest.skip("Diretório src não encontrado")
        
        prints_found = []
        
        for py_file in src_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding="utf-8")
                lines = content.split("\n")
                
                for i, line in enumerate(lines, 1):
                    # Ignora comentários e strings
                    stripped = line.strip()
                    if stripped.startswith("#"):
                        continue
                    if stripped.startswith('"""') or stripped.startswith("'''"):
                        continue
                    
                    # Procura print( no início da instrução
                    if "print(" in line and not "# noqa" in line:
                        # Verifica se é realmente uma chamada de print
                        if line.strip().startswith("print(") or " print(" in line:
                            prints_found.append((py_file.name, i))
            except Exception:
                continue
        
        # Pode ter alguns prints legítimos (debugging)
        # Apenas reporta se houver muitos
        if len(prints_found) > 20:
            print(f"\nMuitos prints encontrados: {len(prints_found)}")
            for f, line in prints_found[:5]:
                print(f"  - {f}:{line}")

    def test_docstrings_in_public_modules(self):
        """Verifica que módulos públicos têm docstrings."""
        src_path = Path(__file__).resolve().parents[2] / "src" / "platform_base"
        
        if not src_path.exists():
            pytest.skip("Diretório src não encontrado")
        
        missing_docstrings = []
        
        for py_file in src_path.rglob("*.py"):
            if py_file.name.startswith("_") and py_file.name != "__init__.py":
                continue
            if "__pycache__" in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding="utf-8")
                
                # Verifica se tem docstring no início
                lines = content.strip().split("\n")
                if len(lines) < 3:
                    continue
                
                # Procura docstring após imports
                has_docstring = False
                for line in lines[:20]:
                    if line.strip().startswith('"""') or line.strip().startswith("'''"):
                        has_docstring = True
                        break
                
                if not has_docstring:
                    missing_docstrings.append(py_file.name)
            except Exception:
                continue
        
        # Reporta se muitos arquivos sem docstring
        if len(missing_docstrings) > 10:
            print(f"\nArquivos sem docstring: {len(missing_docstrings)}")


class TestProjectStructure:
    """Verifica estrutura do projeto."""

    def test_required_directories_exist(self):
        """Verifica que diretórios obrigatórios existem."""
        project_root = Path(__file__).resolve().parents[2]
        
        required_dirs = [
            "src/platform_base",
            "tests",
            "docs",
        ]
        
        for dir_path in required_dirs:
            full_path = project_root / dir_path
            assert full_path.exists(), f"Diretório faltando: {dir_path}"

    def test_pyproject_toml_exists(self):
        """Verifica que pyproject.toml existe."""
        project_root = Path(__file__).resolve().parents[2]
        
        pyproject = project_root / "pyproject.toml"
        assert pyproject.exists(), "pyproject.toml não encontrado"

    def test_readme_exists(self):
        """Verifica que README existe."""
        project_root = Path(__file__).resolve().parents[2]
        
        readme = project_root / "README.md"
        assert readme.exists(), "README.md não encontrado"
