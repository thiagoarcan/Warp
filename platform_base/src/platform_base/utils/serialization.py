from __future__ import annotations

from datetime import datetime
from typing import Any

import numpy as np


def to_jsonable(obj: Any) -> Any:
    """Convert common numpy/datetime objects to JSON-friendly structures."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.integer | np.floating):
        return obj.item()
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {key: to_jsonable(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [to_jsonable(value) for value in obj]
    return obj
