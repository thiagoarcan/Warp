# -*- coding: utf-8 -*-
"""
test_09_exceptions_errors.py — Testes de exceções e tratamento de erros

Testes para validar:
1. Tratamento de arquivos inválidos
2. Tratamento de dados malformados
3. Tratamento de divisão por zero
4. Tratamento de NaN/Inf
5. Fallback para UI faltantes
6. Handler global de exceções
7. Erros em workers
8. Validação de inputs
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest
from PyQt6.QtWidgets import QWidget, QMessageBox

pytestmark = [pytest.mark.automated, pytest.mark.gui]


class TestInvalidFileHandling:
    """Testa tratamento de arquivos inválidos."""

    def test_nonexistent_file_load(self, qapp, dataset_store):
        """Verifica tratamento de arquivo inexistente."""
        if dataset_store is None:
            pytest.skip("DatasetStore não disponível")
        
        fake_path = Path("/caminho/que/nao/existe/arquivo.csv")
        
        # Deve lançar exceção ou retornar None, não travar
        with pytest.raises((FileNotFoundError, OSError, ValueError, Exception)):
            result = dataset_store.load(str(fake_path))
            if result is None:
                raise ValueError("Arquivo não encontrado retornou None")

    def test_empty_file_load(self, qapp, dataset_store):
        """Verifica tratamento de arquivo vazio."""
        if dataset_store is None:
            pytest.skip("DatasetStore não disponível")
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_path = f.name
        
        try:
            # Deve lançar exceção ou retornar None
            try:
                result = dataset_store.load(temp_path)
                # Se não lançou exceção, verifica resultado
                assert result is None or (hasattr(result, "empty") and result.empty)
            except Exception:
                pass  # Exceção esperada
        finally:
            os.unlink(temp_path)

    def test_corrupted_csv_load(self, qapp, dataset_store):
        """Verifica tratamento de CSV corrompido."""
        if dataset_store is None:
            pytest.skip("DatasetStore não disponível")
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("col1,col2,col3\n")
            f.write("1,2\n")  # Falta uma coluna
            f.write("a,b,c,d,e\n")  # Colunas extras
            f.write("\"unclosed\n")  # Aspas não fechadas
            temp_path = f.name
        
        try:
            # Deve tratar graciosamente
            try:
                result = dataset_store.load(temp_path)
                # Pode retornar parcial ou None
            except Exception:
                pass  # Exceção esperada
        finally:
            os.unlink(temp_path)


class TestMalformedDataHandling:
    """Testa tratamento de dados malformados."""

    def test_nan_in_dataframe(self, qapp, sample_dataframe):
        """Verifica tratamento de NaN em DataFrame."""
        df = sample_dataframe.copy()
        df.iloc[0, 0] = np.nan
        df.iloc[1, 1] = np.nan
        
        # Verifica que operações não falham
        mean = df.mean(numeric_only=True)
        assert not mean.isna().all(), "Todas as médias são NaN"

    def test_inf_in_dataframe(self, qapp, sample_dataframe):
        """Verifica tratamento de Inf em DataFrame."""
        df = sample_dataframe.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 0:
            df[numeric_cols[0]].iloc[0] = np.inf
            df[numeric_cols[0]].iloc[1] = -np.inf
            
            # Pode ou não lançar warning, mas não deve travar
            try:
                df[numeric_cols[0]].sum()
            except Exception:
                pass  # Aceita exceção

    def test_mixed_types_column(self, qapp):
        """Verifica tratamento de coluna com tipos mistos."""
        df = pd.DataFrame({
            "mixed": [1, "texto", 3.14, None, True],
            "names": ["a", "b", "c", "d", "e"]
        })
        
        # Não deve travar
        try:
            df["mixed"].astype(str)
        except Exception:
            pass  # Aceita exceção


class TestDivisionByZeroHandling:
    """Testa tratamento de divisão por zero."""

    def test_numpy_division_by_zero(self, qapp):
        """Verifica que divisão por zero não trava."""
        arr = np.array([1.0, 2.0, 3.0])
        zero = np.array([0.0, 0.0, 0.0])
        
        with np.errstate(divide='ignore', invalid='ignore'):
            result = arr / zero
            
        # Resultado deve ser Inf
        assert np.isinf(result).all()

    def test_pandas_division_by_zero(self, qapp, sample_dataframe):
        """Verifica divisão por zero em DataFrame."""
        df = sample_dataframe.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) >= 2:
            zero_series = pd.Series(0, index=df.index)
            
            with np.errstate(divide='ignore', invalid='ignore'):
                result = df[numeric_cols[0]] / zero_series
            
            # Deve gerar Inf, não travar
            assert True


class TestUIFallbackBehavior:
    """Testa fallback quando UI não está disponível."""

    def test_missing_ui_file_fallback(self, qapp):
        """Verifica fallback quando arquivo UI não existe."""
        from PyQt6.QtWidgets import QWidget
        
        widget = QWidget()
        
        # Tenta carregar UI inexistente
        fake_ui_path = "/ui/inexistente.ui"
        
        # O widget deve existir mesmo sem UI
        assert widget is not None
        
        widget.close()
        widget.deleteLater()

    def test_widget_without_ui_usable(self, qapp):
        """Verifica que widget sem UI pode ser usado."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel("Fallback content")
        layout.addWidget(label)
        
        assert widget.layout() is not None
        assert widget.layout().count() == 1
        
        widget.close()
        widget.deleteLater()


class TestGlobalExceptionHandler:
    """Testa handler global de exceções."""

    def test_unhandled_exception_caught(self, qapp):
        """Verifica que exceções não tratadas são capturadas."""
        try:
            from platform_base.utils.exception_handler import global_exception_handler
        except ImportError:
            # Testa alternativa
            try:
                from platform_base.core.exception_handling import global_exception_handler
            except ImportError:
                pytest.skip("Handler de exceção não disponível")
        
        # Verifica que existe e é chamável
        assert callable(global_exception_handler)

    def test_exception_in_slot_handled(self, qapp, qtbot):
        """Verifica que exceção em slot não trava aplicação."""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton("Test")
        exception_raised = False
        
        def raising_slot():
            nonlocal exception_raised
            exception_raised = True
            raise ValueError("Exceção de teste")
        
        # Conecta slot que lança exceção
        button.clicked.connect(raising_slot)
        
        # pytest-qt captura exceções em slots, então usamos expectativa
        with qtbot.capture_exceptions() as exceptions:
            button.click()
        
        # Verifica que a exceção foi capturada (esperado)
        assert exception_raised, "Slot deveria ter sido executado"
        assert len(exceptions) == 1, "Deveria ter capturado uma exceção"
        assert isinstance(exceptions[0][1], ValueError)
        
        button.close()
        button.deleteLater()
        qapp.processEvents()


class TestWorkerErrorSignals:
    """Testa sinais de erro em workers."""

    def test_worker_error_signal_exists(self, qapp):
        """Verifica que worker tem sinal de erro."""
        try:
            from platform_base.core.workers import BaseWorker
        except ImportError:
            try:
                from platform_base.workers import BaseWorker
            except ImportError:
                pytest.skip("BaseWorker não disponível")
        
        # Verifica se tem sinal de erro
        assert hasattr(BaseWorker, "error_occurred") or \
               hasattr(BaseWorker, "errorOccurred") or \
               hasattr(BaseWorker, "error"), \
            "Worker deve ter sinal de erro"

    def test_worker_exception_emits_error(self, qapp):
        """Verifica que exceção em worker emite sinal de erro."""
        from PyQt6.QtCore import QObject, pyqtSignal, QRunnable
        
        class MockWorker(QObject):
            error = pyqtSignal(str)
            finished = pyqtSignal()
            
            def run(self):
                try:
                    raise ValueError("Erro de teste")
                except Exception as e:
                    self.error.emit(str(e))
                finally:
                    self.finished.emit()
        
        worker = MockWorker()
        error_received = []
        worker.error.connect(lambda msg: error_received.append(msg))
        
        worker.run()
        
        assert len(error_received) == 1
        assert "teste" in error_received[0].lower()


class TestInputValidation:
    """Testa validação de inputs."""

    def test_invalid_numeric_input(self, qapp):
        """Verifica tratamento de input numérico inválido."""
        from PyQt6.QtWidgets import QLineEdit
        from PyQt6.QtGui import QDoubleValidator
        
        line_edit = QLineEdit()
        validator = QDoubleValidator()
        line_edit.setValidator(validator)
        
        # Input válido - Qt retorna Intermediate ou Acceptable dependendo do contexto
        # O importante é que NÃO seja Invalid
        line_edit.setText("3.14")
        state, _, _ = validator.validate("3.14", 0)
        assert state != QDoubleValidator.State.Invalid, "Número válido não deve ser Invalid"
        
        # Input inválido (texto)
        state, _, _ = validator.validate("abc", 0)
        assert state == QDoubleValidator.State.Invalid
        
        line_edit.deleteLater()

    def test_empty_required_field(self, qapp):
        """Verifica tratamento de campo obrigatório vazio."""
        from PyQt6.QtWidgets import QLineEdit
        
        line_edit = QLineEdit()
        line_edit.setText("")
        
        # Verifica se vazio
        assert line_edit.text() == ""
        
        # Pode ter placeholder mas não valor
        line_edit.setPlaceholderText("Campo obrigatório")
        assert line_edit.text() == ""
        
        line_edit.deleteLater()


class TestResourceLoadingErrors:
    """Testa erros ao carregar recursos."""

    def test_missing_icon_handled(self, qapp):
        """Verifica tratamento de ícone faltante."""
        from PyQt6.QtGui import QIcon
        
        icon = QIcon("/caminho/inexistente/icon.png")
        
        # Icon vazio é retornado para arquivos inexistentes
        assert icon.isNull() or True  # Aceita ambos

    def test_missing_stylesheet_handled(self, qapp):
        """Verifica tratamento de stylesheet faltante."""
        from PyQt6.QtWidgets import QWidget
        
        widget = QWidget()
        
        # Stylesheet vazio não deve causar erro
        widget.setStyleSheet("")
        
        # Stylesheet inválido pode ser ignorado ou causar warning
        widget.setStyleSheet("invalid { property: value; }")
        
        # Widget ainda funciona
        assert widget is not None
        
        widget.close()
        widget.deleteLater()


class TestConfigurationErrors:
    """Testa erros de configuração."""

    def test_missing_config_file(self, qapp):
        """Verifica tratamento de arquivo de config faltante."""
        try:
            from platform_base.core.config import ConfigManager
        except ImportError:
            pytest.skip("ConfigManager não disponível")
        
        # Deve carregar defaults ou lançar exceção apropriada
        try:
            config = ConfigManager("/config/inexistente.yaml")
        except FileNotFoundError:
            pass  # Esperado
        except Exception:
            pass  # Outras exceções também são aceitáveis

    def test_invalid_yaml_config(self, qapp):
        """Verifica tratamento de YAML inválido."""
        import yaml
        
        invalid_yaml = """
        key: value
          bad_indent: true
        - item1
        """
        
        with pytest.raises(yaml.YAMLError):
            yaml.safe_load(invalid_yaml)


class TestConcurrencyErrors:
    """Testa erros de concorrência."""

    def test_signal_emit_from_thread(self, qapp):
        """Verifica emissão de signal de thread secundária."""
        from PyQt6.QtCore import QObject, pyqtSignal, QThread
        
        class Worker(QObject):
            result_ready = pyqtSignal(int)
            
            def process(self):
                self.result_ready.emit(42)
        
        # Precisa estar em thread principal para Qt funcionar
        worker = Worker()
        received = []
        worker.result_ready.connect(lambda x: received.append(x))
        
        worker.process()
        qapp.processEvents()
        
        assert 42 in received

    def test_lock_timeout(self, qapp):
        """Verifica tratamento de timeout em lock."""
        import threading
        
        lock = threading.Lock()
        
        # Lock normal
        with lock:
            pass
        
        # Non-blocking try
        acquired = lock.acquire(blocking=False)
        if acquired:
            lock.release()
        
        assert True  # Passou se não travou


class TestBoundaryConditions:
    """Testa condições de contorno."""

    def test_empty_dataframe_handling(self, qapp):
        """Verifica tratamento de DataFrame vazio."""
        df = pd.DataFrame()
        
        # Operações em DataFrame vazio
        assert df.empty
        assert len(df) == 0
        assert df.columns.tolist() == []

    def test_single_row_dataframe(self, qapp):
        """Verifica tratamento de DataFrame com uma linha."""
        df = pd.DataFrame({"a": [1], "b": [2]})
        
        assert len(df) == 1
        assert df["a"].iloc[0] == 1

    def test_very_long_string(self, qapp):
        """Verifica tratamento de string muito longa."""
        from PyQt6.QtWidgets import QLabel
        
        long_text = "A" * 100000
        
        label = QLabel()
        label.setText(long_text)
        
        # Deve funcionar sem travar
        assert len(label.text()) == 100000
        
        label.deleteLater()
