"""
doc
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from fastapi import HTTPException

from ..support.globals import log


def safe_segment(name: str) -> str:
    """A single filesystem path segment, safe to join onto a trusted base path. Starlette percent-decodes path
    params (%2E%2E -> ..) and query/body strings are never decoded at all, so any of these must be rejected before
    they reach os.path.join/os.path.join-like string concatenation - otherwise ".." (or an embedded "/"/"\\")
    escapes the caller's own folder. Raises 400 rather than silently rewriting the value, so callers can't be
    fooled into thinking their file landed where they asked."""

    if not name or name in (".", "..") or "/" in name or "\\" in name or "\0" in name:
        raise HTTPException(status_code=400, detail="Invalid path segment.")
    return name


class FileHandler:
    """doc"""

    @staticmethod
    def get_local_simulation_path():
        """doc"""

        path = os.path.join(str(Path(__file__).parent.parent.resolve()), "simulations")
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    @staticmethod
    def get_local_user_path(username):
        """doc"""

        return os.path.join(FileHandler.get_local_simulation_path(), safe_segment(username))

    @staticmethod
    def get_local_model_path(username, model_name):
        """doc"""

        return os.path.join(FileHandler.get_local_user_path(username), safe_segment(model_name))

    @staticmethod
    def get_local_model_folder_path(username, model_name, model_folder_name):
        """doc"""

        return os.path.join(FileHandler.get_local_model_path(username, model_name), safe_segment(model_folder_name))

        # return "./peridigm/src/src/materials/umats/"

    @staticmethod
    def remove_folder_if_older(path, days, recursive):
        """doc"""

        now = time.time()
        names = []
        for foldername in os.listdir(path):
            folder_path = os.path.join(path, foldername)

            if os.path.getmtime(folder_path) < now - days * 86400:
                names.append(foldername)
                shutil.rmtree(folder_path)
            elif recursive:
                for subfoldername in os.listdir(folder_path):
                    if os.path.getmtime(os.path.join(folder_path, subfoldername)) < now - days * 86400:
                        names.append(os.path.join(foldername, subfoldername))
                        shutil.rmtree(os.path.join(folder_path, subfoldername))
        return names

    @staticmethod
    def install_frontmatter_requirements(requirements):
        """pip-installs an own model's comma-separated requirements, each once per environment: startup runs this
        for every own model, and pip re-clones a git URL even when it is installed, which held up every dev
        reload. The record lives in the temp dir, so it is gone whenever the packages might be (new container,
        reboot). ponytail: an edited requirement version is only picked up after that."""
        if not requirements:
            return
        record = Path(tempfile.gettempdir()) / f"perihub-installed-requirements-{sys.prefix.replace(os.sep, '_')}"
        installed = set(record.read_text().splitlines()) if record.exists() else set()
        for req in (r.strip() for r in requirements.split(",")):
            if not req or req in installed:
                continue
            print(f"Installing requirement: {req}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
            installed.add(req)
            record.write_text("\n".join(sorted(installed)))

    @staticmethod
    def get_all_output_files_with_extension(directory, model_name, output, extension, deviations_enabled):
        entries = os.listdir(directory)
        matching_files = []

        default_file = os.path.join(directory, model_name + "_" + output + extension)

        if not deviations_enabled and os.path.exists(default_file):
            return [default_file]

        for entry in entries:
            full_path = os.path.join(directory, entry)
            if (
                os.path.isfile(full_path)
                and (
                    entry.rsplit("_", 1)[0] == (model_name + "_" + output)
                    and entry.rsplit("_", 1)[1].split(".")[0].isdigit()
                    or entry.split(".")[0] == (model_name + "_" + output)
                )
                and entry.endswith(extension)
            ):
                matching_files.append(full_path)

        if len(matching_files) == 0:
            log.warning("No matching files found")
            raise HTTPException(status_code=404, detail="No matching files found")

        if len(matching_files) > 1 and os.path.exists(default_file):
            matching_files.remove(default_file)

        return sorted(matching_files, key=lambda f: [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", f)])
