"""
Setup e inicialização do sistema de profiling

Provides functions to initialize profiling from configuration
"""

from pathlib import Path
from typing import Any

import yaml

from platform_base.utils.logging import get_logger

from .decorators import set_global_profiler
from .profiler import create_auto_profiler_from_config


logger = get_logger(__name__)


def setup_profiling_from_config(config_path: str) -> Any | None:
    """
    Inicializa profiling a partir de arquivo de configuração

    Args:
        config_path: Caminho para arquivo platform.yaml

    Returns:
        AutoProfiler instance ou None se desabilitado
    """
    try:
        config_file = Path(config_path)
        if not config_file.exists():
            logger.warning("profiling_config_not_found", path=config_path)
            return None

        with open(config_file, encoding="utf-8") as f:
            full_config = yaml.safe_load(f)

        profiling_config = full_config.get("profiling", {})

        if not profiling_config.get("enabled", False):
            logger.info("profiling_disabled")
            return None

        # Cria profiler
        profiler = create_auto_profiler_from_config(profiling_config)

        # Define como profiler global para decoradores
        set_global_profiler(profiler)

        logger.info("profiling_initialized",
                   automatic=profiling_config.get("automatic", True),
                   threshold=profiling_config.get("threshold_seconds", 1.0),
                   targets=len(profiling_config.get("targets", [])))

        return profiler

    except Exception as e:
        logger.exception("profiling_setup_failed", error=str(e))
        return None


def setup_profiling_from_dict(config: dict[str, Any]) -> Any | None:
    """
    Inicializa profiling a partir de dicionário de configuração

    Args:
        config: Configuração de profiling

    Returns:
        AutoProfiler instance ou None se desabilitado
    """
    try:
        if not config.get("enabled", False):
            logger.info("profiling_disabled")
            return None

        # Cria profiler
        profiler = create_auto_profiler_from_config(config)

        # Define como profiler global para decoradores
        set_global_profiler(profiler)

        logger.info("profiling_initialized",
                   automatic=config.get("automatic", True),
                   threshold=config.get("threshold_seconds", 1.0),
                   targets=len(config.get("targets", [])))

        return profiler

    except Exception as e:
        logger.exception("profiling_setup_failed", error=str(e))
        return None


# Factory functions para testes
def create_test_profiler(output_dir: str = "test_profiling") -> Any:
    """Cria profiler para testes com configuração mínima"""
    config = {
        "enabled": True,
        "automatic": True,
        "threshold_seconds": 0.1,  # Threshold baixo para testes
        "output_dir": output_dir,
        "formats": ["stats"],
        "targets": [
            {
                "name": "test_interpolation",
                "operation": "interpolate",
                "points": 1000,
                "max_time": 1.0,
            },
        ],
        "memory": {
            "enabled": True,
            "threshold_mb": 10,
            "track_allocations": True,
        },
    }

    return create_auto_profiler_from_config(config)
