"""
doc
"""
import filecmp
import json
import os
import shutil
import time

import jwt
import paramiko
from support.globals import log


class FileHandler:
    """doc"""

    @staticmethod
    def get_remote_path():
        """doc"""

        return "./PeridigmJobs/apiModels/"

    @staticmethod
    def get_remote_model_path(username, model_name):
        """doc"""

        return "./PeridigmJobs/apiModels/" + username + "/" + model_name

    @staticmethod
    def _get_remote_umat_path(cluster):
        """doc"""

        if cluster == "None":
            return "/Peridigm/src/materials/umats/"
        if cluster == "Cara":
            return "/home/f_peridi/software/peridigm/"
        return "./peridigm/src/src/materials/umats/"

    @staticmethod
    def get_remote_user_path(username):
        """doc"""

        return "./PeridigmJobs/apiModels/" + username

    @staticmethod
    def _get_user_path(username):
        """doc"""

        return "./PeridigmJobs/apiModels/" + username

    @staticmethod
    def get_user_name(request, dev):
        """doc"""
        if dev:
            return "dev"

        encoded_token = request.headers.get("Authorization")
        print(encoded_token)
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

        with open("./support/allowedMaxNodes.json", "r", encoding="UTF-8") as file:
            data = json.load(file)

        if username in data:
            return data[username]["allowedNodes"]

        return data["guest"]["allowedNodes"]

    @staticmethod
    def get_max_fe_size(username):
        """doc"""

        with open("./support/allowedMaxNodes.json", "r", encoding="UTF-8") as file:
            data = json.load(file)

        if username in data:
            return data[username]["allowedFeSize"]

        return data["guest"]["allowedFeSize"]

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
                    if (
                        os.path.getmtime(os.path.join(folder_path, subfoldername))
                        < now - days * 86400
                    ):
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
                    if (
                        os.path.getmtime(os.path.join(folder_path, subfoldername))
                        < now - days * 86400
                    ):
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
            for subfilename in sftp.listdir(os.path.join(remotepath, filename)):
                if recursive:
                    for sub_sub_file_name in sftp.listdir(
                        os.path.join(remotepath, subfilename)
                    ):
                        sftp.remove(os.path.join(remotepath, sub_sub_file_name))
                sftp.remove(os.path.join(remotepath, subfilename))
            sftp.remove(os.path.join(remotepath, filename))
        sftp.rmdir(remotepath)

    @staticmethod
    def copy_model_to_cluster(username, model_name, cluster):
        """doc"""

        if cluster == "None":
            localpath = "./Output/" + os.path.join(username, model_name)
            remotepath = "./peridigmJobs/" + os.path.join(username, model_name)
            if not os.path.exists(remotepath):
                os.makedirs(remotepath)
                # os.chown(remotepath, 'test')
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
                    if (
                        name.split(".")[-1] == "txt"
                        or name.split(".")[-1] == "e"
                        or name.split(".")[-1] == "g"
                    ):
                        mesh_exist = True

                if not input_exist:
                    log.warning(
                        "Inputfile of " + model_name + " has not been created yet"
                    )
                    return "Inputfile of " + model_name + " has not been created yet"

                if not mesh_exist:
                    log.warning(
                        "Meshfile of " + model_name + " has not been created yet"
                    )
                    return "Meshfile of " + model_name + " has not been created yet"

                for name in files:
                    shutil.copy(
                        os.path.join(root, name),
                        os.path.join(remotepath, name),
                    )
                    # os.chmod(os.path.join(remotepath,name), 0o0777)
                    # os.chown(os.path.join(remotepath,name), 'test')
            return "Success"

        localpath = "./Output/" + os.path.join(username, model_name)
        remotepath = FileHandler.get_remote_model_path(username, model_name)
        userpath = FileHandler._get_user_path(username)
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
    def copy_lib_to_cluster(username, model_name, cluster):
        """doc"""

        localpath = "./Output/" + os.path.join(username, model_name)
        remotepath = FileHandler._get_remote_umat_path(cluster)
        try:
            ssh, sftp = FileHandler.sftp_to_cluster(cluster)
        except paramiko.SFTPError:
            log.error("ssh connection to " + cluster + " failed!")
            return "ssh connection to " + cluster + " failed!"

        if not os.path.exists(localpath):
            log.error("Shared libray can not been found")
            return "Shared libray can not been found"
        for root, _, files in os.walk(localpath):
            if len(files) == 0:
                log.error("Shared libray can not been found")
            for name in files:
                if name.split(".")[-1] == "so":
                    print(os.path.join(root, name))
                    print(os.path.join(remotepath, "libusermat.so"))
                    sftp.put(
                        os.path.join(root, name),
                        os.path.join(remotepath, "libusermat.so"),
                    )
                    return "Success"

        sftp.close()
        ssh.close()

        log.error("Shared libray can not been found")
        return "Shared libray can not been found"

    @staticmethod
    def copy_file_to_from_peridigm_container(
        username, model_name, file_name, to_or_from
    ):
        """doc"""

        localpath = "./Output/" + os.path.join(username, model_name)
        remotepath = "./peridigmJobs/" + os.path.join(username, model_name)
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
        username, model_name, cluster, all_data, filetype=".e"
    ):
        """doc"""
        resultpath = "./Results/" + os.path.join(username, model_name)
        if not os.path.exists(resultpath):
            os.makedirs(resultpath)

        if cluster == "None":
            remotepath = "./peridigmJobs/" + os.path.join(username, model_name)
            for _, _, files in os.walk(remotepath):
                if len(files) == 0:
                    return False

                for filename in files:
                    if all_data or filetype in filename:
                        if os.path.exists(os.path.join(resultpath, filename)):
                            if not filecmp.cmp(
                                os.path.join(remotepath, filename),
                                os.path.join(resultpath, filename),
                            ):
                                shutil.copy(
                                    os.path.join(remotepath, filename),
                                    os.path.join(resultpath, filename),
                                )
                        else:
                            shutil.copy(
                                os.path.join(remotepath, filename),
                                os.path.join(resultpath, filename),
                            )
                    # os.chmod(os.path.join(remotepath,name), 0o0777)
                    # os.chown(os.path.join(remotepath,name), 'test')
            return True

        remotepath = FileHandler.get_remote_model_path(username, model_name)
        ssh, sftp = FileHandler.sftp_to_cluster(cluster)
        try:
            for filename in sftp.listdir(remotepath):
                if all_data or ".e" in filename:
                    if os.path.exists(os.path.join(resultpath, filename)):
                        remote_info = sftp.stat(os.path.join(remotepath, filename))
                        remote_size = remote_info.st_size
                        local_size = os.path.getsize(os.path.join(resultpath, filename))
                        print(
                            "compare "
                            + filename
                            + " remote_size: "
                            + str(remote_size)
                            + ", localsize: "
                            + str(local_size)
                        )
                        if abs(remote_size - local_size) > 5:
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
        return True

    @staticmethod
    def sftp_to_cluster(cluster):
        """doc"""

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if cluster == "FA-Cluster":
            username = "f_peridi"
            server = "129.247.54.37"
            keypath = "./rsaFiles/id_rsa_cluster"
            try:
                ssh.connect(
                    server,
                    username=username,
                    allow_agent=False,
                    key_filename=keypath,
                )
            except paramiko.SSHException:
                log.error("ssh connection to " + server + " failed!")
                return "ssh connection to " + server + " failed!"

        elif cluster == "Cara":
            username = "f_peridi"
            server = "cara.dlr.de"
            keypath = "./rsaFiles/id_rsa_cara"
            try:
                ssh.connect(
                    server,
                    username=username,
                    allow_agent=False,
                    key_filename=keypath,
                )
            except paramiko.SSHException:
                log.error("ssh connection to " + server + " failed!")
                return "ssh connection to " + server + " failed!"

        elif cluster == "None":
            username = "root"
            server = "perihub_peridigm"
            try:
                ssh.connect(
                    server,
                    username=username,
                    allow_agent=False,
                    password="root",
                )
            except paramiko.SSHException:
                log.error("ssh connection to " + server + " failed!")
                return "ssh connection to " + server + " failed!"

        sftp = ssh.open_sftp()
        return ssh, sftp

    @staticmethod
    def ssh_to_cluster(cluster):
        """doc"""

        if cluster == "FA-Cluster":
            username = "f_peridi"
            server = "129.247.54.37"
            keypath = "./rsaFiles/id_rsa_cluster"

        elif cluster == "Cara":
            username = "f_peridi"
            server = "cara.dlr.de"
            keypath = "./rsaFiles/id_rsa_cara"

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(
                server,
                username=username,
                allow_agent=False,
                key_filename=keypath,
            )
        except paramiko.SSHException:
            log.error("ssh connection to " + server + " failed!")
            return "ssh connection to " + server + " failed!"
        return ssh

    @staticmethod
    def write_get_cara_job_id():
        """doc"""
        ssh, sftp = FileHandler.sftp_to_cluster("Cara")
        command = " squeue -u f_peridi | grep -o -E '[0-9]{7}' > jobIds.txt"
        ssh.exec_command(command)
        job_ids_file = sftp.file("./jobIds.txt", "r")
        job_ids = job_ids_file.read()
        sftp.close()
        ssh.close()
        return str(job_ids)

    @staticmethod
    def write_cara_job_id_to_model(username, model_name, job_id):
        """doc"""
        localpath = "./Output/" + os.path.join(username, model_name)

        if not os.path.exists(localpath):
            os.makedirs(localpath)

        job_id_file = os.path.join(localpath, "jobId.txt")

        with open(job_id_file, "w", encoding="UTF-8") as file:
            file.write(job_id)

    @staticmethod
    def get_cara_job_id_model(username, model_name):
        """doc"""
        localpath = "./Output/" + os.path.join(username, model_name)
        job_id_path = os.path.join(localpath, "jobId.txt")

        if not os.path.exists(job_id_path):
            log.error("No pid")
            return "No pid"

        with open(job_id_path, "r", encoding="UTF-8") as file:
            response = file.read()

        return str(response)
