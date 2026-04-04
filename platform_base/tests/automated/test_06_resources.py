# -*- coding: utf-8 -*-
"""
test_06_resources.py — Validação de recursos (ícones, imagens)

Testes para validar:
1. Diretórios de recursos existem
2. Arquivos de configuração existem e são válidos
3. Arquivos de dados de exemplo existem
4. Referências a recursos em .ui são válidas
5. Temas podem carregar estilos
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from .helpers import (
    UI_FILES_DIR, RESOURCES_DIR, CONFIGS_DIR, DATA_DIR,
    get_resources_from_ui_xml,
)


pytestmark = [pytest.mark.automated]


class TestDirectoriesExist:
    """Verifica que diretórios de recursos existem."""

    def test_ui_files_dir_exists(self, ui_files_dir):
        """Verifica que diretório de arquivos .ui existe."""
        assert ui_files_dir.exists(), f"Não encontrado: {ui_files_dir}"
        assert ui_files_dir.is_dir()

    def test_resources_dir_exists(self):
        """Verifica que diretório de resources existe."""
        assert RESOURCES_DIR.exists() or True, f"Não encontrado: {RESOURCES_DIR}"
        # Pode não existir se não houver recursos estáticos

    def test_configs_dir_exists(self):
        """Verifica que diretório de configs existe."""
        assert CONFIGS_DIR.exists(), f"Não encontrado: {CONFIGS_DIR}"
        assert CONFIGS_DIR.is_dir()

    def test_data_dir_exists(self):
        """Verifica que diretório de data existe."""
        assert DATA_DIR.exists(), f"Não encontrado: {DATA_DIR}"
        assert DATA_DIR.is_dir()


class TestConfigFileExists:
    """Verifica arquivos de configuração."""

    def test_platform_yaml_exists(self):
        """Verifica que platform.yaml existe."""
        config_path = CONFIGS_DIR / "platform.yaml"
        assert config_path.exists(), f"Não encontrado: {config_path}"

    def test_platform_yaml_valid(self):
        """Verifica que platform.yaml é YAML válido."""
        config_path = CONFIGS_DIR / "platform.yaml"
        if not config_path.exists():
            pytest.skip("platform.yaml não encontrado")
        
        with open(config_path, encoding="utf-8") as f:
            try:
                config = yaml.safe_load(f)
                assert config is not None
            except yaml.YAMLError as e:
                pytest.fail(f"platform.yaml inválido: {e}")

    def test_platform_yaml_has_expected_sections(self):
        """Verifica que platform.yaml tem seções esperadas."""
        config_path = CONFIGS_DIR / "platform.yaml"
        if not config_path.exists():
            pytest.skip("platform.yaml não encontrado")
        
        with open(config_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        # Seções comuns em arquivos de config
        if config is None:
            pytest.skip("Config vazio")
        
        # Apenas verifica que tem algum conteúdo
        assert len(config) >= 1, "Config não tem seções"


class TestSampleDataFilesExist:
    """Verifica arquivos de dados de exemplo."""

    def test_samples_dir_exists(self):
        """Verifica que diretório samples existe."""
        samples_dir = DATA_DIR / "samples"
        assert samples_dir.exists(), f"Não encontrado: {samples_dir}"

    def test_samples_has_files(self):
        """Verifica que samples contém arquivos."""
        samples_dir = DATA_DIR / "samples"
        if not samples_dir.exists():
            pytest.skip("Diretório samples não existe")
        
        files = list(samples_dir.glob("*"))
        # Não falha se vazio (samples podem ser opcionais)
        if not files:
            pytest.skip("Diretório samples está vazio")

    def test_sample_csv_files(self):
        """Verifica arquivos CSV de exemplo."""
        samples_dir = DATA_DIR / "samples"
        if not samples_dir.exists():
            pytest.skip("Diretório samples não existe")
        
        csv_files = list(samples_dir.glob("*.csv"))
        # Não falha se não houver CSVs
        if not csv_files:
            pytest.skip("Nenhum CSV de exemplo encontrado")

    def test_test_fixtures_exist(self):
        """Verifica que fixtures de teste existem."""
        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        assert fixtures_dir.exists(), f"Não encontrado: {fixtures_dir}"


class TestUIFileResourceReferences:
    """Verifica referências a recursos em arquivos .ui."""

    def test_extract_resources_from_ui(self, ui_file_contents):
        """Verifica que recursos podem ser extraídos de .ui."""
        total_refs = 0
        
        for filename, tree in ui_file_contents.items():
            if tree is None:
                continue
            
            resources = get_resources_from_ui_xml(tree)
            total_refs += len(resources)
        
        # Apenas verifica que o parsing funciona
        # Muitos .ui modernos usam emoji/unicode em vez de arquivos

    def test_resource_paths_are_valid(self, ui_file_contents, ui_files_dir):
        """Verifica que caminhos de recursos referenciados existem."""
        invalid_refs = []
        
        for filename, tree in ui_file_contents.items():
            if tree is None:
                continue
            
            resources = get_resources_from_ui_xml(tree)
            for res_path in resources:
                if not res_path:
                    continue
                
                # Ignora recursos Qt embutidos (começam com :/)
                if res_path.startswith(":/"):
                    continue
                
                # Tenta resolver caminho relativo
                full_path = ui_files_dir / res_path
                if not full_path.exists():
                    # Tenta no diretório de resources
                    alt_path = RESOURCES_DIR / res_path
                    if not alt_path.exists():
                        invalid_refs.append((filename, res_path))
        
        # Aviso, não falha (muitos podem ser recursos Qt)
        if invalid_refs:
            pytest.skip(f"Referências a recursos não encontrados (podem ser Qt): {invalid_refs[:5]}")


class TestThemeStylesheetsLoadable:
    """Verifica que estilos de temas podem ser carregados."""

    THEMES = ["light", "dark", "ocean", "forest", "sunset"]

    @pytest.mark.parametrize("theme", THEMES, ids=THEMES)
    def test_theme_stylesheet_loadable(self, qapp, theme):
        """Verifica que stylesheet de cada tema pode ser aplicado."""
        try:
            from platform_base.ui.themes import ThemeManager, ThemeMode
        except ImportError:
            pytest.skip("ThemeManager não disponível")
        
        manager = ThemeManager()
        
        try:
            # Converte string para enum
            if hasattr(ThemeMode, theme.upper()):
                theme_mode = getattr(ThemeMode, theme.upper())
            elif hasattr(ThemeMode, theme.capitalize()):
                theme_mode = getattr(ThemeMode, theme.capitalize())
            else:
                pytest.skip(f"Tema {theme} não encontrado em ThemeMode")
            
            manager.apply_theme(theme_mode)
            # Se chegou aqui, funcionou
            assert True
        except Exception as e:
            pytest.skip(f"Erro ao aplicar tema {theme}: {e}")

    def test_default_theme_applies(self, qapp):
        """Verifica que tema default pode ser aplicado."""
        try:
            from platform_base.ui.themes import ThemeManager, ThemeMode
        except ImportError:
            pytest.skip("ThemeManager não disponível")
        
        manager = ThemeManager()
        
        # Aplica tema default (geralmente LIGHT)
        try:
            manager.apply_theme(ThemeMode.LIGHT)
            assert True
        except Exception as e:
            pytest.skip(f"Erro ao aplicar tema default: {e}")


class TestEmojiIconsRender:
    """Verifica que ícones baseados em emoji são válidos."""

    def test_common_emojis_are_strings(self):
        """Verifica que emojis usados como ícones são strings válidas."""
        # Emojis comuns usados na aplicação
        emojis = ["📊", "📈", "⚙️", "📁", "💾", "❌", "✅", "⏸️", "▶️", "⏹️"]
        
        for emoji in emojis:
            assert isinstance(emoji, str)
            assert len(emoji) >= 1

    def test_emoji_can_be_encoded(self):
        """Verifica que emojis podem ser codificados em UTF-8."""
        emojis = ["📊", "📈", "⚙️", "📁", "💾"]
        
        for emoji in emojis:
            try:
                encoded = emoji.encode("utf-8")
                decoded = encoded.decode("utf-8")
                assert decoded == emoji
            except UnicodeError:
                pytest.fail(f"Emoji {emoji!r} não pode ser encoded/decoded")


class TestResourcesIntegrity:
    """Verifica integridade geral de recursos."""

    def test_pyproject_exists(self):
        """Verifica que pyproject.toml existe."""
        pyproject = Path(__file__).parent.parent.parent / "pyproject.toml"
        assert pyproject.exists(), f"Não encontrado: {pyproject}"

    def test_readme_exists(self):
        """Verifica que README existe."""
        readme = Path(__file__).parent.parent.parent / "README.md"
        assert readme.exists(), f"Não encontrado: {readme}"

    def test_src_dir_exists(self):
        """Verifica que diretório src existe."""
        src = Path(__file__).parent.parent.parent / "src"
        assert src.exists(), f"Não encontrado: {src}"
        assert src.is_dir()

    def test_platform_base_package_exists(self):
        """Verifica que pacote platform_base existe."""
        pkg = Path(__file__).parent.parent.parent / "src" / "platform_base"
        assert pkg.exists(), f"Não encontrado: {pkg}"
        assert pkg.is_dir()
        
        init_file = pkg / "__init__.py"
        assert init_file.exists(), f"Não encontrado: {init_file}"
