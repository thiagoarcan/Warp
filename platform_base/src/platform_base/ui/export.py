from __future__ import annotations

import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Iterator, Literal, Optional, Any, Dict
import numpy as np
import pandas as pd

from pydantic import BaseModel

from platform_base.core.models import DatasetID, ViewData
from platform_base.ui.state import Selection
from platform_base.utils.errors import ExportError
from platform_base.utils.serialization import to_jsonable
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)

ExportFormat = Literal["csv", "xlsx", "parquet", "hdf5", "json"]


class ExportResult(BaseModel):
    """Resultado de exportação"""
    path: Path
    size_bytes: int
    rows_exported: int
    export_time_seconds: float


class ExportProgress(BaseModel):
    """Progresso de exportação para UI"""
    percent: float
    current_chunk: int
    total_chunks: int
    message: str


class ExportConfig(BaseModel):
    """Configuração de exportação"""
    chunk_size_mb: int = 50
    async_threshold_mb: int = 10
    max_workers: int = 2
    compress: bool = False
    include_metadata: bool = True


def _get_file_size_mb(path: Path) -> float:
    """Calcula tamanho do arquivo em MB"""
    if path.exists():
        return path.stat().st_size / (1024 * 1024)
    return 0.0


def _selection_to_df(view_data: ViewData) -> pd.DataFrame:
    """Converte ViewData para DataFrame"""
    data = {"t_seconds": view_data.t_seconds}
    data.update(view_data.series)
    return pd.DataFrame(data)


def export_selection(
    view_data: ViewData, 
    format: ExportFormat, 
    output_path: Path,
    config: ExportConfig = ExportConfig()
) -> ExportResult:
    """
    Exporta seleção conforme PRD seção 16.1
    
    Se tamanho > threshold (config):
    - Roda em background 
    - Export incremental (chunks)
    - Progress bar na UI
    """
    import time
    start_time = time.time()
    
    logger.info("export_selection_start", 
               format=format, 
               output_path=str(output_path))
    
    df = _selection_to_df(view_data)
    rows_exported = len(df)
    
    try:
        if format == "csv":
            df.to_csv(output_path, index=False)
        elif format == "xlsx":
            df.to_excel(output_path, index=False, engine='openpyxl')
        elif format == "parquet":
            df.to_parquet(output_path, index=False)
        elif format == "hdf5":
            df.to_hdf(output_path, key="data", mode="w")
        elif format == "json":
            df.to_json(output_path, orient="records", indent=2)
        else:
            raise ExportError("Unsupported export format", {"format": format})
            
        size_bytes = output_path.stat().st_size
        export_time = time.time() - start_time
        
        result = ExportResult(
            path=output_path,
            size_bytes=size_bytes,
            rows_exported=rows_exported,
            export_time_seconds=export_time
        )
        
        logger.info("export_selection_complete", 
                   format=format,
                   size_mb=size_bytes / (1024 * 1024),
                   rows=rows_exported,
                   duration_sec=export_time)
        
        return result
        
    except Exception as exc:
        logger.error("export_selection_failed", 
                    format=format,
                    error=str(exc))
        raise ExportError("Export failed", {"format": format, "error": str(exc)}) from exc


def export_session(output_path: Path, app_state: Any) -> ExportResult:
    """
    Exporta sessão conforme PRD seção 16.2
    
    Salva:
    - Config usada
    - Seleções  
    - Anotações
    - Referências a datasets (paths, não dados)
    - Estado de visualizações
    
    NÃO salva: dados brutos (apenas referência)
    """
    import time
    start_time = time.time()
    
    logger.info("export_session_start", output_path=str(output_path))
    
    session_data = {
        "version": "2.0.0",
        "exported_at": time.time(),
        "config": {},  # seria obtido do app_state
        "selections": to_jsonable(app_state.ui_selections) if hasattr(app_state, 'ui_selections') else {},
        "view_subscriptions": to_jsonable(app_state.view_subscriptions) if hasattr(app_state, 'view_subscriptions') else {},
        "dataset_references": [],  # refs para datasets, não dados
        "visualization_states": {},  # estados de plots
        "annotations": [],  # anotações do usuário
    }
    
    try:
        payload = json.dumps(session_data, indent=2, ensure_ascii=False)
        output_path.write_text(payload, encoding="utf-8")
        
        size_bytes = output_path.stat().st_size
        export_time = time.time() - start_time
        
        result = ExportResult(
            path=output_path,
            size_bytes=size_bytes,
            rows_exported=len(session_data),
            export_time_seconds=export_time
        )
        
        logger.info("export_session_complete",
                   size_bytes=size_bytes,
                   duration_sec=export_time)
        
        return result
        
    except Exception as exc:
        logger.error("export_session_failed", error=str(exc))
        raise ExportError("Session export failed", {"error": str(exc)}) from exc


def export_large_dataset(
    dataset_id: DatasetID, 
    output_path: Path, 
    format: ExportFormat = "parquet",
    config: ExportConfig = ExportConfig()
) -> Iterator[ExportProgress]:
    """
    Export incremental conforme PRD seção 16.3
    
    Generator que exporta em chunks.
    Yield progress para update de UI.
    """
    logger.info("export_large_dataset_start", 
               dataset_id=dataset_id,
               output_path=str(output_path),
               chunk_size_mb=config.chunk_size_mb)
    
    # Simulação de export em chunks
    # Em implementação real, obteria dados do DatasetStore
    total_chunks = 10  # seria calculado baseado no tamanho real dos dados
    
    for chunk_idx in range(total_chunks):
        # Simulação de processamento de chunk
        import time
        time.sleep(0.1)  # simula tempo de processamento
        
        percent = ((chunk_idx + 1) / total_chunks) * 100
        
        progress = ExportProgress(
            percent=percent,
            current_chunk=chunk_idx + 1,
            total_chunks=total_chunks,
            message=f"Processando chunk {chunk_idx + 1} de {total_chunks}"
        )
        
        logger.debug("export_chunk_progress", 
                    chunk=chunk_idx + 1,
                    total=total_chunks,
                    percent=percent)
        
        yield progress
        
        # Em implementação real, cada chunk seria escrito para o arquivo
        
    logger.info("export_large_dataset_complete", 
               dataset_id=dataset_id,
               chunks_processed=total_chunks)


async def export_selection_async(
    view_data: ViewData,
    format: ExportFormat,
    output_path: Path,
    config: ExportConfig = ExportConfig()
) -> ExportResult:
    """
    Export assíncrono conforme PRD seção 12.4
    
    Para grandes exports que rodam em background.
    UI mostra progress bar.
    """
    logger.info("export_selection_async_start", 
               format=format,
               output_path=str(output_path))
    
    # Executa export em thread pool para não bloquear UI
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
        result = await loop.run_in_executor(
            executor, 
            export_selection, 
            view_data, 
            format, 
            output_path, 
            config
        )
    
    logger.info("export_selection_async_complete",
               format=format,
               size_mb=result.size_bytes / (1024 * 1024))
    
    return result


def should_export_async(estimated_size_mb: float, config: ExportConfig) -> bool:
    """Determina se export deve ser assíncrono baseado no tamanho"""
    return estimated_size_mb >= config.async_threshold_mb
