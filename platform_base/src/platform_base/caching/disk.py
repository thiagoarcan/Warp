from __future__ import annotations

import hashlib
import pickle
import time
from collections import OrderedDict
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

from joblib import Memory

from platform_base.utils.errors import CacheError, handle_error
from platform_base.utils.logging import get_logger


if TYPE_CHECKING:
    from collections.abc import Callable


logger = get_logger(__name__)


class DiskCache:
    """
    Disk cache with joblib.Memory integration, TTL, and LRU cleanup.

    Features:
    - Integração com joblib.Memory para caching de funções
    - TTL configurável via timestamp
    - Limite de tamanho com LRU cleanup
    - Persistência no path configurado
    - Métodos: get, set, clear, cleanup
    - Logging estruturado de operações
    """

    def __init__(
        self,
        location: str | Path,
        ttl_seconds: int | None = None,
        max_size_bytes: int | None = None,
    ):
        """
        Initialize disk cache.

        Args:
            location: Directory path for cache storage
            ttl_seconds: Time-to-live in seconds (None for no expiration)
            max_size_bytes: Maximum cache size in bytes (None for no limit)
        """
        self.location = Path(location)
        self.location.mkdir(parents=True, exist_ok=True)
        self._ttl_seconds = ttl_seconds
        self._max_size_bytes = max_size_bytes

        # joblib.Memory for function caching
        self._memory = Memory(location=str(self.location), verbose=0)

        # TTL timestamp file
        self._stamp_file = self.location / ".ttl"

        # LRU tracking file
        self._lru_file = self.location / ".lru"

        # Initialize LRU order
        self._lru_order: OrderedDict[str, float] = self._load_lru_order()

        logger.info(
            "disk_cache_initialized",
            location=str(self.location),
            ttl_seconds=ttl_seconds,
            max_size_bytes=max_size_bytes,
        )

    def _load_lru_order(self) -> OrderedDict[str, float]:
        """Load LRU order from persistent file."""
        try:
            if self._lru_file.exists():
                with open(self._lru_file, "rb") as f:
                    return pickle.load(f)
        except Exception as e:
            logger.warning(
                "lru_order_load_failed",
                error=str(e),
                lru_file=str(self._lru_file),
            )
        return OrderedDict()

    def _save_lru_order(self) -> None:
        """Save LRU order to persistent file."""
        try:
            with open(self._lru_file, "wb") as f:
                pickle.dump(self._lru_order, f)
        except Exception as e:
            logger.warning(
                "lru_order_save_failed",
                error=str(e),
                lru_file=str(self._lru_file),
            )

    def _get_cache_key(self, key: str) -> str:
        """Generate cache key hash."""
        return hashlib.md5(key.encode()).hexdigest()

    def _get_file_path(self, cache_key: str) -> Path:
        """Get file path for cache key."""
        return self.location / f"{cache_key}.cache"

    def _expired(self) -> bool:
        """Check if entire cache is expired based on TTL."""
        if self._ttl_seconds is None:
            return False
        if not self._stamp_file.exists():
            return True
        try:
            stamp = datetime.fromisoformat(self._stamp_file.read_text(encoding="utf-8"))
            # Make stamp timezone-aware if it isn't
            if stamp.tzinfo is None:
                stamp = stamp.replace(tzinfo=UTC)
            return datetime.now(UTC) - stamp > timedelta(seconds=self._ttl_seconds)
        except Exception as e:
            logger.warning("ttl_check_failed", error=str(e))
            return True

    def _touch(self) -> None:
        """Update TTL timestamp."""
        try:
            self._stamp_file.write_text(datetime.now(UTC).isoformat(), encoding="utf-8")
        except Exception as e:
            logger.warning("ttl_touch_failed", error=str(e))

    def _get_cache_size(self) -> int:
        """Get total cache size in bytes."""
        total_size = 0
        try:
            for file_path in self.location.glob("*.cache"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception as e:
            logger.warning("cache_size_calculation_failed", error=str(e))
        return total_size

    def _enforce_size_limit(self) -> None:
        """Enforce cache size limit using LRU eviction."""
        if self._max_size_bytes is None:
            return

        current_size = self._get_cache_size()
        if current_size <= self._max_size_bytes:
            return

        logger.info(
            "cache_size_limit_exceeded",
            current_size=current_size,
            max_size=self._max_size_bytes,
        )

        # Sort by access time (oldest first)
        sorted_items = sorted(self._lru_order.items(), key=lambda x: x[1])

        # Get most recently added item to protect it
        most_recent_key = sorted_items[-1][0] if sorted_items else None

        for cache_key, _ in sorted_items:
            # Skip the most recently added item
            if cache_key == most_recent_key:
                continue
            file_path = self._get_file_path(cache_key)
            if file_path.exists():
                try:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    del self._lru_order[cache_key]
                    current_size -= file_size

                    logger.debug(
                        "cache_file_evicted",
                        cache_key=cache_key,
                        file_size=file_size,
                        remaining_size=current_size,
                    )

                    if current_size <= self._max_size_bytes:
                        break
                except Exception as e:
                    logger.warning(
                        "cache_eviction_failed",
                        cache_key=cache_key,
                        error=str(e),
                    )

        self._save_lru_order()

        logger.info(
            "cache_size_enforcement_completed",
            final_size=current_size,
            max_size=self._max_size_bytes,
        )

    def get(self, key: str) -> Any | None:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if self._expired():
            logger.debug("cache_expired_on_get", key=key)
            self.clear()
            return None

        cache_key = self._get_cache_key(key)
        file_path = self._get_file_path(cache_key)

        try:
            if not file_path.exists():
                logger.debug("cache_miss", key=key, cache_key=cache_key)
                return None

            with open(file_path, "rb") as f:
                value = pickle.load(f)

            # Update LRU order
            self._lru_order[cache_key] = time.time()
            self._lru_order.move_to_end(cache_key)
            self._save_lru_order()

            logger.debug("cache_hit", key=key, cache_key=cache_key)
            return value

        except Exception as e:
            error = CacheError(
                f"Failed to get cache value for key: {key}",
                context={"key": key, "cache_key": cache_key, "error": str(e)},
            )
            handle_error(error)
            return None

    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        cache_key = self._get_cache_key(key)
        file_path = self._get_file_path(cache_key)

        try:
            with open(file_path, "wb") as f:
                pickle.dump(value, f)

            # Update LRU order
            self._lru_order[cache_key] = time.time()
            self._lru_order.move_to_end(cache_key)
            self._save_lru_order()

            # Update TTL
            if self._ttl_seconds is not None:
                self._touch()

            # Enforce size limit
            self._enforce_size_limit()

            logger.debug(
                "cache_set",
                key=key,
                cache_key=cache_key,
                file_size=file_path.stat().st_size,
            )

        except Exception as e:
            error = CacheError(
                f"Failed to set cache value for key: {key}",
                context={"key": key, "cache_key": cache_key, "error": str(e)},
            )
            handle_error(error)

    def clear(self) -> None:
        """Clear entire cache."""
        try:
            # Clear joblib cache
            self._memory.clear(warn=False)

            # Clear manual cache files
            for file_path in self.location.glob("*.cache"):
                try:
                    file_path.unlink()
                except Exception as e:
                    logger.warning(
                        "cache_file_deletion_failed",
                        file_path=str(file_path),
                        error=str(e),
                    )

            # Clear LRU order
            self._lru_order.clear()
            self._save_lru_order()

            # Clear TTL stamp
            if self._stamp_file.exists():
                try:
                    self._stamp_file.unlink()
                except Exception as e:
                    logger.warning("ttl_stamp_deletion_failed", error=str(e))

            logger.info("cache_cleared", location=str(self.location))

        except Exception as e:
            error = CacheError(
                "Failed to clear cache",
                context={"location": str(self.location), "error": str(e)},
            )
            handle_error(error)

    def cleanup(self) -> None:
        """
        Clean up expired entries and enforce size limits.

        This method is called automatically but can be invoked manually
        for maintenance.
        """
        try:
            if self._expired():
                logger.info("cache_cleanup_ttl_expired")
                self.clear()
                return

            # Clean up orphaned files (not in LRU order)
            cache_files = {f.stem for f in self.location.glob("*.cache")}
            lru_keys = set(self._lru_order.keys())
            orphaned = cache_files - lru_keys

            for orphaned_key in orphaned:
                orphaned_file = self._get_file_path(orphaned_key)
                try:
                    orphaned_file.unlink()
                    logger.debug("orphaned_cache_file_removed", cache_key=orphaned_key)
                except Exception as e:
                    logger.warning(
                        "orphaned_file_removal_failed",
                        cache_key=orphaned_key,
                        error=str(e),
                    )

            # Remove LRU entries for non-existent files
            missing_keys = lru_keys - cache_files
            for missing_key in missing_keys:
                del self._lru_order[missing_key]

            if missing_keys:
                self._save_lru_order()
                logger.debug("lru_order_cleaned", removed_count=len(missing_keys))

            # Enforce size limit
            self._enforce_size_limit()

            cache_size = self._get_cache_size()
            cache_count = len(list(self.location.glob("*.cache")))

            logger.info(
                "cache_cleanup_completed",
                cache_size=cache_size,
                cache_count=cache_count,
                orphaned_removed=len(orphaned),
                missing_removed=len(missing_keys),
            )

        except Exception as e:
            error = CacheError(
                "Cache cleanup failed",
                context={"location": str(self.location), "error": str(e)},
            )
            handle_error(error)

    def cache_function(self, func: Callable) -> Callable:
        """
        Decorator for caching function results using joblib.Memory.

        Args:
            func: Function to cache

        Returns:
            Wrapped function with caching
        """
        try:
            cached = self._memory.cache(func)

            def wrapper(*args, **kwargs):
                if self._expired():
                    logger.debug("cache_function_ttl_expired", func_name=func.__name__)
                    self.clear()

                result = cached(*args, **kwargs)

                if self._ttl_seconds is not None:
                    self._touch()

                # Periodic cleanup (every 100 calls)
                if hasattr(wrapper, "_call_count"):
                    wrapper._call_count += 1
                else:
                    wrapper._call_count = 1

                if wrapper._call_count % 100 == 0:
                    self.cleanup()

                return result

            wrapper.__wrapped__ = func
            wrapper.__name__ = getattr(func, "__name__", "unknown")

            logger.debug(
                "function_cached",
                func_name=func.__name__,
                location=str(self.location),
            )

            return wrapper

        except Exception as e:
            error = CacheError(
                f"Failed to cache function: {func.__name__}",
                context={"func_name": func.__name__, "error": str(e)},
            )
            handle_error(error)
            return func

    def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        try:
            cache_size = self._get_cache_size()
            cache_count = len(list(self.location.glob("*.cache")))

            stats = {
                "location": str(self.location),
                "ttl_seconds": self._ttl_seconds,
                "max_size_bytes": self._max_size_bytes,
                "current_size_bytes": cache_size,
                "entry_count": cache_count,
                "lru_entries": len(self._lru_order),
                "expired": self._expired(),
            }

            if self._ttl_seconds is not None and self._stamp_file.exists():
                try:
                    stamp = datetime.fromisoformat(self._stamp_file.read_text())
                    # Make stamp timezone-aware if it isn't
                    if stamp.tzinfo is None:
                        stamp = stamp.replace(tzinfo=UTC)
                    stats["last_updated"] = stamp.isoformat()
                    stats["time_to_expiry"] = max(0, self._ttl_seconds - (datetime.now(UTC) - stamp).total_seconds())
                except Exception:
                    stats["last_updated"] = None
                    stats["time_to_expiry"] = None
            else:
                stats["last_updated"] = None
                stats["time_to_expiry"] = None

            return stats

        except Exception as e:
            error = CacheError(
                "Failed to get cache statistics",
                context={"location": str(self.location), "error": str(e)},
            )
            handle_error(error)
            return {"error": str(e)}

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()

    def __del__(self):
        """Cleanup on object destruction."""
        try:
            self._save_lru_order()
        except Exception:
            pass  # Ignore errors during destruction


def create_disk_cache_from_config(config: dict) -> DiskCache:
    """
    Create DiskCache instance from platform configuration.

    Args:
        config: Configuration dictionary from platform.yaml

    Returns:
        Configured DiskCache instance

    Example:
        >>> config = {
        ...     "enabled": True,
        ...     "ttl_hours": 24,
        ...     "max_size_gb": 10,
        ...     "path": ".cache"
        ... }
        >>> cache = create_disk_cache_from_config(config)
    """
    if not config.get("enabled", True):
        logger.warning("disk_cache_disabled_by_config")
        # Return a no-op cache for disabled case
        return DiskCache(location=config.get("path", ".cache"))

    ttl_hours = config.get("ttl_hours")
    ttl_seconds = ttl_hours * 3600 if ttl_hours is not None else None

    max_size_gb = config.get("max_size_gb")
    max_size_bytes = int(max_size_gb * 1024 * 1024 * 1024) if max_size_gb is not None else None

    location = config.get("path", ".cache")

    logger.info(
        "creating_disk_cache_from_config",
        location=location,
        ttl_hours=ttl_hours,
        max_size_gb=max_size_gb,
        enabled=config.get("enabled", True),
    )

    return DiskCache(
        location=location,
        ttl_seconds=ttl_seconds,
        max_size_bytes=max_size_bytes,
    )
