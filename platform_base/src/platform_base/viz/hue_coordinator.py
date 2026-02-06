"""
Hue Coordinator - Manages consistent color assignment across visualization contexts
Original implementation for Platform Base v2.0
"""

from typing import Dict, List, Optional, Tuple


class HueCoordinator:
    """Ensures consistent color mapping for data series across multiple visualization contexts"""
    
    def __init__(self):
        self._series_hue_registry: Dict[str, str] = {}
        self._hue_pool = self._generate_distinct_hues()
        self._next_hue_idx = 0
        self._reserved_hues: set = set()
        
    def _generate_distinct_hues(self) -> List[str]:
        """Generate visually distinct color palette using HSL color space"""
        palette = [
            "#2E86DE", "#EE5A6F", "#10AC84", "#F79F1F", "#5F27CD",
            "#00D2D3", "#FF6348", "#1DD1A1", "#FFC312", "#C44569",
            "#54A0FF", "#48DBFB", "#FF9FF3", "#FECA57", "#00D8D6",
            "#576574", "#222F3E", "#2C3A47", "#CAD3C8", "#6AB04C",
        ]
        return palette
        
    def assign_hue_to_series(self, series_identifier: str) -> str:
        """
        Assign or retrieve consistent hue for a series
        
        Args:
            series_identifier: Unique identifier for data series
            
        Returns:
            Hex color code
        """
        if series_identifier in self._series_hue_registry:
            return self._series_hue_registry[series_identifier]
            
        # Find next available hue
        available_hues = [h for h in self._hue_pool if h not in self._reserved_hues]
        
        if not available_hues:
            # Generate deterministic color from hash if pool exhausted
            # Use built-in hash for better performance and no security concerns
            hash_val = hash(series_identifier) & 0xFFFFFF  # 24-bit color
            r = (hash_val >> 16) & 0xFF
            g = (hash_val >> 8) & 0xFF
            b = hash_val & 0xFF
            hue_code = f"#{r:02X}{g:02X}{b:02X}"
        else:
            hue_code = available_hues[self._next_hue_idx % len(available_hues)]
            self._next_hue_idx += 1
            self._reserved_hues.add(hue_code)
            
        self._series_hue_registry[series_identifier] = hue_code
        return hue_code
        
    def release_series_hue(self, series_identifier: str):
        """Release color assignment when series is removed"""
        if series_identifier in self._series_hue_registry:
            hue = self._series_hue_registry[series_identifier]
            self._reserved_hues.discard(hue)
            del self._series_hue_registry[series_identifier]
            
    def get_hue_for_series(self, series_identifier: str) -> Optional[str]:
        """Retrieve assigned hue without creating new assignment"""
        return self._series_hue_registry.get(series_identifier)
        
    def clear_registry(self):
        """Reset all color assignments"""
        self._series_hue_registry.clear()
        self._reserved_hues.clear()
        self._next_hue_idx = 0


_global_hue_coordinator = None


def get_hue_coordinator() -> HueCoordinator:
    """Get or create global hue coordinator instance"""
    global _global_hue_coordinator
    if _global_hue_coordinator is None:
        _global_hue_coordinator = HueCoordinator()
    return _global_hue_coordinator
