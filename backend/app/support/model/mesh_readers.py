# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Read the points of a mesh file for the model view.

Covers the generated `<model>.txt` and uploaded meshes (`meshSource == "upload"`): PeriLab text point clouds
and Exodus files. G-code is previewed in the browser (GcodeView.svelte), so it isn't read here.
"""

import numpy as np
from exodusreader import exodusreader


def read_points(path: str, two_d: bool) -> tuple[np.ndarray, np.ndarray]:
    """xyz of shape (n, 3) and 1-based block ids of shape (n,); ValueError if the file can't be read as a mesh."""
    lower = path.lower()
    if lower.endswith((".e", ".g")):
        return _read_exodus(path)
    if lower.endswith(".txt"):
        return _read_txt(path, two_d)
    raise ValueError(f"No point preview for {path.rsplit('/', 1)[-1]}")


def _read_txt(path: str, two_d: bool) -> tuple[np.ndarray, np.ndarray]:
    # Whitespace separated `x y [z] block_id ...`; comment and `header:` lines are skipped.
    xyz, block = [], []
    with open(path, "r", encoding="UTF-8") as file:
        for line in file:
            line = line.replace(",", "").strip()
            if not line or line.startswith("#") or line.startswith("header"):
                continue
            parts = line.split()
            try:
                if two_d:
                    xyz.append((float(parts[0]), float(parts[1]), 0.0))
                    block.append(int(parts[2]))
                else:
                    xyz.append((float(parts[0]), float(parts[1]), float(parts[2])))
                    block.append(int(parts[3]))
            except (ValueError, IndexError):
                if two_d:
                    raise ValueError("Model don't support 2D model, switch two dimensional model off")
                raise ValueError("Model don't support 3D model, switch to two dimensional model")
    return np.array(xyz, dtype=float).reshape(-1, 3), np.array(block, dtype=int)


def _read_exodus(path: str) -> tuple[np.ndarray, np.ndarray]:
    try:
        points, _, _, _, _, blocks, _ = exodusreader.read_timestep(path, 0)
    except Exception as e:
        raise ValueError(f"Can't read Exodus mesh: {e}")
    block = np.ones(len(points), dtype=int)
    for block_id, connectivity in enumerate(blocks, start=1):
        block[np.asarray(connectivity).ravel()] = block_id
    return np.asarray(points, dtype=float), block
