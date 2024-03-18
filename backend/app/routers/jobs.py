# SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import json
import os

import paramiko
from fastapi import APIRouter, HTTPException, Request

from support.base_models import Jobs, ModelData, ResponseModel, Status
from support.file_handler import FileHandler
from support.globals import dev, dlr, log, trial
from support.writer.sbatch_writer import SbatchCreator

router = APIRouter(prefix="/jobs", tags=["Jobs Methods"])


@router.put("/run")
async def run_model(
    model_data: ModelData,
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
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
    return_string = FileHandler.copy_model_to_cluster(username, model_name, model_folder_name, cluster)

    if return_string != "Success":
        raise HTTPException(
            status_code=404,
            detail=return_string,
        )

    return_string = FileHandler.copy_lib_to_cluster(username, model_name, model_folder_name, cluster, user_mat)
    if return_string != "Success":
        raise HTTPException(
            status_code=404,
            detail=return_string,
        )

    if cluster == "Cara":
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
        remotepath = "./PeridigmJobs/apiModels/" + os.path.join(username, model_name, model_folder_name)
        ssh, sftp = FileHandler.sftp_to_cluster("Cara")
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

    elif cluster == "None":
        server = "perihub_perilab"
        remotepath = "/simulations/" + os.path.join(username, model_name, model_folder_name)
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
        sh_string = sbatch.create_sh()
        with open(
            os.path.join("." + remotepath, "runPeridigm.sh"),
            "w",
            encoding="UTF-8",
        ) as file:
            file.write(sh_string)
        os.chmod(os.path.join("." + remotepath, "runPeridigm.sh"), 0o0755)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(
                server,
                username="root",
                allow_agent=False,
                password="root",
            )
        except paramiko.SSHException:
            log.error("ssh connection to %s failed!", server)
            return "ssh connection to " + server + " failed!"
        command = (
            "cd /app"
            + remotepath
            + " \n rm "
            + model_name
            + ".log \n sh /app"
            + remotepath
            + "/runPeridigm.sh > "
            + model_name
            + ".log 2>&1"
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


@router.put("/cancel")
def cancel_job(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    cluster: str = "None",
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    if cluster == "None":
        server = "perihub_perilab"
        remotepath = "/simulations/" + os.path.join(username, model_name, model_folder_name)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(
                server,
                username="root",
                allow_agent=False,
                password="root",
            )
        except paramiko.SSHException:
            log.error("ssh connection to %s failed!", server)
            return "ssh connection to " + server + " failed!"
        command = (
            "kill $(cat /app"
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
    command = "scancel -n " + model_name + "_" + model_folder_name
    ssh.exec_command(command)
    ssh.close()

    log.info("Job: %s has been canceled", model_name + "_" + model_folder_name)

    return ResponseModel(
        data=True,
        message="Job: " + model_name + "_" + model_folder_name + " has been canceled",
    )


@router.get("/getJobs")
def get_jobs(
    model_name: str = "Dogbone",
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    jobs = []

    localpath = os.path.join("./simulations", username, model_name)

    # print(localpath)

    if not os.path.exists(localpath):
        return ResponseModel(data=jobs, message="No jobs")

    if dlr and not dev:
        ssh, sftp = FileHandler.sftp_to_cluster("Cara")

    for _, dirs, _ in os.walk(localpath):
        # log.info(dirs)
        for model_folder_name in dirs:
            modelpath = os.path.join(localpath, model_folder_name)

            if os.path.exists(modelpath):
                job = Jobs(
                    id=len(jobs) + 1,
                    name=model_name,
                    sub_name=model_folder_name,
                    cluster="",
                    created=True,
                    submitted=False,
                    results=False,
                )

                remotepath = "./simulations/" + os.path.join(username, model_name, model_folder_name)
                if os.path.exists(os.path.join(remotepath)):
                    job.cluster = "None"
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
                        cluster="",
                        created=True,
                        submitted=False,
                        results=False,
                    )

                remotepath = "./PeridigmJobs/apiModels/" + os.path.join(username, model_name, model_folder_name)

                if dlr and not dev:
                    if FileHandler.sftp_exists(sftp=sftp, path=remotepath):
                        job.cluster = "Cara"
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

                        job.submitted = FileHandler.cara_job_running(remotepath, model_name, model_folder_name)

                        # print(job.cluster)
                        jobs.append(job)

    if dlr and not dev:
        sftp.close()
        ssh.close()

    return ResponseModel(data=jobs, message="Jobs found")


@router.get("/getStatus")
def get_status(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    own_mesh: bool = False,
    cluster: str = "None",
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    status = Status()

    localpath = "./simulations/" + os.path.join(username, model_name, model_folder_name)

    # log.info("localpath: %s", localpath)

    if os.path.exists(localpath):
        status.created = True

    if cluster == "None":
        remotepath = "./simulations/" + os.path.join(username, model_name, model_folder_name)
        # log.info(remotepath)
        if os.path.exists(os.path.join(remotepath, "pid.txt")):
            status.submitted = True
        if os.path.exists(remotepath):
            for files in os.listdir(remotepath):
                if ".e" in files:
                    status.results = True

    elif cluster == "Cara":
        remotepath = "./PeridigmJobs/apiModels/" + os.path.join(username, model_name, model_folder_name)
        ssh, sftp = FileHandler.sftp_to_cluster(cluster)

        try:
            for filename in sftp.listdir(remotepath):
                if ".e" in filename:
                    status.results = True
        except IOError:
            sftp.close()
            ssh.close()
            return ResponseModel(data=status, message="Status received")

        sftp.close()
        ssh.close()
        status.submitted = FileHandler.cara_job_running(remotepath, model_name, model_folder_name)

    return ResponseModel(data=status, message="Status received")
