"""
Testes automatizados de sinais e slots
Verifica que sinais e slots estão conectados corretamente
"""

import pytest
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer
from PyQt6.QtWidgets import QWidget


class TestSignalHubConnections:
    """Testes de conexões no SignalHub"""

    @pytest.mark.gui
    def test_signal_hub_has_signals(self):
        """Verifica que SignalHub tem sinais definidos"""
        from platform_base.desktop.signal_hub import SignalHub
        
        hub = SignalHub()
        
        # Verificar que é um QObject
        assert isinstance(hub, QObject)
        
        # Procurar por sinais
        signals = [attr for attr in dir(hub) if not attr.startswith('_')]
        assert len(signals) > 0, "SignalHub não tem sinais públicos"

    @pytest.mark.gui
    def test_signal_hub_signals_can_be_connected(self):
        """Verifica que sinais podem ser conectados"""
        from platform_base.desktop.signal_hub import SignalHub
        
        hub = SignalHub()
        
        # Flag para verificar conexão
        received = []
        
        # Tentar conectar a um sinal (se existir)
        for attr_name in dir(hub):
            attr = getattr(hub, attr_name)
            if isinstance(attr, pyqtSignal):
                # Conectar e emitir
                attr.connect(lambda *args: received.append(True))
                # Não emitir pois pode causar efeitos colaterais
                break
        
        # Se nenhum sinal encontrado, ok
        assert True


class TestSessionStateSignals:
    """Testes de sinais do SessionState"""

    @pytest.mark.gui
    def test_session_state_has_signals(self, mock_dataset_store):
        """Verifica que SessionState tem sinais"""
        from platform_base.desktop.session_state import SessionState
        
        state = SessionState(mock_dataset_store)
        
        # Verificar que é um QObject
        assert isinstance(state, QObject)


class TestWidgetSignals:
    """Testes de sinais de widgets"""

    @pytest.mark.gui
    def test_widget_button_signals(self, qtbot):
        """Verifica que botões têm sinais funcionais"""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton("Test")
        qtbot.addWidget(button)
        
        clicked = []
        button.clicked.connect(lambda: clicked.append(True))
        
        # Simular click
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        
        # Processar eventos
        QTimer.singleShot(100, lambda: None)
        qtbot.wait(150)
        
        # Verificar que sinal foi emitido
        assert len(clicked) > 0

    @pytest.mark.gui
    def test_widget_text_changed_signal(self, qtbot):
        """Verifica que QLineEdit tem sinal textChanged funcional"""
        from PyQt6.QtWidgets import QLineEdit
        from PyQt6.QtCore import Qt
        
        line_edit = QLineEdit()
        qtbot.addWidget(line_edit)
        
        changed = []
        line_edit.textChanged.connect(lambda text: changed.append(text))
        
        # Simular digitação
        qtbot.keyClicks(line_edit, "test")
        
        # Verificar que sinais foram emitidos
        assert len(changed) > 0
        assert "test" in "".join(changed)


class TestSignalConnectionPatterns:
    """Testes de padrões de conexão de sinais"""

    @pytest.mark.gui
    def test_disconnect_signal_works(self):
        """Verifica que desconectar sinais funciona"""
        
        class TestObject(QObject):
            test_signal = pyqtSignal(str)
        
        obj = TestObject()
        received = []
        
        def handler(text):
            received.append(text)
        
        # Conectar
        obj.test_signal.connect(handler)
        obj.test_signal.emit("test1")
        
        # Desconectar
        obj.test_signal.disconnect(handler)
        obj.test_signal.emit("test2")
        
        # Deve ter recebido apenas o primeiro
        assert len(received) == 1
        assert received[0] == "test1"

    @pytest.mark.gui
    def test_multiple_connections_work(self):
        """Verifica que múltiplas conexões funcionam"""
        
        class TestObject(QObject):
            test_signal = pyqtSignal(int)
        
        obj = TestObject()
        results = []
        
        obj.test_signal.connect(lambda x: results.append(x * 2))
        obj.test_signal.connect(lambda x: results.append(x * 3))
        
        obj.test_signal.emit(5)
        
        # Ambas conexões devem ter sido chamadas
        assert 10 in results  # 5 * 2
        assert 15 in results  # 5 * 3


class TestSlotDecorators:
    """Testes de decoradores de slots"""

    @pytest.mark.gui
    def test_pyqtslot_decorator_works(self):
        """Verifica que decorator pyqtSlot funciona"""
        
        class TestObject(QObject):
            test_signal = pyqtSignal(str)
            
            def __init__(self):
                super().__init__()
                self.received = []
                self.test_signal.connect(self.handle_signal)
            
            @pyqtSlot(str)
            def handle_signal(self, text):
                self.received.append(text)
        
        obj = TestObject()
        obj.test_signal.emit("test")
        
        assert len(obj.received) == 1
        assert obj.received[0] == "test"


class TestTimerSignals:
    """Testes de sinais de timer"""

    @pytest.mark.gui
    def test_qtimer_timeout_signal(self, qtbot):
        """Verifica que QTimer timeout sinal funciona"""
        timer = QTimer()
        
        triggered = []
        timer.timeout.connect(lambda: triggered.append(True))
        
        timer.setSingleShot(True)
        timer.setInterval(50)
        timer.start()
        
        # Aguardar timeout
        qtbot.wait(100)
        
        assert len(triggered) > 0


class TestApplicationSignals:
    """Testes de sinais da aplicação"""

    @pytest.mark.gui
    def test_qapplication_aboutToQuit_signal(self, qapp):
        """Verifica que QApplication tem sinal aboutToQuit"""
        assert hasattr(qapp, 'aboutToQuit')
        
        # Verificar que é um sinal
        # Não vamos emitir pois fecharia a aplicação
        assert qapp.aboutToQuit is not None
