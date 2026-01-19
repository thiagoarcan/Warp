from __future__ import annotations

from functools import lru_cache
from typing import Callable


def memory_cache(maxsize: int = 128) -> Callable:
    """Decorator for in-memory LRU caching."""
    def decorator(func: Callable) -> Callable:
        return lru_cache(maxsize=maxsize)(func)

    return decorator
