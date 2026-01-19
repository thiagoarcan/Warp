from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class MenuAction:
    name: str
    handler: Callable
    description: str = ""


class ContextMenu:
    def __init__(self, actions: list[MenuAction]):
        self.actions = actions

    def show(self, event) -> None:
        _ = event

    def execute_action(self, action: MenuAction, context) -> None:
        action.handler(context)
