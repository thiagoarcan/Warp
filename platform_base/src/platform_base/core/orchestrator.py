from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from platform_base.utils.errors import ValidationError
from platform_base.utils.logging import get_logger


if TYPE_CHECKING:
    from collections.abc import Callable


logger = get_logger(__name__)


@dataclass(frozen=True)
class Task:
    name: str
    func: Callable[..., Any]
    deps: tuple[str, ...] = ()


class Orchestrator:
    """Minimal DAG-based orchestrator."""

    def __init__(self):
        self._tasks: dict[str, Task] = {}

    def register(self, task: Task) -> None:
        if task.name in self._tasks:
            raise ValidationError("Task already registered", {"task": task.name})
        self._tasks[task.name] = task

    def run(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        inputs = inputs or {}
        results: dict[str, Any] = {}
        graph: dict[str, list[str]] = defaultdict(list)
        indegree: dict[str, int] = dict.fromkeys(self._tasks, 0)

        for task in self._tasks.values():
            for dep in task.deps:
                graph[dep].append(task.name)
                indegree[task.name] += 1

        queue = deque([name for name, degree in indegree.items() if degree == 0])
        while queue:
            name = queue.popleft()
            task = self._tasks[name]
            kwargs = {dep: results.get(dep, inputs.get(dep)) for dep in task.deps}
            results[name] = task.func(**kwargs)
            for neighbor in graph[name]:
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    queue.append(neighbor)

        if len(results) != len(self._tasks):
            raise ValidationError("Task graph has cycle", {"tasks": list(self._tasks)})

        logger.info("orchestrator_run_complete", tasks=list(self._tasks))
        return results
