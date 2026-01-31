from __future__ import annotations

from collections import OrderedDict
from functools import lru_cache
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from collections.abc import Callable


def memory_cache(maxsize: int = 128) -> Callable:
    """Decorator for in-memory LRU caching."""
    def decorator(func: Callable) -> Callable:
        return lru_cache(maxsize=maxsize)(func)

    return decorator


class MemoryCache:
    """In-memory LRU cache with configurable size."""

    def __init__(self, maxsize: int = 1000):
        """
        Initialize memory cache.

        Args:
            maxsize: Maximum number of items to cache
        """
        self._maxsize = maxsize
        self._cache: OrderedDict[str, Any] = OrderedDict()

    def get(self, key: str) -> Any | None:
        """Get item from cache, returns None if not found."""
        if key in self._cache:
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Set item in cache with LRU eviction."""
        if key in self._cache:
            self._cache.move_to_end(key)
            self._cache[key] = value
        else:
            if len(self._cache) >= self._maxsize:
                # Remove oldest item
                self._cache.popitem(last=False)
            self._cache[key] = value

    def delete(self, key: str) -> bool:
        """Delete item from cache, returns True if deleted."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all items from cache."""
        self._cache.clear()

    def __contains__(self, key: str) -> bool:
        """Check if key exists in cache."""
        return key in self._cache

    def __len__(self) -> int:
        """Return number of items in cache."""
        return len(self._cache)
