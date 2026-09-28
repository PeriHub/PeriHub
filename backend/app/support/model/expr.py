# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Safe arithmetic/comparison expressions for YAML models (`HEIGHT / 21`, `x < spacing and y > 0`).

Parsed with `ast` and evaluated by walking a whitelist of node types — never `eval` — so a model
file can't reach attributes, imports or builtins. Works on numpy arrays, which is how `where:`
block conditions are applied to all points at once.
"""

import ast
import math
import operator
from functools import reduce

import numpy as np

FUNCTIONS = {
    "abs": np.abs,
    "sqrt": np.sqrt,
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "min": np.minimum,
    "max": np.maximum,
    "floor": np.floor,
    "ceil": np.ceil,
    "round": np.round,
    "int": lambda v: np.trunc(v).astype(int) if isinstance(v, np.ndarray) else int(v),
}
CONSTANTS = {"pi": math.pi, "true": True, "false": False}

_BINARY = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}
_COMPARE = {
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
}


class ExpressionError(ValueError):
    pass


def evaluate(expression, names: dict):
    """Evaluate `expression` (str or plain number) with `names` in scope."""
    if isinstance(expression, (int, float)):
        return expression
    if not isinstance(expression, str):
        raise ExpressionError(f"expected a number or expression, got {type(expression).__name__}")
    try:
        tree = ast.parse(expression.strip(), mode="eval")
    except SyntaxError as e:
        raise ExpressionError(f"invalid expression '{expression}': {e.msg}") from None
    return _eval(tree.body, names)


def _eval(node, names):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in names:
            return names[node.id]
        if node.id in CONSTANTS:
            return CONSTANTS[node.id]
        raise ExpressionError(f"unknown name '{node.id}'")
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
        return _BINARY[type(node.op)](_eval(node.left, names), _eval(node.right, names))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        value = _eval(node.operand, names)
        return -value if isinstance(node.op, ast.USub) else value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return np.logical_not(_eval(node.operand, names))
    if isinstance(node, ast.BoolOp):
        values = [_eval(v, names) for v in node.values]
        return reduce(np.logical_and if isinstance(node.op, ast.And) else np.logical_or, values)
    if isinstance(node, ast.Compare) and all(type(op) in _COMPARE for op in node.ops):
        # Chained `a < x < b` means `a < x and x < b`, elementwise.
        left, results = _eval(node.left, names), []
        for op, comparator in zip(node.ops, node.comparators):
            right = _eval(comparator, names)
            results.append(_COMPARE[type(op)](left, right))
            left = right
        return reduce(np.logical_and, results)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and not node.keywords:
        if node.func.id not in FUNCTIONS:
            raise ExpressionError(f"unknown function '{node.func.id}'")
        return FUNCTIONS[node.func.id](*[_eval(a, names) for a in node.args])
    raise ExpressionError(f"'{ast.unparse(node)}' is not allowed in an expression")
