"""
Lazy Loading System - Carregamento sob demanda para arquivos grandes

Features:
- Carregamento sob demanda de chunks de dados
- Virtual scrolling para listas grandes
- Memory-efficient data access
- Background loading com prefetch

Category 7 - Performance
"""

from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generic, TypeVar

import numpy as np
from PyQt6.QtCore import QObject, QThread, pyqtSignal

from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

logger = get_logger(__name__)


T = TypeVar("T")


@dataclass
class ChunkInfo:
    """Informações sobre um chunk de dados"""
    chunk_id: int
    start_index: int
    end_index: int
    size: int
    loaded: bool = False
    loading: bool = False
    last_access: float = field(default_factory=time.time)
    data: np.ndarray | None = None


class LRUCache(Generic[T]):
    """
    Cache LRU (Least Recently Used) para chunks de dados.
    
    Mantém os chunks mais recentemente usados em memória
    e remove os menos usados quando atinge o limite.
    """
    
    def __init__(self, max_size: int = 100, max_memory_mb: float = 500):
        """
        Inicializa cache LRU.
        
        Args:
            max_size: Número máximo de itens no cache
            max_memory_mb: Limite de memória em MB
        """
        self._cache: OrderedDict[str, T] = OrderedDict()
        self._max_size = max_size
        self._max_memory_bytes = max_memory_mb * 1024 * 1024
        self._current_memory = 0
        self._lock = threading.RLock()
    
    def get(self, key: str) -> T | None:
        """Obtém item do cache (move para o fim como mais recente)."""
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                return self._cache[key]
            return None
    
    def put(self, key: str, value: T, size_bytes: int = 0):
        """Adiciona item ao cache."""
        with self._lock:
            # Remove item existente se houver
            if key in self._cache:
                self._cache.move_to_end(key)
                return
            
            # Libera espaço se necessário
            while (len(self._cache) >= self._max_size or 
                   self._current_memory + size_bytes > self._max_memory_bytes):
                if not self._cache:
                    break
                _, old_value = self._cache.popitem(last=False)
                if hasattr(old_value, 'nbytes'):
                    self._current_memory -= old_value.nbytes
            
            # Adiciona novo item
            self._cache[key] = value
            self._current_memory += size_bytes
    
    def remove(self, key: str) -> bool:
        """Remove item do cache."""
        with self._lock:
            if key in self._cache:
                value = self._cache.pop(key)
                if hasattr(value, 'nbytes'):
                    self._current_memory -= value.nbytes
                return True
            return False
    
    def clear(self):
        """Limpa todo o cache."""
        with self._lock:
            self._cache.clear()
            self._current_memory = 0
    
    def __contains__(self, key: str) -> bool:
        return key in self._cache
    
    def __len__(self) -> int:
        return len(self._cache)
    
    @property
    def memory_usage(self) -> int:
        """Uso de memória atual em bytes."""
        return self._current_memory


class ChunkLoader(QThread):
    """Worker thread para carregar chunks em background."""
    
    chunk_loaded = pyqtSignal(int, np.ndarray)  # chunk_id, data
    load_failed = pyqtSignal(int, str)  # chunk_id, error
    
    def __init__(
        self,
        chunk_id: int,
        load_func: Callable[[int, int], np.ndarray],
        start_index: int,
        end_index: int,
        parent: QObject | None = None
    ):
        super().__init__(parent)
        self.chunk_id = chunk_id
        self.load_func = load_func
        self.start_index = start_index
        self.end_index = end_index
    
    def run(self):
        """Executa carregamento do chunk."""
        try:
            data = self.load_func(self.start_index, self.end_index)
            self.chunk_loaded.emit(self.chunk_id, data)
        except Exception as e:
            logger.exception("chunk_load_failed", chunk_id=self.chunk_id, error=str(e))
            self.load_failed.emit(self.chunk_id, str(e))


class LazyDataArray:
    """
    Array de dados com carregamento lazy.
    
    Carrega dados sob demanda em chunks, mantendo apenas
    os chunks mais recentemente usados em memória.
    """
    
    def __init__(
        self,
        total_size: int,
        chunk_size: int = 10000,
        load_func: Callable[[int, int], np.ndarray] | None = None,
        max_cached_chunks: int = 50,
        max_memory_mb: float = 500,
    ):
        """
        Inicializa LazyDataArray.
        
        Args:
            total_size: Tamanho total dos dados
            chunk_size: Tamanho de cada chunk
            load_func: Função para carregar chunk (start, end) -> data
            max_cached_chunks: Máximo de chunks em cache
            max_memory_mb: Limite de memória para cache
        """
        self._total_size = total_size
        self._chunk_size = chunk_size
        self._load_func = load_func
        
        # Cache de chunks
        self._cache = LRUCache[np.ndarray](max_cached_chunks, max_memory_mb)
        
        # Informações de chunks
        self._chunks: dict[int, ChunkInfo] = {}
        self._init_chunks()
        
        # Threading
        self._lock = threading.RLock()
        self._pending_loads: dict[int, ChunkLoader] = {}
        
        logger.debug("lazy_data_array_created",
                    total_size=total_size,
                    chunk_size=chunk_size,
                    num_chunks=len(self._chunks))
    
    def _init_chunks(self):
        """Inicializa informações de chunks."""
        num_chunks = (self._total_size + self._chunk_size - 1) // self._chunk_size
        
        for i in range(num_chunks):
            start = i * self._chunk_size
            end = min((i + 1) * self._chunk_size, self._total_size)
            self._chunks[i] = ChunkInfo(
                chunk_id=i,
                start_index=start,
                end_index=end,
                size=end - start,
            )
    
    def __len__(self) -> int:
        return self._total_size
    
    def __getitem__(self, index: int | slice) -> np.ndarray:
        """Acesso a dados por índice ou slice."""
        if isinstance(index, slice):
            return self._get_slice(index)
        return self._get_single(index)
    
    def _get_single(self, index: int) -> Any:
        """Obtém valor único."""
        if index < 0:
            index = self._total_size + index
        if index < 0 or index >= self._total_size:
            raise IndexError(f"Index {index} out of range [0, {self._total_size})")
        
        chunk_id = index // self._chunk_size
        local_index = index % self._chunk_size
        
        chunk_data = self._get_chunk(chunk_id)
        return chunk_data[local_index]
    
    def _get_slice(self, s: slice) -> np.ndarray:
        """Obtém slice de dados."""
        start, stop, step = s.indices(self._total_size)
        
        if step != 1:
            # Para step != 1, carrega tudo e aplica slice
            # (menos eficiente, mas funcional)
            result = []
            for i in range(start, stop, step):
                result.append(self._get_single(i))
            return np.array(result)
        
        # Determina chunks necessários
        start_chunk = start // self._chunk_size
        end_chunk = (stop - 1) // self._chunk_size
        
        # Coleta dados de cada chunk
        result_parts = []
        for chunk_id in range(start_chunk, end_chunk + 1):
            chunk_data = self._get_chunk(chunk_id)
            chunk_info = self._chunks[chunk_id]
            
            # Calcula slice local dentro do chunk
            local_start = max(0, start - chunk_info.start_index)
            local_end = min(chunk_info.size, stop - chunk_info.start_index)
            
            result_parts.append(chunk_data[local_start:local_end])
        
        return np.concatenate(result_parts)
    
    def _get_chunk(self, chunk_id: int) -> np.ndarray:
        """Obtém chunk de dados, carregando se necessário."""
        cache_key = f"chunk_{chunk_id}"
        
        # Verifica cache
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        
        # Carrega chunk
        chunk_info = self._chunks[chunk_id]
        if self._load_func is None:
            raise ValueError("No load function provided")
        
        data = self._load_func(chunk_info.start_index, chunk_info.end_index)
        
        # Armazena em cache
        self._cache.put(cache_key, data, data.nbytes)
        chunk_info.loaded = True
        chunk_info.last_access = time.time()
        
        return data
    
    def prefetch(self, indices: list[int]):
        """Pré-carrega chunks para os índices especificados."""
        chunk_ids = set()
        for idx in indices:
            if 0 <= idx < self._total_size:
                chunk_ids.add(idx // self._chunk_size)
        
        for chunk_id in chunk_ids:
            cache_key = f"chunk_{chunk_id}"
            if cache_key not in self._cache:
                self._get_chunk(chunk_id)
    
    def prefetch_range(self, start: int, end: int):
        """Pré-carrega chunks para um range de índices."""
        start_chunk = max(0, start // self._chunk_size)
        end_chunk = min(len(self._chunks) - 1, (end - 1) // self._chunk_size)
        
        for chunk_id in range(start_chunk, end_chunk + 1):
            self._get_chunk(chunk_id)
    
    def clear_cache(self):
        """Limpa cache de chunks."""
        self._cache.clear()
        for chunk in self._chunks.values():
            chunk.loaded = False
    
    @property
    def memory_usage(self) -> int:
        """Uso de memória do cache em bytes."""
        return self._cache.memory_usage
    
    @property
    def loaded_chunks(self) -> int:
        """Número de chunks carregados."""
        return sum(1 for c in self._chunks.values() if c.loaded)
    
    @property
    def total_chunks(self) -> int:
        """Número total de chunks."""
        return len(self._chunks)


class LazyFileReader(ABC):
    """
    Leitor de arquivo com carregamento lazy.
    
    Base abstrata para implementações específicas de formato.
    """
    
    def __init__(self, file_path: Path, chunk_size: int = 10000):
        """
        Inicializa leitor lazy.
        
        Args:
            file_path: Caminho do arquivo
            chunk_size: Tamanho de cada chunk
        """
        self.file_path = file_path
        self.chunk_size = chunk_size
        
        self._total_rows: int | None = None
        self._columns: list[str] | None = None
        self._data_arrays: dict[str, LazyDataArray] = {}
        
        # Inicializa metadados
        self._init_metadata()
    
    @abstractmethod
    def _init_metadata(self):
        """Inicializa metadados do arquivo (total_rows, columns)."""
    
    @abstractmethod
    def _load_chunk(self, column: str, start: int, end: int) -> np.ndarray:
        """Carrega chunk de dados para uma coluna."""
    
    @property
    def total_rows(self) -> int:
        """Número total de linhas."""
        if self._total_rows is None:
            self._init_metadata()
        return self._total_rows or 0
    
    @property
    def columns(self) -> list[str]:
        """Lista de colunas."""
        if self._columns is None:
            self._init_metadata()
        return self._columns or []
    
    def get_column(self, column: str) -> LazyDataArray:
        """
        Obtém array lazy para uma coluna.
        
        Args:
            column: Nome da coluna
            
        Returns:
            LazyDataArray para a coluna
        """
        if column not in self._data_arrays:
            self._data_arrays[column] = LazyDataArray(
                total_size=self.total_rows,
                chunk_size=self.chunk_size,
                load_func=lambda s, e, c=column: self._load_chunk(c, s, e),
            )
        return self._data_arrays[column]
    
    def __getitem__(self, column: str) -> LazyDataArray:
        return self.get_column(column)


class LazyCSVReader(LazyFileReader):
    """Leitor lazy para arquivos CSV."""
    
    def __init__(
        self,
        file_path: Path,
        chunk_size: int = 10000,
        delimiter: str = ",",
        encoding: str = "utf-8",
    ):
        self.delimiter = delimiter
        self.encoding = encoding
        super().__init__(file_path, chunk_size)
    
    def _init_metadata(self):
        """Inicializa metadados do CSV."""
        import csv

        # Conta linhas e obtém colunas
        with open(self.file_path, 'r', encoding=self.encoding) as f:
            reader = csv.reader(f, delimiter=self.delimiter)
            self._columns = next(reader)  # Header
            self._total_rows = sum(1 for _ in reader)
        
        logger.debug("lazy_csv_metadata",
                    file=str(self.file_path),
                    rows=self._total_rows,
                    columns=len(self._columns))
    
    def _load_chunk(self, column: str, start: int, end: int) -> np.ndarray:
        """Carrega chunk de dados do CSV."""
        import pandas as pd
        
        col_idx = self._columns.index(column)
        
        # Lê apenas as linhas necessárias
        df = pd.read_csv(
            self.file_path,
            delimiter=self.delimiter,
            encoding=self.encoding,
            skiprows=range(1, start + 1),  # +1 para pular header
            nrows=end - start,
            usecols=[col_idx],
        )
        
        return df.iloc[:, 0].values


class VirtualListModel:
    """
    Modelo virtual para listas grandes.
    
    Carrega apenas os itens visíveis, perfeito para
    QListView/QTreeView com milhares de itens.
    """
    
    def __init__(
        self,
        total_items: int,
        item_loader: Callable[[int], Any],
        cache_size: int = 200,
    ):
        """
        Inicializa modelo virtual.
        
        Args:
            total_items: Número total de itens
            item_loader: Função para carregar item por índice
            cache_size: Tamanho do cache de itens
        """
        self._total_items = total_items
        self._item_loader = item_loader
        self._cache = LRUCache[Any](cache_size)
    
    def __len__(self) -> int:
        return self._total_items
    
    def __getitem__(self, index: int) -> Any:
        cache_key = f"item_{index}"
        
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        
        item = self._item_loader(index)
        self._cache.put(cache_key, item)
        return item
    
    def prefetch_visible(self, first_visible: int, last_visible: int, margin: int = 50):
        """
        Pré-carrega itens visíveis e margem.
        
        Args:
            first_visible: Primeiro índice visível
            last_visible: Último índice visível
            margin: Margem de pré-carregamento
        """
        start = max(0, first_visible - margin)
        end = min(self._total_items, last_visible + margin)
        
        for i in range(start, end):
            _ = self[i]  # Força carregamento


def create_lazy_array(
    file_path: Path,
    column: str,
    chunk_size: int = 10000,
) -> LazyDataArray:
    """
    Cria LazyDataArray a partir de arquivo.
    
    Args:
        file_path: Caminho do arquivo
        column: Coluna a carregar
        chunk_size: Tamanho de chunks
        
    Returns:
        LazyDataArray configurado
    """
    suffix = file_path.suffix.lower()
    
    if suffix == '.csv':
        reader = LazyCSVReader(file_path, chunk_size)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")
    
    return reader.get_column(column)


__all__ = [
    "ChunkInfo",
    "ChunkLoader",
    "LRUCache",
    "LazyCSVReader",
    "LazyDataArray",
    "LazyFileReader",
    "VirtualListModel",
    "create_lazy_array",
]
