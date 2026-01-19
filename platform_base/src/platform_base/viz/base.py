from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Tuple, Literal
import numpy as np

try:
    import numba
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

from platform_base.viz.config import PlotConfig
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


def _create_lttb_numba():
    """Create numba-optimized LTTB if available."""
    if not NUMBA_AVAILABLE:
        return None
        
    @numba.jit(nopython=True, cache=True)
    def _lttb_numba(x: np.ndarray, y: np.ndarray, max_points: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Numba-optimized Largest Triangle Three Buckets (LTTB) algorithm.
        
        Preserva features críticos (peaks, valleys, edges) durante downsampling.
        """
        n = len(x)
        
        if n <= max_points:
            return x, y
        
        if max_points < 3:
            # Para casos extremos, retorna primeiro, meio e último ponto
            indices = np.array([0, n//2, n-1])
            return x[indices], y[indices]
        
        # Inicializa resultado
        result_x = np.empty(max_points)
        result_y = np.empty(max_points)
        
        # Sempre inclui primeiro e último ponto
        result_x[0] = x[0]
        result_y[0] = y[0]
        result_x[max_points-1] = x[n-1]
        result_y[max_points-1] = y[n-1]
        
        # Calcula tamanho do bucket
        bucket_size = (n - 2) / (max_points - 2)
        
        # Último ponto selecionado (índice no array original)
        a = 0
        
        for i in range(1, max_points - 1):
            # Calcula limites do bucket atual
            avg_range_start = int((i - 1) * bucket_size) + 1
            avg_range_end = int(i * bucket_size) + 1
            
            # Calcula ponto médio do próximo bucket para referência
            next_avg_range_start = int(i * bucket_size) + 1
            next_avg_range_end = min(int((i + 1) * bucket_size) + 1, n)
            
            # Calcula centroide do próximo bucket
            avg_x = 0.0
            avg_y = 0.0
            avg_count = 0
            
            for j in range(next_avg_range_start, next_avg_range_end):
                avg_x += x[j]
                avg_y += y[j]
                avg_count += 1
            
            if avg_count > 0:
                avg_x /= avg_count
                avg_y /= avg_count
            else:
                avg_x = x[next_avg_range_start] if next_avg_range_start < n else x[n-1]
                avg_y = y[next_avg_range_start] if next_avg_range_start < n else y[n-1]
            
            # Encontra ponto no bucket atual que forma maior triângulo
            max_area = 0.0
            max_area_point = avg_range_start
            
            for j in range(avg_range_start, min(avg_range_end, n)):
                # Calcula área do triângulo formado por:
                # - último ponto selecionado (a)
                # - ponto atual (j)  
                # - centroide do próximo bucket (avg_x, avg_y)
                
                area = abs((x[a] - avg_x) * (y[j] - y[a]) - (x[a] - x[j]) * (avg_y - y[a]))
                
                if area > max_area:
                    max_area = area
                    max_area_point = j
            
            # Seleciona ponto com maior área
            result_x[i] = x[max_area_point]
            result_y[i] = y[max_area_point]
            a = max_area_point
        
        return result_x, result_y
    
    logger.info("lttb_numba_compiled")
    return _lttb_numba


# Initialize numba LTTB function
_lttb_numba = _create_lttb_numba()


def _detect_features(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Detecta features críticos (peaks, valleys, edges) para preservação.
    
    Returns:
        peaks_indices, valleys_indices, edges_indices
    """
    n = len(y)
    if n < 3:
        return np.array([]), np.array([]), np.array([])
    
    # Detecta peaks (máximos locais)
    peaks = []
    valleys = []
    edges = []
    
    # Calcula segunda derivada para detectar mudanças de curvatura  
    if n >= 5:
        dy = np.gradient(y)
        ddy = np.gradient(dy)
        
        # Detecta pontos de inflexão (edges)
        sign_changes = np.diff(np.sign(ddy))
        edges = np.where(np.abs(sign_changes) > 0)[0] + 1
    
    # Detecta peaks e valleys usando comparação local
    for i in range(1, n-1):
        if y[i] > y[i-1] and y[i] > y[i+1]:
            peaks.append(i)
        elif y[i] < y[i-1] and y[i] < y[i+1]:
            valleys.append(i)
    
    return np.array(peaks), np.array(valleys), np.array(edges)


def _downsample_lttb(
    x: np.ndarray, 
    y: np.ndarray, 
    max_points: int,
    preserve_features: List[Literal["peaks", "valleys", "edges"]] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Algoritmo LTTB com preservação de features conforme PRD seção 10.4
    
    Args:
        x: Array de timestamps
        y: Array de valores
        max_points: Número máximo de pontos para manter
        preserve_features: Lista de features para preservar
        
    Returns:
        Tuple com arrays downsampled (x_down, y_down)
    """
    n = len(x)
    
    if n <= max_points:
        logger.debug("lttb_no_downsampling_needed", n_points=n, max_points=max_points)
        return x, y
    
    preserve_features = preserve_features or ["peaks", "valleys", "edges"]
    
    # Detecta features importantes se solicitado
    critical_indices = set()
    
    if preserve_features:
        peaks, valleys, edges = _detect_features(x, y)
        
        if "peaks" in preserve_features:
            critical_indices.update(peaks)
        if "valleys" in preserve_features:
            critical_indices.update(valleys) 
        if "edges" in preserve_features:
            critical_indices.update(edges)
        
        logger.debug("features_detected", 
                    peaks=len(peaks), 
                    valleys=len(valleys), 
                    edges=len(edges),
                    total_critical=len(critical_indices))
    
    # Use Numba-optimized LTTB for large datasets
    if NUMBA_AVAILABLE and _lttb_numba is not None and n > 50000:
        logger.debug("using_numba_lttb", n_points=n, max_points=max_points)
        x_down, y_down = _lttb_numba(x, y, max_points)
    else:
        # Fallback to numpy implementation
        x_down, y_down = _lttb_numpy(x, y, max_points)
    
    # Se temos features críticos, força sua inclusão no resultado
    if critical_indices:
        # Combina pontos LTTB com features críticos
        lttb_indices = np.searchsorted(x, x_down)
        all_indices = np.unique(np.concatenate([lttb_indices, list(critical_indices)]))
        
        # Se excedeu max_points, remove pontos menos importantes
        if len(all_indices) > max_points:
            # Prioriza features críticos, depois pontos LTTB
            critical_array = np.array(list(critical_indices))
            lttb_only = np.setdiff1d(lttb_indices, critical_array)
            
            n_keep_lttb = max_points - len(critical_array)
            if n_keep_lttb > 0:
                keep_lttb = lttb_only[:n_keep_lttb]
                all_indices = np.unique(np.concatenate([critical_array, keep_lttb]))
            else:
                all_indices = critical_array[:max_points]
        
        all_indices = np.sort(all_indices)
        x_down = x[all_indices]
        y_down = y[all_indices]
        
        logger.debug("features_preserved", 
                    critical_preserved=len(critical_indices),
                    final_points=len(x_down))
    
    logger.debug("lttb_downsampling_complete",
                original_points=n,
                downsampled_points=len(x_down),
                reduction_ratio=len(x_down)/n)
    
    return x_down, y_down


def _lttb_numpy(x: np.ndarray, y: np.ndarray, max_points: int) -> Tuple[np.ndarray, np.ndarray]:
    """Pure numpy implementation of LTTB algorithm."""
    n = len(x)
    
    if max_points < 3:
        indices = np.linspace(0, n-1, max_points, dtype=int)
        return x[indices], y[indices]
    
    # Always include first and last point
    result_x = np.empty(max_points)
    result_y = np.empty(max_points)
    
    result_x[0] = x[0]
    result_y[0] = y[0]
    result_x[max_points-1] = x[n-1]
    result_y[max_points-1] = y[n-1]
    
    bucket_size = (n - 2) / (max_points - 2)
    a = 0  # Last selected point index
    
    for i in range(1, max_points - 1):
        # Calculate bucket boundaries
        avg_range_start = int((i - 1) * bucket_size) + 1
        avg_range_end = int(i * bucket_size) + 1
        
        # Calculate average point for next bucket
        next_avg_range_start = int(i * bucket_size) + 1
        next_avg_range_end = min(int((i + 1) * bucket_size) + 1, n)
        
        # Calculate centroid of next bucket
        if next_avg_range_end > next_avg_range_start:
            avg_x = np.mean(x[next_avg_range_start:next_avg_range_end])
            avg_y = np.mean(y[next_avg_range_start:next_avg_range_end])
        else:
            avg_x = x[next_avg_range_start] if next_avg_range_start < n else x[n-1]
            avg_y = y[next_avg_range_start] if next_avg_range_start < n else y[n-1]
        
        # Find point in current bucket that forms largest triangle
        max_area = 0.0
        max_area_point = avg_range_start
        
        bucket_end = min(avg_range_end, n)
        for j in range(avg_range_start, bucket_end):
            # Calculate triangle area
            area = abs((x[a] - avg_x) * (y[j] - y[a]) - (x[a] - x[j]) * (avg_y - y[a]))
            
            if area > max_area:
                max_area = area
                max_area_point = j
        
        result_x[i] = x[max_area_point] 
        result_y[i] = y[max_area_point]
        a = max_area_point
    
    return result_x, result_y


class BaseFigure(ABC):
    def __init__(self, config: PlotConfig):
        self.config = config

    @abstractmethod
    def render(self, data):
        raise NotImplementedError
    
    def _apply_downsampling(self, x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Aplica downsampling conforme configuração.
        
        Returns:
            Tuple com dados possivelmente reduzidos (x, y)
        """
        if not hasattr(self.config, 'downsample') or not self.config.downsample:
            return x, y
        
        downsample_config = self.config.downsample
        max_points = downsample_config.max_points
        
        if len(x) <= max_points:
            return x, y
            
        method = downsample_config.method
        preserve_features = downsample_config.preserve_features or []
        
        if method == "lttb":
            return _downsample_lttb(x, y, max_points, preserve_features)
        elif method == "minmax":
            # Implementação simplificada de min-max
            return self._downsample_minmax(x, y, max_points)
        elif method == "adaptive":
            # Implementação simplificada adaptativa
            return self._downsample_adaptive(x, y, max_points)
        else:
            logger.warning("unknown_downsample_method", method=method)
            return x, y
    
    def _downsample_minmax(self, x: np.ndarray, y: np.ndarray, max_points: int) -> Tuple[np.ndarray, np.ndarray]:
        """Simple min-max downsampling."""
        n = len(x)
        if n <= max_points:
            return x, y
            
        # Divide into buckets and take min/max from each bucket
        bucket_size = n // (max_points // 2)  # Each bucket contributes 2 points (min, max)
        
        result_indices = []
        for i in range(0, n, bucket_size):
            bucket_end = min(i + bucket_size, n)
            bucket_y = y[i:bucket_end]
            
            min_idx = i + np.argmin(bucket_y)
            max_idx = i + np.argmax(bucket_y)
            
            # Add both min and max indices
            if min_idx != max_idx:
                result_indices.extend(sorted([min_idx, max_idx]))
            else:
                result_indices.append(min_idx)
        
        # Limit to max_points
        result_indices = result_indices[:max_points]
        result_indices = np.unique(result_indices)
        
        return x[result_indices], y[result_indices]
    
    def _downsample_adaptive(self, x: np.ndarray, y: np.ndarray, max_points: int) -> Tuple[np.ndarray, np.ndarray]:
        """Adaptive downsampling based on local variance."""
        n = len(x)
        if n <= max_points:
            return x, y
        
        # Calculate local variance 
        window = max(3, n // max_points)
        variance = np.zeros(n)
        
        for i in range(n):
            start = max(0, i - window//2)
            end = min(n, i + window//2 + 1)
            variance[i] = np.var(y[start:end])
        
        # Select points with highest local variance
        high_variance_indices = np.argsort(variance)[-max_points:]
        high_variance_indices = np.sort(high_variance_indices)
        
        return x[high_variance_indices], y[high_variance_indices]
