"""
ActivityLogPanel - Painel de log de atividades em tempo real

Exibe todas as operações que a aplicação está executando com progresso detalhado
"""

from datetime import datetime
from typing import Union

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ActivityLogPanel(QWidget):
    """
    Painel de log de atividades em tempo real.
    
    Exibe:
    - Log detalhado de todas as operações
    - Progresso de operações em andamento
    - Timestamps de cada ação
    - Botões para limpar/exportar logs
    """
    
    clear_requested = pyqtSignal()
    export_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        # Store operation progress data: {operation_id: {widget, progress, label}}
        self._operation_progress: dict[str, dict[str, Union[QWidget, QProgressBar, QLabel]]] = {}

        
    def _init_ui(self):
        """Inicializa a interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # === Header ===
        header_layout = QHBoxLayout()
        
        title_label = QLabel("📝 Log de Atividades")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Botão para limpar log
        self.clear_btn = QPushButton("🗑️ Limpar")
        self.clear_btn.setToolTip("Limpa todo o histórico de logs")
        self.clear_btn.clicked.connect(self.clear_requested.emit)
        header_layout.addWidget(self.clear_btn)
        
        # Botão para exportar log
        self.export_btn = QPushButton("💾 Exportar")
        self.export_btn.setToolTip("Exporta o log para arquivo")
        self.export_btn.clicked.connect(self.export_requested.emit)
        header_layout.addWidget(self.export_btn)
        
        layout.addLayout(header_layout)
        
        # === Log Text Area ===
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        layout.addWidget(self.log_text, stretch=3)
        
        # === Progress Area ===
        self.progress_widget = QWidget()
        self.progress_layout = QVBoxLayout(self.progress_widget)
        self.progress_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.progress_widget, stretch=1)
        
    def log_message(self, message: str, level: str = "INFO"):
        """
        Adiciona uma mensagem ao log.
        
        Args:
            message: Mensagem a ser logada
            level: Nível do log (INFO, WARNING, ERROR, SUCCESS)
        """
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # Cor baseada no nível
        color = {
            "INFO": "#2196F3",     # Azul
            "WARNING": "#FFC107",  # Amarelo
            "ERROR": "#F44336",    # Vermelho
            "SUCCESS": "#4CAF50",  # Verde
            "DEBUG": "#9E9E9E",    # Cinza
        }.get(level, "#000000")
        
        # Emoji baseado no nível
        emoji = {
            "INFO": "ℹ️",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "SUCCESS": "✅",
            "DEBUG": "🔍",
        }.get(level, "•")
        
        # Formata mensagem com HTML
        html_message = (
            f'<span style="color: #666;">[{timestamp}]</span> '
            f'<span style="color: {color}; font-weight: bold;">{emoji} {level}:</span> '
            f'<span>{message}</span>'
        )
        
        self.log_text.append(html_message)
        
        # Auto-scroll para o final
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def log_info(self, message: str):
        """Log de informação"""
        self.log_message(message, "INFO")
    
    def log_warning(self, message: str):
        """Log de aviso"""
        self.log_message(message, "WARNING")
    
    def log_error(self, message: str):
        """Log de erro"""
        self.log_message(message, "ERROR")
    
    def log_success(self, message: str):
        """Log de sucesso"""
        self.log_message(message, "SUCCESS")
    
    def log_debug(self, message: str):
        """Log de debug"""
        self.log_message(message, "DEBUG")
    
    def add_operation_progress(self, operation_id: str, operation_name: str):
        """
        Adiciona uma barra de progresso para uma operação.
        
        Args:
            operation_id: ID único da operação
            operation_name: Nome descritivo da operação
        """
        if operation_id in self._operation_progress:
            return
        
        # Container para operação
        op_widget = QWidget()
        op_layout = QVBoxLayout(op_widget)
        op_layout.setContentsMargins(0, 5, 0, 5)
        
        # Label com nome da operação
        label = QLabel(f"⏳ {operation_name}")
        label.setStyleSheet("font-weight: bold;")
        op_layout.addWidget(label)
        
        # Progress bar
        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setTextVisible(True)
        progress.setFormat("%p% - Processando...")
        op_layout.addWidget(progress)
        
        self.progress_layout.addWidget(op_widget)
        self._operation_progress[operation_id] = {
            "widget": op_widget,
            "progress": progress,
            "label": label,
        }
        
        self.log_info(f"Iniciada operação: {operation_name}")
    
    def update_operation_progress(
        self, operation_id: str, progress: int, status: str = ""
    ):
        """
        Atualiza o progresso de uma operação.
        
        Args:
            operation_id: ID da operação
            progress: Progresso (0-100)
            status: Mensagem de status opcional
        """
        if operation_id not in self._operation_progress:
            return
        
        op_data = self._operation_progress[operation_id]
        progress_bar = op_data["progress"]
        
        progress_bar.setValue(progress)
        if status:
            progress_bar.setFormat(f"%p% - {status}")
    
    def complete_operation(self, operation_id: str, success: bool = True):
        """
        Marca uma operação como completa e remove a barra de progresso.
        
        Args:
            operation_id: ID da operação
            success: Se a operação foi bem-sucedida
        """
        if operation_id not in self._operation_progress:
            return
        
        op_data = self._operation_progress[operation_id]
        label = op_data["label"]
        operation_name = label.text().replace("⏳ ", "")
        
        # Remove widget
        widget = op_data["widget"]
        self.progress_layout.removeWidget(widget)
        widget.deleteLater()
        
        del self._operation_progress[operation_id]
        
        # Log de conclusão
        if success:
            self.log_success(f"Concluída operação: {operation_name}")
        else:
            self.log_error(f"Falhou operação: {operation_name}")
    
    def clear_log(self):
        """Limpa todo o log"""
        self.log_text.clear()
        self.log_info("Log limpo")
    
    def get_log_content(self) -> str:
        """Retorna o conteúdo do log como texto puro"""
        return self.log_text.toPlainText()
    
    def export_log(self, filepath: str):
        """Exporta o log para um arquivo"""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.get_log_content())
            self.log_success(f"Log exportado para: {filepath}")
        except Exception as e:
            self.log_error(f"Erro ao exportar log: {e}")
