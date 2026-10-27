"""PeriLab evaluates deck expressions as Julia, so anything beyond arithmetic over the solver variables must be
refused before submission (support/deck_guard.py)."""

import json
from pathlib import Path

import pytest
import yaml
from fastapi import HTTPException

from backend.app.support.deck_guard import EXPRESSION_KEYS, EXPRESSION_MAPPINGS, check_input_deck, is_safe_expression

SAFE = [
    "0",
    "-100*t",
    "20e+3",
    "1.5e-3*t",
    "-x",
    ".5*t",
    "100*sin(2*pi*t)+3",
    "x > 0.5 && y < 1",
    "1:10",
    "t <= 0.5 ? 2*t : 1",
    "1/xi^2",
    "ns_Dogbone_1.txt",
    "max(0, min(1, t))",
]
UNSAFE = [
    "run(`id`)",
    'read("/etc/passwd")',
    "run(Cmd([string(Char(115),Char(104))]))",
    "ENV",
    "@eval 1",
    "x = 1",
    "pi = 3",
    "exit()",
    "t; run",
    '"a"',
    "x[1]",
    "Δt",
    "$x",
    "sin(x) |> run",
]


@pytest.mark.parametrize("text", SAFE)
def test_accepts_solver_expressions(text):
    assert is_safe_expression(text)


@pytest.mark.parametrize("text", UNSAFE)
def test_rejects_code(text):
    assert not is_safe_expression(text)


def _deck(tmp_path, peri):
    path = tmp_path / "deck.yaml"
    path.write_text(yaml.dump({"PeriLab": peri}))
    return str(path)


@pytest.mark.parametrize(
    "peri",
    [
        {"Boundary Conditions": {"BC_1": {"Variable": "Displacements", "Value": "run(`id`)"}}},
        {"Compute Class Parameters": {"c": {"Equation": "open(x)"}}},
        {"Discretization": {"Node Sets": {"Node Set 1": "read(x)"}}},
        {"Discretization": {"Gcode": {"Blocks": {1: "exit(x > 0)"}}}},
        {"Discretization": {"Input Mesh File": "/etc/passwd"}},
        {"Blocks": {"block_1": {"Influence Function": "run(x)"}}},
        {"Models": {"Material Models": {"m": {"Material Model": "Correspondence UMAT", "File": "/usr/lib/libc.so.6"}}}},
        {"Models": {"Material Models": {"m": {"Material Model": "Correspondence UMAT", "File": "../other/umat.so"}}}},
        {"Models": {"Thermal Models": {"t": {"Thermal Model": "HETVAL", "File": "/tmp/hetval.so"}}}},
        {"Discretization": {"Input External Topology": {"File": "/etc/passwd"}}},
    ],
)
def test_check_input_deck_rejects(tmp_path, peri):
    with pytest.raises(HTTPException) as exc:
        check_input_deck(_deck(tmp_path, peri))
    assert exc.value.status_code == 422


def test_check_input_deck_accepts_generated_deck(tmp_path):
    peri = {
        "Discretization": {"Input Mesh File": "Dogbone.txt", "Node Sets": {"Node Set 1": "ns_Dogbone_1.txt"}},
        "Blocks": {"block_1": {"Block ID": 1, "Material Model": "PD Solid Elastic", "Horizon": 0.5}},
        "Boundary Conditions": {"BC_1": {"Variable": "Displacements", "Coordinate": "x", "Value": "-1000*t"}},
    }
    check_input_deck(_deck(tmp_path, peri))


def test_check_input_deck_accepts_umat_in_job_folder(tmp_path):
    peri = {"Models": {"Material Models": {"m": {"Material Model": "Correspondence UMAT", "File": "umat.so"}}}}
    check_input_deck(_deck(tmp_path, peri))


PERILAB_SCHEMA = Path(__file__).resolve().parents[4] / "src" / "lib" / "perilab" / "schema.json"


def _evaluated_keys(node, found):
    """Every property name whose schema carries PeriLab's `x-perilab-eval` marker."""
    if isinstance(node, dict):
        for key, child in (node.get("properties") or {}).items():
            if isinstance(child, dict) and child.get("x-perilab-eval"):
                found.add(key)
        for child in node.values():
            _evaluated_keys(child, found)
    elif isinstance(node, list):
        for child in node:
            _evaluated_keys(child, found)
    return found


def test_deck_guard_covers_every_key_perilab_evaluates():
    # A PeriLab update that evaluates a new key fails here on `npm run perilab-schema`, instead of silently
    # giving every account (guests included) code execution in the solver container.
    found = _evaluated_keys(json.loads(PERILAB_SCHEMA.read_text()), set())
    assert found, "schema.json has no x-perilab-eval markers - regenerate it with a PeriLab that emits them"
    assert found <= EXPRESSION_KEYS | EXPRESSION_MAPPINGS, found - (EXPRESSION_KEYS | EXPRESSION_MAPPINGS)
