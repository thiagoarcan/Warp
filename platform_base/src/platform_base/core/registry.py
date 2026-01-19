from __future__ import annotations

from platform_base.core.protocols import PluginProtocol
from platform_base.utils.errors import PluginError
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class PluginRegistry:
    """Registry with validation and isolation guards."""

    def __init__(self):
        self._plugins: dict[str, PluginProtocol] = {}

    def register(self, plugin: PluginProtocol) -> None:
        if not isinstance(plugin, PluginProtocol):
            raise PluginError("Plugin does not implement protocol", {"plugin": str(plugin)})
        if plugin.name in self._plugins:
            raise PluginError("Plugin already registered", {"name": plugin.name})
        self._plugins[plugin.name] = plugin
        logger.info("plugin_registered", name=plugin.name, version=plugin.version)

    def unregister(self, name: str) -> None:
        self._plugins.pop(name, None)

    def get(self, name: str) -> PluginProtocol:
        if name not in self._plugins:
            raise PluginError("Plugin not found", {"name": name})
        return self._plugins[name]

    def list_plugins(self) -> list[str]:
        return sorted(self._plugins.keys())

    def safe_call(self, name: str, method: str, *args, **kwargs):
        plugin = self.get(name)
        try:
            func = getattr(plugin, method)
            return func(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001
            logger.error("plugin_call_failed", name=name, method=method, error=str(exc))
            raise PluginError("Plugin call failed", {"name": name, "method": method}) from exc
