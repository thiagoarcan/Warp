"""
Performance - Otimização de renderização para grandes volumes de dados

Implementa:
- Decimation (redução de pontos para display)
- Level of Detail (LOD) adaptativo
- Data caching
- Lazy loading para streaming
- Double buffering

Metas de performance:
- 1M pontos: < 500ms render
- 10M pontos: < 2s render
- 100M pontos: streaming com chunks

Autor: Platform Base Team
Versão: 2.0.0
"""

from __future__ import annotations

import gc
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

import numpy as np
from PyQt6.QtCore import QMutex, QObject, pyqtSignal

from platform_base.utils.logging import get_logger


if TYPE_CHECKING:
    from collections.abc import Callable

    from matplotlib.axes import Axes

logger = get_logger(__name__)


class DecimationMethod(Enum):
    """Métodos de decimação de dados"""
    MINMAX = auto()      # Min/Max preservando picos
    LTTB = auto()        # Largest Triangle Three Buckets
    RANDOM = auto()      # Amostragem aleatória
    EVERY_NTH = auto()   # Pega cada N pontos
    AVERAGE = auto()     # Média por bucket


@dataclass
class PerformanceConfig:
    """Configuração de performance"""
    # Thresholds de pontos
    direct_render_limit: int = 10_000     # Render direto
    decimation_limit: int = 100_000       # Usar decimação
    streaming_limit: int = 1_000_000      # Usar streaming

    # Target de pontos após decimação
    target_display_points: int = 5_000

    # LOD levels
    lod_levels: int = 4

    # Método padrão
    decimation_method: DecimationMethod = DecimationMethod.MINMAX

    # Cache
    cache_enabled: bool = True
    cache_size: int = 100

    # Streaming
    chunk_size: int = 100_000
    preload_chunks: int = 2


@dataclass
class DataChunk:
    """Chunk de dados para streaming"""
    index: int
    start_idx: int
    end_idx: int
    data: np.ndarray | None = None
    decimated_data: np.ndarray | None = None
    loaded: bool = False
    loading: bool = False
    timestamp: float = field(default_factory=time.time)


class DataDecimator:
    """
    Decimador de dados para renderização eficiente

    Implementa vários algoritmos de decimação mantendo
    características visuais importantes dos dados.
    """

    def __init__(self, config: PerformanceConfig | None = None):
        """
        Inicializa o decimador

        Args:
            config: Configuração de performance
        """
        self._config = config or PerformanceConfig()
        self._cache: dict[int, tuple[np.ndarray, np.ndarray]] = {}
        self._mutex = QMutex()

    def decimate(
        self,
        x_data: np.ndarray,
        y_data: np.ndarray,
        target_points: int | None = None,
        method: DecimationMethod | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Decima os dados para número alvo de pontos

        Args:
            x_data: Dados do eixo X
            y_data: Dados do eixo Y
            target_points: Número alvo de pontos (None usa config)
            method: Método de decimação (None usa config)

        Returns:
            Tupla (x_decimado, y_decimado)
        """
        n_points = len(y_data)
        target = target_points or self._config.target_display_points
        method = method or self._config.decimation_method

        # Se já está dentro do limite, retorna direto
        if n_points <= target:
            return x_data, y_data

        # Verifica cache
        cache_key = hash((y_data.tobytes()[:1000], target, method.value))
        if self._config.cache_enabled and cache_key in self._cache:
            logger.debug(f"decimation_cache_hit: key={cache_key}")
            return self._cache[cache_key]

        # Executa decimação
        start_time = time.perf_counter()

        if method == DecimationMethod.MINMAX:
            result = self._decimate_minmax(x_data, y_data, target)
        elif method == DecimationMethod.LTTB:
            result = self._decimate_lttb(x_data, y_data, target)
        elif method == DecimationMethod.RANDOM:
            result = self._decimate_random(x_data, y_data, target)
        elif method == DecimationMethod.EVERY_NTH:
            result = self._decimate_nth(x_data, y_data, target)
        elif method == DecimationMethod.AVERAGE:
            result = self._decimate_average(x_data, y_data, target)
        else:
            result = self._decimate_minmax(x_data, y_data, target)

        elapsed = time.perf_counter() - start_time
        logger.info(
            f"decimation_complete: method={method.name}, "
            f"original={n_points}, decimated={len(result[0])}, "
            f"time={elapsed*1000:.1f}ms",
        )

        # Armazena no cache
        if self._config.cache_enabled:
            self._mutex.lock()
            try:
                # Limita tamanho do cache
                if len(self._cache) >= self._config.cache_size:
                    # Remove entradas mais antigas
                    oldest_keys = list(self._cache.keys())[:10]
                    for k in oldest_keys:
                        del self._cache[k]
                self._cache[cache_key] = result
            finally:
                self._mutex.unlock()

        return result

    def _decimate_minmax(
        self,
        x_data: np.ndarray,
        y_data: np.ndarray,
        target_points: int,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Decimação Min/Max - preserva picos e vales

        Para cada bucket, mantém min e max, preservando
        características visuais importantes.
        """
        n_points = len(y_data)
        n_buckets = target_points // 2  # 2 pontos por bucket
        bucket_size = n_points / n_buckets

        x_out = []
        y_out = []

        for i in range(n_buckets):
            start = int(i * bucket_size)
            end = int((i + 1) * bucket_size)

            if start >= end:
                continue

            bucket_y = y_data[start:end]
            bucket_x = x_data[start:end]

            # Encontra índices de min e max
            min_idx = np.argmin(bucket_y)
            max_idx = np.argmax(bucket_y)

            # Ordena por posição X para manter a ordem temporal
            if min_idx < max_idx:
                x_out.extend([bucket_x[min_idx], bucket_x[max_idx]])
                y_out.extend([bucket_y[min_idx], bucket_y[max_idx]])
            else:
                x_out.extend([bucket_x[max_idx], bucket_x[min_idx]])
                y_out.extend([bucket_y[max_idx], bucket_y[min_idx]])

        return np.array(x_out), np.array(y_out)

    def _decimate_lttb(
        self,
        x_data: np.ndarray,
        y_data: np.ndarray,
        target_points: int,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Largest Triangle Three Buckets (LTTB)

        Algoritmo perceptualmente eficiente que preserva
        a forma visual dos dados selecionando pontos
        que maximizam a área de triângulos.
        """
        n_points = len(y_data)

        if target_points >= n_points:
            return x_data, y_data

        # Sempre inclui primeiro e último ponto
        bucket_size = (n_points - 2) / (target_points - 2)

        x_out = [x_data[0]]
        y_out = [y_data[0]]


        for i in range(target_points - 2):
            # Bucket atual
            bucket_start = int((i + 0) * bucket_size) + 1
            bucket_end = int((i + 1) * bucket_size) + 1

            # Próximo bucket para calcular média
            next_bucket_start = int((i + 1) * bucket_size) + 1
            next_bucket_end = int((i + 2) * bucket_size) + 1
            next_bucket_end = min(next_bucket_end, n_points)

            # Média do próximo bucket
            if next_bucket_end > next_bucket_start:
                avg_x = np.mean(x_data[next_bucket_start:next_bucket_end])
                avg_y = np.mean(y_data[next_bucket_start:next_bucket_end])
            else:
                avg_x = x_data[-1]
                avg_y = y_data[-1]

            # Encontra ponto no bucket atual que maximiza área do triângulo
            max_area = -1
            max_idx = bucket_start

            prev_x = x_out[-1]
            prev_y = y_out[-1]

            for j in range(bucket_start, min(bucket_end, n_points)):
                # Área do triângulo (fórmula simplificada)
                area = abs(
                    (prev_x - avg_x) * (y_data[j] - prev_y) -
                    (prev_x - x_data[j]) * (avg_y - prev_y),
                )
                if area > max_area:
                    max_area = area
                    max_idx = j

            x_out.append(x_data[max_idx])
            y_out.append(y_data[max_idx])

        # Adiciona último ponto
        x_out.append(x_data[-1])
        y_out.append(y_data[-1])

        return np.array(x_out), np.array(y_out)

    def _decimate_random(
        self,
        x_data: np.ndarray,
        y_data: np.ndarray,
        target_points: int,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Amostragem aleatória

        Simples mas não preserva características visuais.
        """
        n_points = len(y_data)
        indices = np.sort(np.random.choice(n_points, target_points, replace=False))
        return x_data[indices], y_data[indices]

    def _decimate_nth(
        self,
        x_data: np.ndarray,
        y_data: np.ndarray,
        target_points: int,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Pega cada N pontos

        Rápido mas pode perder picos.
        """
        n_points = len(y_data)
        n = max(1, n_points // target_points)
        indices = np.arange(0, n_points, n)
        return x_data[indices], y_data[indices]

    def _decimate_average(
        self,
        x_data: np.ndarray,
        y_data: np.ndarray,
        target_points: int,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Média por bucket

        Suaviza os dados mas perde detalhes.
        """
        n_points = len(y_data)
        bucket_size = n_points / target_points

        x_out = []
        y_out = []

        for i in range(target_points):
            start = int(i * bucket_size)
            end = int((i + 1) * bucket_size)

            if start >= end:
                continue

            x_out.append(np.mean(x_data[start:end]))
            y_out.append(np.mean(y_data[start:end]))

        return np.array(x_out), np.array(y_out)

    def clear_cache(self):
        """Limpa o cache de decimação"""
        self._mutex.lock()
        try:
            self._cache.clear()
        finally:
            self._mutex.unlock()
        gc.collect()


class LODManager:
    """
    Level of Detail (LOD) Manager

    Gerencia diferentes níveis de detalhe para
    zoom adaptativo.
    """

    def __init__(
        self,
        x_data: np.ndarray,
        y_data: np.ndarray,
        config: PerformanceConfig | None = None,
    ):
        """
        Inicializa o gerenciador de LOD

        Args:
            x_data: Dados originais do eixo X
            y_data: Dados originais do eixo Y
            config: Configuração de performance
        """
        self._x_data = x_data
        self._y_data = y_data
        self._config = config or PerformanceConfig()
        self._decimator = DataDecimator(self._config)
        self._lod_cache: dict[int, tuple[np.ndarray, np.ndarray]] = {}
        self._mutex = QMutex()

        # Pré-computa LODs
        self._precompute_lods()

    def _precompute_lods(self):
        """Pré-computa níveis de LOD"""
        n_points = len(self._y_data)
        n_levels = self._config.lod_levels

        for level in range(n_levels):
            # Cada nível tem menos pontos
            factor = 2 ** (n_levels - level - 1)
            target = min(n_points, self._config.target_display_points * factor)

            x_dec, y_dec = self._decimator.decimate(
                self._x_data, self._y_data, target,
            )
            self._lod_cache[level] = (x_dec, y_dec)

            logger.debug(f"lod_precomputed: level={level}, points={len(x_dec)}")

    def get_data_for_view(
        self,
        x_min: float,
        x_max: float,
        view_width_pixels: int = 1000,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Obtém dados apropriados para a view atual

        Args:
            x_min: Limite inferior do eixo X
            x_max: Limite superior do eixo X
            view_width_pixels: Largura da view em pixels

        Returns:
            Dados decimados apropriados para a view
        """
        # Filtra dados para range visível
        mask = (self._x_data >= x_min) & (self._x_data <= x_max)
        visible_x = self._x_data[mask]
        visible_y = self._y_data[mask]

        n_visible = len(visible_y)

        # Se poucos pontos, retorna direto
        if n_visible <= view_width_pixels * 2:
            return visible_x, visible_y

        # Seleciona LOD apropriado
        target_points = view_width_pixels * 2  # 2 pontos por pixel

        # Encontra melhor nível de LOD
        best_level = 0
        for level, (x_lod, y_lod) in self._lod_cache.items():
            if len(x_lod) >= target_points:
                best_level = level

        # Retorna dados do LOD filtrados para range
        x_lod, y_lod = self._lod_cache.get(best_level, (visible_x, visible_y))
        mask = (x_lod >= x_min) & (x_lod <= x_max)

        return x_lod[mask], y_lod[mask]


class StreamingDataManager(QObject):
    """
    Gerenciador de dados para streaming de grandes volumes

    Carrega dados em chunks sob demanda para suportar
    datasets de 100M+ pontos.
    """

    # Signals
    chunk_loaded = pyqtSignal(int)  # chunk_index
    loading_progress = pyqtSignal(int, int)  # loaded, total

    def __init__(
        self,
        data_source: Callable[[int, int], np.ndarray],
        total_points: int,
        config: PerformanceConfig | None = None,
    ):
        """
        Inicializa o gerenciador de streaming

        Args:
            data_source: Função que retorna dados[start:end]
            total_points: Total de pontos no dataset
            config: Configuração de performance
        """
        super().__init__()

        self._data_source = data_source
        self._total_points = total_points
        self._config = config or PerformanceConfig()
        self._chunks: dict[int, DataChunk] = {}
        self._decimator = DataDecimator(self._config)
        self._mutex = QMutex()

        # Inicializa chunks
        self._init_chunks()

    def _init_chunks(self):
        """Inicializa estrutura de chunks"""
        chunk_size = self._config.chunk_size
        n_chunks = (self._total_points + chunk_size - 1) // chunk_size

        for i in range(n_chunks):
            start_idx = i * chunk_size
            end_idx = min((i + 1) * chunk_size, self._total_points)

            self._chunks[i] = DataChunk(
                index=i,
                start_idx=start_idx,
                end_idx=end_idx,
            )

        logger.info(f"streaming_init: total_points={self._total_points}, chunks={n_chunks}")

    def get_data_for_range(
        self,
        start: int,
        end: int,
        target_points: int | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Obtém dados para um range específico

        Args:
            start: Índice inicial
            end: Índice final
            target_points: Número alvo de pontos

        Returns:
            Tupla (x_data, y_data)
        """
        target = target_points or self._config.target_display_points

        # Identifica chunks necessários
        chunk_size = self._config.chunk_size
        start_chunk = start // chunk_size
        end_chunk = (end - 1) // chunk_size

        # Carrega chunks necessários
        for chunk_idx in range(start_chunk, end_chunk + 1):
            if chunk_idx in self._chunks:
                self._load_chunk(chunk_idx)

        # Combina dados dos chunks
        x_parts = []
        y_parts = []

        for chunk_idx in range(start_chunk, end_chunk + 1):
            chunk = self._chunks.get(chunk_idx)
            if chunk and chunk.loaded and chunk.data is not None:
                # Calcula índices locais
                local_start = max(0, start - chunk.start_idx)
                local_end = min(len(chunk.data), end - chunk.start_idx)

                if local_start < local_end:
                    chunk_data = chunk.data[local_start:local_end]
                    x_parts.append(np.arange(chunk.start_idx + local_start,
                                            chunk.start_idx + local_end))
                    y_parts.append(chunk_data)

        if not y_parts:
            return np.array([]), np.array([])

        x_data = np.concatenate(x_parts)
        y_data = np.concatenate(y_parts)

        # Decima se necessário
        if len(y_data) > target:
            return self._decimator.decimate(x_data, y_data, target)

        return x_data, y_data

    def _load_chunk(self, chunk_idx: int):
        """Carrega um chunk de dados"""
        chunk = self._chunks.get(chunk_idx)
        if not chunk or chunk.loaded or chunk.loading:
            return

        self._mutex.lock()
        try:
            chunk.loading = True
        finally:
            self._mutex.unlock()

        try:
            # Carrega dados
            data = self._data_source(chunk.start_idx, chunk.end_idx)
            chunk.data = data

            # Pré-decima para visualização rápida
            x_data = np.arange(chunk.start_idx, chunk.end_idx)
            chunk.decimated_data = self._decimator.decimate(
                x_data, data,
                self._config.target_display_points // 10,
            )[1]

            chunk.loaded = True
            chunk.timestamp = time.time()

            self.chunk_loaded.emit(chunk_idx)

            logger.debug(f"chunk_loaded: idx={chunk_idx}, points={len(data)}")

        except Exception as e:
            logger.exception(f"chunk_load_error: idx={chunk_idx}, error={e}")
        finally:
            chunk.loading = False

    def preload_chunks(self, current_chunk: int):
        """Pré-carrega chunks adjacentes"""
        n_preload = self._config.preload_chunks

        for offset in range(-n_preload, n_preload + 1):
            chunk_idx = current_chunk + offset
            if 0 <= chunk_idx < len(self._chunks):
                self._load_chunk(chunk_idx)

    def unload_distant_chunks(self, current_chunk: int, keep_range: int = 5):
        """Descarrega chunks distantes para liberar memória"""
        for chunk_idx, chunk in list(self._chunks.items()):
            if abs(chunk_idx - current_chunk) > keep_range and chunk.loaded:
                chunk.data = None
                chunk.decimated_data = None
                chunk.loaded = False
                logger.debug(f"chunk_unloaded: idx={chunk_idx}")

        gc.collect()

    def get_overview(self, target_points: int = 1000) -> tuple[np.ndarray, np.ndarray]:
        """
        Obtém visão geral de todo o dataset

        Útil para minimap ou navegação.
        """
        # Usa dados decimados de cada chunk
        x_parts = []
        y_parts = []

        points_per_chunk = max(1, target_points // len(self._chunks))

        for _chunk_idx, chunk in sorted(self._chunks.items()):
            if chunk.decimated_data is not None:
                step = max(1, len(chunk.decimated_data) // points_per_chunk)
                y_sample = chunk.decimated_data[::step]
                x_sample = np.linspace(chunk.start_idx, chunk.end_idx, len(y_sample))
                x_parts.append(x_sample)
                y_parts.append(y_sample)

        if not y_parts:
            return np.array([]), np.array([])

        return np.concatenate(x_parts), np.concatenate(y_parts)


class PerformanceRenderer:
    """
    Renderizador de alta performance

    Coordena decimação, LOD e streaming para
    renderização eficiente em matplotlib.
    """

    def __init__(self, config: PerformanceConfig | None = None):
        """
        Inicializa o renderizador

        Args:
            config: Configuração de performance
        """
        self._config = config or PerformanceConfig()
        self._decimator = DataDecimator(self._config)
        self._lod_managers: dict[str, LODManager] = {}
        self._render_times: list[float] = []

    def render_line(
        self,
        ax: Axes,
        x_data: np.ndarray,
        y_data: np.ndarray,
        series_id: str = "default",
        **plot_kwargs,
    ):
        """
        Renderiza linha com otimização automática

        Args:
            ax: Axes do matplotlib
            x_data: Dados do eixo X
            y_data: Dados do eixo Y
            series_id: ID da série para cache
            **plot_kwargs: Argumentos para ax.plot()
        """
        start_time = time.perf_counter()
        n_points = len(y_data)

        # Determina estratégia
        if n_points <= self._config.direct_render_limit:
            # Render direto
            x_render, y_render = x_data, y_data
            strategy = "direct"
        elif n_points <= self._config.decimation_limit:
            # Decimação simples
            x_render, y_render = self._decimator.decimate(x_data, y_data)
            strategy = "decimation"
        else:
            # LOD para grandes volumes
            if series_id not in self._lod_managers:
                self._lod_managers[series_id] = LODManager(x_data, y_data, self._config)

            lod = self._lod_managers[series_id]
            xlim = ax.get_xlim()
            x_render, y_render = lod.get_data_for_view(xlim[0], xlim[1])
            strategy = "lod"

        # Renderiza
        ax.plot(x_render, y_render, **plot_kwargs)

        # Log de performance
        elapsed = time.perf_counter() - start_time
        self._render_times.append(elapsed)

        logger.info(
            f"render_complete: strategy={strategy}, "
            f"original={n_points}, rendered={len(x_render)}, "
            f"time={elapsed*1000:.1f}ms",
        )

    def get_performance_stats(self) -> dict[str, Any]:
        """Retorna estatísticas de performance"""
        if not self._render_times:
            return {}

        return {
            "total_renders": len(self._render_times),
            "avg_render_ms": np.mean(self._render_times) * 1000,
            "max_render_ms": np.max(self._render_times) * 1000,
            "min_render_ms": np.min(self._render_times) * 1000,
        }

    def clear_cache(self):
        """Limpa todos os caches"""
        self._decimator.clear_cache()
        self._lod_managers.clear()
        self._render_times.clear()
        gc.collect()


# Singleton instance
_performance_renderer: PerformanceRenderer | None = None


def get_performance_renderer(
    config: PerformanceConfig | None = None,
) -> PerformanceRenderer:
    """
    Obtém instância singleton do renderizador de performance

    Args:
        config: Configuração (só usado na primeira chamada)

    Returns:
        Instância do PerformanceRenderer
    """
    global _performance_renderer

    if _performance_renderer is None:
        _performance_renderer = PerformanceRenderer(config)

    return _performance_renderer


def decimate_for_plot(
    x_data: np.ndarray,
    y_data: np.ndarray,
    target_points: int = 5000,
    method: DecimationMethod = DecimationMethod.MINMAX,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Função de conveniência para decimação rápida

    Args:
        x_data: Dados do eixo X
        y_data: Dados do eixo Y
        target_points: Número alvo de pontos
        method: Método de decimação

    Returns:
        Tupla (x_decimado, y_decimado)
    """
    config = PerformanceConfig(
        target_display_points=target_points,
        decimation_method=method,
    )
    decimator = DataDecimator(config)
    return decimator.decimate(x_data, y_data, target_points, method)


# Exports
__all__ = [
    "DataDecimator",
    "DecimationMethod",
    "LODManager",
    "PerformanceConfig",
    "PerformanceRenderer",
    "StreamingDataManager",
    "decimate_for_plot",
    "get_performance_renderer",
]
