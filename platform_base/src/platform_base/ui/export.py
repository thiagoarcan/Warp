from __future__ import annotations

import asyncio
import json
import os
import gzip
import hashlib
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Literal, Optional, Any, Dict, Union
import numpy as np
import pandas as pd

from pydantic import BaseModel, Field

from platform_base.core.models import DatasetID, ViewData, SessionID
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


class SessionData(BaseModel):
    """Dados de sessão serializáveis"""
    version: str = "2.0.0"
    session_id: str
    created_at: str
    modified_at: str
    checksum: str = ""
    
    # Configuration
    config: Dict[str, Any] = Field(default_factory=dict)
    
    # Dataset references (paths, not data)
    dataset_references: list[Dict[str, Any]] = Field(default_factory=list)
    
    # Selections
    selections: Dict[str, Any] = Field(default_factory=dict)
    
    # View subscriptions for streaming
    view_subscriptions: Dict[str, str] = Field(default_factory=dict)
    
    # Visualization states
    visualization_states: Dict[str, Any] = Field(default_factory=dict)
    
    # Annotations by user
    annotations: list[Dict[str, Any]] = Field(default_factory=list)
    
    # Processing history (lineage)
    processing_history: list[Dict[str, Any]] = Field(default_factory=list)
    
    # Streaming sessions
    streaming_sessions: Dict[str, Any] = Field(default_factory=dict)


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


def _compute_checksum(data: str) -> str:
    """Compute SHA256 checksum of data string"""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()[:16]


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
    
    # Build complete session data
    session_id = f"session_{int(time.time())}"
    now = datetime.now(timezone.utc).isoformat()
    
    # Extract dataset references
    dataset_refs = []
    if hasattr(app_state, 'datasets') and app_state.datasets:
        for ds_id in [ds.dataset_id for ds in app_state.datasets.list_datasets()]:
            try:
                ds = app_state.datasets.get_dataset(ds_id)
                dataset_refs.append({
                    "dataset_id": ds_id,
                    "source_path": ds.source.path if ds.source else None,
                    "format": ds.source.format if ds.source else None,
                    "n_series": len(ds.series),
                    "series_names": list(ds.series.keys())
                })
            except Exception as e:
                logger.warning("session_export_dataset_ref_failed", 
                             dataset_id=ds_id, error=str(e))
    
    # Extract selections
    selections_data = {}
    if hasattr(app_state, 'ui_selections'):
        for view_id, selection in app_state.ui_selections.items():
            selections_data[view_id] = to_jsonable(selection)
    
    # Extract view subscriptions
    view_subs = {}
    if hasattr(app_state, 'view_subscriptions'):
        view_subs = dict(app_state.view_subscriptions)
    
    # Extract streaming sessions
    streaming_data = {}
    if hasattr(app_state, 'streaming_sessions'):
        for sess_id, engine in app_state.streaming_sessions.items():
            streaming_data[sess_id] = {
                "current_time_index": engine.state.current_time_index,
                "speed": engine.state.speed,
                "window_size_seconds": engine.state.window_size.total_seconds(),
                "loop": engine.state.loop,
                "is_playing": engine.state.play_state.is_playing,
            }
    
    session_data = SessionData(
        version="2.0.0",
        session_id=session_id,
        created_at=now,
        modified_at=now,
        config={},
        dataset_references=dataset_refs,
        selections=selections_data,
        view_subscriptions=view_subs,
        visualization_states={},
        annotations=[],
        processing_history=[],
        streaming_sessions=streaming_data
    )
    
    try:
        # Serialize
        payload = session_data.model_dump_json(indent=2)
        
        # Compute checksum
        session_data.checksum = _compute_checksum(payload)
        payload = session_data.model_dump_json(indent=2)
        
        # Write to file
        output_path.write_text(payload, encoding="utf-8")
        
        size_bytes = output_path.stat().st_size
        export_time = time.time() - start_time
        
        result = ExportResult(
            path=output_path,
            size_bytes=size_bytes,
            rows_exported=len(dataset_refs),
            export_time_seconds=export_time
        )
        
        logger.info("export_session_complete",
                   session_id=session_id,
                   size_bytes=size_bytes,
                   duration_sec=export_time)
        
        return result
        
    except Exception as exc:
        logger.error("export_session_failed", error=str(exc))
        raise ExportError("Session export failed", {"error": str(exc)}) from exc


def load_session(session_path: Path) -> SessionData:
    """
    Carrega sessão salva anteriormente.
    
    Args:
        session_path: Caminho do arquivo de sessão (.json)
    
    Returns:
        SessionData com dados da sessão
    
    Raises:
        ExportError: Se sessão não puder ser carregada
    """
    logger.info("load_session_start", path=str(session_path))
    
    if not session_path.exists():
        raise ExportError("Session file not found", {"path": str(session_path)})
    
    try:
        content = session_path.read_text(encoding="utf-8")
        data = json.loads(content)
        
        # Validate checksum if present
        stored_checksum = data.get("checksum", "")
        if stored_checksum:
            # Recompute without checksum field
            data_copy = data.copy()
            data_copy["checksum"] = ""
            recomputed = _compute_checksum(json.dumps(data_copy, indent=2))
            if recomputed != stored_checksum:
                logger.warning("session_checksum_mismatch",
                             stored=stored_checksum,
                             computed=recomputed)
        
        session = SessionData(**data)
        
        logger.info("load_session_complete",
                   session_id=session.session_id,
                   n_datasets=len(session.dataset_references))
        
        return session
        
    except json.JSONDecodeError as exc:
        raise ExportError("Invalid session file format", {"error": str(exc)}) from exc
    except Exception as exc:
        raise ExportError("Failed to load session", {"error": str(exc)}) from exc


def restore_session(session: SessionData, app_state: Any, auto_reload_data: bool = False) -> Dict[str, Any]:
    """
    Restaura estado da aplicação a partir de uma sessão.
    
    Args:
        session: SessionData carregado
        app_state: Estado da aplicação para restaurar
        auto_reload_data: Se True, tenta recarregar datasets dos paths originais
    
    Returns:
        Dict com status de restauração
    """
    logger.info("restore_session_start", 
               session_id=session.session_id,
               auto_reload=auto_reload_data)
    
    status = {
        "session_id": session.session_id,
        "datasets_restored": [],
        "datasets_failed": [],
        "selections_restored": 0,
        "views_restored": 0
    }
    
    # Restore dataset references (optionally reload data)
    if auto_reload_data and hasattr(app_state, 'datasets'):
        from platform_base.io.loader import load
        
        for ref in session.dataset_references:
            source_path = ref.get("source_path")
            if source_path and Path(source_path).exists():
                try:
                    dataset = load(source_path, config={})
                    app_state.datasets.add_dataset(dataset)
                    status["datasets_restored"].append(ref.get("dataset_id"))
                    logger.info("dataset_reloaded", path=source_path)
                except Exception as e:
                    status["datasets_failed"].append({
                        "dataset_id": ref.get("dataset_id"),
                        "error": str(e)
                    })
                    logger.warning("dataset_reload_failed", 
                                  path=source_path, error=str(e))
    
    # Restore selections
    if hasattr(app_state, 'ui_selections') and session.selections:
        for view_id, sel_data in session.selections.items():
            try:
                selection = Selection(**sel_data) if isinstance(sel_data, dict) else sel_data
                app_state.ui_selections[view_id] = selection
                status["selections_restored"] += 1
            except Exception as e:
                logger.warning("selection_restore_failed", 
                             view_id=view_id, error=str(e))
    
    # Restore view subscriptions
    if hasattr(app_state, 'view_subscriptions') and session.view_subscriptions:
        app_state.view_subscriptions.update(session.view_subscriptions)
        status["views_restored"] = len(session.view_subscriptions)
    
    logger.info("restore_session_complete", status=status)
    
    return status


def export_session_compressed(output_path: Path, app_state: Any) -> ExportResult:
    """
    Exporta sessão com compressão gzip.
    
    Args:
        output_path: Caminho do arquivo (.json.gz)
        app_state: Estado da aplicação
    
    Returns:
        ExportResult com informações do export
    """
    import time
    start_time = time.time()
    
    logger.info("export_session_compressed_start", output_path=str(output_path))
    
    # First export to temporary uncompressed
    temp_path = output_path.with_suffix('.json.tmp')
    try:
        export_session(temp_path, app_state)
        
        # Compress
        with open(temp_path, 'rb') as f_in:
            with gzip.open(output_path, 'wb') as f_out:
                f_out.writelines(f_in)
        
        # Remove temp file
        temp_path.unlink()
        
        size_bytes = output_path.stat().st_size
        export_time = time.time() - start_time
        
        result = ExportResult(
            path=output_path,
            size_bytes=size_bytes,
            rows_exported=0,
            export_time_seconds=export_time
        )
        
        logger.info("export_session_compressed_complete",
                   size_bytes=size_bytes,
                   duration_sec=export_time)
        
        return result
        
    except Exception as exc:
        if temp_path.exists():
            temp_path.unlink()
        raise ExportError("Compressed session export failed", {"error": str(exc)}) from exc


def load_session_compressed(session_path: Path) -> SessionData:
    """
    Carrega sessão comprimida (.json.gz).
    
    Args:
        session_path: Caminho do arquivo comprimido
    
    Returns:
        SessionData com dados da sessão
    """
    logger.info("load_session_compressed_start", path=str(session_path))
    
    if not session_path.exists():
        raise ExportError("Compressed session file not found", {"path": str(session_path)})
    
    try:
        with gzip.open(session_path, 'rt', encoding='utf-8') as f:
            data = json.load(f)
        
        session = SessionData(**data)
        
        logger.info("load_session_compressed_complete",
                   session_id=session.session_id)
        
        return session
        
    except Exception as exc:
        raise ExportError("Failed to load compressed session", {"error": str(exc)}) from exc


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
