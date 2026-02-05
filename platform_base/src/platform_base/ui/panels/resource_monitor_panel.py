"""
ResourceMonitorPanel - Painel de monitoramento de recursos

Exibe em tempo real o consumo de recursos computacionais por tarefa
"""

import psutil
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ResourceMonitorPanel(QWidget):
    """
    Painel de monitoramento de recursos.
    
    Exibe:
    - CPU total e por núcleo
    - Memória RAM (usada/disponível)
    - Disco (I/O)
    - Tabela de tarefas ativas com consumo individual
    """
    
    resource_update = pyqtSignal(dict)  # Emite estatísticas atualizadas
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._init_timer()
        
    def _init_ui(self):
        """Inicializa a interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # === CPU Group ===
        cpu_group = QGroupBox("💻 CPU")
        cpu_layout = QVBoxLayout()
        
        self.cpu_label = QLabel("CPU: 0%")
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        self.cpu_progress.setTextVisible(True)
        
        cpu_layout.addWidget(self.cpu_label)
        cpu_layout.addWidget(self.cpu_progress)
        cpu_group.setLayout(cpu_layout)
        layout.addWidget(cpu_group)
        
        # === Memory Group ===
        mem_group = QGroupBox("🧠 Memória")
        mem_layout = QVBoxLayout()
        
        self.mem_label = QLabel("RAM: 0 MB / 0 MB")
        self.mem_progress = QProgressBar()
        self.mem_progress.setRange(0, 100)
        self.mem_progress.setTextVisible(True)
        
        mem_layout.addWidget(self.mem_label)
        mem_layout.addWidget(self.mem_progress)
        mem_group.setLayout(mem_layout)
        layout.addWidget(mem_group)
        
        # === Disk Group ===
        disk_group = QGroupBox("💾 Disco")
        disk_layout = QVBoxLayout()
        
        self.disk_read_label = QLabel("Leitura: 0 MB/s")
        self.disk_write_label = QLabel("Escrita: 0 MB/s")
        
        disk_layout.addWidget(self.disk_read_label)
        disk_layout.addWidget(self.disk_write_label)
        disk_group.setLayout(disk_layout)
        layout.addWidget(disk_group)
        
        # === Tasks Table ===
        tasks_group = QGroupBox("📊 Tarefas Ativas")
        tasks_layout = QVBoxLayout()
        
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(4)
        self.tasks_table.setHorizontalHeaderLabels(["Tarefa", "CPU %", "RAM (MB)", "Status"])
        self.tasks_table.horizontalHeader().setStretchLastSection(True)
        
        tasks_layout.addWidget(self.tasks_table)
        tasks_group.setLayout(tasks_layout)
        layout.addWidget(tasks_group)
        
    def _init_timer(self):
        """Inicializa timer de atualização"""
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self._update_stats)
        self._update_timer.start(1000)  # Atualiza a cada 1 segundo
        
        # Variáveis para cálculo de I/O
        self._last_disk_io = psutil.disk_io_counters()
        
    def _update_stats(self):
        """Atualiza estatísticas de recursos"""
        # === CPU ===
        cpu_percent = psutil.cpu_percent(interval=0.1)
        self.cpu_label.setText(f"CPU: {cpu_percent:.1f}%")
        self.cpu_progress.setValue(int(cpu_percent))
        
        # Cor da progress bar baseada no uso
        if cpu_percent < 50:
            style = "QProgressBar::chunk { background-color: #4CAF50; }"
        elif cpu_percent < 80:
            style = "QProgressBar::chunk { background-color: #FFC107; }"
        else:
            style = "QProgressBar::chunk { background-color: #F44336; }"
        self.cpu_progress.setStyleSheet(style)
        
        # === Memória ===
        mem = psutil.virtual_memory()
        mem_used_mb = mem.used / (1024 * 1024)
        mem_total_mb = mem.total / (1024 * 1024)
        mem_percent = mem.percent
        
        self.mem_label.setText(f"RAM: {mem_used_mb:.0f} MB / {mem_total_mb:.0f} MB")
        self.mem_progress.setValue(int(mem_percent))
        
        if mem_percent < 50:
            style = "QProgressBar::chunk { background-color: #4CAF50; }"
        elif mem_percent < 80:
            style = "QProgressBar::chunk { background-color: #FFC107; }"
        else:
            style = "QProgressBar::chunk { background-color: #F44336; }"
        self.mem_progress.setStyleSheet(style)
        
        # === Disco I/O ===
        current_disk_io = psutil.disk_io_counters()
        if self._last_disk_io:
            read_bytes = current_disk_io.read_bytes - self._last_disk_io.read_bytes
            write_bytes = current_disk_io.write_bytes - self._last_disk_io.write_bytes
            read_mb_s = read_bytes / (1024 * 1024)
            write_mb_s = write_bytes / (1024 * 1024)
            
            self.disk_read_label.setText(f"Leitura: {read_mb_s:.2f} MB/s")
            self.disk_write_label.setText(f"Escrita: {write_mb_s:.2f} MB/s")
        
        self._last_disk_io = current_disk_io
        
        # === Emitir sinal com estatísticas ===
        stats = {
            "cpu_percent": cpu_percent,
            "mem_percent": mem_percent,
            "mem_used_mb": mem_used_mb,
            "mem_total_mb": mem_total_mb,
        }
        self.resource_update.emit(stats)
    
    def add_task(self, task_name: str, task_id: str):
        """Adiciona uma tarefa à tabela de monitoramento"""
        row = self.tasks_table.rowCount()
        self.tasks_table.insertRow(row)
        self.tasks_table.setItem(row, 0, QTableWidgetItem(task_name))
        self.tasks_table.setItem(row, 1, QTableWidgetItem("0%"))
        self.tasks_table.setItem(row, 2, QTableWidgetItem("0 MB"))
        self.tasks_table.setItem(row, 3, QTableWidgetItem("Em execução"))
        
        # Armazena task_id como dado do item
        self.tasks_table.item(row, 0).setData(1000, task_id)
    
    def update_task(self, task_id: str, cpu_percent: float, mem_mb: float, status: str):
        """Atualiza informações de uma tarefa específica"""
        for row in range(self.tasks_table.rowCount()):
            item = self.tasks_table.item(row, 0)
            if item and item.data(1000) == task_id:
                self.tasks_table.setItem(row, 1, QTableWidgetItem(f"{cpu_percent:.1f}%"))
                self.tasks_table.setItem(row, 2, QTableWidgetItem(f"{mem_mb:.1f} MB"))
                self.tasks_table.setItem(row, 3, QTableWidgetItem(status))
                break
    
    def remove_task(self, task_id: str):
        """Remove uma tarefa da tabela"""
        for row in range(self.tasks_table.rowCount()):
            item = self.tasks_table.item(row, 0)
            if item and item.data(1000) == task_id:
                self.tasks_table.removeRow(row)
                break
    
    def clear_tasks(self):
        """Limpa todas as tarefas"""
        self.tasks_table.setRowCount(0)
