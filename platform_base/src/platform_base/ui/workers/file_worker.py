"""
FileLoadWorker - Worker thread para carregamento de arquivos

Implementa carregamento assíncrono com progress feedback
"""

from __future__ import annotations

import time
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication

from platform_base.io.loader import load, LoadConfig, get_file_info
from platform_base.core.models import Dataset
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class FileLoadWorker(QObject):
    """
    Worker thread para carregamento de arquivos
    
    Emite sinais de progresso e resultado
    """
    
    # Signals
    progress = pyqtSignal(int, str)  # percent, message
    finished = pyqtSignal(object)    # Dataset object
    error = pyqtSignal(str)          # error message
    
    def __init__(self, file_path: str, load_config: LoadConfig):
        super().__init__()
        
        self.file_path = file_path
        self.load_config = load_config
        
    def load_file(self):
        """Carrega arquivo com progress reporting"""
        try:
            file_path = Path(self.file_path)
            
            # Phase 1: File info
            self.progress.emit(10, "Analisando arquivo...")
            QApplication.processEvents()
            
            file_info = get_file_info(self.file_path)
            logger.info("file_info_obtained", 
                       size_mb=file_info.get("size_mb", 0),
                       format=file_info.get("format", "unknown"))
            
            # Phase 2: Loading
            self.progress.emit(30, "Carregando dados...")
            QApplication.processEvents()
            
            start_time = time.perf_counter()
            dataset = load(self.file_path, self.load_config)
            load_duration = time.perf_counter() - start_time
            
            # Phase 3: Validation
            self.progress.emit(80, "Validando dados...")
            QApplication.processEvents()
            
            # Basic validation
            if len(dataset.series) == 0:
                raise ValueError("Nenhuma série numérica encontrada no arquivo")
            
            if len(dataset.t_seconds) == 0:
                raise ValueError("Nenhum timestamp válido encontrado")
            
            # Phase 4: Complete
            self.progress.emit(100, "Carregamento concluído")
            QApplication.processEvents()
            
            logger.info("file_load_completed", 
                       file_path=self.file_path,
                       n_series=len(dataset.series),
                       n_points=len(dataset.t_seconds),
                       duration_ms=load_duration * 1000)
            
            self.finished.emit(dataset)
            
        except Exception as e:
            logger.error("file_load_failed", 
                        file_path=self.file_path, 
                        error=str(e))
            self.error.emit(str(e))