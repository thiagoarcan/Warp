"""
FileLoadWorker - Worker thread para carregamento de arquivos

Implementa carregamento assíncrono com progress feedback
VERSÃO SIMPLIFICADA - sem processEvents que causa travamento
"""

from __future__ import annotations

import time
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal

from platform_base.io.loader import LoadConfig, load
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class FileLoadWorker(QObject):
    """
    Worker thread para carregamento de arquivos

    Emite sinais de progresso e resultado
    SIMPLIFICADO: Sem processEvents - deixa Qt gerenciar eventos automaticamente
    """

    # Signals
    progress = pyqtSignal(int, str)  # percent, message
    finished = pyqtSignal(object)    # Dataset object
    error = pyqtSignal(str)          # error message

    def __init__(self, file_path: str, load_config: LoadConfig):
        super().__init__()

        # Ensure proper encoding for Windows paths with Unicode characters
        if isinstance(file_path, str):
            self.file_path = str(Path(file_path).resolve())
        else:
            self.file_path = str(file_path)

        self.load_config = load_config

    def load_file(self):
        """Carrega arquivo - VERSÃO SIMPLIFICADA sem bloqueio"""
        filename = "unknown"
        try:
            # Get filename safely
            try:
                filename = Path(self.file_path).name
            except Exception:
                filename = "unknown_file"

            logger.info("worker_starting", filename=filename)
            self.progress.emit(10, f"Carregando {filename}...")

            # Direct load - sem validação prévia
            start_time = time.perf_counter()
            dataset = load(self.file_path, self.load_config)
            load_duration = time.perf_counter() - start_time

            logger.info("raw_load_completed", filename=filename, duration_ms=load_duration * 1000)

            # Validação mínima
            if not dataset.series or len(dataset.series) == 0:
                raise ValueError(f"Dataset {filename}: nenhuma série encontrada")

            if not hasattr(dataset, "t_seconds") or len(dataset.t_seconds) == 0:
                raise ValueError(f"Dataset {filename}: timestamps inválidos")

            # Set dataset ID
            dataset.dataset_id = Path(self.file_path).stem

            self.progress.emit(100, f"✅ {filename}")

            logger.info("file_load_completed",
                       filename=filename,
                       n_series=len(dataset.series),
                       n_points=len(dataset.t_seconds),
                       duration_ms=load_duration * 1000)

            # Emit result
            self.finished.emit(dataset)

        except Exception as e:
            error_msg = str(e)
            logger.exception("file_load_failed", filename=filename, error=error_msg)
            self.error.emit(error_msg)
