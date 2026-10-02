# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Refuses input decks that would make PeriLab run arbitrary code.

PeriLab evaluates several deck strings as Julia (`Base.eval(Meta.parse(...))`): boundary condition `Value`, compute
`Equation`, `Influence Function`, `Environmental Temperature`, node-set entries and G-code `Blocks` conditions. Decks
come from guests (generate_model) and members (write_input_file), so without this check any account - including an
anonymous guest - gets a shell in the solver container. Checked once at submission (support/solver_backend.py), the
one place every deck passes, rather than per writer.

A string passes if it is a plain file name (no call possible without parentheses) or an arithmetic/boolean expression
over the solver's variables and a fixed set of math functions: no strings, backticks, macros, indexing, assignment or
other identifiers, so nothing can reach `run`, `open`, `ENV`, ... Mesh file names must stay inside the job folder.
"""

import re

import yaml
from fastapi import HTTPException, status

EXPRESSION_KEYS = {"Value", "Equation", "Influence Function", "Environmental Temperature"}
# String values directly inside these mappings are evaluated too (node-set definitions, G-code block conditions).
EXPRESSION_MAPPINGS = {"Node Sets", "Blocks"}
FILE_KEYS = {"Input Mesh File"}

# ponytail: Phase 0 allowlist of what built-in configs and the amplitude tool produce; extend when a model needs more.
ALLOWED_NAMES = {
    *("x", "y", "z", "t", "st", "xi", "xiX", "xiY", "xiZ", "pi", "true", "false"),
    *("sin", "cos", "tan", "asin", "acos", "atan", "sinh", "cosh", "tanh"),
    *("exp", "log", "log10", "sqrt", "abs", "min", "max", "sign", "floor", "ceil", "round", "ifelse"),
}
_NUMBER = re.compile(r"(?<![A-Za-z_])\d+\.?\d*(?:[eE][+-]?\d+)?|(?<![A-Za-z_\d])\.\d+(?:[eE][+-]?\d+)?")
_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_OPERATORS = re.compile(r"[\s+\-*/^().,<>=!&|:?%]*")
_ASSIGNMENT = re.compile(r"(?<![=!<>])=(?!=)")
_FILE_NAME = re.compile(r"[A-Za-z0-9_\-]+\.[A-Za-z0-9]+")


def is_safe_expression(text: str) -> bool:
    if _FILE_NAME.fullmatch(text):
        return True
    if _ASSIGNMENT.search(text):
        return False
    rest = _NUMBER.sub(" ", text)
    if any(name not in ALLOWED_NAMES for name in _NAME.findall(rest)):
        return False
    return _OPERATORS.fullmatch(_NAME.sub(" ", rest)) is not None


def _reject(key: str, value: str):
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail=f"Input deck: {key} {value!r} is not allowed. Use arithmetic over x, y, z, t and math functions only.",
    )


def _walk(node, key=None) -> None:
    if isinstance(node, dict):
        for child_key, child in node.items():
            if child_key in EXPRESSION_MAPPINGS and isinstance(child, dict):
                for name, value in child.items():
                    if isinstance(value, str) and not is_safe_expression(value):
                        _reject(f"{child_key}/{name}", value)
            _walk(child, child_key)
    elif isinstance(node, list):
        for child in node:
            _walk(child, key)
    elif isinstance(node, str):
        if key in EXPRESSION_KEYS and not is_safe_expression(node):
            _reject(key, node)
        if key in FILE_KEYS and ("/" in node or "\\" in node or node in ("", ".", "..")):
            _reject(key, node)


def check_input_deck(path: str) -> None:
    """422 if the deck at `path` isn't valid YAML or contains a string PeriLab would evaluate unsafely."""
    with open(path, encoding="UTF-8") as file:
        try:
            deck = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=f"Input deck: {e}")
    _walk(deck)
