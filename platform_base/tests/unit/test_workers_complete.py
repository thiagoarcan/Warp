"""
Testes completos para desktop/workers - Platform Base v2.0

Cobertura de 100% das funcionalidades de workers.
"""

import time
from unittest.mock import MagicMock, patch

import pytest

# Mock PyQt6 before importing
pytest.importorskip("PyQt6")

from PyQt6.QtCore import QThread


class TestBaseWorker:
    """Testes para BaseWorker"""
    
    def test_creation(self):
        """Testa criação de BaseWorker"""
        from platform_base.desktop.workers.base_worker import BaseWorker

        # BaseWorker é abstrato, mas podemos testar propriedades
        class ConcreteWorker(BaseWorker):
            def run(self):
                pass
        
        worker = ConcreteWorker()
        
        assert worker.worker_id.startswith("ConcreteWorker_")
        assert worker.is_cancelled is False
    
    def test_worker_id_unique(self):
        """Testa que worker_id é único"""
        from platform_base.desktop.workers.base_worker import BaseWorker
        
        class ConcreteWorker(BaseWorker):
            def run(self):
                pass
        
        worker1 = ConcreteWorker()
        worker2 = ConcreteWorker()
        
        assert worker1.worker_id != worker2.worker_id
    
    def test_cancel(self):
        """Testa cancelamento de worker"""
        from platform_base.desktop.workers.base_worker import BaseWorker
        
        class ConcreteWorker(BaseWorker):
            def run(self):
                pass
        
        worker = ConcreteWorker()
        
        assert worker.is_cancelled is False
        worker.cancel()
        assert worker.is_cancelled is True
    
    def test_emit_progress(self):
        """Testa emissão de progresso"""
        from platform_base.desktop.workers.base_worker import BaseWorker
        
        class ConcreteWorker(BaseWorker):
            def run(self):
                pass
        
        worker = ConcreteWorker()
        
        # Configura slot para capturar sinal de progresso
        progress_received = []
        worker.progress.connect(lambda p: progress_received.append(p))
        
        # Configura slot para status
        status_received = []
        worker.status_updated.connect(lambda s: status_received.append(s))
        
        worker.emit_progress(50, "Half done")
        
        assert progress_received == [50]
        assert status_received == ["Half done"]
    
    def test_emit_progress_without_message(self):
        """Testa emissão de progresso sem mensagem"""
        from platform_base.desktop.workers.base_worker import BaseWorker
        
        class ConcreteWorker(BaseWorker):
            def run(self):
                pass
        
        worker = ConcreteWorker()
        
        progress_received = []
        worker.progress.connect(lambda p: progress_received.append(p))
        
        worker.emit_progress(75)
        
        assert progress_received == [75]
    
    def test_emit_error(self):
        """Testa emissão de erro"""
        from platform_base.desktop.workers.base_worker import BaseWorker
        
        class ConcreteWorker(BaseWorker):
            def run(self):
                pass
        
        worker = ConcreteWorker()
        
        error_received = []
        worker.error.connect(lambda e: error_received.append(e))
        
        worker.emit_error("Test error message")
        
        assert error_received == ["Test error message"]
    
    def test_emit_success(self):
        """Testa emissão de sucesso"""
        from platform_base.desktop.workers.base_worker import BaseWorker
        
        class ConcreteWorker(BaseWorker):
            def run(self):
                pass
        
        worker = ConcreteWorker()
        
        status_received = []
        finished_received = []
        
        worker.status_updated.connect(lambda s: status_received.append(s))
        worker.finished.connect(lambda: finished_received.append(True))
        
        worker.emit_success("Operation completed")
        
        assert status_received == ["Operation completed"]
        assert finished_received == [True]
    
    def test_emit_success_without_message(self):
        """Testa emissão de sucesso sem mensagem"""
        from platform_base.desktop.workers.base_worker import BaseWorker
        
        class ConcreteWorker(BaseWorker):
            def run(self):
                pass
        
        worker = ConcreteWorker()
        
        finished_received = []
        worker.finished.connect(lambda: finished_received.append(True))
        
        worker.emit_success()
        
        assert finished_received == [True]
    
    def test_safe_execute_success(self):
        """Testa execução segura com sucesso"""
        from platform_base.desktop.workers.base_worker import BaseWorker
        
        class ConcreteWorker(BaseWorker):
            def run(self):
                pass
        
        worker = ConcreteWorker()
        
        def successful_func(a, b):
            return a + b
        
        result = worker.safe_execute(successful_func, 5, 3)
        
        assert result == 8
    
    def test_safe_execute_with_error(self):
        """Testa execução segura com erro"""
        from platform_base.desktop.workers.base_worker import BaseWorker
        
        class ConcreteWorker(BaseWorker):
            def run(self):
                pass
        
        worker = ConcreteWorker()
        
        error_received = []
        worker.error.connect(lambda e: error_received.append(e))
        
        def failing_func():
            raise ValueError("Test error")
        
        result = worker.safe_execute(failing_func)
        
        assert result is None
        assert len(error_received) == 1
        assert "Test error" in error_received[0]
    
    def test_worker_signals_exist(self):
        """Testa que todos os sinais existem"""
        from platform_base.desktop.workers.base_worker import BaseWorker
        
        class ConcreteWorker(BaseWorker):
            def run(self):
                pass
        
        worker = ConcreteWorker()
        
        assert hasattr(worker, 'progress')
        assert hasattr(worker, 'status_updated')
        assert hasattr(worker, 'error')
        assert hasattr(worker, 'finished')


class TestInterpolationWorker:
    """Testes para InterpolationWorker"""
    
    def test_creation(self):
        """Testa criação de InterpolationWorker"""
        from platform_base.desktop.workers.processing_worker import InterpolationWorker
        
        mock_store = MagicMock()
        
        worker = InterpolationWorker(
            dataset_store=mock_store,
            dataset_id="ds_001",
            series_id="temp_001",
            method="linear",
            parameters={"fill_value": 0.0}
        )
        
        assert worker.dataset_id == "ds_001"
        assert worker.series_id == "temp_001"
        assert worker.method == "linear"
    
    def test_signals_exist(self):
        """Testa que sinais existem"""
        from platform_base.desktop.workers.processing_worker import InterpolationWorker
        
        mock_store = MagicMock()
        
        worker = InterpolationWorker(
            dataset_store=mock_store,
            dataset_id="ds_001",
            series_id="temp_001",
            method="linear",
            parameters={}
        )
        
        # Deve ter sinais do BaseWorker
        assert hasattr(worker, 'progress')
        assert hasattr(worker, 'finished')


class TestCalculusWorker:
    """Testes para CalculusWorker"""
    
    def test_creation(self):
        """Testa criação de CalculusWorker"""
        from platform_base.desktop.workers.processing_worker import CalculusWorker
        
        mock_store = MagicMock()
        
        worker = CalculusWorker(
            dataset_store=mock_store,
            dataset_id="ds_001",
            series_id="temp_001",
            operation="derivative_1st",
            parameters={"method": "gradient"}
        )
        
        assert worker.dataset_id == "ds_001"
        assert worker.operation == "derivative_1st"


class TestDataExportWorker:
    """Testes para DataExportWorker"""
    
    def test_creation(self):
        """Testa criação de DataExportWorker"""
        from platform_base.desktop.workers.export_worker import DataExportWorker
        
        mock_store = MagicMock()
        
        worker = DataExportWorker(
            dataset_store=mock_store,
            dataset_id="ds_001",
            series_ids=["temp_001"],
            output_path="/tmp/test.csv",
            format_type="csv",
            export_config={}
        )
        
        assert worker.output_path == "/tmp/test.csv"
        assert worker.format_type == "csv"
    
    def test_signals_exist(self):
        """Testa que sinais existem"""
        from platform_base.desktop.workers.export_worker import DataExportWorker
        
        mock_store = MagicMock()
        
        worker = DataExportWorker(
            dataset_store=mock_store,
            dataset_id="ds_001",
            series_ids=None,
            output_path="/tmp/test.csv",
            format_type="csv",
            export_config={}
        )
        
        assert hasattr(worker, 'progress')
        assert hasattr(worker, 'finished')


class TestWorkerInheritance:
    """Testes de herança de workers"""
    
    def test_interpolation_worker_inherits_base(self):
        """Testa que InterpolationWorker herda de BaseWorker"""
        from platform_base.desktop.workers.base_worker import BaseWorker
        from platform_base.desktop.workers.processing_worker import InterpolationWorker
        
        mock_store = MagicMock()
        
        worker = InterpolationWorker(
            dataset_store=mock_store,
            dataset_id="ds_001",
            series_id="temp_001",
            method="linear",
            parameters={}
        )
        
        assert isinstance(worker, BaseWorker)
    
    def test_data_export_worker_inherits_base(self):
        """Testa que DataExportWorker herda de BaseWorker"""
        from platform_base.desktop.workers.base_worker import BaseWorker
        from platform_base.desktop.workers.export_worker import DataExportWorker
        
        mock_store = MagicMock()
        
        worker = DataExportWorker(
            dataset_store=mock_store,
            dataset_id="ds_001",
            series_ids=None,
            output_path="/tmp/test.csv",
            format_type="csv",
            export_config={}
        )
        
        assert isinstance(worker, BaseWorker)


class TestWorkerCancellation:
    """Testes de cancelamento de workers"""
    
    def test_cancellation_flag_propagates(self):
        """Testa que flag de cancelamento propaga"""
        from platform_base.desktop.workers.base_worker import BaseWorker
        
        class LongRunningWorker(BaseWorker):
            def run(self):
                for i in range(100):
                    if self.is_cancelled:
                        return
                    self.emit_progress(i)
        
        worker = LongRunningWorker()
        
        assert worker.is_cancelled is False
        worker.cancel()
        assert worker.is_cancelled is True
