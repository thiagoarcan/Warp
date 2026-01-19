from __future__ import annotations

from abc import ABC, abstractmethod

from platform_base.viz.config import PlotConfig


class BaseFigure(ABC):
    def __init__(self, config: PlotConfig):
        self.config = config

    @abstractmethod
    def render(self, data):
        raise NotImplementedError
