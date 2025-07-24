# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""
doc
"""
import ast
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import jwt
import paramiko
from fastapi import HTTPException
from random_username.generate import generate_username

from ..support.globals import (
    cluster_job_path,
    cluster_password,
    cluster_url,
    cluster_user,
    log,
    trial,
)

allowed_max_nodes = {
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

    @staticmethod
    def get_remote_path():
        """doc"""

        return cluster_job_path

    @staticmethod
    def get_remote_user_path(username):
        """doc"""

        return os.path.join(FileHandler.get_remote_path(), username)

    @staticmethod
    def get_remote_model_path(username, model_name, model_folder_name):
        """doc"""

        return os.path.join(FileHandler.get_remote_user_path(username), model_name, model_folder_name)

    @staticmethod
    def _get_remote_umat_path(cluster):
        """doc"""

        if not cluster:
            return "/Peridigm/src/materials/umats/"
        else:
            return "/home/f_peridi/software/peridigm/"
        # return "./peridigm/src/src/materials/umats/"

    @staticmethod
    def _get_user_path(username):
        """doc"""

        return "./PeridigmJobs/apiModels/" + username

    @staticmethod
    def get_user_name_from_token(encoded_token, dev):
        """doc"""

        if dev:
            return "dev"

        if encoded_token is None or encoded_token == "" or encoded_token == "undefined":
            return "guest"

        decoded_token = jwt.decode(encoded_token.split(" ")[1], options={"verify_signature": False})

        return decoded_token["preferred_username"]

    @staticmethod
    def get_user_name(request, dev):
        """doc"""
        if dev:
            return "dev"

        user_name = request.headers.get("userName")
        if user_name is not None and user_name != "" and user_name != "undefined":
            return user_name

        encoded_token = request.headers.get("Authorization")
        if encoded_token is None or encoded_token == "":
            return "guest"

        decoded_token = jwt.decode(
            encoded_token.split(" ")[1],
            options={"verify_signature": False},
        )

        return decoded_token["preferred_username"]

    @staticmethod
    def get_max_nodes(username):
        """doc"""

        if username in allowed_max_nodes:
            return allowed_max_nodes[username]["allowedNodes"]

        return allowed_max_nodes["guest"]["allowedNodes"]

    @staticmethod
    def get_max_fe_size(username):
        """doc"""

        if username in allowed_max_nodes:
            return allowed_max_nodes[username]["allowedFeSize"]

        return allowed_max_nodes["guest"]["allowedFeSize"]

    @staticmethod
    def get_user_mail(request):
        """doc"""
        encoded_token = request.headers.get("Authorization")
        if encoded_token is None or encoded_token == "":
            return ""

        decoded_token = jwt.decode(
            encoded_token.split(" ")[1],
            options={"verify_signature": False},
        )

        return decoded_token["email"]

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
    def remove_folder_if_older_sftp(sftp: paramiko.SFTPClient, path, days, recursive):
        """doc"""

        now = time.time()
        names = []
        for foldername in sftp.listdir(path):
            folder_path = os.path.join(path, foldername)

            if os.path.getmtime(folder_path) < now - days * 86400:
                FileHandler.remove_all_folder_sftp(sftp, folder_path, True)
                names.append(foldername)
            elif recursive:
                for subfoldername in sftp.listdir(folder_path):
                    if os.path.getmtime(os.path.join(folder_path, subfoldername)) < now - days * 86400:
                        names.append(os.path.join(folder_path, subfoldername))
                        FileHandler.remove_all_folder_sftp(
                            sftp,
                            os.path.join(folder_path, subfoldername),
                            True,
                        )
        return names

    @staticmethod
    def remove_all_folder_sftp(sftp: paramiko.SFTPClient, remotepath, recursive):
        """doc"""

        for filename in sftp.listdir(remotepath):
            for sub_filename in sftp.listdir(os.path.join(remotepath, filename)):
                for sub_sub_file_name in sftp.listdir(os.path.join(remotepath, sub_filename)):
                    if recursive:
                        for sub_sub_sub_file_name in sftp.listdir(os.path.join(remotepath, sub_sub_file_name)):
                            sftp.remove(os.path.join(remotepath, sub_sub_sub_file_name))
                    sftp.remove(os.path.join(remotepath, sub_sub_file_name))
                sftp.remove(os.path.join(remotepath, sub_filename))
            sftp.remove(os.path.join(remotepath, filename))
        sftp.rmdir(remotepath)

    @staticmethod
    def remove_all_folder_ssh(ssh: paramiko.SSHClient, remotepath):
        """doc"""

        # Remove the folder and its contents
        stdin, stdout, stderr = ssh.exec_command("rm -rf " + remotepath)

        # Print the output and any errors
        print(stdout.read().decode())
        print(stderr.read().decode())

    @staticmethod
    def copy_model_to_cluster(username, model_name, model_folder_name, cluster):
        """doc"""

        if not cluster:
            return "Success"

        localpath = FileHandler.get_local_model_folder_path(username, model_name, model_folder_name)
        remotepath = FileHandler.get_remote_model_path(username, model_name, model_folder_name)
        userpath = FileHandler.get_remote_user_path(username)
        ssh, sftp = FileHandler.sftp_to_cluster(cluster)

        try:
            sftp.chdir(userpath)
        except FileNotFoundError:
            sftp.mkdir(userpath)
            sftp.chdir(userpath)

        try:
            sftp.chdir(model_name)  # Test if remote_path exists
        except FileNotFoundError:
            sftp.mkdir(model_name)  # Create remote_path
            sftp.chdir(model_name)

        try:
            sftp.chdir(model_folder_name)  # Test if remote_path exists
        except FileNotFoundError:
            sftp.mkdir(model_folder_name)  # Create remote_path
            sftp.chdir(model_folder_name)

        if not os.path.exists(localpath):
            log.warning(model_name + " has not been created yet")
            return model_name + " has not been created yet"
        for root, _, files in os.walk(localpath):
            if len(files) == 0:
                log.warning(model_name + " has not been created yet")
                return model_name + " has not been created yet"
            input_exist = False
            mesh_exist = False
            for name in files:
                if name.split(".")[-1] == "yaml":
                    input_exist = True
                if name.split(".")[-1] == "txt" or name.split(".")[-1] == "e":
                    mesh_exist = True

            if not input_exist:
                log.warning("Inputfile of " + model_name + " has not been created yet")
                return "Inputfile of " + model_name + " has not been created yet"

            if not mesh_exist:
                log.warning("Meshfile of " + model_name + " has not been created yet")
                return "Meshfile of " + model_name + " has not been created yet"

            for name in files:
                sftp.put(os.path.join(root, name), name)

        sftp.close()
        ssh.close()

        return "Success"

    @staticmethod
    def copy_lib_to_cluster(username, model_name, model_folder_name, cluster, user_mat):
        """doc"""

        if not cluster:
            return "Success"

        localpath = FileHandler.get_local_model_folder_path(username, model_name, model_folder_name)
        remotepath = FileHandler._get_remote_umat_path(cluster)
        try:
            ssh, sftp = FileHandler.sftp_to_cluster(cluster)
        except paramiko.SFTPError:
            log.error("ssh connection to cluster failed!")
            return "ssh connection to cluster failed!"
        except Exception as e:
            return str(e)

        if not os.path.exists(localpath):
            log.error("Shared libray can not been found")
            return "Shared libray can not been found"
        for root, _, files in os.walk(localpath):
            if len(files) == 0:
                log.error("Shared libray can not been found")
            for name in files:
                lib_file_path = os.path.join(remotepath, "libusermat.so")
                lib_base_file_path = os.path.join(remotepath, "libusermat_base.so")
                if user_mat:
                    if name.split(".")[-1] == "so":
                        try:
                            print(sftp.stat(lib_base_file_path))
                        except IOError:
                            sftp.rename(
                                lib_file_path,
                                lib_base_file_path,
                            )
                        sftp.put(
                            os.path.join(root, name),
                            lib_file_path,
                        )
                        return "Success"
                else:
                    try:
                        print(sftp.stat(lib_base_file_path))
                        # sftp.remove(lib_file_path)
                        sftp.rename(
                            lib_base_file_path,
                            lib_file_path,
                        )
                        return "Success"
                    except IOError:
                        return "Success"

        sftp.close()
        ssh.close()

        log.error("Shared libray can not been found")
        return "Shared libray can not been found"

    @staticmethod
    def copy_file_to_from_peridigm_container(username, model_name, model_folder_name, file_name, to_or_from):
        """doc"""

        localpath = FileHandler.get_local_model_folder_path(username, model_name, model_folder_name)
        remotepath = "./simulations/" + os.path.join(username, model_name, model_folder_name)
        if not os.path.exists(remotepath):
            os.makedirs(remotepath)
            # os.chown(remotepath, 'test')
        if not os.path.exists(localpath):
            log.error(model_name + " has not been created yet")
            return model_name + " has not been created yet"

        try:
            if to_or_from:
                shutil.copy(
                    os.path.join(localpath, file_name),
                    os.path.join(remotepath, file_name),
                )
            else:
                shutil.copy(
                    os.path.join(remotepath, file_name),
                    os.path.join(localpath, file_name),
                )
        except IOError:
            log.error("File not found")
            return "File not found"

        return "Success"

    @staticmethod
    def copy_results_from_cluster(
        username,
        model_name,
        model_folder_name,
        cluster,
        all_data,
        tasks,
        output,
        filetype=".e",
    ):
        """doc"""
        resultpath = "./simulations/" + os.path.join(username, model_name, model_folder_name)
        if not os.path.exists(resultpath):
            os.makedirs(resultpath)

        if not cluster:
            return True

        log.info("Start copying")

        remotepath = FileHandler.get_remote_model_path(username, model_name, model_folder_name)
        ssh, sftp = FileHandler.sftp_to_cluster(cluster)
        # if tasks != 1:
        #     try:
        #         command = "module load netCDF" + "\n"
        #         command += "module load GCCcore/10.2.0" + "\n"
        #         command += (
        #             "cd "
        #             + remotepath
        #             + "\n python /home/f_peridi/peridigm/build/scripts/MergeFiles.py "
        #             + model_name
        #             + "_"
        #             + output
        #             + " "
        #             + str(tasks)
        #         )
        #         ssh.exec_command(command)
        #     except Exception:
        #         log.error("MergeFiles.py failed")
        #         pass
        try:
            for filename in sftp.listdir(remotepath):
                if all_data or filename.endswith(".e"):
                    if os.path.exists(os.path.join(resultpath, filename)):
                        remote_info = sftp.stat(os.path.join(remotepath, filename))
                        remote_time = remote_info.st_mtime
                        # remote_size = remote_info.st_size
                        local_time = os.path.getmtime(os.path.join(resultpath, filename))
                        # local_size = os.path.getsize(os.path.join(resultpath, filename))
                        print(
                            "compare "
                            + filename
                            + " remote_time: "
                            + str(remote_time)
                            + ", local_time: "
                            + str(local_time)
                        )
                        if remote_time > local_time:
                            os.remove(os.path.join(resultpath, filename))
                            log.info("Copy " + filename)
                            sftp.get(
                                os.path.join(remotepath, filename),
                                os.path.join(resultpath, filename),
                            )
                    else:
                        sftp.get(
                            os.path.join(remotepath, filename),
                            os.path.join(resultpath, filename),
                        )
        except paramiko.SFTPError:
            return False
        sftp.close()
        ssh.close()
        log.info("Copied")
        return True

    @staticmethod
    def sftp_to_cluster(cluster):
        """doc"""

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if cluster:
            username = cluster_user
            server = cluster_url
            password = cluster_password
            # keypath = "./rsaFiles/id_rsa_cluster"
            # log.info("ssh connection to " + server + " with user: " + username)
            try:
                ssh.connect(
                    server,
                    username=username,
                    allow_agent=False,
                    password=password,
                    # key_filename=keypath,
                )
            except paramiko.SSHException:
                log.error("ssh connection to " + server + " failed!")
                raise HTTPException(status_code=400, detail="ssh connection to " + server + " failed!")
            except socket.gaierror as e:
                log.error(f"ssh connection to {server} failed: {e}")
                raise HTTPException(status_code=400, detail=f"ssh connection to {server} failed: {e}")

        elif not cluster:
            username = "root"
            server = "perihub_perilab"

            while True:
                try:
                    ssh.connect(
                        server,
                        username=username,
                        allow_agent=False,
                        password="root",
                    )
                except paramiko.SSHException:
                    if server != "localhost":
                        server = "localhost"
                        continue
                    else:
                        log.error(
                            "ssh connection to %s failed! Is the PeriLab Service running?",
                            server,
                        )
                        raise Exception("ssh connection to " + server + " failed! Is the PeriLab Service running?")
                except Exception as e:
                    log.error("An error occurred:", e)
                    raise Exception("An error occurred:" + e)
                break

        sftp = ssh.open_sftp()
        return ssh, sftp

    @staticmethod
    def sftp_exists(sftp, path):
        try:
            sftp.stat(path)
            return True
        except FileNotFoundError:
            return False

    @staticmethod
    def ssh_to_cluster(cluster):
        """doc"""

        if cluster:
            username = cluster_user
            server = cluster_url
            keypath = "./rsaFiles/id_rsa_cluster"
            # password = cluster_password

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(
                server,
                username=username,
                allow_agent=False,
                # password=password,
                key_filename=keypath,
            )
        except paramiko.SSHException:
            log.error("ssh connection to " + server + " failed!")
            return "ssh connection to " + server + " failed!"
        return ssh

    @staticmethod
    def cluster_job_running(remotepath, model_name, model_folder_name):
        """doc"""
        ssh, sftp = FileHandler.sftp_to_cluster(True)
        command = (
            "cd "
            + remotepath
            + " \n squeue -n "
            + model_name
            + "_"
            + model_folder_name
            + " | grep -o -E '[0-9]{7}' > jobId.txt"
        )
        ssh.exec_command(command)
        job_id_path = os.path.join(remotepath, "jobId.txt")
        job_id = None
        if FileHandler.sftp_exists(sftp=sftp, path=job_id_path):
            job_id_file = sftp.file(job_id_path, "r")
            job_id = job_id_file.read()
        sftp.close()
        ssh.close()
        return len(str(job_id)) > 5

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

    # @staticmethod
    # def write_get_cara_job_ids():
    #     """doc"""
    #     ssh, sftp = FileHandler.sftp_to_cluster(True)
    #     command = " squeue -u f_peridi | grep -o -E '[0-9]{7}' > jobIds.txt"
    #     ssh.exec_command(command)
    #     job_ids_file = sftp.file("./jobIds.txt", "r")
    #     job_ids = job_ids_file.read()
    #     sftp.close()
    #     ssh.close()
    #     return str(job_ids)

    # @staticmethod
    # def write_cara_job_id_to_model(localpath, job_id):
    #     """doc"""

    #     if not os.path.exists(localpath):
    #         os.makedirs(localpath)

    #     job_id_file = os.path.join(localpath, "jobId.txt")

    #     with open(job_id_file, "w", encoding="UTF-8") as file:
    #         file.write(job_id)

    # @staticmethod
    # def get_cara_job_id_model(localpath):
    #     """doc"""
    #     job_id_path = os.path.join(localpath, "jobId.txt")

    #     if not os.path.exists(job_id_path):
    #         log.error("No pid")
    #         return "No pid"

    #     with open(job_id_path, "r", encoding="UTF-8") as file:
    #         response = file.read()

    #     return str(response)
