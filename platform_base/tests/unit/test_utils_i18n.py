"""
Tests for utils/i18n.py - Internationalization System

Tests for I18n class and translation functions.
"""

import json
import tempfile
from pathlib import Path

import pytest


class TestI18nClass:
    """Tests for I18n class"""

    def test_i18n_creation_default_language(self):
        """Test creating I18n with default language"""
        from platform_base.utils.i18n import I18n
        
        i18n = I18n()
        
        assert i18n.language == "pt-BR"

    def test_i18n_creation_custom_language(self):
        """Test creating I18n with custom language"""
        from platform_base.utils.i18n import I18n
        
        i18n = I18n("en-US")
        
        assert i18n.language == "en-US"

    def test_i18n_tr_translated(self):
        """Test tr returns translated text"""
        from platform_base.utils.i18n import I18n
        
        i18n = I18n("pt-BR")
        
        # This should be translated
        result = i18n.tr("File")
        assert result == "Arquivo"

    def test_i18n_tr_not_translated(self):
        """Test tr returns original text if no translation"""
        from platform_base.utils.i18n import I18n
        
        i18n = I18n("pt-BR")
        
        # Non-existent key returns original
        result = i18n.tr("NonExistentKey12345")
        assert result == "NonExistentKey12345"

    def test_i18n_set_language(self):
        """Test set_language changes language"""
        from platform_base.utils.i18n import I18n
        
        i18n = I18n("pt-BR")
        i18n.set_language("en-US")
        
        assert i18n.language == "en-US"

    def test_i18n_set_language_pt_br(self):
        """Test set_language to pt-BR loads translations"""
        from platform_base.utils.i18n import I18n
        
        i18n = I18n("en-US")
        i18n.set_language("pt-BR")
        
        # Should now have Portuguese translations
        assert i18n.tr("File") == "Arquivo"

    def test_i18n_set_language_other_clears_translations(self):
        """Test set_language to other language clears translations"""
        from platform_base.utils.i18n import I18n
        
        i18n = I18n("pt-BR")
        i18n.set_language("fr-FR")
        
        # Should return original (no French translations)
        assert i18n.tr("File") == "File"

    def test_i18n_get_language(self):
        """Test get_language returns current language"""
        from platform_base.utils.i18n import I18n
        
        i18n = I18n("de-DE")
        
        assert i18n.get_language() == "de-DE"

    def test_i18n_add_translation(self):
        """Test add_translation adds custom translation"""
        from platform_base.utils.i18n import I18n
        
        i18n = I18n("pt-BR")
        i18n.add_translation("Custom Key", "Chave Personalizada")
        
        assert i18n.tr("Custom Key") == "Chave Personalizada"

    def test_i18n_add_translation_overwrites(self):
        """Test add_translation overwrites existing translation"""
        from platform_base.utils.i18n import I18n
        
        i18n = I18n("pt-BR")
        original = i18n.tr("File")
        
        i18n.add_translation("File", "Ficheiro")
        
        assert i18n.tr("File") == "Ficheiro"
        assert original != i18n.tr("File")
        
        # Restore original (don't affect global)
        i18n.add_translation("File", original)


class TestI18nFileSave:
    """Tests for I18n save_translations"""

    def test_save_translations(self):
        """Test saving translations to file"""
        from platform_base.utils.i18n import I18n
        
        i18n = I18n("pt-BR")
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name
        
        try:
            i18n.save_translations(temp_path)
            
            # Verify file exists and contains valid JSON
            with open(temp_path, encoding="utf-8") as f:
                data = json.load(f)
            
            assert isinstance(data, dict)
            assert len(data) > 0
        finally:
            Path(temp_path).unlink()

    def test_save_translations_utf8(self):
        """Test save_translations preserves UTF-8 characters"""
        from platform_base.utils.i18n import I18n
        
        i18n = I18n("pt-BR")
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name
        
        try:
            i18n.save_translations(temp_path)
            
            with open(temp_path, encoding="utf-8") as f:
                content = f.read()
            
            # Should contain Portuguese characters
            assert "Arquivo" in content or "Análise" in content
        finally:
            Path(temp_path).unlink()


class TestI18nFileLoad:
    """Tests for I18n load_translations"""

    def test_load_translations(self):
        """Test loading translations from file"""
        from platform_base.utils.i18n import I18n
        
        i18n = I18n("en-US")  # Start with no translations
        
        # Create test file
        translations = {"Test Key": "Test Value"}
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(translations, f)
            temp_path = f.name
        
        try:
            i18n.load_translations(temp_path)
            
            assert i18n.tr("Test Key") == "Test Value"
        finally:
            Path(temp_path).unlink()

    def test_load_translations_file_not_found(self):
        """Test load_translations handles missing file gracefully"""
        from platform_base.utils.i18n import I18n
        
        i18n = I18n("pt-BR")
        
        # Should not raise
        i18n.load_translations("/nonexistent/path/translations.json")

    def test_load_translations_invalid_json(self):
        """Test load_translations handles invalid JSON gracefully"""
        from platform_base.utils.i18n import I18n
        
        i18n = I18n("pt-BR")
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("not valid json {{{")
            temp_path = f.name
        
        try:
            # Should not raise
            i18n.load_translations(temp_path)
        finally:
            Path(temp_path).unlink()


class TestConvenienceFunctions:
    """Tests for module-level convenience functions"""

    def test_tr_function(self):
        """Test tr convenience function"""
        from platform_base.utils.i18n import set_language, tr

        # Ensure pt-BR is set
        set_language("pt-BR")
        
        result = tr("File")
        assert result == "Arquivo"

    def test_set_language_function(self):
        """Test set_language convenience function"""
        from platform_base.utils.i18n import get_language, set_language
        
        original = get_language()
        
        try:
            set_language("es-ES")
            assert get_language() == "es-ES"
        finally:
            set_language(original)

    def test_get_language_function(self):
        """Test get_language convenience function"""
        from platform_base.utils.i18n import get_language
        
        result = get_language()
        assert isinstance(result, str)

    def test_get_i18n_function(self):
        """Test get_i18n returns I18n instance"""
        from platform_base.utils.i18n import I18n, get_i18n
        
        result = get_i18n()
        assert isinstance(result, I18n)


class TestTranslations:
    """Tests for actual translations"""

    def test_menu_translations_exist(self):
        """Test common menu items are translated"""
        from platform_base.utils.i18n import TRANSLATIONS_PT_BR
        
        assert "File" in TRANSLATIONS_PT_BR
        assert "Edit" in TRANSLATIONS_PT_BR
        assert "Help" in TRANSLATIONS_PT_BR

    def test_action_translations_exist(self):
        """Test common actions are translated"""
        from platform_base.utils.i18n import TRANSLATIONS_PT_BR
        
        assert "Open" in TRANSLATIONS_PT_BR
        assert "Save" in TRANSLATIONS_PT_BR
        assert "Close" in TRANSLATIONS_PT_BR

    def test_button_translations_exist(self):
        """Test common buttons are translated"""
        from platform_base.utils.i18n import TRANSLATIONS_PT_BR
        
        assert "OK" in TRANSLATIONS_PT_BR
        assert "Cancel" in TRANSLATIONS_PT_BR
        assert "Apply" in TRANSLATIONS_PT_BR

    def test_translation_values_are_portuguese(self):
        """Test translation values are in Portuguese"""
        from platform_base.utils.i18n import I18n

        # Use fresh instance to avoid pollution
        i18n = I18n("pt-BR")
        
        assert i18n.tr("File") == "Arquivo"
        assert i18n.tr("Edit") == "Editar"
        assert i18n.tr("Help") == "Ajuda"

    def test_translations_dict_is_nonempty(self):
        """Test translations dictionary has content"""
        from platform_base.utils.i18n import TRANSLATIONS_PT_BR
        
        assert len(TRANSLATIONS_PT_BR) > 100  # Should have many translations
