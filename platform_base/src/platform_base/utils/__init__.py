# Utilities package
"""
Platform Base Utilities

Utilitários diversos:
- Logging
- Gerenciamento de IDs
- Tratamento de erros
- Internacionalização
- Gerenciamento de recursos
"""

from platform_base.utils.resource_manager import (
    CloseEventHandler,
    MatplotlibResourceManager,
    ResourceTracker,
    cleanup_on_close,
    force_cleanup,
    get_matplotlib_manager,
    get_resource_tracker,
)


__all__ = [
    "CloseEventHandler",
    "MatplotlibResourceManager",
    # Resource Management
    "ResourceTracker",
    "cleanup_on_close",
    "force_cleanup",
    "get_matplotlib_manager",
    "get_resource_tracker",
]
