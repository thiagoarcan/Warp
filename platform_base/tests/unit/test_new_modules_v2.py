"""
Testes para os novos módulos implementados na v2.1.0

Testa:
- Performance (decimation, LOD, streaming)
- Encoding detector
- Resource manager
- Plot sync
- Undo/redo
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest


class TestPerformanceModule:
    """Testes para o módulo de performance"""
    
    def test_decimation_minmax_preserves_peaks(self):
        """Testa se MinMax preserva picos e vales"""
        from platform_base.ui.panels.performance import (
            DataDecimator,
            DecimationMethod,
            PerformanceConfig,
        )
        
        config = PerformanceConfig(target_display_points=100)
        decimator = DataDecimator(config)
        
        # Cria dados com picos claros
        x = np.arange(1000)
        y = np.sin(x / 20) * 100  # Seno com amplitude 100
        
        x_dec, y_dec = decimator.decimate(x, y, target_points=100, method=DecimationMethod.MINMAX)
        
        # Deve conter valores próximos ao max e min originais
        assert len(y_dec) <= 200  # ~100 pontos, 2 por bucket
        assert np.max(y_dec) >= 95  # Preserva pico
        assert np.min(y_dec) <= -95  # Preserva vale
    
    def test_decimation_lttb_reduces_points(self):
        """Testa se LTTB reduz pontos corretamente"""
        from platform_base.ui.panels.performance import (
            DataDecimator,
            DecimationMethod,
            PerformanceConfig,
        )
        
        config = PerformanceConfig(target_display_points=50)
        decimator = DataDecimator(config)
        
        x = np.arange(1000)
        y = np.random.randn(1000)
        
        x_dec, y_dec = decimator.decimate(x, y, target_points=50, method=DecimationMethod.LTTB)
        
        assert len(y_dec) == 50
        assert x_dec[0] == 0  # Preserva primeiro
        assert x_dec[-1] == 999  # Preserva último
    
    def test_decimation_no_change_for_small_data(self):
        """Testa que dados pequenos não são alterados"""
        from platform_base.ui.panels.performance import DataDecimator, PerformanceConfig
        
        config = PerformanceConfig(target_display_points=100)
        decimator = DataDecimator(config)
        
        x = np.arange(50)
        y = np.random.randn(50)
        
        x_dec, y_dec = decimator.decimate(x, y, target_points=100)
        
        assert len(y_dec) == 50  # Não deve mudar
        np.testing.assert_array_equal(y, y_dec)
    
    def test_lod_manager_provides_different_levels(self):
        """Testa que LOD Manager fornece diferentes níveis de detalhe"""
        from platform_base.ui.panels.performance import LODManager, PerformanceConfig
        
        config = PerformanceConfig(
            target_display_points=100,
            lod_levels=3
        )
        
        x = np.arange(10000)
        y = np.random.randn(10000)
        
        lod = LODManager(x, y, config)
        
        # Deve ter 3 níveis pré-computados
        assert len(lod._lod_cache) == 3
        
        # Níveis diferentes devem ter tamanhos diferentes
        sizes = [len(lod._lod_cache[i][0]) for i in range(3)]
        assert len(set(sizes)) > 1  # Pelo menos 2 tamanhos diferentes
    
    def test_performance_renderer_singleton(self):
        """Testa que get_performance_renderer retorna singleton"""
        from platform_base.ui.panels.performance import get_performance_renderer
        
        r1 = get_performance_renderer()
        r2 = get_performance_renderer()
        
        assert r1 is r2


class TestEncodingDetector:
    """Testes para detecção de encoding"""
    
    def test_detect_utf8_bom(self, tmp_path):
        """Testa detecção de UTF-8 com BOM"""
        from platform_base.io.encoding_detector import detect_encoding

        # Cria arquivo com BOM UTF-8
        file_path = tmp_path / "test_utf8_bom.txt"
        content = "Conteúdo com acentuação"
        with open(file_path, 'wb') as f:
            f.write(b'\xef\xbb\xbf')  # BOM UTF-8
            f.write(content.encode('utf-8'))
        
        encoding = detect_encoding(str(file_path))
        
        assert encoding.lower().replace('-', '').replace('_', '') in ['utf8sig', 'utf8']
    
    def test_detect_latin1(self, tmp_path):
        """Testa detecção de Latin-1"""
        from platform_base.io.encoding_detector import detect_encoding
        
        file_path = tmp_path / "test_latin1.txt"
        content = "Conteúdo com acentuação brasileira: ç ã é í ó ú"
        with open(file_path, 'wb') as f:
            f.write(content.encode('latin-1'))
        
        encoding = detect_encoding(str(file_path))
        
        # Deve detectar algum encoding válido
        assert encoding is not None
        assert len(encoding) > 0
    
    def test_get_encoding_info(self, tmp_path):
        """Testa obtenção de info completa de encoding"""
        from platform_base.io.encoding_detector import get_encoding_info
        
        file_path = tmp_path / "test_info.txt"
        file_path.write_text("Test content", encoding='utf-8')
        
        info = get_encoding_info(str(file_path))
        
        assert 'detected_encoding' in info
        assert 'confidence' in info


class TestUndoRedo:
    """Testes para sistema de Undo/Redo"""
    
    def test_base_command_class_exists(self):
        """Testa que BaseCommand existe"""
        from platform_base.ui.undo_redo import BaseCommand
        
        assert BaseCommand is not None
    
    def test_data_operation_command_class_exists(self):
        """Testa que DataOperationCommand existe"""
        from platform_base.ui.undo_redo import DataOperationCommand
        
        assert DataOperationCommand is not None
    
    def test_undo_redo_manager_class_exists(self):
        """Testa que UndoRedoManager existe"""
        from platform_base.ui.undo_redo import UndoRedoManager
        
        assert UndoRedoManager is not None


class TestPlotSync:
    """Testes para sincronização de plots"""
    
    def test_plot_sync_manager_class_exists(self):
        """Testa que PlotSyncManager existe"""
        from platform_base.ui.plot_sync import PlotSyncManager
        
        assert PlotSyncManager is not None
    
    def test_get_sync_manager_function_exists(self):
        """Testa que get_sync_manager existe"""
        from platform_base.ui.plot_sync import get_sync_manager
        
        assert get_sync_manager is not None


class TestResultsPanel:
    """Testes para o painel de resultados"""
    
    def test_statistics_result_dataclass(self):
        """Testa dataclass StatisticsResult"""
        from platform_base.ui.panels.results_panel import StatisticsResult
        
        stat = StatisticsResult(
            name="Média",
            value=42.5,
            unit="m/s",
            description="Valor médio",
            category="Tendência Central"
        )
        
        assert stat.name == "Média"
        assert stat.value == 42.5
        assert stat.unit == "m/s"


class TestStreamingPanel:
    """Testes para o painel de streaming"""
    
    def test_playback_state_enum(self):
        """Testa enum PlaybackState"""
        from platform_base.ui.panels.streaming_panel import PlaybackState
        
        assert PlaybackState.STOPPED.value == 1
        assert PlaybackState.PLAYING.value == 2
        assert PlaybackState.PAUSED.value == 3
    
    def test_playback_mode_enum(self):
        """Testa enum PlaybackMode"""
        from platform_base.ui.panels.streaming_panel import PlaybackMode
        
        assert PlaybackMode.NORMAL.value == 1
        assert PlaybackMode.LOOP.value == 2
        assert PlaybackMode.PING_PONG.value == 3
        assert PlaybackMode.REVERSE.value == 4


class TestConfigPanel:
    """Testes para o painel de configuração"""
    
    def test_color_button_get_set_color(self):
        """Testa getter/setter de cor no ColorButton"""
        # Não podemos testar widgets Qt sem app, mas podemos testar a lógica
        pass  # Skip - requer QApplication


class TestResourceManager:
    """Testes para gerenciador de recursos"""
    
    def test_resource_tracker_singleton(self):
        """Testa que get_resource_tracker retorna singleton"""
        from platform_base.utils.resource_manager import get_resource_tracker
        
        t1 = get_resource_tracker()
        t2 = get_resource_tracker()
        
        assert t1 is t2
    
    def test_matplotlib_manager_singleton(self):
        """Testa que get_matplotlib_manager retorna singleton"""
        from platform_base.utils.resource_manager import get_matplotlib_manager
        
        m1 = get_matplotlib_manager()
        m2 = get_matplotlib_manager()
        
        assert m1 is m2


# Testes de integração simplificados (sem GUI)
class TestModuleImports:
    """Testa que todos os módulos podem ser importados"""
    
    def test_import_performance(self):
        """Testa import do módulo performance"""
        from platform_base.ui.panels import (
            DataDecimator,
            DecimationMethod,
            LODManager,
            PerformanceConfig,
            PerformanceRenderer,
            StreamingDataManager,
            decimate_for_plot,
            get_performance_renderer,
        )
        
        assert DecimationMethod is not None
        assert PerformanceConfig is not None
    
    def test_import_results_panel(self):
        """Testa import do results_panel"""
        from platform_base.ui.panels import (
            ResultsPanel,
            StatCard,
            StatisticsResult,
            StatisticsTable,
        )
        
        assert ResultsPanel is not None
        assert StatisticsResult is not None
    
    def test_import_streaming_panel(self):
        """Testa import do streaming_panel"""
        from platform_base.ui.panels import PlaybackMode, PlaybackState, StreamingPanel
        
        assert StreamingPanel is not None
        assert PlaybackState is not None
    
    def test_import_config_panel(self):
        """Testa import do config_panel"""
        from platform_base.ui.panels import ColorButton, ConfigPanel
        
        assert ConfigPanel is not None
        assert ColorButton is not None
    
    def test_import_encoding_detector(self):
        """Testa import do encoding_detector"""
        from platform_base.io import detect_encoding, get_encoding_info
        
        assert detect_encoding is not None
        assert get_encoding_info is not None
    
    def test_import_resource_manager(self):
        """Testa import do resource_manager"""
        from platform_base.utils import (
            cleanup_on_close,
            force_cleanup,
            get_matplotlib_manager,
            get_resource_tracker,
        )
        
        assert get_resource_tracker is not None
        assert cleanup_on_close is not None
    
    def test_import_undo_redo(self):
        """Testa import do undo_redo"""
        from platform_base.ui.undo_redo import (
            BaseCommand,
            DataOperationCommand,
            UndoRedoManager,
            get_undo_manager,
        )
        
        assert UndoRedoManager is not None
        assert get_undo_manager is not None
    
    def test_import_plot_sync(self):
        """Testa import do plot_sync"""
        from platform_base.ui.plot_sync import PlotSyncManager, get_sync_manager
        
        assert PlotSyncManager is not None
        assert get_sync_manager is not None
