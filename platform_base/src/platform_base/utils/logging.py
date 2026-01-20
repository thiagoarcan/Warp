import logging
import sys
from pathlib import Path
from typing import Optional

try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False


def setup_logging(level: str = "INFO", json_logs: bool = False, log_file: Optional[str] = None) -> None:
    """
    Setup logging para Platform Base
    
    Args:
        level: Nível de log (DEBUG, INFO, WARNING, ERROR)
        json_logs: Se True, usa formato JSON
        log_file: Arquivo de log opcional
    """
    if STRUCTLOG_AVAILABLE:
        _setup_structlog(level, json_logs, log_file)
    else:
        _setup_stdlib_logging(level, log_file)


def _setup_structlog(level: str, json_logs: bool, log_file: Optional[str]) -> None:
    """Configure structlog + stdlib logging"""
    processors = [
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=processors[-1],
        foreign_pre_chain=processors[:-1],
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    handlers = [console_handler]
    
    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    root = logging.getLogger()
    root.handlers = handlers
    root.setLevel(level)

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def _setup_stdlib_logging(level: str, log_file: Optional[str]) -> None:
    """Fallback para logging padrão se structlog não disponível"""
    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(format_str))
    handlers.append(console_handler)
    
    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(format_str))
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        handlers=handlers,
        format=format_str
    )


def configure_logging(level: str = "INFO", json_logs: bool = True) -> None:
    """Legacy function for compatibility"""
    setup_logging(level, json_logs)


def get_logger(name: Optional[str] = None):
    """Return a logger (structlog if available, stdlib otherwise)"""
    if STRUCTLOG_AVAILABLE:
        return structlog.get_logger(name)
    else:
        return logging.getLogger(name or __name__)
