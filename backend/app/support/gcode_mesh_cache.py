"""Reuse of the mesh PeriLab generates from G-code (Phase 1).

PeriLab writes the nodes it slices from `<name>.gcode` to `<name>.txt` next to it, in its own job folder, and with
`Gcode: Overwrite Mesh: false` reads that file instead of slicing again. Every job gets a fresh folder holding only
the files of the model folder (solver_backend.py uploads them all), so the mesh has to be copied back into the model
folder after a run (`keep`, called from job_queue.sync_status) to be there next time.

PeriLab reuses whatever `.txt` it finds, so a mesh made from another G-code or other Gcode settings would silently be
used for the new ones. `<name>.txt.key` records what the mesh was made from (hash of the G-code and the deck's Gcode
section); `drop_if_stale`, run on every submit, deletes the mesh when that no longer matches.
"""

import hashlib
import json
import os

import yaml

from .file_handler import safe_segment


def _gcode_of(deck_text: str | bytes) -> tuple[str, dict] | None:
    """(G-code file name, Gcode settings) of a deck, or None if it doesn't read a G-code mesh."""
    discretization = ((yaml.safe_load(deck_text) or {}).get("PeriLab") or {}).get("Discretization") or {}
    name = discretization.get("Input Mesh File")
    if discretization.get("Type") != "Gcode" or not isinstance(name, str) or not name.endswith(".gcode"):
        return None
    safe_segment(name)
    # Overwrite Mesh only says whether to reuse the mesh, not what it looks like.
    settings = {k: v for k, v in (discretization.get("Gcode") or {}).items() if k != "Overwrite Mesh"}
    return name, settings


def _key(gcode: bytes, settings: dict) -> str:
    digest = hashlib.sha256(gcode)
    digest.update(json.dumps(settings, sort_keys=True, default=str).encode())
    return digest.hexdigest()


def _mesh_name(gcode_name: str) -> str:
    return gcode_name[: -len(".gcode")] + ".txt"


def keep(client, job_id: str, model_folder: str, deck_name: str) -> None:
    """Copies the mesh of a finished job into `model_folder`, with its key. No-op for non-G-code decks."""
    gcode = _gcode_of(client.get_file(job_id, deck_name))
    if gcode is None:
        return
    gcode_name, settings = gcode
    mesh_name = _mesh_name(gcode_name)
    if mesh_name not in client.list_files(job_id):
        return
    key = _key(client.get_file(job_id, gcode_name), settings)
    with open(os.path.join(model_folder, mesh_name), "wb") as file:
        file.write(client.get_file(job_id, mesh_name))
    with open(os.path.join(model_folder, mesh_name + ".key"), "w", encoding="UTF-8") as file:
        file.write(key)


def drop_if_stale(model_folder: str, deck_path: str) -> None:
    """Deletes the cached mesh (and key) when the deck's G-code or Gcode settings differ from what it was made from,
    so PeriLab can't reuse it for the wrong part."""
    with open(deck_path, "rb") as file:
        gcode = _gcode_of(file.read())
    if gcode is None:
        return
    gcode_name, settings = gcode
    mesh_path = os.path.join(model_folder, _mesh_name(gcode_name))
    key_path = mesh_path + ".key"
    if not os.path.exists(mesh_path):
        return
    gcode_path = os.path.join(model_folder, gcode_name)
    stored = current = None
    if os.path.exists(key_path):
        with open(key_path, encoding="UTF-8") as file:
            stored = file.read()
    if os.path.exists(gcode_path):
        with open(gcode_path, "rb") as file:
            current = _key(file.read(), settings)
    if stored is None or stored != current:
        os.remove(mesh_path)
        if os.path.exists(key_path):
            os.remove(key_path)
