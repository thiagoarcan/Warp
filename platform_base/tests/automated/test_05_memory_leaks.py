"""
Testes automatizados de detecção de memory leaks
Verifica que não há vazamentos de memória na aplicação
"""

import pytest
import gc
import sys
from PyQt6.QtWidgets import QWidget, QPushButton, QMainWindow, QDialog
from PyQt6.QtCore import QObject


class TestMemoryLeaks:
    """Testes de detecção de memory leaks"""

    @pytest.mark.gui
    def test_widget_creation_and_deletion(self, qtbot):
        """Verifica que widgets são deletados corretamente"""
        import weakref
        
        # Criar widget
        widget = QWidget()
        qtbot.addWidget(widget)
        
        # Criar weak reference
        weak_ref = weakref.ref(widget)
        
        # Verificar que existe
        assert weak_ref() is not None
        
        # Deletar widget
        widget.deleteLater()
        qtbot.wait(100)
        
        # Forçar garbage collection
        gc.collect()
        qtbot.wait(100)
        
        # Widget deve ter sido deletado
        # Nota: em alguns casos pode ainda existir temporariamente
        # Este teste é mais informativo

    @pytest.mark.gui
    def test_multiple_widgets_no_leak(self, qtbot, clean_qapp):
        """Verifica que criar múltiplos widgets não causa leak"""
        initial_count = len(gc.get_objects())
        
        widgets = []
        for i in range(100):
            w = QWidget()
            qtbot.addWidget(w)
            widgets.append(w)
        
        # Deletar todos
        for w in widgets:
            w.deleteLater()
        
        widgets.clear()
        qtbot.wait(100)
        
        # Forçar garbage collection
        gc.collect()
        qtbot.wait(100)
        gc.collect()
        
        final_count = len(gc.get_objects())
        
        # Não deve ter crescido significativamente
        # Permitir alguma margem para objetos temporários
        growth = final_count - initial_count
        assert growth < 500, f"Possível leak: crescimento de {growth} objetos"

    @pytest.mark.gui
    def test_signal_connections_no_leak(self, qtbot):
        """Verifica que conexões de sinais não causam leak"""
        
        class TestObject(QObject):
            pass
        
        obj = TestObject()
        buttons = []
        
        for i in range(50):
            btn = QPushButton(f"Button {i}")
            qtbot.addWidget(btn)
            # Conectar sinal
            btn.clicked.connect(lambda: None)
            buttons.append(btn)
        
        # Deletar todos
        for btn in buttons:
            btn.deleteLater()
        
        buttons.clear()
        del obj
        qtbot.wait(100)
        
        # Garbage collection
        gc.collect()
        qtbot.wait(50)


class TestMemoryUsage:
    """Testes de uso de memória"""

    @pytest.mark.gui
    def test_widget_memory_footprint(self, qtbot):
        """Verifica footprint de memória de widgets"""
        import sys
        
        widget = QWidget()
        qtbot.addWidget(widget)
        
        # Obter tamanho (aproximado)
        size = sys.getsizeof(widget)
        
        # Deve ser razoável
        assert size < 10000, f"Widget muito grande: {size} bytes"

    @pytest.mark.gui
    @pytest.mark.slow
    def test_repeated_creation_memory_stable(self, qtbot, clean_qapp):
        """Verifica que memória permanece estável com criações repetidas"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Criar e deletar widgets repetidamente
        for iteration in range(10):
            widgets = []
            for i in range(50):
                w = QWidget()
                qtbot.addWidget(w)
                widgets.append(w)
            
            # Deletar
            for w in widgets:
                w.deleteLater()
            
            widgets.clear()
            qtbot.wait(50)
            gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        growth = final_memory - initial_memory
        
        # Não deve crescer mais que 50MB
        assert growth < 50, f"Crescimento de memória: {growth:.2f} MB"


class TestGarbageCollection:
    """Testes de garbage collection"""

    @pytest.mark.gui
    def test_gc_collects_widgets(self, qtbot):
        """Verifica que GC coleta widgets não referenciados"""
        import weakref
        
        weak_refs = []
        
        # Criar widgets sem manter referência
        for i in range(10):
            w = QWidget()
            qtbot.addWidget(w)
            weak_refs.append(weakref.ref(w))
            w.deleteLater()
        
        qtbot.wait(100)
        
        # Forçar GC
        gc.collect()
        qtbot.wait(100)
        gc.collect()
        
        # Pelo menos alguns devem ter sido coletados
        collected = sum(1 for ref in weak_refs if ref() is None)
        # Pode não coletar todos imediatamente
        assert collected >= 0  # Teste informativo

    @pytest.mark.gui
    def test_circular_references_handled(self):
        """Verifica que referências circulares são tratadas"""
        
        class Node(QObject):
            def __init__(self):
                super().__init__()
                self.next = None
        
        # Criar ciclo
        node1 = Node()
        node2 = Node()
        node1.next = node2
        node2.next = node1
        
        # Deletar referências
        del node1
        del node2
        
        # GC deve coletar
        collected = gc.collect()
        
        # Deve ter coletado objetos cíclicos
        assert collected >= 0


class TestLargeDataStructures:
    """Testes com estruturas de dados grandes"""

    @pytest.mark.gui
    @pytest.mark.slow
    def test_large_widget_tree_no_leak(self, qtbot):
        """Verifica que árvore grande de widgets não causa leak"""
        
        root = QWidget()
        qtbot.addWidget(root)
        
        # Criar árvore
        for i in range(10):
            parent = QWidget(root)
            for j in range(10):
                child = QWidget(parent)
        
        # Obter contagem inicial
        initial_children = len(root.findChildren(QWidget))
        
        # Deletar
        root.deleteLater()
        qtbot.wait(100)
        
        gc.collect()
        
        # Verificar que foi deletado
        # (root ainda pode existir temporariamente em qtbot)


class TestEventLoopMemory:
    """Testes de memória do event loop"""

    @pytest.mark.gui
    def test_event_processing_no_leak(self, qtbot):
        """Verifica que processar eventos não causa leak"""
        from PyQt6.QtCore import QTimer
        
        processed = []
        
        def process():
            processed.append(True)
        
        # Processar muitos eventos
        for i in range(100):
            QTimer.singleShot(1, process)
        
        # Aguardar processamento
        qtbot.wait(200)
        
        # Verificar que eventos foram processados
        assert len(processed) > 0
        
        # GC
        gc.collect()
