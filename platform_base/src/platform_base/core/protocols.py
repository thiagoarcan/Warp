from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np
from numpy.typing import NDArray

from platform_base.core.models import InterpResult, SyncResult


@runtime_checkable
class PluginProtocol(Protocol):
    name: str
    version: str
    capabilities: list[str]


@runtime_checkable
class InterpolationPlugin(PluginProtocol, Protocol):
    def interpolate(
        self,
        values: NDArray[np.float64],
        t_seconds: NDArray[np.float64],
        params: dict,
    ) -> InterpResult:
        ...


@runtime_checkable
class SyncPlugin(PluginProtocol, Protocol):
    def synchronize(
        self,
        series_dict: dict[str, NDArray[np.float64]],
        t_dict: dict[str, NDArray[np.float64]],
        params: dict,
    ) -> SyncResult:
        ...
