"""
doc
"""
# Copyright (C) 2021 Deutsches Zentrum fuer Luft- und Raumfahrt(DLR, German Aerospace Center) <www.dlr.de>

# pylint: disable=no-self-argument, no-method-argument, no-member, import-error

# import uvicorn
import csv
import io
import json
import os
import re
import shutil
import subprocess
import time
import zipfile
from re import match
from typing import List, Optional

import paramiko
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Request, UploadFile, status

# from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from gcodereader import gcodereader

from models.CompactTension.compact_tension import CompactTension
from models.DCBmodel.dcb_model import DCBmodel
from models.Dogbone.dogbone import Dogbone
from models.ENFmodel.enf_model import ENFmodel

# from fastapi.responses import HTMLResponse
# from fastapi.responses import StreamingResponse
from models.KalthoffWinkler.kalthoff_winkler import KalthoffWinkler
from models.OwnModel.own_model import OwnModel
from models.PlateWithHole.plate_with_hole import PlateWithHole
from models.PlateWithOpening.plate_with_opening import PlateWithOpening
from models.Smetana.smetana import Smetana
from support.analysis import Analysis
from support.base_models import FileType, Jobs, ModelData, ResponseModel, Status
from support.crack_analysis import CrackAnalysis
from support.file_handler import FileHandler
from support.globals import log
from support.image_export import ImageExport
from support.sbatch_creator import SbatchCreator
from support.video_export import VideoExport

# from fa_pyutils.sshtools import cara
# import fa_pyutils.service.duration as duration


# class NotFoundException(Exception):
#     """doc"""

#     def __init__(self, name: str):
#         """doc"""
#         self.name = name


tags_metadata = [
    {
        "name": "Post Methods",
        "description": "Generate, translate or upload models",
    },
    {"name": "Put Methods", "description": "Run, cancel or write jobs"},
    {
        "name": "Get Methods",
        "description": "Get mesh files, input files or postprocessing data",
    },
    {
        "name": "Delete Methods",
        "description": "Delete user or model data",
    },
    {
        "name": "Documentation Methods",
        "description": "Retrieve markdown documentation or bibtex files",
    },
]

app = FastAPI(openapi_tags=tags_metadata)

app.mount("/assets", StaticFiles(directory="assets"), name="assets")

origins = [
    "http://localhost",
    "http://localhost:6010",
    "http://localhost:8080",
    "https://localhost:6010",
    "http://fa-jenkins2:6010",
    "https://fa-jenkins2:6010",
    "https://perihub.fa-services.intra.dlr.de",
    "https://bpmn.nimbus.dlr.de",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

dev = os.getenv("DEV")
internal = os.getenv("INTERNAL")
if dev == "True":
    log.info("--- Running in development mode ---")
if internal == "True":
    log.info("--- Running in internal mode ---")
    from shepard_client.models.influx_point import InfluxPoint
    from shepard_client.models.timeseries import Timeseries
    from shepard_client.models.timeseries_payload import TimeseriesPayload


class ModelControl:
    """doc"""

    # @app.exception_handler(NotFoundException)
    # async def notFound_exception_handler(request: Request, exc: NotFoundException):
    #     """doc"""
    #     return JSONResponse(
    #         status_code=404,
    #         content={"message": f"{exc.name} can't be found"},
    #     )

    @app.post("/generateModel", tags=["Post Methods"])
    def generate_model(
        model_data: ModelData,
        model_name: str = "Dogbone",
        model_folder_name: str = "Default",
        request: Request = "",
    ):  # material: dict, Output: dict):
        """doc"""

        username = FileHandler.get_user_name(request, dev)

        max_nodes = FileHandler.get_max_nodes(username)

        localpath = FileHandler.get_local_model_path(username, model_name, model_folder_name)

        if not os.path.exists(localpath):
            os.makedirs(localpath)

        json_file = os.path.join(localpath, model_name + ".json")
        ignore_mesh = False

        if os.path.exists(json_file):
            with open(json_file, "r", encoding="UTF-8") as file:
                json_data = json.load(file)
                print(model_data.model)
                if (
                    model_data.model == json_data["model"]
                    and model_data.boundaryConditions == json_data["boundaryConditions"]
                ):
                    log.info("Model not changed")
                    ignore_mesh = True

        with open(json_file, "w", encoding="UTF-8") as file:
            file.write(model_data.to_json())

        # length = 152
        # length = 50
        # width = 10
        # height = 4.95
        # number_nodes = 12

        length = model_data.model.length
        cracklength = model_data.model.cracklength
        width = model_data.model.width
        height = model_data.model.height
        if model_name in {"Dogbone", "Kalthoff-Winkler"}:
            number_nodes = 2 * int(model_data.model.discretization / 2)
        else:
            number_nodes = 2 * int(model_data.model.discretization / 2) + 1
        if model_name in {"CompactTension"}:
            dx_value = [
                1.25 * length / number_nodes,
                1.25 * length / number_nodes,
                1.25 * length / number_nodes,
            ]
        elif model_name in {"Smetana"}:
            dx_value = [
                8 * height / number_nodes,
                8 * height / number_nodes,
                8 * height / number_nodes,
            ]
        else:
            dx_value = [
                height / number_nodes,
                height / number_nodes,
                height / number_nodes,
            ]

        start_time = time.time()

        log.info("Create %s", model_name)

        if model_data.model.ownModel is False:
            if model_name == "ENFmodel":
                enf = ENFmodel(
                    model_data=model_data,
                    model_folder_name=model_folder_name,
                    username=username,
                    max_nodes=max_nodes,
                    ignore_mesh=ignore_mesh,
                    dx_value=dx_value,
                )
                result = enf.create_model()

            elif model_name == "DCBmodel":
                dcb = DCBmodel(
                    model_data=model_data,
                    model_folder_name=model_folder_name,
                    username=username,
                    max_nodes=max_nodes,
                    ignore_mesh=ignore_mesh,
                    dx_value=dx_value,
                )
                result = dcb.create_model()

            elif model_name == "Dogbone":
                dogbone = Dogbone(
                    model_data=model_data,
                    model_folder_name=model_folder_name,
                    username=username,
                    max_nodes=max_nodes,
                    ignore_mesh=ignore_mesh,
                    dx_value=dx_value,
                )
                result = dogbone.create_model()

            elif model_name == "Kalthoff-Winkler":
                kalthoff = KalthoffWinkler(
                    model_data=model_data,
                    model_folder_name=model_folder_name,
                    username=username,
                    max_nodes=max_nodes,
                    ignore_mesh=ignore_mesh,
                    dx_value=dx_value,
                )
                result = kalthoff.create_model()

            elif model_name == "PlateWithOpening":
                plate_with_opening = PlateWithOpening(
                    model_data=model_data,
                    model_folder_name=model_folder_name,
                    username=username,
                    max_nodes=max_nodes,
                    ignore_mesh=ignore_mesh,
                    dx_value=dx_value,
                )
                result = plate_with_opening.create_model()

            elif model_name == "PlateWithHole":
                plate_with_hole = PlateWithHole(
                    model_data=model_data,
                    model_folder_name=model_folder_name,
                    username=username,
                    max_nodes=max_nodes,
                    ignore_mesh=ignore_mesh,
                    dx_value=dx_value,
                )
                result = plate_with_hole.create_model()

            elif model_name == "CompactTension":
                compact_tension = CompactTension(
                    model_folder_name=model_folder_name,
                    xend=length,
                    zend=width,
                    crack_length=model_data.model.cracklength,
                    notch_enabled=model_data.model.notchEnabled,
                    dx_value=dx_value,
                    two_d=model_data.model.twoDimensional,
                    rot=model_data.model.rotatedAngles,
                    angle=model_data.model.angles,
                    material=model_data.materials,
                    damage=model_data.damages,
                    block=model_data.blocks,
                    boundary_condition=model_data.boundaryConditions,
                    contact=model_data.contact,
                    compute=model_data.computes,
                    output=model_data.outputs,
                    solver=model_data.solver,
                    model_data=model_data,
                    username=username,
                    max_nodes=max_nodes,
                    ignore_mesh=ignore_mesh,
                )
                result = compact_tension.create_model()

            elif model_name == "Smetana":
                smetana = Smetana(
                    model_folder_name=model_folder_name,
                    mesh_res=model_data.model.discretization,
                    xend=length,
                    plyThickness=height,
                    zend=width,
                    dx_value=dx_value,
                    damage=model_data.damages,
                    contact=model_data.contact,
                    compute=model_data.computes,
                    output=model_data.outputs,
                    solver=model_data.solver,
                    model_data=model_data,
                    username=username,
                    ignore_mesh=ignore_mesh,
                    amplitude_factor=model_data.model.amplitudeFactor,
                    wavelength=model_data.model.wavelength,
                    angle=model_data.model.angles,
                    two_d=model_data.model.twoDimensional,
                )
                result = smetana.create_model()

            else:
                log.error("Model Name unknown")
                return "Model Name unknown"

        else:
            if model_data.model.translated:
                disc_type = "e"
            else:
                disc_type = "txt"

            own = OwnModel(
                filename=model_name,
                model_folder_name=model_folder_name,
                dx_value=dx_value,
                disc_type=disc_type,
                model_data=model_data,
                username=username,
            )
            result = own.create_model()

        log.info("%s has been created in %.2f seconds", model_name, time.time() - start_time)

        if result != "Model created":
            return ResponseModel(data=False, message=result)

        return ResponseModel(
            data=True,
            message=f"{model_name} has been created in {time.time() - start_time} seconds.",
        )

    @app.post("/translateModel", tags=["Post Methods"])
    def translate_model(model_name: str, model_folder_name: str, file_type: str, request: Request):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        start_time = time.time()

        localpath = FileHandler.get_local_model_path(username, model_name, model_folder_name)

        if not os.path.exists(localpath):
            os.makedirs(localpath)

        inputformat = "'ansys (cdb)'"
        if file_type == "cdb":
            inputformat = "ansys"
        if file_type == "inp":
            inputformat = "abaqus"
            # inputformat = "'ansys (cdb)'"

        command = (
            "java -jar ./support/jCoMoT/jCoMoT-0.0.1-all.jar -ifile "
            + os.path.join(localpath, model_name + "." + file_type)
            + " -iformat "
            + inputformat
            + " -oformat peridigm -opath "
            + localpath
        )  # + \
        # " && mv " + os.path.join(localpath, 'mesh.g.ascii ') + os.path.join(localpath, model_name) + '.g.ascii' + \
        # " && mv " + os.path.join(localpath, 'model.peridigm ') + os.path.join(localpath, model_name) + '.peridigm'
        # " && mv " + os.path.join(localpath, 'discretization.g.ascii ') + os.path.join(localpath, model_name)
        # + '.g.ascii' + \
        try:
            subprocess.call(command, shell=True)
        except subprocess.SubprocessError:
            log.error("%s results can not be found", model_name)
            return "%s results can not be found", model_name

        log.info("Rename mesh File")
        os.rename(
            os.path.join(localpath, "mesh.g.ascii"),
            os.path.join(localpath, model_name + ".g.ascii"),
        )
        log.info("Rename peridigm File")
        os.rename(
            os.path.join(localpath, "model.peridigm"),
            os.path.join(localpath, model_name + ".peridigm"),
        )

        log.info("Copy mesh File")
        if (
            FileHandler.copy_file_to_from_peridigm_container(username, model_name, model_name + ".g.ascii", True)
            != "Success"
        ):
            log.error("%s can not be translated", model_name)
            return "%s can not be translated", model_name

        log.info("Copy peridigm File")
        if (
            FileHandler.copy_file_to_from_peridigm_container(username, model_name, model_name + ".peridigm", True)
            != "Success"
        ):
            log.error("%s can not be translated", model_name)
            return "%s can not be translated", model_name

        # if return_string!='Success':
        #     return return_string

        server = "perihub_peridigm"
        remotepath = "/app/peridigmJobs/" + os.path.join(username, model_name)
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
            "/usr/local/netcdf/bin/ncgen "
            + os.path.join(remotepath, model_name)
            + ".g.ascii -o "
            + os.path.join(remotepath, model_name)
            + ".g"
            + " && python3 /peridigm/scripts/peridigm_to_yaml.py "
            + os.path.join(remotepath, model_name)
            + ".peridigm"
            + " && rm "
            + os.path.join(remotepath, model_name)
            + ".peridigm"
        )
        # ' && rm ' +  os.path.join(remotepath, model_name) + '.g.ascii' + \
        log.info("Peridigm to yaml")
        _, stdout, _ = ssh.exec_command(command)
        stdout.channel.set_combine_stderr(True)
        # output = stdout.readlines()
        ssh.close()

        log.info("Copy mesh File")
        FileHandler.copy_file_to_from_peridigm_container(username, model_name, model_name + ".g", False)
        log.info("Copy yaml File")
        FileHandler.copy_file_to_from_peridigm_container(username, model_name, model_name + ".yaml", False)

        log.info(
            "%s has been translated in %.2f seconds",
            model_name,
            time.time() - start_time,
        )
        return ResponseModel(
            data=True,
            message=f"{model_name} has been translated in {(time.time() - start_time):.2f} seconds",
        )

    @app.post("/translateGcode", tags=["Post Methods"])
    async def translate_gcode(model_name: str, model_folder_name: str, discretization: float, request: Request):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        start_time = time.time()

        localpath = FileHandler.get_local_model_path(username, model_name, model_folder_name)
        output_path = FileHandler.get_local_user_path(username)

        gcodereader.GcodeReader.read(model_name, localpath, output_path, discretization)

        log.info(
            "%s has been translated in %.2f seconds",
            model_name,
            time.time() - start_time,
        )
        return ResponseModel(
            data=True,
            message=f"{model_name} has been translated in {(time.time() - start_time):.2f} seconds",
        )

    @app.post("/uploadfiles", tags=["Post Methods"])
    async def upload_files(
        model_name: str,
        model_folder_name: str,
        request: Request,
        files: List[UploadFile] = File(...),
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        localpath = FileHandler.get_local_model_path(username, model_name, model_folder_name)

        if not os.path.exists(localpath):
            os.makedirs(localpath)

        for file in files:
            file_location = localpath + f"/{file.filename}"
            with open(file_location, "wb+") as file_object:
                shutil.copyfileobj(file.file, file_object)

        return ResponseModel(
            data=True,
            message=f"file '{files[0].filename}' saved at '{file_location}'",
        )

    @app.put("/writeInputFile", tags=["Put Methods"])
    def write_input_file(
        model_name: str,
        model_folder_name: str,
        input_string: str,
        file_type: FileType = FileType.YAML,
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        with open(
            "./Output/" + os.path.join(username, model_name, model_folder_name) + "/" + model_name + "." + file_type,
            "w",
            encoding="UTF-8",
        ) as file:
            file.write(input_string)

        log.info("%s-InputFile has been saved", model_name)
        return ResponseModel(
            data=True,
            message=model_name + "-InputFile has been saved",
        )

    @app.put("/runModel", tags=["Put Methods"])
    async def run_model(
        model_data: ModelData,
        model_name: str = "Dogbone",
        model_folder_name: str = "Default",
        file_type: FileType = FileType.YAML,
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)
        usermail = FileHandler.get_user_mail(request)
        FileHandler.get_local_model_path(username, model_name, model_folder_name)

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
        if user_mat:
            return_string = FileHandler.copy_lib_to_cluster(username, model_name, model_folder_name, cluster)
            if return_string != "Success":
                raise HTTPException(
                    status_code=404,
                    detail=return_string,
                )

        if cluster == "FA-Cluster":
            remotepath = "./PeridigmJobs/apiModels/" + os.path.join(username, model_name, model_folder_name)
            ssh = FileHandler.ssh_to_cluster("FA-Cluster")
            command = (
                "cd "
                + remotepath
                + " \n qperidigm -d -c "
                + str(model_data.job.tasks)
                + " -O tgz -J "
                + model_name
                + " -E /home/f_peridi/Peridigm/build/bin/Peridigm "
                + model_name
                + "."
                + file_type
            )
            ssh.exec_command(command)
            ssh.close()

            log.info("%s has been submitted", model_name)
            return ResponseModel(data=True, message=model_name + " has been submitted")

        elif cluster == "Cara":
            # initial_jobs = FileHandler.write_get_cara_job_id()
            # log.info(initial_jobs)
            sbatch = SbatchCreator(
                filename=model_name,
                model_folder_name=model_folder_name,
                output=model_data.outputs,
                job=model_data.job,
                usermail=usermail,
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

            # await asyncio.sleep(30)
            # # job_id=cara.sshClusterJob(command)

            # current_jobs = FileHandler.write_get_cara_job_id()
            # log.info(current_jobs)

            # job_id = current_jobs.replace(initial_jobs, "").strip()

            # if job_id == "":
            #     log.warning("%s submission failed!", model_name)
            #     raise HTTPException(
            #         status_code=404,
            #         detail=model_name + " submission failed!",
            #     )

            # FileHandler.write_cara_job_id_to_model(localpath, job_id)

            # log.info("%s has been submitted with Job Id: %s", model_name, job_id.decode('utf-8'))
            # return ResponseModel(
            #     data=True,
            #     message=model_name + " has been submitted with Job Id: " + job_id.decode('utf-8'),
            # )
            log.info("%s has been submitted", model_name)
            return ResponseModel(
                data=True,
                message=model_name + " has been submitted",
            )

        elif cluster == "None":
            server = "perihub_peridigm"
            remotepath = "/peridigmJobs/" + os.path.join(username, model_name, model_folder_name)
            if os.path.exists(os.path.join("." + remotepath, "pid.txt")):
                log.warning("%s already submitted", model_name)
                return model_name + " already submitted"
            sbatch = SbatchCreator(
                filename=model_name,
                model_folder_name=model_folder_name,
                filetype=file_type,
                remotepath=remotepath,
                output=model_data.outputs,
                job=model_data.job,
                usermail=usermail,
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

    @app.put("/cancelJob", tags=["Put Methods"])
    def cancel_job(
        model_name: str = "Dogbone",
        model_folder_name: str = "Default",
        cluster: str = "None",
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        if cluster == "None":
            server = "perihub_peridigm"
            remotepath = "/peridigmJobs/" + os.path.join(username, model_name, model_folder_name)
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
                "kill -9 `cat /app"
                + os.path.join(remotepath, "pid.txt")
                + "` \n rm /app"
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

    @app.get("/generateMesh", tags=["Get Methods"])
    def generate_mesh(model_name: str, model_folder_name: str, param: str, request: Request):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        # json=param,
        print(param)

        request = requests.patch(
            "https://129.247.54.235:5000/1/PyCODAC/api/micofam/{zip}",
            verify=False,
        )
        try:
            with zipfile.ZipFile(io.BytesIO(request.content)) as zip_file:
                localpath = "./Output/" + os.path.join(username, model_name, model_folder_name)

                if not os.path.exists(localpath):
                    os.makedirs(localpath)

                zip_file.extractall(localpath)

        except IOError:
            log.error("Micofam request failed")
            return "Micofam request failed"

        output_files = os.listdir(localpath)
        filtered_values = list(filter(lambda v: match(r"^.+\.inp$", v), output_files))
        os.rename(
            os.path.join(localpath, filtered_values[0]),
            os.path.join(localpath, model_name + ".inp"),
        )

        # return requests.patch('https://localhost:5000/1/PyCODAC/api/micofam/%7Bzip%7D', headers=headers, files=files)

        # file_path = './Output/' + os.path.join(username, model_name) + '/'  + model_name + '.' + file_type
        # if not os.path.exists(file_path):
        #     return 'Inputfile can\'t be found'
        # try:
        #     return FileResponse(file_path)
        # except Exception:
        log.info("Mesh generated")
        return ResponseModel(data=True, message="Mesh generated")

    @app.get("/getImagePython", tags=["Get Methods"])
    def get_image_python(
        model_name: str = "Dogbone",
        model_folder_name: str = "Default",
        cluster: str = "None",
        tasks: int = 32,
        output: str = "Output1",
        variable: str = "Displacement",
        axis: str = "X",
        displ_factor: int = 20,
        marker_size: int = 16,
        length: float = 0.13,
        height: float = 0.02,
        triangulate: bool = False,
        dx_value: float = 0.004,
        step: int = -1,
        cb_left: Optional[bool] = False,
        transparent: Optional[bool] = True,
        three_d: Optional[bool] = False,
        elevation: Optional[float] = 30,
        azimuth: Optional[float] = 30,
        roll: Optional[float] = 0,
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        if not FileHandler.copy_results_from_cluster(
            username, model_name, model_folder_name, cluster, False, tasks, output
        ):
            raise IOError  # NotFoundException(name=model_name)

        resultpath = "./Results/" + os.path.join(username, model_name, model_folder_name)
        file = os.path.join(resultpath, model_name + "_" + output + ".e")

        # try:
        filepath = ImageExport.get_result_image_from_exodus(
            file,
            displ_factor,
            marker_size,
            variable,
            axis,
            length,
            height,
            triangulate,
            dx_value,
            step,
            cb_left,
            transparent,
            three_d,
            elevation,
            azimuth,
            roll,
        )
        # except ValueError:
        #     log.error("%s ValueError %s", model_name, cluster)
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="ValueError",
        #     )

        try:
            return FileResponse(filepath)
        except IOError:
            log.error("%s results can not be found on %s", model_name, cluster)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=model_name + " results can not be found on " + cluster,
            )

    @app.get("/getPlotPython", tags=["Get Methods"])
    def get_plot_python(
        model_name: str = "Dogbone",
        model_folder_name: str = "Default",
        cluster: str = "None",
        tasks: int = 32,
        output: str = "Output1",
        x_variable: str = "Time",
        x_axis: str = "X",
        y_variable: str = "External_Displacement",
        y_axis: str = "X",
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        if not FileHandler.copy_results_from_cluster(
            username, model_name, model_folder_name, cluster, False, tasks, output
        ):
            raise IOError  # NotFoundException(name=model_name)

        resultpath = "./Results/" + os.path.join(username, model_name)
        file = os.path.join(resultpath, model_name + "_" + output + ".e")

        filepath = ImageExport.get_plot_image_from_exodus(file, x_variable, x_axis, y_variable, y_axis)

        try:
            return FileResponse(filepath)
        except IOError:
            log.error("%s results can not be found on %s", model_name, cluster)
            return model_name + " results can not be found on " + cluster

    @app.get("/getFractureAnalysis", tags=["Get Methods"])
    def get_fracture_analysis(
        model_name: str = "Dogbone",
        model_folder_name: str = "Default",
        length: float = 35,
        height: float = 10,
        crack_length: float = 17.5,
        young_modulus: float = 5000,
        poissions_ratio: float = 0.33,
        yield_stress: float = 74,
        cluster: str = "None",
        tasks: int = 32,
        output: str = "Output1",
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        if not FileHandler.copy_results_from_cluster(
            username, model_name, model_folder_name, cluster, False, tasks, output
        ):
            raise IOError  # NotFoundException(name=model_name)

        resultpath = "./Results/" + os.path.join(username, model_name, model_folder_name)
        file = os.path.join(resultpath, model_name + "_" + output + ".e")

        file_name, filepath = CrackAnalysis.write_nodemap(file)

        filepath = CrackAnalysis.fracture_analysis(
            model_name,
            length,
            height,
            crack_length,
            young_modulus,
            poissions_ratio,
            yield_stress,
            file_name,
            filepath,
        )

        try:
            return FileResponse(filepath)
        except IOError:
            log.error("%s results can not be found on %s", model_name, cluster)
            return model_name + " results can not be found on " + cluster

    @app.get("/getGif", tags=["Get Methods"])
    def get_gif(
        model_name: str = "Dogbone",
        model_folder_name: str = "Default",
        cluster: str = "None",
        output: str = "Output1",
        tasks: int = 32,
        variable: str = "Displacement",
        axis: str = "X",
        apply_displacements: bool = False,
        displ_factor: int = 200,
        max_edge_distance: float = 2.0,
        length: float = 4.4,
        height: float = 1.1,
        fps: int = 2,
        dpi: int = 100,
        x_min: Optional[float] = None,
        x_max: Optional[float] = None,
        y_min: Optional[float] = None,
        y_max: Optional[float] = None,
        size: Optional[float] = 20,
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        if not FileHandler.copy_results_from_cluster(
            username, model_name, model_folder_name, cluster, False, tasks, output
        ):
            raise IOError  # NotFoundException(name=model_name)

        resultpath = "./Results/" + os.path.join(username, model_name, model_folder_name)
        file = os.path.join(resultpath, model_name + "_" + output + ".e")

        filepath = VideoExport.get_gif_from_exodus(
            file,
            apply_displacements,
            displ_factor,
            max_edge_distance,
            variable,
            axis,
            length,
            height,
            fps,
            dpi,
            x_min,
            x_max,
            y_min,
            y_max,
            size,
        )

        try:
            return FileResponse(filepath)
        except IOError:
            log.error("%s results can not be found on %s", model_name, cluster)
            return model_name + " results can not be found on " + cluster

    @app.get("/getTriangulatedMeshFromExodus", tags=["Get Methods"])
    def get_triangulated_mesh_from_exodus(
        model_name: str = "Dogbone",
        model_folder_name: str = "Default",
        cluster: str = "None",
        output: str = "Output1",
        tasks: int = 32,
        displ_factor: int = 10,
        timestep: int = -1,
        max_edge_distance: float = 0.5,
        length: float = 0.13,
        height: float = 0.02,
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        if not FileHandler.copy_results_from_cluster(
            username, model_name + model_folder_name, cluster, False, tasks, output
        ):
            raise IOError  # NotFoundException(name=model_name)

        resultpath = "./Results/" + os.path.join(username, model_name, model_folder_name)
        file = os.path.join(resultpath, model_name + "_" + output + ".e")

        filepath = VideoExport.get_triangulated_mesh_from_exodus(
            file,
            displ_factor,
            timestep,
            max_edge_distance,
            length,
            height,
        )

        try:
            return FileResponse(filepath)
        except IOError:
            log.error("%s results can not be found on %s", model_name, cluster)
            return model_name + " results can not be found on " + cluster

    @app.get("/getResultFile", tags=["Get Methods"])
    def get_result_file(
        model_name: str = "Dogbone",
        model_folder_name: str = "Default",
        cluster: str = "None",
        output: str = "Output1",
        tasks: int = 32,
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        if not FileHandler.copy_results_from_cluster(
            username, model_name, model_folder_name, cluster, False, tasks, output
        ):
            raise IOError  # NotFoundException(name=model_name)

        filepath = Analysis.get_result_file(username, model_name, model_folder_name, output)
        # print(crack_length)
        # response = [[0, 1, 2, 3], [0, 2, 3, 5]]

        try:
            return FileResponse(filepath)
        except IOError:
            log.error("%s results can not be found on %s", model_name, cluster)
            return model_name + " results can not be found on " + cluster

    @app.get("/getGlobalDataTimeseries", tags=["Get Methods"])
    def get_global_data_timeseries(
        model_name: str = "Dogbone",
        model_folder_name: str = "Default",
        cluster: str = "None",
        output: str = "Output1",
        tasks: int = 32,
        variable: str = "External_Force",
        axis: str = "X",
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        if not FileHandler.copy_results_from_cluster(
            username, model_name, model_folder_name, cluster, False, tasks, output
        ):
            raise IOError  # NotFoundException(name=model_name)

        resultpath = "./Results/" + os.path.join(username, model_name, model_folder_name)
        file = os.path.join(resultpath, model_name + "_" + output + ".e")

        global_data = Analysis.get_global_data(file, variable, axis)
        global_time = Analysis.get_global_data(file, "Time", "")

        factor = int(1e9)

        points = []
        for i, seconds in enumerate(global_time):
            value = global_data[i]
            timestamp = seconds * factor
            points.append(InfluxPoint(value=value, timestamp=timestamp))

        timeseries = Timeseries(
            measurement=variable,
            location=cluster,
            device="Peridigm",
            symbolic_name=model_name + "_" + output + "_" + variable,
            field="value",
        )

        payload = TimeseriesPayload(timeseries=timeseries, points=points)

        return payload.to_dict(True)

    # @app.post("/calculateG1c", tags=["Post Methods"])
    # def calculate_g1c(
    #     model: Model,
    #     youngs_modulus: float = 2974,
    #     model_name: str = "Dogbone",
    #     model_folder_name: str = "Default",
    #     cluster: str = "None",
    #     request: Request = "",
    # ):
    #     """doc"""
    #     username = FileHandler.get_user_name(request, dev)

    #     if not FileHandler.copy_results_from_cluster(
    #         username, model_name, model_folder_name, cluster, False
    #     ):
    #         raise IOError  # NotFoundException(name=model_name)

    #     response = Analysis.get_g1c_k1c(username, model_name, model, youngs_modulus)
    #     # print(crack_length)
    #     # response = [[0, 1, 2, 3], [0, 2, 3, 5]]
    #     try:
    #         return FileResponse(response)
    #     except IOError:
    #         log.error("%s results can not be found on %s", model_name, cluster)
    #         return model_name + " results can not be found on " + cluster

    # @app.post("/calculateG2c", tags=["Post Methods"])
    # def calculate_g2c(
    #     model: Model,
    #     model_name: str = "Dogbone",
    #     model_folder_name: str = "Default",
    #     cluster: str = "None",
    #     output: str = "Output1",
    #     request: Request = "",
    # ):
    #     """doc"""
    #     username = FileHandler.get_user_name(request, dev)

    #     if not FileHandler.copy_results_from_cluster(
    #         username, model_name, model_folder_name, cluster, False
    #     ):
    #         raise IOError  # NotFoundException(name=model_name)

    #     response = Analysis.get_g2c(username, model_name, output, model)
    #     # print(crack_length)
    #     # response = [[0, 1, 2, 3], [0, 2, 3, 5]]
    #     try:
    #         return response
    #     except IOError:
    #         log.error("%s results can not be found on %s", model_name, cluster)
    #         return model_name + " results can not be found on " + cluster

    @app.get("/getLogFile", tags=["Get Methods"])
    def get_log_file(
        model_name: str = "Dogbone",
        model_folder_name: str = "Default",
        cluster: str = "None",
        request: Request = "",
    ):
        """doc"""

        username = FileHandler.get_user_name(request, dev)
        # usermail = FileHandler.get_user_mail(request)

        if cluster == "None":
            remotepath = "./peridigmJobs/" + os.path.join(username, model_name, model_folder_name)
            try:
                output_files = os.listdir(remotepath)
                filtered_values = list(filter(lambda v: match(r"^.+\.log$", v), output_files))
            except IOError:
                log.error("LogFile can not be found in %s", remotepath)

                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="LogFile can't be found in " + remotepath,
                )
            if len(filtered_values) == 0:
                log.error("LogFile can not be found in %s", remotepath)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="LogFile can't be found in " + remotepath,
                )

            with open(
                os.path.join(remotepath, filtered_values[-1]),
                "r",
                encoding="UTF-8",
            ) as file:
                response = file.read()

            return ResponseModel(data=response, message="Logfile received")

        # if cluster == "FA-Cluster":

        remotepath = FileHandler.get_remote_model_path(username, model_name, model_folder_name)

        # elif cluster == "Cara":
        #     remotepath = "./PeridigmJobs/apiModels/" + os.path.join(
        #         username, model_name
        #     )

        # else:
        #     log.error("%s unknown", cluster)
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND, detail=cluster + " unknown"
        #     )

        ssh, sftp = FileHandler.sftp_to_cluster(cluster)

        try:
            output_files = sftp.listdir(remotepath)
            filtered_values = list(filter(lambda v: match(r"^.+\.log$", v), output_files))
        except paramiko.SFTPError:
            log.error("LogFile can not be found in %s", remotepath)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LogFile can't be found in " + remotepath,
            )
        if len(filtered_values) == 0:
            log.error("LogFile can not be found in %s", remotepath)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LogFile can't be found in " + remotepath,
            )
        sftp.chdir(remotepath)
        logfile = sftp.file(filtered_values[-1], "r")
        response = logfile.read()
        sftp.close()
        ssh.close()

        return ResponseModel(data=response, message="Logfile received")

    @app.get("/getMaxFeSize", tags=["Get Methods"])
    def get_max_fe_size(request: Request = ""):
        """doc"""

        username = FileHandler.get_user_name(request, dev)

        return FileHandler.get_max_fe_size(username)

    @app.get("/getModel", tags=["Get Methods"])
    def get_model(
        model_name: str = "Dogbone",
        model_folder_name: str = "Default",
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        folder_path = os.path.join(FileHandler.get_local_user_path(username), model_name)
        zip_file = os.path.join(folder_path, model_name + "_" + model_folder_name)
        try:
            shutil.make_archive(zip_file, "zip", os.path.join(folder_path, model_folder_name))

            response = FileResponse(
                zip_file + ".zip",
                media_type="application/x-zip-compressed",
            )
            response.headers["Content-Disposition"] = (
                "attachment; filename=" + model_name + "_" + model_folder_name + ".zip"
            )
            # return StreamingResponse(iterfile(), media_type="application/x-zip-compressed")
            return response
        except shutil.Error:
            log.error("%s files can not be found", model_name)
            return model_name + " files can not be found"

    @app.get("/getPlot", tags=["Get Methods"])
    def get_plot(
        model_name: str = "Dogbone",
        model_folder_name: str = "Default",
        cluster: str = "None",
        output: str = "Output1",
        tasks: int = 32,
        x_variable: str = "Time",
        x_axis: str = "X",
        x_absolute: bool = True,
        y_variable: str = "External_Displacement",
        y_axis: str = "X",
        y_absolute: bool = True,
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        if not FileHandler.copy_results_from_cluster(
            username, model_name, model_folder_name, cluster, False, tasks, output
        ):
            raise IOError  # NotFoundException(name=model_name)

        resultpath = "./Results/" + os.path.join(username, model_name, model_folder_name)
        file = os.path.join(resultpath, model_name + "_" + output + ".e")

        x_data = Analysis.get_global_data(file, x_variable, x_axis, x_absolute)
        y_data = Analysis.get_global_data(file, y_variable, y_axis, y_absolute)

        return ResponseModel(data=[x_data, y_data], message="Plot received")

    @app.get("/getPointData", tags=["Get Methods"])
    def get_point_data(
        model_name: str = "Dogbone",
        model_folder_name: str = "Default",
        own_model: bool = False,
        own_mesh: bool = False,
        mesh_file: str = "Dogbone.txt",
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        point_string = ""
        block_id_string = ""
        if own_mesh:
            try:
                with open(
                    "./peridigmJobs/"
                    + os.path.join(username, model_name, model_folder_name)
                    + "/"
                    + model_name
                    + ".g.ascii",
                    "r",
                    encoding="UTF-8",
                ) as file:
                    model_data = file.read()
                    num_of_blocks = re.findall(r"num_el_blk\s=\s\d*\s;", model_data)
                    num_of_blocks = int(num_of_blocks[0][13:][:2])
                    coords = re.findall(r"coord.\s=\s[-\d.,\se]{1,}", model_data)
                    nodes = re.findall(r"node_ns[\d]*\s=\s[\d,\s]*", model_data)
                    block_id = [1] * len(coords[0])
                    for i in range(0, 3):
                        coords[i] = coords[i][8:].replace(" ", "").split(",")
                    for i in range(0, num_of_blocks):
                        nodes[i] = nodes[i * 2][8:].replace(" ", "").split("=")[1].split(",")
                        for node in nodes[i]:
                            block_id[int(node) - 1] = i + 1
                    for i in range(0, len(coords[0])):
                        point_string += coords[0][i] + "," + coords[1][i] + "," + coords[2][i] + ","
                        block_id_string += str(block_id[i] / num_of_blocks) + ","

                response = [
                    point_string.rstrip(point_string[-1]),
                    block_id_string.rstrip(block_id_string[-1]),
                ]
                return response
            except IOError:
                log.error("%s results can not be found", model_name)
                return model_name + " results can not be found"
        else:
            first_row = True
            max_block_id = 1
            try:
                if own_model:
                    mesh_path = "./Output/" + os.path.join(username, model_name, model_folder_name) + "/" + mesh_file
                else:
                    mesh_path = (
                        "./Output/" + os.path.join(username, model_name, model_folder_name) + "/" + model_name + ".txt"
                    )

                with open(
                    mesh_path,
                    "r",
                    encoding="UTF-8",
                ) as file:
                    reader = csv.reader(file)
                    rows = list(reader)
                    for row in rows:
                        if not first_row:
                            str1 = "".join(row)
                            parts = str1.split()
                            point_string += parts[0] + "," + parts[1] + "," + parts[2] + ","
                            if int(parts[3]) > max_block_id:
                                max_block_id = int(parts[3])
                        first_row = False
                    first_row = True
                    for row in rows:
                        if not first_row:
                            str1 = "".join(row)
                            parts = str1.split()
                            block_id_string += str(int(parts[3]) / max_block_id) + ","
                        first_row = False
                response = [
                    point_string.rstrip(point_string[-1]),
                    block_id_string.rstrip(block_id_string[-1]),
                ]
                return ResponseModel(data=response, message="Points received")
            except IOError:
                log.error("%s results can not be found", model_name)
                return model_name + " results can not be found"

    @app.get("/getResults", tags=["Get Methods"])
    def get_results(
        model_name: str = "Dogbone",
        model_folder_name: str = "Default",
        output: str = "Output1",
        tasks: int = 32,
        cluster: str = "None",
        all_data: bool = False,
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        if not FileHandler.copy_results_from_cluster(
            username, model_name, model_folder_name, cluster, all_data, tasks, output
        ):
            raise HTTPException(
                status_code=404,
                detail=model_name + " results can not be found on " + cluster,
            )

        # resultpath = './Results/' + os.path.join(username, model_name)
        userpath = "./Results/" + username
        folder_path = os.path.join(userpath, model_name)
        zip_file = os.path.join(folder_path, model_name + "_" + model_folder_name)

        try:
            shutil.make_archive(zip_file, "zip", os.path.join(folder_path, model_folder_name))

            response = FileResponse(
                zip_file + ".zip",
                media_type="application/x-zip-compressed",
            )
            response.headers["Content-Disposition"] = (
                "attachment; filename=" + model_name + "_" + model_folder_name + ".zip"
            )
            # return StreamingResponse(iterfile(), media_type="application/x-zip-compressed")
            return response
        except IOError:
            log.error("%s results can not be found on %s", model_name, cluster)
            return model_name + " results can not be found on " + cluster

    @app.get("/getJobs", tags=["Get Methods"])
    def get_jobs(
        model_name: str = "Dogbone",
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        jobs = []

        localpath = os.path.join("./Output", username, model_name)

        print(localpath)

        if not os.path.exists(localpath):
            return ResponseModel(data=jobs, message="No jobs")

        ssh, sftp = FileHandler.sftp_to_cluster("Cara")

        for _, dirs, _ in os.walk(localpath):
            # log.info(dirs)
            for model_folder_name in dirs:
                modelpath = os.path.join(localpath, model_folder_name)

                if os.path.exists(modelpath):
                    job = Jobs(
                        len(jobs) + 1,
                        model_name,
                        model_folder_name,
                        "",
                        True,
                        False,
                        False,
                        {},
                    )

                    remotepath = "./peridigmJobs/" + os.path.join(username, model_name, model_folder_name)
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
                            len(jobs) + 1,
                            model_name,
                            model_folder_name,
                            "",
                            True,
                            False,
                            False,
                            {},
                        )

                    remotepath = "./PeridigmJobs/apiModels/" + os.path.join(username, model_name, model_folder_name)

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

        sftp.close()
        ssh.close()

        return ResponseModel(data=jobs, message="Jobs found")

    @app.get("/getStatus", tags=["Get Methods"])
    def get_status(
        model_name: str = "Dogbone",
        model_folder_name: str = "Default",
        own_mesh: bool = False,
        cluster: str = "None",
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        status = Status(False, False, False)

        if own_mesh:
            localpath = "./peridigmJobs/" + os.path.join(username, model_name, model_folder_name)
        else:
            localpath = "./Output/" + os.path.join(username, model_name, model_folder_name)

        log.info("localpath: %s", localpath)

        if os.path.exists(localpath):
            status.created = True

        if cluster == "None":
            remotepath = "./peridigmJobs/" + os.path.join(username, model_name, model_folder_name)
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

    @app.get("/viewInputFile", tags=["Get Methods"])
    def view_input_file(
        model_name: str = "Dogbone",
        model_folder_name: str = "Default",
        own_mesh: bool = False,
        file_type: FileType = FileType.YAML,
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        if own_mesh:
            file_path = (
                "./peridigmJobs/"
                + os.path.join(username, model_name, model_folder_name)
                + "/"
                + model_name
                + "."
                + file_type
            )
        else:
            file_path = (
                "./Output/" + os.path.join(username, model_name, model_folder_name) + "/" + model_name + "." + file_type
            )
        if not os.path.exists(file_path):
            log.error("Inputfile can't be found")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inputfile can't be found",
            )
        try:
            with open(file_path, "r") as f:
                string = f.read()
            return ResponseModel(data=string, message="Input File received")
        except IOError:
            log.error("Inputfile can't be found")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inputfile can't be found",
            )

    @app.delete("/deleteModel", tags=["Delete Methods"])
    def delete_model(
        model_name: str = "Dogbone",
        model_folder_name: str = "Default",
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        localpath = FileHandler.get_local_model_path(username, model_name, model_folder_name)
        if os.path.exists(localpath):
            shutil.rmtree(localpath)
        log.info("%s has been deleted", model_name)
        return ResponseModel(data=True, message=model_name + " has been deleted")

    @app.delete("/deleteModelFromCluster", tags=["Delete Methods"])
    def delete_model_from_cluster(
        model_name: str = "Dogbone",
        model_folder_name: str = "Default",
        cluster: str = "None",
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        if cluster == "None":
            remotepath = "./peridigmJobs/" + os.path.join(username, model_name + model_folder_name)
            if os.path.exists(remotepath):
                shutil.rmtree(remotepath)
            log.info("%s has been deleted", model_name)
            return ResponseModel(data=True, message=model_name + " has been deleted")

        if cluster == "FA-Cluster":
            remotepath = "./PeridigmJobs/apiModels/" + os.path.join(username, model_name, model_folder_name)

        elif cluster == "Cara":
            remotepath = "./PeridigmJobs/apiModels/" + os.path.join(username, model_name, model_folder_name)

        else:
            log.info("%s unknown", cluster)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=cluster + " unknown",
            )

        ssh, sftp = FileHandler.sftp_to_cluster(cluster)

        for filename in sftp.listdir(remotepath):
            sftp.remove(os.path.join(remotepath, filename))
        sftp.rmdir(remotepath)
        sftp.close()
        ssh.close()
        log.info("%s has been deleted", model_name)
        return ResponseModel(data=True, message=model_name + " has been deleted")

    @app.delete("/deleteUserData", tags=["Delete Methods"])
    def delete_user_data(check_date: bool, request: Request, days: Optional[int] = 7):
        """doc"""
        if check_date:
            localpath = "./Output"
            if os.path.exists(localpath):
                names = FileHandler.remove_folder_if_older(localpath, days, True)
                if len(names) != 0:
                    log.info("Data of %s has been deleted", ", ".join(names))
                    return "Data of " + ", ".join(names) + " has been deleted"
            log.info("Nothing has been deleted")
            return ResponseModel(data=True, message="Nothing has been deleted")

        username = FileHandler.get_user_name(request, dev)

        localpath = "./Output/" + username
        if os.path.exists(localpath):
            shutil.rmtree(localpath)
        log.info("Data of %s has been deleted", username)
        return ResponseModel(data=True, message="Data of " + username + " has been deleted")

    @app.delete("/deleteUserDataFromCluster", tags=["Delete Methods"])
    def delete_user_data_from_cluster(
        cluster: str,
        check_date: bool,
        request: Request,
        days: Optional[int] = 7,
    ):
        """doc"""

        if check_date:
            if cluster == "None":
                localpath = "./peridigmJobs"
                names = FileHandler.remove_folder_if_older(localpath, days, True)
            else:
                remotepath = FileHandler.get_remote_path(cluster)

                ssh, sftp = FileHandler.sftp_to_cluster(cluster)

                names = FileHandler.remove_folder_if_older_sftp(sftp, remotepath, days, True)

                sftp.close()
                ssh.close()

            log.info("Data of %s has been deleted", names)
            return ResponseModel(data=True, message="Data of " + names + " has been deleted")

        username = FileHandler.get_user_name(request, dev)

        if cluster == "None":
            remotepath = "./peridigmJobs/" + username
            if os.path.exists(remotepath):
                shutil.rmtree(remotepath)
            log.info("Data of %s has been deleted", username)
            return ResponseModel(data=True, message="Data of " + username + " has been deleted")

        remotepath = FileHandler.get_remote_user_path(username)

        ssh, sftp = FileHandler.sftp_to_cluster(cluster)

        FileHandler.remove_all_folder_ssh(ssh, remotepath)

        sftp.close()
        ssh.close()

        log.info("Data of %s has been deleted", username)
        return ResponseModel(data=True, message="Data of " + username + " has been deleted")

    @app.get("/getDocs", tags=["Documentation Methods"])
    def get_docs(name: str = "Introduction"):
        """doc"""

        path = name.split("_")

        if len(path) == 1:
            remotepath = "./guides/" + path[0] + ".md"
        else:
            remotepath = "./guides/" + path[0] + "/" + path[1] + ".md"

        with open(remotepath, "r", encoding="UTF-8") as file:
            response = file.read()

        return response

    @app.get("/getPublications", tags=["Documentation Methods"])
    def get_publications():
        """doc"""

        remotepath = "./Publications/papers.bib"

        with open(remotepath, "r", encoding="UTF-8") as file:
            response = file.read()

        return response
