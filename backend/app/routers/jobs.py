# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import json
import os
import socket

import paramiko
from fastapi import APIRouter, HTTPException, Request

from ..support.base_models import Jobs, ModelData, ResponseModel, Status
from ..support.file_handler import FileHandler
from ..support.globals import cluster_enabled, cluster_perilab_path, dev, log, trial
from ..support.writer.sbatch_writer import SbatchCreator

router = APIRouter(prefix="/jobs", tags=["Jobs Methods"])


@router.put("/run", operation_id="run_model")
async def run_model(
    model_data: ModelData,
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    verbose: bool = False,
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)
    usermail = FileHandler.get_user_mail(request)

    material = model_data.materials
    user_mat = False
    for mat in material:
        if mat.matType == "User Correspondence":
            user_mat = True
            break

    cluster = model_data.job.cluster
    sbatch = model_data.job.sbatch
    return_string = FileHandler.copy_model_to_cluster(username, model_name, model_folder_name, cluster)

    if return_string != "Success":
        return ResponseModel(
            data=False,
            message=return_string,
        )

    return_string = FileHandler.copy_lib_to_cluster(username, model_name, model_folder_name, cluster, user_mat)
    if return_string != "Success":
        return ResponseModel(
            data=False,
            message=return_string,
        )

    if cluster and sbatch:
        # initial_jobs = FileHandler.write_get_cara_job_id()
        # log.info(initial_jobs)
        sbatch = SbatchCreator(
            filename=model_name,
            model_folder_name=model_folder_name,
            output=model_data.outputs,
            job=model_data.job,
            usermail=usermail,
            trial=trial,
        )
        sbatch_string = sbatch.create_sbatch()
        remotepath = FileHandler.get_remote_model_path(username, model_name, model_folder_name)
        ssh, sftp = FileHandler.sftp_to_cluster(cluster)
        file = sftp.file(remotepath + "/" + model_name + ".sbatch", "w", -1)
        file.write(sbatch_string)
        file.flush()
        sftp.close()

        command = "cd " + remotepath + " \n sbatch " + model_name + ".sbatch"
        ssh.exec_command(command)
        ssh.close()

        log.info("%s has been submitted", model_name)
        return ResponseModel(
            data=True,
            message=model_name + " has been submitted",
        )

    elif cluster:
        remotepath = FileHandler.get_remote_model_path(username, model_name, model_folder_name)
        if os.path.exists(os.path.join("." + remotepath, "pid.txt")):
            log.warning("%s already submitted", model_name)
            return model_name + " already submitted"
        sbatch = SbatchCreator(
            filename=model_name,
            model_folder_name=model_folder_name,
            remotepath=remotepath,
            output=model_data.outputs,
            job=model_data.job,
            usermail=usermail,
            trial=trial,
        )
        sh_string = sbatch.create_sh(verbose, False, cluster_perilab_path)
        ssh, sftp = FileHandler.sftp_to_cluster(cluster)
        file = sftp.file(remotepath + "/" + "runPerilab.sh", "w", -1)
        file.write(sh_string)
        file.flush()
        sftp.close()

        command = 'bash --login -c "cd ' + remotepath + ' \n sh runPerilab.sh"'
        ssh.exec_command(command)
        ssh.close()

        log.info("%s has been submitted", model_name)
        return ResponseModel(
            data=True,
            message=model_name + " has been submitted",
        )

    elif not cluster:
        server = "perihub_perilab"
        remotepath = FileHandler.get_local_model_folder_path(username, model_name, model_folder_name)
        log.info(remotepath)
        if os.path.exists(os.path.join("." + remotepath, "pid.txt")):
            log.warning("%s already submitted", model_name)
            return model_name + " already submitted"
        sbatch = SbatchCreator(
            filename=model_name,
            model_folder_name=model_folder_name,
            remotepath=remotepath,
            output=model_data.outputs,
            job=model_data.job,
            usermail=usermail,
            trial=trial,
        )
        sh_string = sbatch.create_sh(verbose)
        with open(
            os.path.join(remotepath, "runPerilab.sh"),
            "w",
            encoding="UTF-8",
        ) as file:
            file.write(sh_string)
        os.chmod(os.path.join(remotepath, "runPerilab.sh"), 0o0755)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        while True:
            try:
                ssh.connect(
                    server,
                    port=22,
                    username="root",
                    allow_agent=False,
                    password="root",
                )
            except paramiko.SSHException:
                log.error("ssh connection to %s failed!", server)
                return ResponseModel(data=False, message="ssh connection to " + server + " failed!")
            except socket.gaierror:
                if server != "localhost":
                    server = "localhost"
                    log.info("retrying ssh connection to %s", server)
                    continue
                else:
                    log.error(
                        "ssh connection to %s failed! Is the PeriLab Service running?",
                        server,
                    )
                    return ResponseModel(
                        data=False,
                        message="ssh connection to " + server + " failed! Is the PeriLab Service running?",
                    )
            except Exception as e:
                log.error(type(e))
                log.error(
                    "ssh connection to %s failed! Is the PeriLab Service running?",
                    server,
                )
                return ResponseModel(
                    data=False,
                    message="ssh connection to " + server + " failed! Is the PeriLab Service running?",
                )
            break
        command = (
            "cd /app" + "/simulations/" + os.path.join(username, model_name, model_folder_name) + " \n sh runPerilab.sh"
        )
        ssh.exec_command(command)
        # stdin, stdout, stderr = ssh.exec_command('nohup python executefile.py >/dev/null 2>&1 &')
        # stdout=stdout.readlines()
        # stderr=stderr.readlines()
        ssh.close()

        # return stdout + stderr
        log.info("%s has been submitted", model_name)
        return ResponseModel(data=True, message=model_name + " has been submitted")

    log.error("%s unknown", cluster)
    return cluster + " unknown"


@router.put("/cancel", operation_id="cancel_job")
def cancel_job(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    cluster: bool = False,
    sbatch: bool = False,
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    if not cluster:
        server = "perihub_perilab"
        remotepath = "/simulations/" + os.path.join(username, model_name, model_folder_name)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        while True:
            try:
                ssh.connect(
                    server,
                    username="root",
                    allow_agent=False,
                    password="root",
                )
            except socket.gaierror:
                if server != "localhost":
                    server = "localhost"
                    continue
                else:
                    log.error("ssh connection to %s failed!", server)
                    return "ssh connection to " + server + " failed!"
            break
        command = (
            "kill -2 $(cat /app"
            + os.path.join(remotepath, "pid.txt")
            + ") \n rm /app"
            + os.path.join(remotepath, "pid.txt")
        )
        _, stdout, stderr = ssh.exec_command(command)
        stdout = stdout.readlines()
        stderr = stderr.readlines()
        ssh.close()

        log.info("Job has been canceled")
        return ResponseModel(data=True, message="Job has been canceled")

    remotepath = FileHandler.get_remote_model_path(username, model_name, model_folder_name)
    ssh, sftp = FileHandler.sftp_to_cluster(cluster)
    # try:
    #     output_files = sftp.listdir(remotepath)
    #     filtered_values = list(
    #         filter(lambda v: match(r"^.+\.log$", v), output_files)
    #     )
    # except paramiko.SFTPError:
    #     log.warning("LogFile can't be found")
    # if len(filtered_values) == 0:
    #     log.warning("LogFile can't be found")

    # job_id = filtered_values[-1].split("-")[-1][:-4]
    if sbatch:
        command = "scancel -n " + model_name + "_" + model_folder_name
        ssh.exec_command(command)
    else:
        command = (
            "kill -2 $(cat " + os.path.join(remotepath, "pid.txt") + ") \n rm " + os.path.join(remotepath, "pid.txt")
        )
        _, stdout, stderr = ssh.exec_command(command)
        stdout = stdout.readlines()
        stderr = stderr.readlines()
        # print(stdout)
        # print(stderr)
    ssh.close()

    log.info("Job: %s has been canceled", model_name + "_" + model_folder_name)

    return ResponseModel(
        data=True,
        message="Job: " + model_name + "_" + model_folder_name + " has been canceled",
    )


@router.get("/getJobFolders", operation_id="get_job_folders")
def get_job_folders(
    model_name: str = "Dogbone",
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    localpath = FileHandler.get_local_model_path(username, model_name)

    # print(localpath)

    if not os.path.exists(localpath):
        return ResponseModel(data=job_folders, message="No jobs")

    job_folders = next(os.walk(localpath))[1]

    return ResponseModel(data=job_folders, message="Jobs found")


@router.get("/getJobs", operation_id="get_jobs")
def get_jobs(
    model_name: str = "Dogbone",
    sbatch: bool = False,
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    jobs = []

    localpath = FileHandler.get_local_model_path(username, model_name)

    # print(localpath)

    if not os.path.exists(localpath):
        return ResponseModel(data=jobs, message="No jobs")

    cluster_accesible = True
    if cluster_enabled:
        try:
            ssh, sftp = FileHandler.sftp_to_cluster(True)
        except:
            cluster_accesible = False

    for _, dirs, _ in os.walk(localpath):
        # log.info(dirs)
        for model_folder_name in dirs:
            modelpath = os.path.join(localpath, model_folder_name)

            if os.path.exists(modelpath):
                job = Jobs(
                    id=len(jobs) + 1,
                    name=model_name,
                    sub_name=model_folder_name,
                    cluster=False,
                    created=True,
                    submitted=False,
                    results=False,
                )

                remotepath = FileHandler.get_local_model_folder_path(username, model_name, model_folder_name)
                if os.path.exists(os.path.join(remotepath)):
                    job.cluster = False
                    if os.path.exists(os.path.join(remotepath, "pid.txt")):
                        job.submitted = True

                    for filename in os.listdir(remotepath):
                        if filename.endswith(".e"):
                            job.results = True

                        if filename.endswith(".json"):
                            filepath = os.path.join(remotepath, filename)
                            with open(filepath) as f:
                                data = json.load(f)
                                job.model = data
                    # print(job.cluster)
                    jobs.append(job)
                    job = Jobs(
                        id=len(jobs) + 1,
                        name=model_name,
                        sub_name=model_folder_name,
                        cluster=False,
                        created=True,
                        submitted=False,
                        results=False,
                    )

                if cluster_enabled and cluster_accesible:
                    remotepath = FileHandler.get_remote_model_path(username, model_name, model_folder_name)
                    if FileHandler.sftp_exists(sftp=sftp, path=remotepath):
                        job.cluster = True
                        # try:
                        for filename in sftp.listdir(remotepath):
                            if filename.endswith(".e"):
                                job.results = True
                            if filename.endswith(".json"):
                                filepath = os.path.join(remotepath, filename)
                                with sftp.open(filepath) as f:
                                    data = json.load(f)
                                    job.model = data
                        # except IOError:
                        #     pass

                        if sbatch:
                            job.submitted = FileHandler.cluster_job_running(
                                ssh, sftp, remotepath, model_name, model_folder_name
                            )
                        else:
                            if "pid.txt" in sftp.listdir(remotepath):
                                job.submitted = True

                        # print(job.cluster)
                        jobs.append(job)

    if cluster_enabled and cluster_accesible:
        sftp.close()
        ssh.close()

    return ResponseModel(data=jobs, message="Jobs found")


@router.get("/getStatus", operation_id="get_status")
def get_status(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    meshfile: str = None,
    own_mesh: bool = False,
    cluster: bool = False,
    sbatch: bool = False,
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    status = Status()

    localpath = FileHandler.get_local_model_folder_path(username, model_name, model_folder_name)

    # log.info("localpath: %s", localpath)

    if os.path.exists(localpath):
        status.created = True

    if meshfile == None or os.path.exists(os.path.join(localpath, meshfile)):
        status.meshfileExist = True

    if cluster:
        remotepath = FileHandler.get_remote_model_path(username, model_name, model_folder_name)
        ssh, sftp = FileHandler.sftp_to_cluster(cluster)

        try:
            for filename in sftp.listdir(remotepath):
                if ".e" in filename:
                    status.results = True
        except IOError:
            sftp.close()
            ssh.close()
            return ResponseModel(data=status, message="Status received")

        if sbatch:
            status.submitted = FileHandler.cluster_job_running(ssh, sftp, remotepath, model_name, model_folder_name)
        else:
            if "pid.txt" in sftp.listdir(remotepath):
                status.submitted = True
        sftp.close()
        ssh.close()

    else:
        remotepath = FileHandler.get_local_model_folder_path(username, model_name, model_folder_name)
        # log.info(remotepath)
        if os.path.exists(os.path.join(remotepath, "pid.txt")):
            status.submitted = True
        if os.path.exists(remotepath):
            for files in os.listdir(remotepath):
                if ".e" in files:
                    status.results = True

    return ResponseModel(data=status, message="Status received")
