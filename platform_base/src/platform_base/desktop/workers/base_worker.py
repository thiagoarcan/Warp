"""
BaseWorker - Base class for QThread workers in Platform Base v2.0

Provides common functionality for background processing workers.
"""

from __future__ import annotations

from typing import Any

from PyQt6.QtCore import QThread, pyqtSignal

from platform_base.utils.logging import get_logger


logger = get_logger(__name__)


class BaseWorker(QThread):
    """
    Base class for worker threads.

    Provides common signals and error handling for all workers.
    All workers should inherit from this class.
    """

    # Common signals
    progress = pyqtSignal(int)  # progress percentage (0-100)
    status_updated = pyqtSignal(str)  # status message
    error = pyqtSignal(str)  # error message
    finished = pyqtSignal()  # worker finished (success or error)

    def __init__(self, parent: QThread | None = None):
        super().__init__(parent)

        self.worker_id = f"{self.__class__.__name__}_{id(self)}"
        self.is_cancelled = False

        logger.debug("worker_created", worker_id=self.worker_id)

    def run(self):
        """
        Main worker execution method.

        Subclasses must implement this method.
        Should periodically check is_cancelled and emit progress signals.
        
        Note:
            This is an abstract method that MUST be overridden by subclasses.
            The implementation should:
            1. Execute the worker's main task
            2. Periodically check self.is_cancelled for cancellation requests
            3. Emit progress via self.emit_progress(percent, message)
            4. Call self.emit_success() on completion or self.emit_error() on failure
        
        Example:
            def run(self):
                try:
                    for i in range(100):
                        if self.is_cancelled:
                            return
                        # Do work...
                        self.emit_progress(i, f"Processing {i}%")
                    self.emit_success("Completed successfully")
                except Exception as e:
                    self.emit_error(str(e))
        """
        # Base implementation - subclasses MUST override
        logger.warning("base_worker_run_not_implemented",
                      worker_id=self.worker_id,
                      message="Subclass must implement run() method")
        self.emit_error("Worker run() method not implemented by subclass")

    def cancel(self):
        """Cancel the worker operation"""
        self.is_cancelled = True
        logger.debug("worker_cancelled", worker_id=self.worker_id)

    def emit_progress(self, progress: int, message: str | None = None):
        """Emit progress update with optional status message"""
        if not self.is_cancelled:
            self.progress.emit(progress)
            if message:
                self.status_updated.emit(message)

    def emit_error(self, error_message: str):
        """Emit error signal and finish"""
        logger.error("worker_error", worker_id=self.worker_id, error=error_message)
        self.error.emit(error_message)
        self.finished.emit()

    def emit_success(self, message: str | None = None):
        """Emit success completion"""
        if message:
            self.status_updated.emit(message)
        logger.info("worker_completed", worker_id=self.worker_id)
        self.finished.emit()

    def safe_execute(self, func, *args, **kwargs) -> Any:
        """
        Safely execute a function with error handling.

        Returns:
            Function result or None if error occurred
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.emit_error(str(e))
            return None
