from __future__ import annotations

from platform_base.utils.logging import get_logger

logger = get_logger(__name__)

__all__ = ["global_exception_handler"]


def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Handler global simples para compatibilidade com testes e runtime."""
    logger.exception("unhandled_exception", exc_type=str(exc_type), error=str(exc_value))
    return None
