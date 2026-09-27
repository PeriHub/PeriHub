# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""
doc
"""

import ast
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from fastapi import HTTPException
from natsort import natsorted

from ..support.globals import log, trial

allowed_max_nodes = {
    "trial": {"allowedNodes": 10000, "allowedFeSize": 150000},
    "guest": {"allowedNodes": 1000000, "allowedFeSize": 15000000},
    "dev": {"allowedNodes": 10000000, "allowedFeSize": 150000000},
}


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

        return os.path.join(FileHandler.get_local_simulation_path(), username)

    @staticmethod
    def get_local_model_path(username, model_name):
        """doc"""

        return os.path.join(FileHandler.get_local_user_path(username), model_name)

    @staticmethod
    def get_local_model_folder_path(username, model_name, model_folder_name):
        """doc"""

        return os.path.join(FileHandler.get_local_model_path(username, model_name), model_folder_name)

        # return "./peridigm/src/src/materials/umats/"

    @staticmethod
    def get_user_name(request, dev):
        """doc"""
        user_name = request.headers.get("userName")
        if user_name is not None and user_name != "" and user_name != "undefined":
            return user_name
        return "user"

    @staticmethod
    def get_max_nodes(username):
        """doc"""
        if trial:
            return allowed_max_nodes["trial"]["allowedNodes"]

        if username in allowed_max_nodes:
            return allowed_max_nodes[username]["allowedNodes"]

        return allowed_max_nodes["guest"]["allowedNodes"]

    @staticmethod
    def get_max_fe_size(username):
        """doc"""
        if trial:
            return allowed_max_nodes["trial"]["allowedFeSize"]

        if username in allowed_max_nodes:
            return allowed_max_nodes[username]["allowedFeSize"]

        return allowed_max_nodes["guest"]["allowedFeSize"]

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
    def get_docstring(script_path):
        if not os.path.exists(script_path):
            return
        with open(script_path, "r") as file:
            tree = ast.parse(file.read())
            return ast.get_docstring(tree, clean=False)

    @staticmethod
    def doc_to_dict(docstring):
        lines = docstring.split("\n")
        doc_dict = {}

        for line in lines:
            if ":" in line:
                param, desc = line.split(":", 1)
                doc_dict[param.strip("| ")] = desc.strip()
        return doc_dict

    @staticmethod
    def install_frontmatter_requirements(requirements):
        if requirements:
            req_list = [req.strip() for req in requirements.split(",")]
            for req in req_list:
                print(f"Installing requirement: {req}")
                subprocess.check_call([sys.executable, "-m", "pip", "install", req])

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

        return natsorted(matching_files)
