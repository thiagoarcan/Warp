"""
Safe Expression Evaluator

Provides secure evaluation of mathematical expressions without using eval().
Uses Python's AST module to parse and evaluate expressions safely.

This module replaces dangerous eval() calls with a controlled evaluator
that only allows specific operations and functions.
"""

from __future__ import annotations

import ast
import operator
from typing import TYPE_CHECKING, Any

import numpy as np

from platform_base.utils.logging import get_logger


if TYPE_CHECKING:
    from collections.abc import Callable


logger = get_logger(__name__)


# Safe binary operators
SAFE_BINARY_OPS: dict[type, Callable[[Any, Any], Any]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

# Safe comparison operators
SAFE_COMPARE_OPS: dict[type, Callable[[Any, Any], bool]] = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}

# Safe unary operators
SAFE_UNARY_OPS: dict[type, Callable[[Any], Any]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
    ast.Not: operator.not_,
}

# Safe boolean operators
SAFE_BOOL_OPS: dict[type, Callable[[list[Any]], bool]] = {
    ast.And: lambda vals: all(vals),
    ast.Or: lambda vals: any(vals),
}

# Safe mathematical functions (numpy-compatible)
SAFE_FUNCTIONS: dict[str, Callable[..., Any]] = {
    # Basic math
    "abs": abs,
    "min": min,
    "max": max,
    "sum": sum,
    "len": len,
    "round": round,
    "pow": pow,
    # Trigonometric
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "asin": np.arcsin,
    "acos": np.arccos,
    "atan": np.arctan,
    "atan2": np.arctan2,
    # Hyperbolic
    "sinh": np.sinh,
    "cosh": np.cosh,
    "tanh": np.tanh,
    # Exponential/Logarithmic
    "sqrt": np.sqrt,
    "log": np.log,
    "log10": np.log10,
    "log2": np.log2,
    "exp": np.exp,
    # Other
    "floor": np.floor,
    "ceil": np.ceil,
    "degrees": np.degrees,
    "radians": np.radians,
    # Custom helpers
    "avg": lambda x: sum(x) / len(x) if x else 0,
    "mean": np.mean,
    "std": np.std,
}

# Safe constants
SAFE_CONSTANTS: dict[str, float] = {
    "pi": float(np.pi),
    "e": float(np.e),
    "inf": float("inf"),
    "nan": float("nan"),
}


class SafeEvalError(Exception):
    """Exception raised when safe evaluation fails."""


class SafeExpressionEvaluator:
    """
    Evaluates mathematical expressions safely using AST parsing.

    This class provides a secure alternative to Python's eval() function
    by only allowing whitelisted operations and functions.

    Example:
        evaluator = SafeExpressionEvaluator()
        result = evaluator.evaluate("sin(x) + cos(y)", {"x": 0.5, "y": 1.0})
    """

    def __init__(
        self,
        extra_functions: dict[str, Callable[..., Any]] | None = None,
        extra_constants: dict[str, float] | None = None,
    ):
        """
        Initialize the evaluator.

        Args:
            extra_functions: Additional allowed functions
            extra_constants: Additional allowed constants
        """
        self.functions = {**SAFE_FUNCTIONS}
        self.constants = {**SAFE_CONSTANTS}

        if extra_functions:
            self.functions.update(extra_functions)
        if extra_constants:
            self.constants.update(extra_constants)

    def evaluate(self, expression: str, context: dict[str, Any] | None = None) -> Any:
        """
        Safely evaluate a mathematical expression.

        Args:
            expression: The expression string to evaluate
            context: Dictionary of variable names and their values

        Returns:
            The result of the expression evaluation

        Raises:
            SafeEvalError: If the expression is invalid or contains forbidden operations
        """
        context = context or {}

        try:
            tree = ast.parse(expression, mode="eval")
            return self._eval_node(tree.body, context)
        except SafeEvalError:
            raise
        except SyntaxError as e:
            raise SafeEvalError(f"Syntax error in expression: {e}") from e
        except Exception as e:
            raise SafeEvalError(f"Evaluation error: {e}") from e

    def _eval_node(self, node: ast.AST, context: dict[str, Any]) -> Any:
        """Recursively evaluate an AST node."""

        # Constant values (numbers, strings, booleans, None)
        if isinstance(node, ast.Constant):
            return node.value

        # Variable names
        if isinstance(node, ast.Name):
            name = node.id
            if name in context:
                return context[name]
            if name in self.constants:
                return self.constants[name]
            if name in self.functions:
                return self.functions[name]
            raise SafeEvalError(f"Unknown variable: {name}")

        # Binary operations (+, -, *, /, etc.)
        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left, context)
            right = self._eval_node(node.right, context)
            op_type = type(node.op)
            if op_type in SAFE_BINARY_OPS:
                return SAFE_BINARY_OPS[op_type](left, right)
            raise SafeEvalError(f"Unsupported binary operator: {op_type.__name__}")

        # Unary operations (+x, -x, not x)
        if isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand, context)
            op_type = type(node.op)
            if op_type in SAFE_UNARY_OPS:
                return SAFE_UNARY_OPS[op_type](operand)
            raise SafeEvalError(f"Unsupported unary operator: {op_type.__name__}")

        # Comparisons (==, !=, <, >, <=, >=)
        if isinstance(node, ast.Compare):
            left = self._eval_node(node.left, context)
            for op, comparator in zip(node.ops, node.comparators, strict=False):
                right = self._eval_node(comparator, context)
                op_type = type(op)
                if op_type not in SAFE_COMPARE_OPS:
                    raise SafeEvalError(f"Unsupported comparison: {op_type.__name__}")
                if not SAFE_COMPARE_OPS[op_type](left, right):
                    return False
                left = right
            return True

        # Boolean operations (and, or)
        if isinstance(node, ast.BoolOp):
            op_type = type(node.op)
            if op_type not in SAFE_BOOL_OPS:
                raise SafeEvalError(f"Unsupported boolean operator: {op_type.__name__}")
            values = [self._eval_node(v, context) for v in node.values]
            return SAFE_BOOL_OPS[op_type](values)

        # Function calls
        if isinstance(node, ast.Call):
            func = self._eval_node(node.func, context)
            if not callable(func):
                raise SafeEvalError(f"Not a callable: {func}")

            # Evaluate arguments
            args = [self._eval_node(arg, context) for arg in node.args]

            # Evaluate keyword arguments
            kwargs = {}
            for kw in node.keywords:
                if kw.arg is None:
                    raise SafeEvalError("**kwargs not allowed in expressions")
                kwargs[kw.arg] = self._eval_node(kw.value, context)

            return func(*args, **kwargs)

        # Ternary expression (x if condition else y)
        if isinstance(node, ast.IfExp):
            test = self._eval_node(node.test, context)
            if test:
                return self._eval_node(node.body, context)
            return self._eval_node(node.orelse, context)

        # List literals
        if isinstance(node, ast.List):
            return [self._eval_node(el, context) for el in node.elts]

        # Tuple literals
        if isinstance(node, ast.Tuple):
            return tuple(self._eval_node(el, context) for el in node.elts)

        # Subscript (x[0], x[key], x[1:3], x[-3:])
        if isinstance(node, ast.Subscript):
            value = self._eval_node(node.value, context)
            
            # Handle slice notation (x[1:3], x[-3:], etc.)
            if isinstance(node.slice, ast.Slice):
                lower = self._eval_node(node.slice.lower, context) if node.slice.lower else None
                upper = self._eval_node(node.slice.upper, context) if node.slice.upper else None
                step = self._eval_node(node.slice.step, context) if node.slice.step else None
                return value[lower:upper:step]
            
            # Regular indexing
            idx = self._eval_node(node.slice, context)
            return value[idx]

        # Attribute access (limited to safe names)
        if isinstance(node, ast.Attribute):
            value = self._eval_node(node.value, context)
            attr = node.attr
            # Only allow safe attribute access
            if hasattr(value, attr) and not attr.startswith("_"):
                return getattr(value, attr)
            raise SafeEvalError(f"Attribute access not allowed: {attr}")

        raise SafeEvalError(f"Unsupported expression type: {type(node).__name__}")

    def compile_condition(
        self,
        condition: str,
        param_names: list[str],
    ) -> Callable[..., bool]:
        """
        Compile a condition string into a callable function.

        Args:
            condition: The condition expression (e.g., "value > 10")
            param_names: List of parameter names (e.g., ["t", "value"])

        Returns:
            A callable that evaluates the condition with given arguments

        Raises:
            SafeEvalError: If condition syntax is invalid

        Example:
            func = evaluator.compile_condition("value > 10", ["t", "value"])
            result = func(0.5, 15)  # Returns True
        """
        # Validate syntax at compile time
        try:
            ast.parse(condition, mode="eval")
        except SyntaxError as e:
            raise SafeEvalError(f"Invalid condition syntax: {e}") from e

        def compiled_func(*args: Any, **kwargs: Any) -> bool:
            context = dict(zip(param_names, args, strict=False))
            context.update(kwargs)
            try:
                result = self.evaluate(condition, context)
                return bool(result)
            except SafeEvalError as e:
                logger.warning(f"safe_eval_condition_failed: {condition} - {e}")
                return False

        return compiled_func


# Global default evaluator instance
_default_evaluator: SafeExpressionEvaluator | None = None


def get_safe_evaluator() -> SafeExpressionEvaluator:
    """Get or create the default safe evaluator instance."""
    global _default_evaluator
    if _default_evaluator is None:
        _default_evaluator = SafeExpressionEvaluator()
    return _default_evaluator


def safe_eval(expression: str, context: dict[str, Any] | None = None) -> Any:
    """
    Safely evaluate a mathematical expression.

    This is a convenience function that uses the default evaluator.

    Args:
        expression: The expression to evaluate
        context: Variable context for evaluation

    Returns:
        The result of the evaluation

    Example:
        result = safe_eval("sin(x) * 2", {"x": 1.57})
    """
    return get_safe_evaluator().evaluate(expression, context)


def compile_safe_condition(
    condition: str,
    param_names: list[str],
) -> Callable[..., bool]:
    """
    Compile a condition string into a safe callable.

    Args:
        condition: The condition expression
        param_names: Parameter names for the resulting function

    Returns:
        A callable that evaluates the condition

    Example:
        is_valid = compile_safe_condition("value > threshold", ["value", "threshold"])
        result = is_valid(15, 10)  # Returns True
    """
    return get_safe_evaluator().compile_condition(condition, param_names)


def safe_eval_threshold(
    expression: str,
    stats: dict[str, float],
) -> float:
    """
    Safely evaluate a threshold expression with statistics context.

    Args:
        expression: Numeric expression (e.g., "mean + 2 * std")
        stats: Dictionary of statistical values

    Returns:
        The computed threshold value

    Raises:
        SafeEvalError: If expression is invalid
    """
    result = get_safe_evaluator().evaluate(expression, stats)
    return float(result)
