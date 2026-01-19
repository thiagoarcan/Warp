"""
DTW (Dynamic Time Warping) Plugin for Advanced Synchronization

Este plugin implementa DTW conforme PRD seção 8.2 como exemplo de plugin avançado.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any
import numpy as np

try:
    import scipy.spatial.distance
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

from platform_base.core.protocols import PluginProtocol, PluginContext, PluginResult
from platform_base.core.models import SyncResult, ResultMetadata, SeriesID
from platform_base.utils.errors import PluginError
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)

# Plugin metadata conforme PRD seção 14.3
PLUGIN_ID = "dtw_align"
VERSION = "1.0.0"


class DTWPlugin:
    """
    Plugin DTW para sincronização avançada conforme PRD seção 8.2
    
    Implementa Dynamic Time Warping para alinhamento de séries temporais
    com diferentes bases temporais ou velocidades de amostragem.
    """
    
    PLUGIN_ID: str = PLUGIN_ID
    VERSION: str = VERSION
    
    def get_manifest(self) -> Dict[str, Any]:
        """Retorna manifest do plugin conforme PRD seção 14.3"""
        return {
            "plugin_id": self.PLUGIN_ID,
            "version": self.VERSION,
            "core_min_version": "2.0.0",
            "core_max_version": None,
            "requires": ["numpy", "scipy"],
            "produces": ["sync_result"],
            "entry_point": "dtw_plugin.DTWPlugin",
            "description": "Dynamic Time Warping for advanced time series synchronization",
            "author": "Platform Base Team",
            "license": "MIT"
        }
    
    def validate_inputs(self, context: PluginContext) -> bool:
        """Valida inputs do plugin"""
        try:
            if not SCIPY_AVAILABLE:
                logger.error("dtw_plugin_scipy_missing", 
                           message="scipy required for DTW plugin")
                return False
            
            # Verifica se temos pelo menos 2 séries para sincronizar
            if len(context.get("series_data", {})) < 2:
                logger.error("dtw_plugin_insufficient_series",
                           n_series=len(context.get("series_data", {})))
                return False
            
            return True
            
        except Exception as e:
            logger.error("dtw_plugin_validation_failed", error=str(e))
            return False
    
    def execute(self, context: PluginContext, params: Dict[str, Any]) -> PluginResult:
        """
        Executa sincronização DTW
        
        Args:
            context: Contexto com dados das séries
            params: Parâmetros do DTW:
                - window_size: janela de busca DTW (opcional)
                - distance_metric: métrica de distância (default: euclidean)
                - step_pattern: padrão de passo (default: symmetric)
                
        Returns:
            PluginResult com resultado da sincronização
        """
        try:
            if not self.validate_inputs(context):
                raise PluginError("DTW plugin input validation failed", {})
            
            series_data = context["series_data"]  # Dict[SeriesID, np.ndarray]
            time_data = context["time_data"]      # Dict[SeriesID, np.ndarray]
            
            # Parâmetros DTW
            window_size = params.get("window_size")
            distance_metric = params.get("distance_metric", "euclidean")
            step_pattern = params.get("step_pattern", "symmetric")
            
            logger.info("dtw_sync_start", 
                       n_series=len(series_data),
                       window_size=window_size,
                       distance_metric=distance_metric)
            
            # Executa DTW entre todas as combinações de séries
            series_ids = list(series_data.keys())
            reference_id = series_ids[0]  # Use primeira série como referência
            
            # Warping paths para cada série
            warp_paths = {}
            aligned_series = {}
            
            # Alinha cada série com a referência
            for series_id in series_ids[1:]:
                ref_values = series_data[reference_id]
                target_values = series_data[series_id]
                
                # Executa DTW
                path, distance = self._compute_dtw(
                    ref_values, 
                    target_values,
                    window_size=window_size,
                    distance_metric=distance_metric
                )
                
                warp_paths[series_id] = {
                    "path": path,
                    "distance": distance
                }
                
                logger.debug("dtw_alignment_computed",
                           reference=reference_id,
                           target=series_id,
                           distance=distance,
                           path_length=len(path))
            
            # Constrói grade temporal comum baseada no warping
            t_common, synced_series = self._build_common_timeline(
                reference_id,
                series_data,
                time_data,
                warp_paths
            )
            
            # Calcula métricas de qualidade
            alignment_error = self._compute_alignment_error(warp_paths)
            confidence = self._compute_confidence(warp_paths, t_common)
            
            # Constrói resultado conforme interface SyncResult
            result = SyncResult(
                t_common=t_common,
                synced_series=synced_series,
                alignment_error=alignment_error,
                confidence=confidence,
                values=np.array([alignment_error]),  # DerivedResult requirement
                metadata=ResultMetadata(
                    method="dtw_align",
                    params=params,
                    version=self.VERSION,
                    timestamp=datetime.utcnow()
                )
            )
            
            logger.info("dtw_sync_complete",
                       alignment_error=alignment_error,
                       confidence=confidence,
                       n_common_points=len(t_common))
            
            return PluginResult(
                success=True,
                result=result,
                message="DTW synchronization completed successfully"
            )
            
        except Exception as e:
            error_msg = f"DTW plugin execution failed: {str(e)}"
            logger.error("dtw_plugin_execution_failed", error=str(e))
            return PluginResult(
                success=False,
                result=None,
                message=error_msg
            )
    
    def _compute_dtw(
        self, 
        x: np.ndarray, 
        y: np.ndarray,
        window_size: Optional[int] = None,
        distance_metric: str = "euclidean"
    ) -> tuple[np.ndarray, float]:
        """
        Computa DTW entre duas séries
        
        Returns:
            (warp_path, total_distance)
        """
        m, n = len(x), len(y)
        
        # Inicializa matriz de distâncias
        if window_size is None:
            window_size = max(m, n)  # Sem restrição de janela
        
        # Matriz de distâncias cumulativas
        dtw_matrix = np.full((m + 1, n + 1), np.inf)
        dtw_matrix[0, 0] = 0
        
        # Preenche matriz DTW com restrição de janela
        for i in range(1, m + 1):
            # Calcula limites da janela
            j_start = max(1, i - window_size)
            j_end = min(n + 1, i + window_size + 1)
            
            for j in range(j_start, j_end):
                # Calcula distância local
                if distance_metric == "euclidean":
                    cost = (x[i-1] - y[j-1]) ** 2
                elif distance_metric == "manhattan":
                    cost = abs(x[i-1] - y[j-1])
                elif distance_metric == "cosine":
                    # Usa scipy se disponível
                    if SCIPY_AVAILABLE:
                        cost = scipy.spatial.distance.cosine([x[i-1]], [y[j-1]])
                    else:
                        cost = (x[i-1] - y[j-1]) ** 2  # fallback
                else:
                    cost = (x[i-1] - y[j-1]) ** 2  # fallback
                
                # Atualiza matriz com menor custo cumulativo
                dtw_matrix[i, j] = cost + min(
                    dtw_matrix[i-1, j],      # inserção
                    dtw_matrix[i, j-1],      # deleção  
                    dtw_matrix[i-1, j-1]     # matching
                )
        
        # Backtracking para encontrar caminho ótimo
        path = []
        i, j = m, n
        
        while i > 0 or j > 0:
            path.append((i-1, j-1))
            
            if i == 0:
                j -= 1
            elif j == 0:
                i -= 1
            else:
                # Escolhe direção de menor custo
                costs = [
                    dtw_matrix[i-1, j-1],   # diagonal
                    dtw_matrix[i-1, j],     # vertical
                    dtw_matrix[i, j-1]      # horizontal
                ]
                min_idx = np.argmin(costs)
                
                if min_idx == 0:    # diagonal
                    i -= 1
                    j -= 1
                elif min_idx == 1:  # vertical
                    i -= 1
                else:               # horizontal
                    j -= 1
        
        path.reverse()
        total_distance = dtw_matrix[m, n]
        
        return np.array(path), total_distance
    
    def _build_common_timeline(
        self,
        reference_id: SeriesID,
        series_data: Dict[SeriesID, np.ndarray],
        time_data: Dict[SeriesID, np.ndarray],
        warp_paths: Dict[SeriesID, Dict[str, Any]]
    ) -> tuple[np.ndarray, Dict[SeriesID, np.ndarray]]:
        """
        Constrói timeline comum e séries alinhadas baseado no warping DTW
        """
        # Use timeline da série de referência como base
        t_common = time_data[reference_id].copy()
        synced_series = {reference_id: series_data[reference_id].copy()}
        
        # Alinha outras séries usando warp paths
        for series_id, warp_info in warp_paths.items():
            path = warp_info["path"]
            
            # Interpola série alinhada baseado no warp path
            ref_indices = path[:, 0]
            target_indices = path[:, 1]
            
            # Cria série alinhada interpolando valores
            aligned_values = np.interp(
                range(len(t_common)),
                ref_indices, 
                series_data[series_id][target_indices]
            )
            
            synced_series[series_id] = aligned_values
        
        return t_common, synced_series
    
    def _compute_alignment_error(self, warp_paths: Dict[SeriesID, Dict[str, Any]]) -> float:
        """Computa erro médio de alinhamento"""
        if not warp_paths:
            return 0.0
        
        total_distance = sum(info["distance"] for info in warp_paths.values())
        return total_distance / len(warp_paths)
    
    def _compute_confidence(
        self, 
        warp_paths: Dict[SeriesID, Dict[str, Any]], 
        t_common: np.ndarray
    ) -> float:
        """
        Computa confiança do alinhamento baseado na consistência dos warp paths
        """
        if not warp_paths:
            return 1.0
        
        # Confiança inversamente relacionada ao erro de alinhamento
        avg_error = self._compute_alignment_error(warp_paths)
        
        # Normaliza erro pelo comprimento da série
        normalized_error = avg_error / len(t_common) if len(t_common) > 0 else avg_error
        
        # Confiança entre 0 e 1 (maior = melhor)
        confidence = np.exp(-normalized_error)
        
        return float(np.clip(confidence, 0.0, 1.0))


# Factory function for plugin registration
def create_plugin() -> DTWPlugin:
    """Factory function para criação do plugin"""
    return DTWPlugin()
