"""
FileLoadWorker - Worker thread para carregamento de arquivos

Implementa carregamento assíncrono com progress feedback
"""

from __future__ import annotations

import time
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication

from platform_base.io.loader import LoadConfig, get_file_info, load
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

        # Ensure proper encoding for Windows paths with Unicode characters
        if isinstance(file_path, str):
            # Convert to Path and back to string to ensure proper encoding
            self.file_path = str(Path(file_path).resolve())
        else:
            self.file_path = str(file_path)

        self.load_config = load_config

    def load_file(self):
        """Carrega arquivo com progress reporting - VERSÃO ROBUSTA"""
        filename = "unknown"
        try:
            # Get filename safely for logging
            try:
                filename = Path(self.file_path).name
            except Exception:
                filename = "unknown_file"

            logger.info("worker_starting", filename=filename)

            # Phase 1: File info with error handling
            try:
                self.progress.emit(10, "Analisando arquivo...")
                if QApplication.instance():
                    QApplication.processEvents()

                file_info = get_file_info(self.file_path)
                logger.info("file_info_obtained",
                           filename=filename,
                           size_mb=file_info.get("size_mb", 0),
                           format=file_info.get("format", "unknown"))
            except Exception as e:
                logger.exception("file_info_failed", filename=filename, error=str(e))
                # Continue anyway

            # Phase 2: Loading with robust error handling
            self.progress.emit(30, "Carregando dados...")
            if QApplication.instance():
                QApplication.processEvents()

            start_time = time.perf_counter()
            dataset = load(self.file_path, self.load_config)
            load_duration = time.perf_counter() - start_time

            logger.info("raw_load_completed", filename=filename, duration_ms=load_duration * 1000)

            # Phase 3: Validation with detailed checks
            self.progress.emit(80, "Validando dados...")
            if QApplication.instance():
                QApplication.processEvents()

            # Enhanced validation
            if not hasattr(dataset, "series") or dataset.series is None:
                raise ValueError(f"Dataset {filename}: objeto series inválido")

            if len(dataset.series) == 0:
                raise ValueError(f"Dataset {filename}: nenhuma série numérica encontrada")

            if not hasattr(dataset, "t_seconds") or dataset.t_seconds is None:
                raise ValueError(f"Dataset {filename}: timestamps inválidos")

            if len(dataset.t_seconds) == 0:
                raise ValueError(f"Dataset {filename}: nenhum timestamp válido encontrado")

            # Set filename as dataset ID for user-friendly display
            try:
                dataset.dataset_id = Path(self.file_path).stem
            except Exception:
                dataset.dataset_id = filename

            # Phase 4: Complete
            self.progress.emit(100, "Carregamento concluído")
            if QApplication.instance():
                QApplication.processEvents()

            logger.info("file_load_completed",
                       filename=filename,
                       dataset_id=dataset.dataset_id,
                       n_series=len(dataset.series),
                       n_points=len(dataset.t_seconds),
                       duration_ms=load_duration * 1000)

            # Emit finished signal
            self.finished.emit(dataset)

        except Exception as e:
            error_msg = str(e)
            logger.exception("file_load_failed",
                        filename=filename,
                        error=error_msg,
                        exception_type=type(e).__name__)

            # Always emit error signal
            try:
                self.error.emit(error_msg)
            except Exception as emit_error:
                logger.exception("error_signal_emit_failed",
                            filename=filename,
                            emit_error=str(emit_error))
