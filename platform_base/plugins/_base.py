from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PluginBase:
    name: str
    version: str
    capabilities: list[str]
