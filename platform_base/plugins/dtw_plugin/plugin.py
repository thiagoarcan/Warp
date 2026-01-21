"""
DTW (Dynamic Time Warping) Plugin for Platform Base

This plugin provides Dynamic Time Warping functionality for temporal signal
alignment and similarity measurement. DTW is particularly useful for:

- Comparing time series with different sampling rates
- Finding optimal alignment between temporal signals  
- Measuring similarity between sequences of different lengths
- Temporal pattern matching and recognition

Features:
- Standard DTW distance calculation
- Constrained DTW with Sakoe-Chiba band
- Warping path visualization
- Batch DTW processing for multiple series
- Performance optimization for large datasets
"""

from __future__ import annotations

import time
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from dataclasses import dataclass

# Import scipy for DTW optimization
try:
    from scipy.spatial.distance import euclidean
    from scipy.optimize import minimize_scalar
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

# Import matplotlib for visualization
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Plugin protocol interface (would be imported from platform_base.core.protocols)
class PluginProtocol:
    """Base protocol that all plugins must implement"""
    
    @property
    def name(self) -> str:
        raise NotImplementedError
    
    @property
    def version(self) -> str:
        raise NotImplementedError
    
    @property
    def description(self) -> str:
        raise NotImplementedError
    
    def initialize(self) -> None:
        """Initialize plugin resources"""
        pass
    
    def cleanup(self) -> None:
        """Cleanup plugin resources"""
        pass


@dataclass
class DTWResult:
    """Result of DTW analysis"""
    distance: float
    path: List[Tuple[int, int]]
    cost_matrix: np.ndarray
    normalized_distance: Optional[float] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class DTWConfig:
    """Configuration for DTW analysis"""
    window_size: Optional[int] = None  # Sakoe-Chiba band constraint
    distance_metric: str = 'euclidean'  # euclidean, manhattan, cosine
    normalize_distance: bool = True
    return_path: bool = True
    return_cost_matrix: bool = False
    step_pattern: str = 'symmetric'  # symmetric, asymmetric
    

class DTWPlugin(PluginProtocol):
    """Dynamic Time Warping plugin implementation"""
    
    def __init__(self):
        self._name = "dtw_plugin"
        self._version = "1.0.0"
        self._description = "Dynamic Time Warping analysis for temporal signal alignment"
        self._initialized = False
        
        # Plugin state
        self.execution_count = 0
        self.total_execution_time = 0.0
        self.last_results: List[DTWResult] = []
        
        # Cache for repeated computations
        self._distance_cache = {}
        self._max_cache_size = 100
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def version(self) -> str:
        return self._version
    
    @property
    def description(self) -> str:
        return self._description
    
    def initialize(self) -> None:
        """Initialize DTW plugin"""
        if self._initialized:
            return
        
        # Validate dependencies
        if not SCIPY_AVAILABLE:
            print("Warning: SciPy not available, using basic implementations")
        
        if not MATPLOTLIB_AVAILABLE:
            print("Warning: Matplotlib not available, visualization disabled")
        
        self._initialized = True
        print(f"DTW Plugin v{self.version} initialized successfully")
    
    def cleanup(self) -> None:
        """Cleanup plugin resources"""
        self._distance_cache.clear()
        self.last_results.clear()
        self._initialized = False
        print("DTW Plugin cleaned up")
    
    def compute_dtw_distance(self, 
                           series1: np.ndarray,
                           series2: np.ndarray,
                           config: Optional[DTWConfig] = None) -> DTWResult:
        """
        Compute DTW distance between two time series
        
        Args:
            series1: First time series
            series2: Second time series  
            config: DTW configuration parameters
            
        Returns:
            DTWResult with distance and optional path/cost matrix
        """
        start_time = time.perf_counter()
        
        if config is None:
            config = DTWConfig()
        
        # Validate inputs
        if len(series1) == 0 or len(series2) == 0:
            raise ValueError("Input series cannot be empty")
        
        # Convert to numpy arrays
        s1 = np.asarray(series1, dtype=np.float64)
        s2 = np.asarray(series2, dtype=np.float64)
        
        # Reshape to 2D if needed (for multivariate series)
        if s1.ndim == 1:
            s1 = s1.reshape(-1, 1)
        if s2.ndim == 1:
            s2 = s2.reshape(-1, 1)
        
        # Check cache
        cache_key = self._get_cache_key(s1, s2, config)
        if cache_key in self._distance_cache:
            cached_result = self._distance_cache[cache_key]
            cached_result.execution_time = time.perf_counter() - start_time
            return cached_result
        
        # Compute DTW
        if config.window_size is not None:
            result = self._dtw_constrained(s1, s2, config)
        else:
            result = self._dtw_unconstrained(s1, s2, config)
        
        # Calculate execution time
        execution_time = time.perf_counter() - start_time
        result.execution_time = execution_time
        
        # Update statistics
        self.execution_count += 1
        self.total_execution_time += execution_time
        
        # Cache result
        self._cache_result(cache_key, result)
        
        # Store for history
        self.last_results.append(result)
        if len(self.last_results) > 10:  # Keep only last 10 results
            self.last_results = self.last_results[-10:]
        
        return result
    
    def _dtw_unconstrained(self, s1: np.ndarray, s2: np.ndarray, config: DTWConfig) -> DTWResult:
        """Compute unconstrained DTW"""
        n, m = len(s1), len(s2)
        
        # Initialize cost matrix
        cost_matrix = np.full((n + 1, m + 1), np.inf)
        cost_matrix[0, 0] = 0
        
        # Fill cost matrix
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                # Compute distance between points
                dist = self._point_distance(s1[i-1], s2[j-1], config.distance_metric)
                
                # DTW step patterns
                if config.step_pattern == 'symmetric':
                    cost_matrix[i, j] = dist + min(
                        cost_matrix[i-1, j],     # insertion
                        cost_matrix[i, j-1],     # deletion  
                        cost_matrix[i-1, j-1]    # match
                    )
                elif config.step_pattern == 'asymmetric':
                    cost_matrix[i, j] = dist + min(
                        cost_matrix[i-1, j] + dist,      # insertion with penalty
                        cost_matrix[i, j-1],             # deletion
                        cost_matrix[i-1, j-1]            # match
                    )
        
        # Extract final distance
        distance = cost_matrix[n, m]
        
        # Normalize distance if requested
        normalized_distance = None
        if config.normalize_distance:
            path_length = n + m  # Approximate path length
            normalized_distance = distance / path_length
        
        # Extract warping path if requested
        path = []
        if config.return_path:
            path = self._extract_path(cost_matrix)
        
        # Prepare cost matrix for return
        return_cost_matrix = cost_matrix[1:, 1:] if config.return_cost_matrix else None
        
        return DTWResult(
            distance=distance,
            path=path,
            cost_matrix=return_cost_matrix,
            normalized_distance=normalized_distance,
            metadata={
                'series1_length': n,
                'series2_length': m,
                'step_pattern': config.step_pattern,
                'distance_metric': config.distance_metric,
                'constrained': False
            }
        )
    
    def _dtw_constrained(self, s1: np.ndarray, s2: np.ndarray, config: DTWConfig) -> DTWResult:
        """Compute DTW with Sakoe-Chiba band constraint"""
        n, m = len(s1), len(s2)
        window = config.window_size
        
        # Initialize cost matrix
        cost_matrix = np.full((n + 1, m + 1), np.inf)
        cost_matrix[0, 0] = 0
        
        # Fill cost matrix with window constraint
        for i in range(1, n + 1):
            # Calculate window bounds
            j_start = max(1, i - window)
            j_end = min(m + 1, i + window + 1)
            
            for j in range(j_start, j_end):
                # Compute distance between points
                dist = self._point_distance(s1[i-1], s2[j-1], config.distance_metric)
                
                # DTW recurrence with constraint
                cost_matrix[i, j] = dist + min(
                    cost_matrix[i-1, j] if j > i - window else np.inf,
                    cost_matrix[i, j-1] if j < i + window else np.inf,
                    cost_matrix[i-1, j-1]
                )
        
        # Extract results similar to unconstrained
        distance = cost_matrix[n, m]
        
        normalized_distance = None
        if config.normalize_distance:
            path_length = n + m
            normalized_distance = distance / path_length
        
        path = []
        if config.return_path:
            path = self._extract_path(cost_matrix)
        
        return_cost_matrix = cost_matrix[1:, 1:] if config.return_cost_matrix else None
        
        return DTWResult(
            distance=distance,
            path=path,
            cost_matrix=return_cost_matrix,
            normalized_distance=normalized_distance,
            metadata={
                'series1_length': n,
                'series2_length': m,
                'step_pattern': config.step_pattern,
                'distance_metric': config.distance_metric,
                'constrained': True,
                'window_size': window
            }
        )
    
    def _point_distance(self, p1: np.ndarray, p2: np.ndarray, metric: str) -> float:
        """Compute distance between two points"""
        if metric == 'euclidean':
            if SCIPY_AVAILABLE:
                return euclidean(p1, p2)
            else:
                return np.sqrt(np.sum((p1 - p2) ** 2))
        elif metric == 'manhattan':
            return np.sum(np.abs(p1 - p2))
        elif metric == 'cosine':
            norm1, norm2 = np.linalg.norm(p1), np.linalg.norm(p2)
            if norm1 == 0 or norm2 == 0:
                return 1.0
            return 1.0 - np.dot(p1, p2) / (norm1 * norm2)
        else:
            raise ValueError(f"Unknown distance metric: {metric}")
    
    def _extract_path(self, cost_matrix: np.ndarray) -> List[Tuple[int, int]]:
        """Extract optimal warping path from cost matrix"""
        n, m = cost_matrix.shape
        i, j = n - 1, m - 1
        path = [(i-1, j-1)]  # Convert to 0-based indexing
        
        while i > 1 or j > 1:
            if i == 1:
                j -= 1
            elif j == 1:
                i -= 1
            else:
                # Find minimum of three predecessors
                move_cost = [
                    cost_matrix[i-1, j-1],  # diagonal
                    cost_matrix[i-1, j],    # up
                    cost_matrix[i, j-1]     # left
                ]
                move = np.argmin(move_cost)
                
                if move == 0:      # diagonal
                    i, j = i-1, j-1
                elif move == 1:    # up
                    i = i-1
                else:              # left
                    j = j-1
            
            path.append((i-1, j-1))  # Convert to 0-based indexing
        
        return path[::-1]  # Reverse to start from beginning
    
    def _get_cache_key(self, s1: np.ndarray, s2: np.ndarray, config: DTWConfig) -> str:
        """Generate cache key for DTW computation"""
        s1_hash = hash(s1.data.tobytes())
        s2_hash = hash(s2.data.tobytes()) 
        config_hash = hash((
            config.window_size,
            config.distance_metric,
            config.normalize_distance,
            config.step_pattern
        ))
        return f"{s1_hash}_{s2_hash}_{config_hash}"
    
    def _cache_result(self, key: str, result: DTWResult):
        """Cache DTW result"""
        if len(self._distance_cache) >= self._max_cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self._distance_cache))
            del self._distance_cache[oldest_key]
        
        self._distance_cache[key] = result
    
    def compute_dtw_batch(self, 
                         series_list: List[np.ndarray],
                         config: Optional[DTWConfig] = None) -> np.ndarray:
        """
        Compute pairwise DTW distances for a list of series
        
        Args:
            series_list: List of time series
            config: DTW configuration
            
        Returns:
            Distance matrix (n x n)
        """
        n = len(series_list)
        distance_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i + 1, n):
                result = self.compute_dtw_distance(series_list[i], series_list[j], config)
                distance = result.normalized_distance if result.normalized_distance is not None else result.distance
                distance_matrix[i, j] = distance
                distance_matrix[j, i] = distance  # Symmetric
        
        return distance_matrix
    
    def visualize_dtw_alignment(self, 
                              series1: np.ndarray,
                              series2: np.ndarray, 
                              result: DTWResult,
                              title: str = "DTW Alignment") -> Optional[Any]:
        """
        Visualize DTW alignment between two series
        
        Args:
            series1: First time series
            series2: Second time series
            result: DTW result with path
            title: Plot title
            
        Returns:
            Matplotlib figure or None if matplotlib not available
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available for visualization")
            return None
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
        
        # Plot original series
        ax1.plot(series1, 'b-', label='Series 1', linewidth=2)
        ax1.plot(series2, 'r-', label='Series 2', linewidth=2)
        ax1.set_title('Original Time Series')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot alignment connections
        ax2.plot(series1, 'b-', label='Series 1', linewidth=2)
        ax2.plot(series2, 'r-', label='Series 2', linewidth=2)
        
        # Draw alignment lines
        if result.path:
            for i, j in result.path[::max(1, len(result.path)//50)]:  # Sample path for visibility
                if i < len(series1) and j < len(series2):
                    ax2.plot([i, j], [series1[i], series2[j]], 'g-', alpha=0.3, linewidth=0.5)
        
        ax2.set_title(f'DTW Alignment (Distance: {result.distance:.2f})')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot cost matrix if available
        if result.cost_matrix is not None:
            im = ax3.imshow(result.cost_matrix.T, cmap='viridis', aspect='auto', origin='lower')
            
            # Plot optimal path
            if result.path:
                path_i, path_j = zip(*result.path)
                ax3.plot(path_i, path_j, 'r-', linewidth=2, label='Optimal Path')
            
            ax3.set_title('DTW Cost Matrix')
            ax3.set_xlabel('Series 1 Index')
            ax3.set_ylabel('Series 2 Index')
            plt.colorbar(im, ax=ax3, label='Cumulative Cost')
        
        plt.tight_layout()
        return fig
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get plugin execution statistics"""
        avg_time = self.total_execution_time / max(1, self.execution_count)
        
        return {
            'plugin_name': self.name,
            'version': self.version,
            'execution_count': self.execution_count,
            'total_execution_time': self.total_execution_time,
            'average_execution_time': avg_time,
            'cache_size': len(self._distance_cache),
            'last_results_count': len(self.last_results),
            'scipy_available': SCIPY_AVAILABLE,
            'matplotlib_available': MATPLOTLIB_AVAILABLE
        }


# Plugin factory function (optional)
def create_plugin() -> DTWPlugin:
    """Factory function to create plugin instance"""
    return DTWPlugin()


# Example usage and testing functions
def example_usage():
    """Example usage of the DTW plugin"""
    # Create plugin instance
    plugin = DTWPlugin()
    plugin.initialize()
    
    try:
        # Generate example time series
        t1 = np.linspace(0, 4*np.pi, 100)
        t2 = np.linspace(0, 4*np.pi, 120)  # Different length
        
        series1 = np.sin(t1) + 0.1 * np.random.randn(len(t1))
        series2 = np.sin(t2 + 0.5) + 0.1 * np.random.randn(len(t2))  # Phase shifted
        
        # Configure DTW
        config = DTWConfig(
            window_size=20,
            distance_metric='euclidean',
            normalize_distance=True,
            return_path=True,
            return_cost_matrix=True
        )
        
        # Compute DTW
        print("Computing DTW distance...")
        result = plugin.compute_dtw_distance(series1, series2, config)
        
        print(f"DTW Distance: {result.distance:.4f}")
        print(f"Normalized Distance: {result.normalized_distance:.4f}")
        print(f"Execution Time: {result.execution_time:.4f}s")
        print(f"Path Length: {len(result.path)}")
        
        # Batch processing example
        print("\\nTesting batch processing...")
        series_list = [series1, series2, np.cos(t1), np.cos(t2)]
        distance_matrix = plugin.compute_dtw_batch(series_list, config)
        print(f"Distance Matrix Shape: {distance_matrix.shape}")
        
        # Visualization example
        if MATPLOTLIB_AVAILABLE:
            print("\\nCreating visualization...")
            fig = plugin.visualize_dtw_alignment(series1, series2, result)
            if fig:
                print("Visualization created successfully")
        
        # Statistics
        stats = plugin.get_statistics()
        print(f"\\nPlugin Statistics: {stats}")
        
    finally:
        plugin.cleanup()


if __name__ == "__main__":
    example_usage()