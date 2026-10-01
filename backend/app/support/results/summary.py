# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Compact digest of a run's result folder, for agents (GET /results/summary).

The other /results endpoints feed the browser - whole point clouds, whole CSV series, PNGs - and are far too
big for an LLM's context. This reduces each Exodus output to min/max per variable at its last *written* step
and each CSV output to final/min/max per column. PeriLab pre-allocates Exodus time steps, so an unfinished run
ends in all-zero steps: the last written one is the step with the largest time, not the last index.
"""

import csv
import os
from typing import Optional

import netCDF4
import numpy as np
from exodusreader import exodusreader

from ..base_models import ColumnSummary, OutputSummary, VariableRange


def _range(values) -> VariableRange:
    values = np.asarray(values, dtype=float)
    return VariableRange(min=float(np.nanmin(values)), max=float(np.nanmax(values)))


def exodus_summary(path: str, name: str) -> Optional[OutputSummary]:
    """`name`'s variables at the last written step; None if the file has no time steps yet."""
    with netCDF4.Dataset(path) as nc:
        times = np.asarray(nc.variables["time_whole"][:], dtype=float)
    if times.size == 0:
        return None
    step = int(np.argmax(times))
    _, point_data, global_data, *_ = exodusreader.read_timestep(path, step)

    variables = {key: _range(values) for key, values in point_data.items() if np.size(values)}
    # Vectors are stored per component ("Displacementsx", ...); add their magnitude under the base name. Tensor
    # rows ("Cauchy Stressxy" -> "Cauchy Stressx") are skipped because their base itself ends in an axis.
    # ponytail: name-suffix heuristic; switch to PeriLab's output metadata once its schema is exported
    for key in point_data:
        base = key[:-1]
        if key.endswith("x") and base[-1:] not in ("x", "y", "z") and base + "y" in point_data:
            components = [point_data[base + axis] for axis in "xyz" if base + axis in point_data]
            variables[base] = _range(np.linalg.norm(np.column_stack(components), axis=1))

    return OutputSummary(
        name=name,
        last_step=step,
        final_time=float(times[step]),
        variables=variables,
        globals={key: float(value) for key, value in (global_data or {}).items()},
    )


def csv_summary(path: str) -> dict[str, ColumnSummary]:
    """final/min/max of every numeric column; a column with any non-numeric value is left out."""
    with open(path, encoding="UTF-8", newline="") as file:
        rows = list(csv.reader(file))
    if len(rows) < 2:
        return {}
    header, body = rows[0], rows[1:]
    columns = {}
    for i, column in enumerate(header):
        try:
            values = [float(row[i]) for row in body]
        except (ValueError, IndexError):
            continue
        columns[column] = ColumnSummary(final=values[-1], min=min(values), max=max(values))
    return columns


def summarize(result_dir: str, model_name: str) -> tuple[list[OutputSummary], dict[str, dict[str, ColumnSummary]]]:
    """Summaries of every `<model_name>_<output>.e` / `.csv` file in a run's result folder."""
    prefix = model_name + "_"
    outputs, csv_outputs = [], {}
    for filename in sorted(os.listdir(result_dir)):
        stem, extension = os.path.splitext(filename)
        if not stem.startswith(prefix):
            continue
        name, path = stem[len(prefix) :], os.path.join(result_dir, filename)
        if extension == ".e":
            output = exodus_summary(path, name)
            if output is not None:
                outputs.append(output)
        elif extension == ".csv":
            csv_outputs[name] = csv_summary(path)
    return outputs, csv_outputs
