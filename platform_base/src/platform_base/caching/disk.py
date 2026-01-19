from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable

from joblib import Memory


class DiskCache:
    """Disk cache with optional TTL invalidation."""

    def __init__(self, location: str, ttl_seconds: int | None = None):
        self.location = Path(location)
        self.location.mkdir(parents=True, exist_ok=True)
        self._memory = Memory(location=str(self.location), verbose=0)
        self._ttl_seconds = ttl_seconds
        self._stamp_file = self.location / ".ttl"

    def _expired(self) -> bool:
        if self._ttl_seconds is None:
            return False
        if not self._stamp_file.exists():
            return False
        stamp = datetime.fromisoformat(self._stamp_file.read_text(encoding="utf-8"))
        return datetime.utcnow() - stamp > timedelta(seconds=self._ttl_seconds)

    def _touch(self) -> None:
        self._stamp_file.write_text(datetime.utcnow().isoformat(), encoding="utf-8")

    def clear(self) -> None:
        self._memory.clear(warn=False)

    def cache(self, func: Callable) -> Callable:
        cached = self._memory.cache(func)

        def wrapper(*args, **kwargs):
            if self._expired():
                self.clear()
            result = cached(*args, **kwargs)
            if self._ttl_seconds is not None:
                self._touch()
            return result

        return wrapper
