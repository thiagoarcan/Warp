"""
UI Workers package

Workers para execução assíncrona de operações em background threads.

Workers disponíveis:
- FileLoadWorker: Carregamento de arquivos de dados
- CalculusWorker: Operações de cálculo (derivadas, integrais, áreas)
- InterpolationWorker: Operações de interpolação
- FilterWorker: Operações de filtragem
- SmoothingWorker: Operações de suavização
- BatchOperationWorker: Execução de múltiplas operações em batch
"""

from platform_base.ui.workers.file_worker import FileLoadWorker
from platform_base.ui.workers.operation_workers import (
    BaseOperationWorker,
    BatchOperationWorker,
    CalculusWorker,
    FilterWorker,
    InterpolationWorker,
    SmoothingWorker,
)

__all__ = [
    'FileLoadWorker',
    'BaseOperationWorker',
    'CalculusWorker',
    'InterpolationWorker',
    'FilterWorker',
    'SmoothingWorker',
    'BatchOperationWorker',
]
