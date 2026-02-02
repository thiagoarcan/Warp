from __future__ import annotations

import inspect
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

    def _call_task_func(
        self, task: Task, results: dict[str, Any], inputs: dict[str, Any]
    ) -> Any:
        """Call task function with proper argument passing.
        
        Supports both named kwargs (when param names match dep names)
        and positional args (when param names don't match dep names).
        """
        dep_values = [results.get(dep, inputs.get(dep)) for dep in task.deps]

        # Get function signature
        try:
            sig = inspect.signature(task.func)
            param_names = list(sig.parameters.keys())
        except (ValueError, TypeError):
            # Fallback to kwargs for functions without inspectable signature
            kwargs = {dep: results.get(dep, inputs.get(dep)) for dep in task.deps}
            return task.func(**kwargs)

        # Check if param names match dep names
        deps_set = set(task.deps)
        params_match = all(p in deps_set for p in param_names if p not in ('args', 'kwargs'))

        if params_match:
            # Use kwargs when parameter names match dependency names
            kwargs = {dep: results.get(dep, inputs.get(dep)) for dep in task.deps}
            return task.func(**kwargs)
        else:
            # Use positional args when parameter names don't match
            return task.func(*dep_values)

    def run(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        inputs = inputs or {}
        results: dict[str, Any] = {}
        graph: dict[str, list[str]] = defaultdict(list)
        indegree: dict[str, int] = dict.fromkeys(self._tasks, 0)

        for task in self._tasks.values():
            for dep in task.deps:
                # Only count dependency if it's a registered task
                # External inputs are considered already satisfied
                if dep in self._tasks:
                    graph[dep].append(task.name)
                    indegree[task.name] += 1

        queue = deque([name for name, degree in indegree.items() if degree == 0])
        while queue:
            name = queue.popleft()
            task = self._tasks[name]
            results[name] = self._call_task_func(task, results, inputs)
            for neighbor in graph[name]:
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    queue.append(neighbor)

        if len(results) != len(self._tasks):
            raise ValidationError("Task graph has cycle", {"tasks": list(self._tasks)})

        logger.info("orchestrator_run_complete", tasks=list(self._tasks))
        return results

