import numpy as np

from platform_base.core.protocols import PluginProtocol
from platform_base.core.registry import PluginRegistry


class DummyPlugin:
    name = "dummy"
    version = "0.1"
    capabilities = ["test"]

    def interpolate(self, values, t_seconds, params):
        return values


def test_registry_registers_plugin():
    registry = PluginRegistry()
    plugin = DummyPlugin()
    registry.register(plugin)
    assert "dummy" in registry.list_plugins()
