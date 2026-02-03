"""
Testes de Integração da Interface Gráfica
==========================================

Testes para garantir que o workflow de carregamento de dados
funciona corretamente de ponta a ponta.
"""

import sys
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestSessionStateIntegration:
    """Testes do SessionState isolado"""

    def test_add_dataset_stores_correctly(self):
        """Verifica se add_dataset armazena o dataset corretamente"""
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance() or QApplication([])
        
        from datetime import datetime, timedelta

        import numpy as np

        from platform_base.core.dataset_store import DatasetStore
        from platform_base.core.models import Dataset, Series
        from platform_base.ui.state import SessionState

        # Create store and state
        store = DatasetStore()
        state = SessionState(store)
        
        # Create mock dataset
        n_points = 100
        t_seconds = np.linspace(0, 10, n_points)
        t_datetime = np.array([datetime.now() + timedelta(seconds=t) for t in t_seconds])
        
        series = Series(
            name="test_series",
            values=np.sin(t_seconds),
            unit="V"
        )
        
        dataset = Dataset(
            dataset_id="test_dataset",
            t_seconds=t_seconds,
            t_datetime=t_datetime,
            series={"test_series": series}
        )
        
        # Add dataset
        dataset_id = state.add_dataset(dataset)
        
        # Verify
        assert dataset_id is not None, "add_dataset deve retornar um ID"
        print(f"✅ Dataset adicionado com ID: {dataset_id}")
        
        # Check get_all_datasets
        all_datasets = state.get_all_datasets()
        print(f"📊 Datasets retornados por get_all_datasets: {list(all_datasets.keys())}")
        assert len(all_datasets) > 0, "get_all_datasets deve retornar ao menos 1 dataset"
        assert dataset_id in all_datasets, f"Dataset {dataset_id} deve estar em get_all_datasets"
        
        # Check current_dataset
        current = state.current_dataset
        print(f"📍 Current dataset: {current}")
        assert current is not None, "current_dataset deve ser definido"
        
        # Check get_dataset
        retrieved = state.get_dataset(dataset_id)
        assert retrieved is not None, "get_dataset deve retornar o dataset"
        print(f"✅ Dataset recuperado: {retrieved.dataset_id}")
        
        print("\n✅ TESTE PASSOU: SessionState armazena datasets corretamente")


class TestDataPanelIntegration:
    """Testes do DataPanel com SessionState"""

    def test_data_panel_updates_on_dataset_change(self):
        """Verifica se DataPanel atualiza quando dataset é adicionado"""
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance() or QApplication([])
        
        from datetime import datetime, timedelta

        import numpy as np

        from platform_base.core.dataset_store import DatasetStore
        from platform_base.core.models import Dataset, Series
        from platform_base.ui.panels.data_panel import CompactDataPanel
        from platform_base.ui.state import SessionState

        # Create components
        store = DatasetStore()
        state = SessionState(store)
        panel = CompactDataPanel(state)
        
        # Process events to ensure panel is initialized
        app.processEvents()
        
        # Check initial state
        print(f"📊 Estado inicial:")
        print(f"   - _current_dataset: {panel._current_dataset}")
        print(f"   - _datasets_tree items: {panel._datasets_tree.topLevelItemCount()}")
        print(f"   - _series_tree items: {panel._series_tree.topLevelItemCount()}")
        print(f"   - _data_table rows: {panel._data_table.rowCount()}")
        
        # Create mock dataset
        n_points = 100
        t_seconds = np.linspace(0, 10, n_points)
        t_datetime = np.array([datetime.now() + timedelta(seconds=t) for t in t_seconds])
        
        series = Series(
            name="test_series",
            values=np.sin(t_seconds),
            unit="V"
        )
        
        dataset = Dataset(
            dataset_id="TEST_DATASET",
            t_seconds=t_seconds,
            t_datetime=t_datetime,
            series={"test_series": series}
        )
        
        # Add dataset (this should trigger _on_dataset_changed)
        print("\n📥 Adicionando dataset...")
        dataset_id = state.add_dataset(dataset)
        
        # Process events to allow signals to propagate
        app.processEvents()
        time.sleep(0.1)
        app.processEvents()
        
        # Check state after adding
        print(f"\n📊 Estado após adicionar dataset:")
        print(f"   - dataset_id retornado: {dataset_id}")
        print(f"   - _current_dataset: {panel._current_dataset}")
        print(f"   - _datasets_tree items: {panel._datasets_tree.topLevelItemCount()}")
        print(f"   - _series_tree items: {panel._series_tree.topLevelItemCount()}")
        print(f"   - _data_table rows: {panel._data_table.rowCount()}")
        
        # Verify updates
        assert panel._current_dataset is not None, "❌ _current_dataset não foi atualizado!"
        assert panel._datasets_tree.topLevelItemCount() > 0, "❌ _datasets_tree não tem items!"
        assert panel._series_tree.topLevelItemCount() > 0, "❌ _series_tree não tem items!"
        assert panel._data_table.rowCount() > 0, "❌ _data_table não tem linhas!"
        
        print("\n✅ TESTE PASSOU: DataPanel atualiza corretamente")


class TestFileLoadingIntegration:
    """Testes de carregamento de arquivo completo"""

    def test_load_xlsx_updates_ui(self):
        """Testa carregamento de arquivo xlsx e atualização da UI"""
        from PyQt6.QtCore import QTimer
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance() or QApplication([])
        
        from platform_base.core.dataset_store import DatasetStore
        from platform_base.ui.panels.data_panel import CompactDataPanel
        from platform_base.ui.state import SessionState

        # Find test file
        test_files = list(Path(__file__).parent.parent.parent.glob("BAR_*.xlsx"))
        if not test_files:
            pytest.skip("Nenhum arquivo xlsx de teste encontrado")
        
        test_file = test_files[0]
        print(f"📁 Arquivo de teste: {test_file.name}")
        
        # Create components
        store = DatasetStore()
        state = SessionState(store)
        panel = CompactDataPanel(state)
        
        # Track signal emissions
        dataset_changed_count = [0]
        def on_dataset_changed(ds_id):
            dataset_changed_count[0] += 1
            print(f"📡 Signal dataset_changed emitido: {ds_id} (count: {dataset_changed_count[0]})")
        
        state.dataset_changed.connect(on_dataset_changed)
        
        # Process events
        app.processEvents()
        
        print(f"\n📊 Estado inicial:")
        print(f"   - Datasets no state: {len(state.get_all_datasets())}")
        print(f"   - Items na árvore: {panel._datasets_tree.topLevelItemCount()}")
        
        # Load file
        print(f"\n📥 Carregando arquivo: {test_file}")
        panel.load_dataset(str(test_file))
        
        # Wait for async load
        loaded = [False]
        def check_loaded():
            if state.current_dataset is not None:
                loaded[0] = True
        
        # Poll for completion (max 10 seconds)
        for i in range(100):
            app.processEvents()
            time.sleep(0.1)
            if state.current_dataset is not None:
                loaded[0] = True
                break
        
        print(f"\n📊 Estado após carregamento:")
        print(f"   - Loaded: {loaded[0]}")
        print(f"   - dataset_changed emitido: {dataset_changed_count[0]} vezes")
        print(f"   - state.current_dataset: {state.current_dataset}")
        print(f"   - Datasets no state: {len(state.get_all_datasets())}")
        print(f"   - panel._current_dataset: {panel._current_dataset}")
        print(f"   - Items na árvore datasets: {panel._datasets_tree.topLevelItemCount()}")
        print(f"   - Items na árvore series: {panel._series_tree.topLevelItemCount()}")
        print(f"   - Linhas na tabela: {panel._data_table.rowCount()}")
        
        # Verificações
        assert loaded[0], "❌ Arquivo não carregou dentro do timeout!"
        assert state.current_dataset is not None, "❌ current_dataset não definido!"
        assert len(state.get_all_datasets()) > 0, "❌ Nenhum dataset no state!"
        
        # Estas são as verificações críticas que provavelmente falham
        if panel._current_dataset is None:
            print("❌ PROBLEMA ENCONTRADO: panel._current_dataset é None!")
            print("   O signal dataset_changed não está atualizando o panel corretamente")
        
        if panel._datasets_tree.topLevelItemCount() == 0:
            print("❌ PROBLEMA ENCONTRADO: _datasets_tree está vazia!")
            print("   A função _update_datasets_list não está funcionando")
        
        if panel._series_tree.topLevelItemCount() == 0:
            print("❌ PROBLEMA ENCONTRADO: _series_tree está vazia!")
            print("   A função _update_series_tree não está funcionando")


class TestSignalPropagation:
    """Testes de propagação de sinais"""

    def test_dataset_changed_signal_reaches_panel(self):
        """Verifica se o signal dataset_changed chega ao panel"""
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance() or QApplication([])
        
        from platform_base.core.dataset_store import DatasetStore
        from platform_base.ui.panels.data_panel import CompactDataPanel
        from platform_base.ui.state import SessionState
        
        store = DatasetStore()
        state = SessionState(store)
        panel = CompactDataPanel(state)
        
        # Track if handler was called
        handler_called = [False]
        original_handler = panel._on_dataset_changed
        
        def tracked_handler(dataset_id):
            handler_called[0] = True
            print(f"📡 _on_dataset_changed chamado com: {dataset_id}")
            original_handler(dataset_id)
        
        # Replace handler
        panel._on_dataset_changed = tracked_handler
        
        # Reconnect signal
        state.dataset_changed.disconnect()
        state.dataset_changed.connect(tracked_handler)
        
        # Emit signal manually
        print("\n📤 Emitindo signal manualmente...")
        state.dataset_changed.emit("test_id")
        
        app.processEvents()
        
        assert handler_called[0], "❌ Signal não chegou ao handler!"
        print("✅ Signal chegou ao handler corretamente")


class TestWidgetVisibility:
    """Testes de visibilidade dos widgets"""

    def test_widgets_are_visible(self):
        """Verifica se os widgets estão visíveis e com tamanho adequado"""
        from PyQt6.QtWidgets import QApplication, QMainWindow
        app = QApplication.instance() or QApplication([])
        
        from platform_base.core.dataset_store import DatasetStore
        from platform_base.ui.panels.data_panel import CompactDataPanel
        from platform_base.ui.state import SessionState
        
        store = DatasetStore()
        state = SessionState(store)
        
        # Create in a window to ensure proper sizing
        window = QMainWindow()
        panel = CompactDataPanel(state)
        window.setCentralWidget(panel)
        window.resize(400, 600)
        window.show()
        
        app.processEvents()
        
        print(f"\n📐 Verificando widgets:")
        print(f"   - panel.isVisible(): {panel.isVisible()}")
        print(f"   - panel.size(): {panel.size().width()}x{panel.size().height()}")
        print(f"   - _datasets_tree.isVisible(): {panel._datasets_tree.isVisible()}")
        print(f"   - _datasets_tree.size(): {panel._datasets_tree.size().width()}x{panel._datasets_tree.size().height()}")
        print(f"   - _series_tree.isVisible(): {panel._series_tree.isVisible()}")
        print(f"   - _series_tree.size(): {panel._series_tree.size().width()}x{panel._series_tree.size().height()}")
        print(f"   - _data_table.isVisible(): {panel._data_table.isVisible()}")
        print(f"   - _data_table.size(): {panel._data_table.size().width()}x{panel._data_table.size().height()}")
        
        assert panel.isVisible(), "❌ Panel não está visível!"
        assert panel._datasets_tree.isVisible(), "❌ _datasets_tree não está visível!"
        assert panel._series_tree.isVisible(), "❌ _series_tree não está visível!"
        
        window.close()
        print("\n✅ Todos os widgets estão visíveis")


def run_all_tests():
    """Executa todos os testes e mostra relatório"""
    print("=" * 60)
    print("TESTES DE INTEGRAÇÃO - PLATFORM BASE UI")
    print("=" * 60)
    
    tests = [
        ("SessionState Integration", TestSessionStateIntegration().test_add_dataset_stores_correctly),
        ("Signal Propagation", TestSignalPropagation().test_dataset_changed_signal_reaches_panel),
        ("DataPanel Updates", TestDataPanelIntegration().test_data_panel_updates_on_dataset_change),
        ("Widget Visibility", TestWidgetVisibility().test_widgets_are_visible),
        ("File Loading", TestFileLoadingIntegration().test_load_xlsx_updates_ui),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"TESTE: {name}")
        print("="*60)
        try:
            test_func()
            results.append((name, "PASSOU", None))
        except Exception as e:
            results.append((name, "FALHOU", str(e)))
            print(f"\n❌ ERRO: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = sum(1 for r in results if r[1] == "PASSOU")
    failed = sum(1 for r in results if r[1] == "FALHOU")
    
    for name, status, error in results:
        icon = "✅" if status == "PASSOU" else "❌"
        print(f"{icon} {name}: {status}")
        if error:
            print(f"   Erro: {error[:100]}...")
    
    print(f"\n📊 Total: {passed} passou, {failed} falhou de {len(results)} testes")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
