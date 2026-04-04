"""
Unit tests for Orchestrator module.

Tests for:
- Task registration
- DAG-based execution
- Dependency resolution
- Cycle detection
"""

import pytest

from platform_base.core.orchestrator import Orchestrator, Task
from platform_base.utils.errors import ValidationError


class TestTask:
    """Tests for Task dataclass"""

    def test_task_creation_minimal(self):
        """Test task creation with minimal args"""
        task = Task(name="test", func=lambda: 1)
        assert task.name == "test"
        assert task.deps == ()

    def test_task_creation_with_deps(self):
        """Test task creation with dependencies"""
        task = Task(
            name="test",
            func=lambda x: x + 1,
            deps=("dep1", "dep2")
        )
        assert task.name == "test"
        assert len(task.deps) == 2
        assert "dep1" in task.deps
        assert "dep2" in task.deps

    def test_task_is_frozen(self):
        """Task should be immutable (frozen dataclass)"""
        task = Task(name="test", func=lambda: 1)
        with pytest.raises(AttributeError):
            task.name = "changed"

    def test_task_with_callable(self):
        """Test task with various callables"""
        def my_func(x: int) -> int:
            return x * 2

        task = Task(name="multiply", func=my_func)
        assert task.func(5) == 10


class TestOrchestratorBasic:
    """Basic tests for Orchestrator"""

    def test_orchestrator_creation(self):
        """Test orchestrator instantiation"""
        orch = Orchestrator()
        assert orch is not None

    def test_register_single_task(self):
        """Test registering a single task"""
        orch = Orchestrator()
        task = Task(name="task1", func=lambda: 42)
        orch.register(task)
        # Should not raise
        assert True

    def test_register_duplicate_raises(self):
        """Registering same task twice should raise"""
        orch = Orchestrator()
        task = Task(name="task1", func=lambda: 42)
        orch.register(task)

        with pytest.raises(ValidationError):
            orch.register(task)

    def test_run_empty_orchestrator(self):
        """Running with no tasks should work"""
        orch = Orchestrator()
        results = orch.run()
        assert results == {}


class TestOrchestratorExecution:
    """Tests for task execution"""

    def test_run_single_task(self):
        """Test running a single task"""
        orch = Orchestrator()
        task = Task(name="answer", func=lambda: 42)
        orch.register(task)

        results = orch.run()
        assert results["answer"] == 42

    def test_run_multiple_independent_tasks(self):
        """Test running multiple independent tasks"""
        orch = Orchestrator()
        orch.register(Task(name="a", func=lambda: 1))
        orch.register(Task(name="b", func=lambda: 2))
        orch.register(Task(name="c", func=lambda: 3))

        results = orch.run()
        assert results["a"] == 1
        assert results["b"] == 2
        assert results["c"] == 3

    def test_run_with_dependencies(self):
        """Test running tasks with dependencies"""
        orch = Orchestrator()
        orch.register(Task(name="base", func=lambda: 10))
        orch.register(Task(
            name="derived",
            func=lambda base: base * 2,
            deps=("base",)
        ))

        results = orch.run()
        assert results["base"] == 10
        assert results["derived"] == 20

    def test_run_chain_of_dependencies(self):
        """Test a chain of dependencies"""
        orch = Orchestrator()
        orch.register(Task(name="a", func=lambda: 1))
        orch.register(Task(name="b", func=lambda a: a + 1, deps=("a",)))
        orch.register(Task(name="c", func=lambda b: b + 1, deps=("b",)))
        orch.register(Task(name="d", func=lambda c: c + 1, deps=("c",)))

        results = orch.run()
        assert results["a"] == 1
        assert results["b"] == 2
        assert results["c"] == 3
        assert results["d"] == 4

    def test_run_with_multiple_deps(self):
        """Test task with multiple dependencies"""
        orch = Orchestrator()
        orch.register(Task(name="x", func=lambda: 10))
        orch.register(Task(name="y", func=lambda: 20))
        orch.register(Task(
            name="sum",
            func=lambda x, y: x + y,
            deps=("x", "y")
        ))

        results = orch.run()
        assert results["sum"] == 30


class TestOrchestratorInputs:
    """Tests for external inputs"""

    def test_run_with_inputs(self):
        """Test running with external inputs"""
        orch = Orchestrator()
        orch.register(Task(
            name="double",
            func=lambda value: value * 2,
            deps=("value",)
        ))

        results = orch.run(inputs={"value": 5})
        assert results["double"] == 10

    def test_run_with_mixed_deps(self):
        """Test task depending on both input and other task"""
        orch = Orchestrator()
        orch.register(Task(name="computed", func=lambda: 100))
        orch.register(Task(
            name="combined",
            func=lambda computed, external: computed + external,
            deps=("computed", "external")
        ))

        results = orch.run(inputs={"external": 50})
        assert results["combined"] == 150


class TestOrchestratorCycleDetection:
    """Tests for cycle detection"""

    def test_detect_simple_cycle(self):
        """Test detecting a simple cycle"""
        orch = Orchestrator()
        orch.register(Task(name="a", func=lambda b: b, deps=("b",)))
        orch.register(Task(name="b", func=lambda a: a, deps=("a",)))

        with pytest.raises(ValidationError, match="cycle"):
            orch.run()

    def test_detect_three_node_cycle(self):
        """Test detecting a three-node cycle"""
        orch = Orchestrator()
        orch.register(Task(name="a", func=lambda c: c, deps=("c",)))
        orch.register(Task(name="b", func=lambda a: a, deps=("a",)))
        orch.register(Task(name="c", func=lambda b: b, deps=("b",)))

        with pytest.raises(ValidationError, match="cycle"):
            orch.run()


class TestOrchestratorComplexGraphs:
    """Tests for complex task graphs"""

    def test_diamond_dependency(self):
        """Test diamond-shaped dependency graph"""
        #     a
        #    / \
        #   b   c
        #    \ /
        #     d
        orch = Orchestrator()
        orch.register(Task(name="a", func=lambda: 1))
        orch.register(Task(name="b", func=lambda a: a + 10, deps=("a",)))
        orch.register(Task(name="c", func=lambda a: a + 100, deps=("a",)))
        orch.register(Task(
            name="d",
            func=lambda b, c: b + c,
            deps=("b", "c")
        ))

        results = orch.run()
        assert results["a"] == 1
        assert results["b"] == 11
        assert results["c"] == 101
        assert results["d"] == 112

    def test_wide_graph(self):
        """Test wide graph with many parallel tasks"""
        orch = Orchestrator()

        # Create 10 independent tasks
        for i in range(10):
            orch.register(Task(name=f"task_{i}", func=lambda i=i: i * 10))

        results = orch.run()
        assert len(results) == 10
        assert results["task_5"] == 50

    def test_deep_graph(self):
        """Test deep graph with long dependency chain"""
        orch = Orchestrator()
        depth = 20

        # First task
        orch.register(Task(name="task_0", func=lambda: 0))

        # Chain of dependencies
        for i in range(1, depth):
            prev = f"task_{i - 1}"
            orch.register(Task(
                name=f"task_{i}",
                func=lambda prev_val, i=i: prev_val + 1,
                deps=(prev,)
            ))

        results = orch.run()
        assert results["task_0"] == 0
        assert results[f"task_{depth - 1}"] == depth - 1
