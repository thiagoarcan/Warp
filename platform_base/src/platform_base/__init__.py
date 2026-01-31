from platform_base.core.dataset_store import DatasetStore
from platform_base.io.loader import load


__all__ = ["DatasetStore", "load_dataset"]
__version__ = "2.0.0"


def load_dataset(path: str, config: dict | None = None):
    """Convenience wrapper for io.loader.load."""
    return load(path, config=config)
