import os

import yaml

from backend.app.support import gcode_mesh_cache


def _deck(sampling=0.4, overwrite=True):
    return yaml.safe_dump(
        {
            "PeriLab": {
                "Discretization": {
                    "Type": "Gcode",
                    "Input Mesh File": "part.gcode",
                    "Gcode": {"Sampling": sampling, "Overwrite Mesh": overwrite},
                }
            }
        }
    )


class FakeClient:
    """The PeriLab job folder after a run: the uploaded deck and G-code plus the mesh PeriLab wrote."""

    def __init__(self, files):
        self.files = files

    def list_files(self, job_id):
        return list(self.files)

    def get_file(self, job_id, path):
        value = self.files[path]
        return value.encode() if isinstance(value, str) else value


def _write(folder, name, content):
    with open(os.path.join(folder, name), "w", encoding="UTF-8") as file:
        file.write(content)


def test_mesh_is_kept_until_gcode_or_settings_change(tmp_path):
    folder = str(tmp_path)
    mesh = os.path.join(folder, "part.txt")
    _write(folder, "part.gcode", "G1 X1")
    _write(folder, "part.yaml", _deck())

    gcode_mesh_cache.keep(
        FakeClient({"part.yaml": _deck(), "part.gcode": "G1 X1", "part.txt": "nodes"}), "j1", folder, "part.yaml"
    )
    assert open(mesh).read() == "nodes"

    # Same G-code and settings - Overwrite Mesh doesn't count - so the mesh stays.
    _write(folder, "part.yaml", _deck(overwrite=False))
    gcode_mesh_cache.drop_if_stale(folder, os.path.join(folder, "part.yaml"))
    assert os.path.exists(mesh)

    _write(folder, "part.yaml", _deck(sampling=0.2, overwrite=False))
    gcode_mesh_cache.drop_if_stale(folder, os.path.join(folder, "part.yaml"))
    assert not os.path.exists(mesh) and not os.path.exists(mesh + ".key")

    gcode_mesh_cache.keep(
        FakeClient({"part.yaml": _deck(0.2), "part.gcode": "G1 X1", "part.txt": "nodes"}), "j2", folder, "part.yaml"
    )
    _write(folder, "part.gcode", "G1 X2")  # a new upload with the same name
    gcode_mesh_cache.drop_if_stale(folder, os.path.join(folder, "part.yaml"))
    assert not os.path.exists(mesh)


def test_mesh_without_key_is_dropped(tmp_path):
    folder = str(tmp_path)
    _write(folder, "part.gcode", "G1 X1")
    _write(folder, "part.yaml", _deck())
    _write(folder, "part.txt", "unknown origin")
    gcode_mesh_cache.drop_if_stale(folder, os.path.join(folder, "part.yaml"))
    assert not os.path.exists(os.path.join(folder, "part.txt"))


def test_non_gcode_decks_are_left_alone(tmp_path):
    folder = str(tmp_path)
    _write(folder, "m.yaml", yaml.safe_dump({"PeriLab": {"Discretization": {"Type": "Text File"}}}))
    _write(folder, "m.txt", "generated mesh")
    gcode_mesh_cache.drop_if_stale(folder, os.path.join(folder, "m.yaml"))
    assert os.path.exists(os.path.join(folder, "m.txt"))
    gcode_mesh_cache.keep(FakeClient({"m.yaml": open(os.path.join(folder, "m.yaml")).read()}), "j", folder, "m.yaml")
