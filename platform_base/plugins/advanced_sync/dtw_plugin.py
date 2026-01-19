from __future__ import annotations

from platform_base.plugins._base import PluginBase
from platform_base.utils.errors import PluginError


class DtwAlignPlugin(PluginBase):
    """Stub for DTW-based alignment."""

    def synchronize(self, *args, **kwargs):
        raise PluginError("DTW plugin not implemented", {"plugin": self.name})
