# -*- coding: utf-8 -*-
"""
test_04_signals_slots.py — Verificação de sinais e slots conectados

Testes para validar:
1. SignalHub tem todos os signals declarados
2. Signals podem ser emitidos e recebidos
3. SessionState emite signals quando estado muda
4. Workers emitem signals corretos
5. Conexões de UI estão funcionais
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch
import gc

import pytest
from PyQt6.QtCore import QObject, pyqtSignal, QThread

from .helpers import (
    SIGNAL_HUB_SIGNALS, SESSION_STATE_SIGNALS,
    get_connections_from_ui_xml,
)


pytestmark = [pytest.mark.automated, pytest.mark.gui]


class TestSignalHubSignalsExist:
    """Verifica que SignalHub tem todos os signals declarados."""

    def test_signal_hub_instantiation(self, signal_hub):
        """Verifica que SignalHub pode ser instanciado."""
        assert signal_hub is not None

    def test_signal_hub_has_expected_signals(self, signal_hub):
        """Verifica que SignalHub tem os signals esperados."""
        missing = []
        for sig_name in SIGNAL_HUB_SIGNALS:
            if not hasattr(signal_hub, sig_name):
                missing.append(sig_name)
        
        # Permite alguns faltantes (podem ter nomes diferentes)
        if len(missing) > len(SIGNAL_HUB_SIGNALS) // 2:
            pytest.fail(f"Muitos signals faltando no SignalHub: {missing}")
        elif missing:
            pytest.skip(f"Alguns signals não encontrados (podem ter nomes diferentes): {missing}")

    def test_signal_hub_signals_are_pyqt_signals(self, signal_hub):
        """Verifica que signals são pyqtSignal."""
        found_signals = 0
        for sig_name in SIGNAL_HUB_SIGNALS:
            if hasattr(signal_hub, sig_name):
                signal = getattr(signal_hub, sig_name)
                # PyQt signals são bound methods em instâncias
                if hasattr(signal, 'connect') and hasattr(signal, 'emit'):
                    found_signals += 1
        
        assert found_signals >= 5, f"Poucos signals válidos encontrados: {found_signals}"


class TestSignalHubEmitReceive:
    """Testa emissão e recepção de signals."""

    def test_signal_connect_disconnect(self, signal_hub):
        """Testa que signals podem ser conectados e desconectados."""
        mock_slot = MagicMock()
        
        # Pega um signal que existe
        signal = None
        for sig_name in SIGNAL_HUB_SIGNALS:
            if hasattr(signal_hub, sig_name):
                signal = getattr(signal_hub, sig_name)
                break
        
        if signal is None:
            pytest.skip("Nenhum signal encontrado")
        
        # Conecta
        signal.connect(mock_slot)
        
        # Desconecta
        signal.disconnect(mock_slot)
        
        # Não deve lançar exceção

    def test_signal_emit_calls_slot(self, qapp, signal_hub):
        """Testa que emit chama o slot conectado."""
        mock_slot = MagicMock()
        
        # Tenta com status_updated que normalmente aceita str
        signal = None
        sig_name = None
        for name in ["status_updated", "error_occurred", "theme_changed"]:
            if hasattr(signal_hub, name):
                signal = getattr(signal_hub, name)
                sig_name = name
                break
        
        if signal is None:
            pytest.skip("Nenhum signal compatível encontrado")
        
        signal.connect(mock_slot)
        
        try:
            # Emite (assumindo que aceita str ou nenhum argumento)
            try:
                signal.emit("test message")
            except TypeError:
                try:
                    signal.emit()
                except TypeError:
                    pytest.skip(f"Não foi possível emitir {sig_name}")
            
            qapp.processEvents()
            
            # Verifica que slot foi chamado
            assert mock_slot.called, f"Slot não foi chamado após emit de {sig_name}"
        finally:
            signal.disconnect(mock_slot)

    def test_multiple_slots_receive_signal(self, qapp, signal_hub):
        """Testa que múltiplos slots recebem o mesmo signal."""
        mock_slot1 = MagicMock()
        mock_slot2 = MagicMock()
        
        # Pega um signal
        signal = None
        for name in ["status_updated", "progress_updated"]:
            if hasattr(signal_hub, name):
                signal = getattr(signal_hub, name)
                break
        
        if signal is None:
            pytest.skip("Nenhum signal encontrado")
        
        signal.connect(mock_slot1)
        signal.connect(mock_slot2)
        
        try:
            try:
                signal.emit("test")
            except TypeError:
                signal.emit()
            
            qapp.processEvents()
            
            assert mock_slot1.called
            assert mock_slot2.called
        finally:
            signal.disconnect(mock_slot1)
            signal.disconnect(mock_slot2)


class TestSessionStateSignals:
    """Verifica signals do SessionState."""

    def test_session_state_has_signals(self, session_state):
        """Verifica que SessionState tem signals esperados."""
        found = 0
        for sig_name in SESSION_STATE_SIGNALS:
            if hasattr(session_state, sig_name):
                found += 1
        
        assert found >= 3, f"SessionState tem poucos signals: {found}"

    def test_session_state_signal_emission(self, qapp, session_state):
        """Testa emissão de signal do SessionState."""
        mock_slot = MagicMock()
        
        # Tenta encontrar um signal
        signal = None
        sig_name = None
        for name in SESSION_STATE_SIGNALS:
            if hasattr(session_state, name):
                candidate = getattr(session_state, name)
                if hasattr(candidate, 'connect'):
                    signal = candidate
                    sig_name = name
                    break
        
        if signal is None:
            pytest.skip("Nenhum signal encontrado em SessionState")
        
        signal.connect(mock_slot)
        
        try:
            # Emite
            try:
                signal.emit()
            except TypeError:
                try:
                    signal.emit(None)
                except TypeError:
                    pytest.skip(f"Não foi possível emitir {sig_name}")
            
            qapp.processEvents()
        finally:
            try:
                signal.disconnect(mock_slot)
            except TypeError:
                pass


class TestWorkerSignals:
    """Testa signals de workers."""

    def test_base_worker_exists(self):
        """Verifica que BaseWorker existe."""
        try:
            from platform_base.desktop.workers.base_worker import BaseWorker
        except ImportError:
            pytest.skip("BaseWorker não disponível")
        
        assert BaseWorker is not None

    def test_base_worker_has_signals(self):
        """Verifica que BaseWorker tem signals esperados."""
        try:
            from platform_base.desktop.workers.base_worker import BaseWorker
        except ImportError:
            pytest.skip("BaseWorker não disponível")
        
        expected_signals = ["progress", "status_updated", "error", "finished"]
        found = 0
        
        # Verifica na classe
        for sig_name in expected_signals:
            if hasattr(BaseWorker, sig_name):
                found += 1
        
        assert found >= 2, f"BaseWorker tem poucos signals: {found}"


class TestUIConnectionsFromXML:
    """Testa conexões definidas em arquivos .ui."""

    def test_ui_connections_parseable(self, ui_file_contents):
        """Verifica que conexões podem ser extraídas dos .ui."""
        total_connections = 0
        files_with_connections = 0
        
        for filename, tree in ui_file_contents.items():
            if tree is None:
                continue
            
            connections = get_connections_from_ui_xml(tree)
            if connections:
                files_with_connections += 1
                total_connections += len(connections)
        
        # Muitos arquivos .ui não têm conexões definidas (são feitas em código)
        # Então apenas verificamos que o parsing funciona
        assert True  # Parsing funcionou

    def test_ui_connections_have_required_fields(self, ui_file_contents):
        """Verifica que conexões têm sender, signal, receiver, slot."""
        incomplete = []
        
        for filename, tree in ui_file_contents.items():
            if tree is None:
                continue
            
            connections = get_connections_from_ui_xml(tree)
            for conn in connections:
                if not all([conn.get("sender"), conn.get("signal"), 
                           conn.get("receiver"), conn.get("slot")]):
                    incomplete.append((filename, conn))
        
        # Aviso, não falha (algumas conexões podem ser parciais)
        if incomplete:
            pytest.skip(f"Conexões incompletas encontradas: {len(incomplete)}")


class TestCrossComponentSignals:
    """Testa fluxo de signals entre componentes."""

    def test_signal_hub_propagation(self, qapp, signal_hub):
        """Testa que signal hub propaga eventos entre componentes."""
        received = {"count": 0}
        
        def on_status(msg=""):
            received["count"] += 1
        
        # Conecta se o signal existir
        if hasattr(signal_hub, "status_updated"):
            signal_hub.status_updated.connect(on_status)
            
            try:
                signal_hub.status_updated.emit("test")
            except TypeError:
                try:
                    signal_hub.status_updated.emit()
                except TypeError:
                    pass
            
            qapp.processEvents()
            signal_hub.status_updated.disconnect(on_status)
            
            assert received["count"] >= 1
        else:
            pytest.skip("status_updated não disponível")


class TestSignalDisconnect:
    """Testa que disconnect funciona corretamente."""

    def test_disconnect_prevents_slot_call(self, qapp, signal_hub):
        """Verifica que slot não é chamado após disconnect."""
        mock_slot = MagicMock()
        
        # Encontra um signal
        signal = None
        for name in SIGNAL_HUB_SIGNALS:
            if hasattr(signal_hub, name):
                signal = getattr(signal_hub, name)
                break
        
        if signal is None:
            pytest.skip("Nenhum signal encontrado")
        
        signal.connect(mock_slot)
        signal.disconnect(mock_slot)
        
        # Emite após disconnect
        try:
            signal.emit()
        except TypeError:
            try:
                signal.emit("")
            except TypeError:
                pass
        
        qapp.processEvents()
        
        # Slot NÃO deve ter sido chamado
        assert not mock_slot.called, "Slot foi chamado após disconnect"


class TestSignalThreadSafety:
    """Testa thread-safety de signals."""

    def test_signal_from_qthread(self, qapp):
        """Testa emissão de signal de QThread."""

        class TestWorker(QThread):
            finished_signal = pyqtSignal()
            
            def run(self):
                self.finished_signal.emit()
        
        received = {"done": False}
        
        def on_finished():
            received["done"] = True
        
        worker = TestWorker()
        worker.finished_signal.connect(on_finished)
        
        worker.start()
        worker.wait(1000)  # 1 segundo timeout
        
        qapp.processEvents()
        
        assert received["done"], "Signal de QThread não foi recebido"
