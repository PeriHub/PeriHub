"""
doc
"""
# Copyright (C) 2021 Deutsches Zentrum fuer Luft- und Raumfahrt(DLR, German Aerospace Center) <www.dlr.de>

# pylint: disable=no-self-argument, no-method-argument, no-member, import-error

# import uvicorn
import asyncio
import shutil
import re
import os
import csv
import time
import subprocess
import zipfile
import io
import json
from re import match
from typing import List
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, File, UploadFile
from fastapi.responses import FileResponse

# from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import paramiko
import requests

# from fastapi.responses import HTMLResponse
# from fastapi.responses import StreamingResponse
from models.GICmodel.gic_model import GICmodel
from models.GIICmodel.giic_model import GIICmodel
from models.DCBmodel.dcb_model import DCBmodel
from models.Dogbone.dogbone import Dogbone
from models.KalthoffWinkler.kalthoff_winkler import KalthoffWinkler
from models.PlateWithHole.plate_with_hole import PlateWithHole
from models.CompactTension.compact_tension import CompactTension
from models.Smetana.smetana import Smetana
from models.OwnModel.own_model import OwnModel
from support.sbatch_creator import SbatchCreator
from support.file_handler import FileHandler
from support.base_models import ModelData, FileType, RunData, Status, Model, Material
from support.analysis import Analysis
from support.image_export import ImageExport
from support.video_export import VideoExport
from support.gcode_reader import GcodeReader
from support.globals import MYGLOBAL, log

from shepard_client.models.timeseries import Timeseries
from shepard_client.models.influx_point import InfluxPoint
from shepard_client.models.timeseries_payload import TimeseriesPayload

from fa_pyutils.sshtools import cara
import fa_pyutils.service.duration as duration



# class NotFoundException(Exception):
#     """doc"""

#     def __init__(self, name: str):
#         """doc"""
#         self.name = name


tags_metadata = [
    {"name": "Post Methods", "description": "Generate, translate or upload models"},
    {"name": "Put Methods", "description": "Run, cancel or write jobs"},
    {
        "name": "Get Methods",
        "description": "Get mesh files, input files or postprocessing data",
    },
    {"name": "Delete Methods", "description": "Delete user or model data"},
    {
        "name": "Documentation Methods",
        "description": "Retrieve markdown documentation or bibtex files",
    },
]

app = FastAPI(openapi_tags=tags_metadata)

origins = [
    "http://localhost",
    "http://localhost:6010",
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
smetana = os.getenv("SMETANA")
if dev == "True":
    log.info("--- Running in development mode ---")
if smetana == "True":
    MYGLOBAL.smetana_enabled = True
else:
    log.warn("Smetana is not enabled")


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
        model_data: ModelData, model_name: str = "Dogbone", request: Request = ""
    ):  # material: dict, Output: dict):
        """doc"""

        username = FileHandler.get_user_name(request, dev)

        max_nodes = FileHandler.get_max_nodes(username)

        localpath = "./Output/" + os.path.join(username, model_name)

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
        height2 = model_data.model.height2
        radius = model_data.model.radius
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

        log.infoHeadline("Create " + model_name)

        if model_data.model.ownModel == False:
            if model_name == "GICmodel":
                gic = GICmodel(
                    xend=length,
                    crack_length=cracklength,
                    yend=height,
                    zend=width,
                    dx_value=dx_value,
                    two_d=model_data.model.twoDimensional,
                    rot=model_data.model.rotatedAngles,
                    angle=model_data.model.angles,
                    material=model_data.materials,
                    damage=model_data.damages,
                    block=model_data.blocks,
                    boundary_condition=model_data.boundaryConditions,
                    contact=model_data.contact,
                    bond_filter=model_data.bondFilters,
                    compute=model_data.computes,
                    output=model_data.outputs,
                    solver=model_data.solver,
                    username=username,
                    max_nodes=max_nodes,
                    ignore_mesh=ignore_mesh,
                )
                result = gic.create_model()

            elif model_name == "GIICmodel":
                giic = GIICmodel(
                    xend=length,
                    crack_length=cracklength,
                    yend=height,
                    zend=width,
                    dx_value=dx_value,
                    two_d=model_data.model.twoDimensional,
                    rot=model_data.model.rotatedAngles,
                    angle=model_data.model.angles,
                    material=model_data.materials,
                    damage=model_data.damages,
                    block=model_data.blocks,
                    boundary_condition=model_data.boundaryConditions,
                    contact=model_data.contact,
                    bond_filter=model_data.bondFilters,
                    compute=model_data.computes,
                    output=model_data.outputs,
                    solver=model_data.solver,
                    username=username,
                    max_nodes=max_nodes,
                    ignore_mesh=ignore_mesh,
                )
                result = giic.create_model()

            elif model_name == "DCBmodel":
                dcb = DCBmodel(
                    xend=length,
                    yend=height,
                    zend=width,
                    dx_value=dx_value,
                    two_d=model_data.model.twoDimensional,
                    rot=model_data.model.rotatedAngles,
                    angle=model_data.model.angles,
                    material=model_data.materials,
                    damage=model_data.damages,
                    block=model_data.blocks,
                    boundary_condition=model_data.boundaryConditions,
                    contact=model_data.contact,
                    bond_filter=model_data.bondFilters,
                    compute=model_data.computes,
                    output=model_data.outputs,
                    solver=model_data.solver,
                    username=username,
                    max_nodes=max_nodes,
                    ignore_mesh=ignore_mesh,
                )
                result = dcb.create_model()

            elif model_name == "Dogbone":
                dogbone = Dogbone(
                    xend=length,
                    height1=height,
                    height2=height2,
                    zend=width,
                    dx_value=dx_value,
                    structured=model_data.model.structured,
                    two_d=model_data.model.twoDimensional,
                    rot=model_data.model.rotatedAngles,
                    angle=model_data.model.angles,
                    material=model_data.materials,
                    damage=model_data.damages,
                    block=model_data.blocks,
                    boundary_condition=model_data.boundaryConditions,
                    contact=model_data.contact,
                    bond_filter=model_data.bondFilters,
                    compute=model_data.computes,
                    output=model_data.outputs,
                    solver=model_data.solver,
                    username=username,
                    max_nodes=max_nodes,
                    ignore_mesh=ignore_mesh,
                )
                result = dogbone.create_model()

            elif model_name == "Kalthoff-Winkler":
                kalthoff = KalthoffWinkler(
                    xend=length,
                    yend=height,
                    zend=width,
                    dx_value=dx_value,
                    two_d=model_data.model.twoDimensional,
                    rot=model_data.model.rotatedAngles,
                    angle=model_data.model.angles,
                    material=model_data.materials,
                    damage=model_data.damages,
                    block=model_data.blocks,
                    boundary_condition=model_data.boundaryConditions,
                    contact=model_data.contact,
                    bond_filter=model_data.bondFilters,
                    compute=model_data.computes,
                    output=model_data.outputs,
                    solver=model_data.solver,
                    username=username,
                    max_nodes=max_nodes,
                    ignore_mesh=ignore_mesh,
                )
                result = kalthoff.create_model()

            elif model_name == "PlateWithHole":
                plate_with_hole = PlateWithHole(
                    xend=length,
                    yend=height,
                    zend=width,
                    radius=radius,
                    dx_value=dx_value,
                    two_d=model_data.model.twoDimensional,
                    rot=model_data.model.rotatedAngles,
                    angle=model_data.model.angles,
                    material=model_data.materials,
                    damage=model_data.damages,
                    block=model_data.blocks,
                    boundary_condition=model_data.boundaryConditions,
                    contact=model_data.contact,
                    bond_filter=model_data.bondFilters,
                    compute=model_data.computes,
                    output=model_data.outputs,
                    solver=model_data.solver,
                    username=username,
                    max_nodes=max_nodes,
                    ignore_mesh=ignore_mesh,
                )
                result = plate_with_hole.create_model()

            elif model_name == "CompactTension":
                compact_tension = CompactTension(
                    xend=length,
                    zend=width,
                    crack_length=model_data.model.cracklength,
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
                    username=username,
                    max_nodes=max_nodes,
                    ignore_mesh=ignore_mesh,
                )
                result = compact_tension.create_model()

            elif model_name == "Smetana":
                if MYGLOBAL.smetana_enabled:
                    smetana = Smetana(
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
                        username=username,
                        ignore_mesh=ignore_mesh,
                        amplitude_factor=model_data.model.amplitudeFactor,
                        wavelength=model_data.model.wavelength,
                        angle=model_data.model.angles,
                        two_d=model_data.model.twoDimensional,
                    )
                    result = smetana.create_model()
                else:
                    log.warning("Smetana is not enabled")
                    return("Smetana is not enabled")
                    
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
                meshFile=model_data.model.meshFile,
                dx_value=dx_value,
                disc_type=disc_type,
                two_d=model_data.model.twoDimensional,
                horizon=model_data.model.horizon,
                material=model_data.materials,
                damage=model_data.damages,
                block=model_data.blocks,
                boundary_condition=model_data.boundaryConditions,
                contact=model_data.contact,
                bond_filter=model_data.bondFilters,
                compute=model_data.computes,
                output=model_data.outputs,
                solver=model_data.solver,
                username=username,
            )
            result = own.create_model()

        log.info(f"{model_name} has been created in {(time.time() - start_time):.2f} seconds")

        if result != "Model created":
            return result

        return f"{model_name} has been created in {(time.time() - start_time):.2f} seconds, dx_value: {str(dx_value)}"

    @app.post("/translateModel", tags=["Post Methods"])
    def translate_model(model_name: str, file_type: str, request: Request):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        start_time = time.time()

        localpath = "./Output/" + os.path.join(username, model_name)

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
            log.error( model_name + " results can not be found")
            return model_name + " results can not be found"

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
            FileHandler.copy_file_to_from_peridigm_container(
                username, model_name, model_name + ".g.ascii", True
            )
            != "Success"
        ):
            log.error(model_name + " can not be translated")
            return model_name + " can not be translated"

        log.info("Copy peridigm File")
        if (
            FileHandler.copy_file_to_from_peridigm_container(
                username, model_name, model_name + ".peridigm", True
            )
            != "Success"
        ):
            log.error(model_name + " can not be translated")
            return model_name + " can not be translated"

        # if return_string!='Success':
        #     return return_string

        server = "perihub_peridigm"
        remotepath = "/app/peridigmJobs/" + os.path.join(username, model_name)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(server, username="root", allow_agent=False, password="root")
        except paramiko.SSHException:
            log.error("ssh connection to " + server + " failed!")
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
        FileHandler.copy_file_to_from_peridigm_container(
            username, model_name, model_name + ".g", False
        )
        log.info("Copy yaml File")
        FileHandler.copy_file_to_from_peridigm_container(
            username, model_name, model_name + ".yaml", False
        )

        log.info(f"{model_name} has been translated in {(time.time() - start_time):.2f} seconds")
        return f"{model_name} has been translated in {(time.time() - start_time):.2f} seconds"

    @app.post("/translatGcode", tags=["Post Methods"])
    def translate_gcode(model_name: str, discretization: int, request: Request):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        start_time = time.time()

        localpath = "./Output/" + os.path.join(username, model_name)

        GcodeReader.gcode_to_peridigm(model_name, localpath, discretization)

        log.info(f"{model_name} has been translated in {(time.time() - start_time):.2f} seconds")
        return f"{model_name} has been translated in {(time.time() - start_time):.2f} seconds"

    @app.post("/uploadfiles", tags=["Post Methods"])
    async def upload_files(
        model_name: str, request: Request, files: List[UploadFile] = File(...)
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        localpath = "./Output/" + os.path.join(username, model_name)

        if not os.path.exists(localpath):
            os.makedirs(localpath)

        for file in files:
            file_location = localpath + f"/{file.filename}"
            with open(file_location, "wb+") as file_object:
                shutil.copyfileobj(file.file, file_object)

        return {"info": f"file '{files[0].file.name}' saved at '{file_location}'"}

    @app.put("/writeInputFile", tags=["Put Methods"])
    def write_input_file(
        model_name: str,
        input_string: str,
        file_type: FileType = FileType.YAML,
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        with open(
            "./Output/"
            + os.path.join(username, model_name)
            + "/"
            + model_name
            + "."
            + file_type,
            "w",
            encoding="UTF-8",
        ) as file:
            file.write(input_string)

        log.info(model_name + "-InputFile has been saved")
        return model_name + "-InputFile has been saved"

    @app.put("/runModel", tags=["Put Methods"])
    async def run_model(
        model_data: ModelData,
        model_name: str = "Dogbone",
        file_type: FileType = FileType.YAML,
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
        return_string = FileHandler.copy_model_to_cluster(username, model_name, cluster)

        if return_string != "Success":
            return return_string
        if user_mat:
            return_string = FileHandler.copy_lib_to_cluster(
                username, model_name, cluster
            )
            if return_string != "Success":
                raise HTTPException(
                    status_code=404,
                    detail=return_string,
                )

        if cluster == "FA-Cluster":
            remotepath = "./PeridigmJobs/apiModels/" + os.path.join(
                username, model_name
            )
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

            log.info(model_name + " has been submitted")
            return model_name + " has been submitted"

        elif cluster == "Cara":
            initial_jobs = FileHandler.write_get_cara_job_id()
            log.info(initial_jobs)
            sbatch = SbatchCreator(
                filename=model_name,
                output=model_data.outputs,
                job=model_data.job,
                usermail=usermail,
            )
            sbatch_string = sbatch.create_sbatch()
            remotepath = "./PeridigmJobs/apiModels/" + os.path.join(
                username, model_name
            )
            ssh, sftp = FileHandler.sftp_to_cluster("Cara")
            file = sftp.file(remotepath + "/" + model_name + ".sbatch", "w", -1)
            file.write(sbatch_string)
            file.flush()
            sftp.close()

            command = "cd " + remotepath + " \n sbatch " + model_name + ".sbatch"
            ssh.exec_command(command)
            ssh.close()
            
            await asyncio.sleep(5)
            # job_id=cara.sshClusterJob(command)

            current_jobs = FileHandler.write_get_cara_job_id()
            log.info(current_jobs)

            job_id = current_jobs.replace(initial_jobs, "").strip()

            FileHandler.write_cara_job_id_to_model(username, model_name, job_id)

            log.info(model_name + " has been submitted with Job Id: " + job_id)
            return model_name + " has been submitted with Job Id: " + job_id

        elif cluster == "None":
            server = "perihub_peridigm"
            remotepath = "/peridigmJobs/" + os.path.join(username, model_name)
            if os.path.exists(os.path.join("." + remotepath, "pid.txt")):
                log.warn(model_name + " already submitted")
                return model_name + " already submitted"
            sbatch = SbatchCreator(
                filename=model_name,
                filetype=file_type,
                remotepath=remotepath,
                output=model_data.outputs,
                job=model_data.job,
                usermail=usermail,
            )
            sh_string = sbatch.create_sh()
            with open(
                os.path.join("." + remotepath, "runPeridigm.sh"), "w", encoding="UTF-8"
            ) as file:
                file.write(sh_string)
            os.chmod(os.path.join("." + remotepath, "runPeridigm.sh"), 0o0755)
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                ssh.connect(server, username="root", allow_agent=False, password="root")
            except paramiko.SSHException:
                log.error("ssh connection to " + server + " failed!")
                return "ssh connection to " + server + " failed!"
            command = (
                "cd /app"
                + remotepath
                + " \n rm "
                + model_name
                + ".log \n sh /app"
                + remotepath
                + "/runPeridigm.sh >> "
                + model_name
                + ".log &"
            )
            ssh.exec_command(command)
            # stdin, stdout, stderr = ssh.exec_command('nohup python executefile.py >/dev/null 2>&1 &')
            # stdout=stdout.readlines()
            # stderr=stderr.readlines()
            ssh.close()

            # return stdout + stderr
            log.info(model_name + " has been submitted")
            return model_name + " has been submitted"

        log.error(cluster + " unknown")
        return cluster + " unknown"

    @app.put("/cancelJob", tags=["Put Methods"])
    def cancel_job(
        model_name: str = "Dogbone", cluster: str = "None", request: Request = ""
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        if cluster == "None":
            server = "perihub_peridigm"
            remotepath = "/peridigmJobs/" + os.path.join(username, model_name)
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                ssh.connect(server, username="root", allow_agent=False, password="root")
            except paramiko.SSHException:
                log.error("ssh connection to " + server + " failed!")
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
            return "Job has been canceled"

        remotepath = FileHandler.get_remote_model_path(cluster, username, model_name)
        ssh, sftp = FileHandler.sftp_to_cluster(cluster)
        try:
            output_files = sftp.listdir(remotepath)
            filtered_values = list(
                filter(lambda v: match(r"^.+\.log$", v), output_files)
            )
        except paramiko.SFTPError:
            log.warn("LogFile can't be found")
        if len(filtered_values) == 0:
            log.warn("LogFile can't be found")

        job_id = filtered_values[-1].split("-")[-1][:-4]
        command = "scancel " + job_id
        ssh.exec_command(command)
        ssh.close()

        log.info("Job: " + job_id + " has been canceled")
        return "Job: " + job_id + " has been canceled"

    @app.get("/generateMesh", tags=["Get Methods"])
    def generate_mesh(model_name: str, param: str, request: Request):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        # json=param,
        print(param)

        request = requests.patch(
            "https://129.247.54.235:5000/1/PyCODAC/api/micofam/{zip}", verify=False
        )
        try:
            with zipfile.ZipFile(io.BytesIO(request.content)) as zip_file:

                localpath = "./Output/" + os.path.join(username, model_name)

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
        return "Mesh generated"

    @app.get("/getImage", tags=["Get Methods"])
    def get_image(
        model_name: str = "Dogbone",
        cluster: str = "None",
        output: str = "Output1",
        variable: str = "Displacement",
        axis: str = "Magnitude",
        dx_value: float = 0.0009,
        width: int = 1920,
        height: int = 1080,
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        if not FileHandler.copy_results_from_cluster(
            username, model_name, cluster, False
        ):
            raise IOError  # NotFoundException(name=model_name)

        # subprocess.run(['./api/app/support/read.sh'], shell=True)
        with subprocess.Popen(
            [
                "sh support/read.sh image "
                + username
                + " "
                + model_name
                + " "
                + output
                + " "
                + variable
                + " "
                + axis
                + " "
                + str(dx_value)
                + " "
                + str(width)
                + " "
                + str(height)
            ],
            shell=True,
        ) as process:
            process.wait()

        try:
            return FileResponse(
                "./Results/"
                + os.path.join(username, model_name)
                + "/"
                + variable
                + "_"
                + axis
                + ".jpg"
            )
        except IOError:
            log.error(model_name + " results can not be found on " + cluster)
            return model_name + " results can not be found on " + cluster

    @app.get("/getImagePython", tags=["Get Methods"])
    def get_image_python(
        model_name: str = "Dogbone",
        cluster: str = "None",
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
        cb_left: Optional[bool]= False,
        transparent: Optional[bool]= True,
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        if not FileHandler.copy_results_from_cluster(
            username, model_name, cluster, False
        ):
            raise IOError  # NotFoundException(name=model_name)

        resultpath = "./Results/" + os.path.join(username, model_name)
        file = os.path.join(resultpath, model_name + "_" + output + ".e")

        filepath = ImageExport.get_result_image_from_exodus(file, displ_factor, marker_size, variable, axis, length, height, triangulate, dx_value, step, cb_left, transparent)

        try:
            return FileResponse(filepath)
        except IOError:
            log.error(model_name + " results can not be found on " + cluster)
            return model_name + " results can not be found on " + cluster

    @app.get("/getPlotPython", tags=["Get Methods"])
    def get_plot_python(
        model_name: str = "Dogbone",
        cluster: str = "None",
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
            username, model_name, cluster, False
        ):
            raise IOError  # NotFoundException(name=model_name)

        resultpath = "./Results/" + os.path.join(username, model_name)
        file = os.path.join(resultpath, model_name + "_" + output + ".e")

        filepath = ImageExport.get_plot_image_from_exodus(file, x_variable, x_axis, y_variable, y_axis)

        try:
            return FileResponse(filepath)
        except IOError:
            log.error(model_name + " results can not be found on " + cluster)
            return model_name + " results can not be found on " + cluster

    @app.get("/getGif", tags=["Get Methods"])
    def get_gif(
        model_name: str = "Dogbone",
        cluster: str = "None",
        output: str = "Output1",
        variable: str = "Displacement",
        axis: str = "X",
        apply_displacements: bool = False,
        displ_factor: int = 200,
        max_edge_distance: float = 0.02,
        length: float = 4.4,
        height: float = 1.1,
        fps: int = 2,
        dpi: int = 100,
        x_min: Optional[float] = None,
        x_max: Optional[float] = None,
        y_min: Optional[float] = None,
        y_max: Optional[float] = None,
        size: Optional[float] = None,
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        if not FileHandler.copy_results_from_cluster(
            username, model_name, cluster, False
        ):
            raise IOError  # NotFoundException(name=model_name)

        resultpath = "./Results/" + os.path.join(username, model_name)
        file = os.path.join(resultpath, model_name + "_" + output + ".e")

        filepath = VideoExport.get_gif_from_exodus(file, apply_displacements, displ_factor, max_edge_distance, variable, axis, length, height, fps, dpi, x_min, x_max, y_min, y_max, size)

        try:
            return FileResponse(filepath)
        except IOError:
            log.error(model_name + " results can not be found on " + cluster)
            return model_name + " results can not be found on " + cluster

    

    @app.get("/getTriangulatedMeshFromExodus", tags=["Get Methods"])
    def get_triangulated_mesh_from_exodus(
        model_name: str = "Dogbone",
        cluster: str = "None",
        output: str = "Output1",
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
            username, model_name, cluster, False
        ):
            raise IOError  # NotFoundException(name=model_name)

        resultpath = "./Results/" + os.path.join(username, model_name)
        file = os.path.join(resultpath, model_name + "_" + output + ".e")

        filepath = VideoExport.get_triangulated_mesh_from_exodus(file, displ_factor, timestep, max_edge_distance, length, height)

        try:
            return FileResponse(filepath)
        except IOError:
            log.error(model_name + " results can not be found on " + cluster)
            return model_name + " results can not be found on " + cluster

    @app.get("/getResultFile", tags=["Get Methods"])
    def get_result_file(
        model_name: str = "Dogbone",
        cluster: str = "None",
        output: str = "Output1",
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        if not FileHandler.copy_results_from_cluster(
            username, model_name, cluster, False
        ):
            raise IOError  # NotFoundException(name=model_name)

        filepath = Analysis.get_result_file(username, model_name, output)
        # print(crack_length)
        # response = [[0, 1, 2, 3], [0, 2, 3, 5]]

        try:
            return FileResponse(filepath)
        except IOError:
            log.error(model_name + " results can not be found on " + cluster)
            return model_name + " results can not be found on " + cluster
            
    @app.get("/getGlobalDataTimeseries", tags=["Get Methods"])
    def get_global_data_timeseries(
        model_name: str = "Dogbone",
        cluster: str = "None",
        output: str = "Output1",
        variable: str = "External_Force",
        axis: str = "X",
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        if not FileHandler.copy_results_from_cluster(
            username, model_name, cluster, False
        ):
            raise IOError  # NotFoundException(name=model_name)

        resultpath = "./Results/" + os.path.join(username, model_name)
        file = os.path.join(resultpath, model_name + "_" + output + ".e")

        global_data = Analysis.get_global_data(file, variable,  axis)
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
            symbolic_name= model_name + "_" + output + "_" + variable,
            field="value",
        )

        payload = TimeseriesPayload(timeseries=timeseries, points=points)

        return payload.to_dict(True)

    @app.post("/calculateG1c", tags=["Post Methods"])
    def calculate_g1c(
        model: Model,
        youngs_modulus: float = 2974,
        model_name: str = "Dogbone",
        cluster: str = "None",
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        if not FileHandler.copy_results_from_cluster(
            username, model_name, cluster, False
        ):
            raise IOError  # NotFoundException(name=model_name)

        response = Analysis.get_g1c_k1c(username, model_name, model, youngs_modulus)
        # print(crack_length)
        # response = [[0, 1, 2, 3], [0, 2, 3, 5]]
        try:
            return FileResponse(response)
        except IOError:
            log.error(model_name + " results can not be found on " + cluster)
            return model_name + " results can not be found on " + cluster

    @app.post("/calculateG2c", tags=["Post Methods"])
    def calculate_g2c(
        model: Model,
        model_name: str = "Dogbone",
        cluster: str = "None",
        output: str = "Output1",
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        if not FileHandler.copy_results_from_cluster(
            username, model_name, cluster, False
        ):
            raise IOError  # NotFoundException(name=model_name)

        response = Analysis.get_g2c(username, model_name, output, model)
        # print(crack_length)
        # response = [[0, 1, 2, 3], [0, 2, 3, 5]]
        try:
            return response
        except IOError:
            log.error(model_name + " results can not be found on " + cluster)
            return model_name + " results can not be found on " + cluster

    @app.get("/getLogFile", tags=["Get Methods"])
    def get_log_file(
        model_name: str = "Dogbone", cluster: str = "None", request: Request = ""
    ):
        """doc"""

        username = FileHandler.get_user_name(request, dev)
        # usermail = FileHandler.get_user_mail(request)

        if cluster == "None":

            remotepath = "./peridigmJobs/" + os.path.join(username, model_name)
            try:
                output_files = os.listdir(remotepath)
                filtered_values = list(
                    filter(lambda v: match(r"^.+\.log$", v), output_files)
                )
            except IOError:
                log.error("LogFile can't be found in " + remotepath)
                return "LogFile can't be found in " + remotepath
            if len(filtered_values) == 0:
                log.error("LogFile can't be found in " + remotepath)
                return "LogFile can't be found in " + remotepath

            with open(
                os.path.join(remotepath, filtered_values[-1]), "r", encoding="UTF-8"
            ) as file:
                response = file.read()

            return response

        if cluster == "FA-Cluster":
            remotepath = "./PeridigmJobs/apiModels/" + os.path.join(
                username, model_name
            )

        elif cluster == "Cara":
            remotepath = "./PeridigmJobs/apiModels/" + os.path.join(
                username, model_name
            )

        else:
            log.error(cluster + " unknown")
            return cluster + " unknown"

        ssh, sftp = FileHandler.sftp_to_cluster(cluster)

        try:
            output_files = sftp.listdir(remotepath)
            filtered_values = list(
                filter(lambda v: match(r"^.+\.log$", v), output_files)
            )
        except paramiko.SFTPError:
            log.error("LogFile can't be found in " + remotepath)
            return "LogFile can't be found in " + remotepath
        if len(filtered_values) == 0:
            log.error("LogFile can't be found in " + remotepath)
            return "LogFile can't be found in " + remotepath
        sftp.chdir(remotepath)
        logfile = sftp.file(filtered_values[-1], "r")
        response = logfile.read()
        sftp.close()
        ssh.close()

        return response

    @app.get("/getMaxFeSize", tags=["Get Methods"])
    def get_max_fe_size(request: Request = ""):
        """doc"""

        username = FileHandler.get_user_name(request, dev)

        return FileHandler.get_max_fe_size(username)

    @app.get("/getModel", tags=["Get Methods"])
    def get_model(model_name: str = "Dogbone", request: Request = ""):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        try:
            shutil.make_archive(
                model_name, "zip", "./Output/" + os.path.join(username, model_name)
            )

            response = FileResponse(
                model_name + ".zip", media_type="application/x-zip-compressed"
            )
            response.headers["Content-Disposition"] = (
                "attachment; filename=" + model_name + ".zip"
            )
            # return StreamingResponse(iterfile(), media_type="application/x-zip-compressed")
            return response
        except shutil.Error:
            log.error(model_name + " files can not be found")
            return model_name + " files can not be found"

    @app.get("/getPlot", tags=["Get Methods"])
    def get_plot(
        model_name: str = "Dogbone",
        cluster: str = "None",
        output: str = "Output1",
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
            username, model_name, cluster, False
        ):
            raise IOError  # NotFoundException(name=model_name)

        resultpath = "./Results/" + os.path.join(username, model_name)
        file = os.path.join(resultpath, model_name + "_" + output + ".e")

        x_data = Analysis.get_global_data(file, x_variable, x_axis, x_absolute)
        y_data = Analysis.get_global_data(file, y_variable, y_axis, y_absolute)

        return x_data, y_data

    @app.get("/getPointData", tags=["Get Methods"])
    def get_point_data(
        model_name: str = "Dogbone", own_model: bool = False, own_mesh: bool = False, mesh_file: str = "Dogbone.txt", request: Request = ""
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        point_string = ""
        block_id_string = ""
        if own_mesh:
            try:
                with open(
                    "./peridigmJobs/"
                    + os.path.join(username, model_name)
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
                        nodes[i] = (
                            nodes[i * 2][8:].replace(" ", "").split("=")[1].split(",")
                        )
                        for node in nodes[i]:
                            block_id[int(node) - 1] = i + 1
                    for i in range(0, len(coords[0])):
                        point_string += (
                            coords[0][i] + "," + coords[1][i] + "," + coords[2][i] + ","
                        )
                        block_id_string += str(block_id[i] / num_of_blocks) + ","

                response = [
                    point_string.rstrip(point_string[-1]),
                    block_id_string.rstrip(block_id_string[-1]),
                ]
                return response
            except IOError:
                log.error(model_name + " results can not be found")
                return model_name + " results can not be found"
        else:
            first_row = True
            max_block_id = 1
            try:
                if own_model:
                    mesh_path = "./Output/" + os.path.join(username, model_name) + "/" + mesh_file
                else:
                    mesh_path = "./Output/" + os.path.join(username, model_name) + "/" + model_name + ".txt"

                with open(mesh_path,
                    "r",
                    encoding="UTF-8",
                ) as file:
                    reader = csv.reader(file)
                    rows = list(reader)
                    for row in rows:
                        if not first_row:
                            str1 = "".join(row)
                            parts = str1.split()
                            point_string += (
                                parts[0] + "," + parts[1] + "," + parts[2] + ","
                            )
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
                return response
            except IOError:
                log.error(model_name + " results can not be found")
                return model_name + " results can not be found"

    @app.get("/getResults", tags=["Get Methods"])
    def get_results(
        model_name: str = "Dogbone",
        cluster: str = "None",
        all_data: bool = False,
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        if not FileHandler.copy_results_from_cluster(
            username, model_name, cluster, all_data
        ):

            raise HTTPException(
                status_code=404,
                detail=model_name + " results can not be found on " + cluster,
            )

        # resultpath = './Results/' + os.path.join(username, model_name)
        userpath = "./Results/" + username
        try:
            shutil.make_archive(
                os.path.join(userpath, model_name), "zip", userpath, model_name
            )

            response = FileResponse(
                os.path.join(userpath, model_name) + ".zip",
                media_type="application/x-zip-compressed",
            )
            response.headers["Content-Disposition"] = (
                "attachment; filename=" + model_name + ".zip"
            )
            # return StreamingResponse(iterfile(), media_type="application/x-zip-compressed")
            return response
        except IOError:
            log.error(model_name + " results can not be found on " + cluster)
            return model_name + " results can not be found on " + cluster

    @app.get("/getStatus", tags=["Get Methods"])
    def get_status(
        model_name: str = "Dogbone",
        own_mesh: bool = False,
        cluster: str = "None",
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        status = Status(False, False, False)

        if own_mesh:
            localpath = "./peridigmJobs/" + os.path.join(username, model_name)
        else:
            localpath = "./Output/" + os.path.join(username, model_name)

        log.info("localpath: " + localpath)
        
        if os.path.exists(localpath):
            status.created = True

        if cluster == "None":
            remotepath = "./peridigmJobs/" + os.path.join(username, model_name)
            if os.path.exists(os.path.join(remotepath, "pid.txt")):
                status.submitted = True
            if os.path.exists(remotepath):
                for files in os.listdir(remotepath):
                    if ".e" in files:
                        status.results = True

        elif cluster == "Cara":
            remotepath = "./PeridigmJobs/apiModels/" + os.path.join(
                username, model_name
            )
            ssh, sftp = FileHandler.sftp_to_cluster(cluster)

            try:
                for filename in sftp.listdir(remotepath):
                    if ".e" in filename:
                        status.results = True
            except IOError:
                sftp.close()
                ssh.close()
                return status

            sftp.close()
            ssh.close()
            job_ids = FileHandler.write_get_cara_job_id()
            job_id = FileHandler.get_cara_job_id_model(username, model_name)
            print(job_id)
            print(job_ids)
            if job_id in job_ids:
                status.submitted = True

        return status

    @app.get("/viewInputFile", tags=["Get Methods"])
    def view_input_file(
        model_name: str = "Dogbone",
        own_mesh: bool = False,
        file_type: FileType = FileType.YAML,
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        if own_mesh:
            file_path = (
                "./peridigmJobs/"
                + os.path.join(username, model_name)
                + "/"
                + model_name
                + "."
                + file_type
            )
        else:
            file_path = (
                "./Output/"
                + os.path.join(username, model_name)
                + "/"
                + model_name
                + "."
                + file_type
            )
        if not os.path.exists(file_path):
            log.error("Inputfile can't be found")
            return "Inputfile can't be found"
        try:
            return FileResponse(file_path)
        except IOError:
            log.error("Inputfile can't be found")
            return "Inputfile can't be found"

    @app.delete("/deleteModel", tags=["Delete Methods"])
    def delete_model(model_name: str = "Dogbone", request: Request = ""):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        localpath = "./Output/" + os.path.join(username, model_name)
        if os.path.exists(localpath):
            shutil.rmtree(localpath)
        log.info(model_name + " has been deleted")
        return model_name + " has been deleted"

    @app.delete("/deleteModelFromCluster", tags=["Delete Methods"])
    def delete_model_from_cluster(
        model_name: str = "Dogbone", cluster: str = "None", request: Request = ""
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        if cluster == "None":
            remotepath = "./peridigmJobs/" + os.path.join(username, model_name)
            if os.path.exists(remotepath):
                shutil.rmtree(remotepath)
            log.info(model_name + " has been deleted")
            return model_name + " has been deleted"

        if cluster == "FA-Cluster":
            remotepath = "./PeridigmJobs/apiModels/" + os.path.join(
                username, model_name
            )

        elif cluster == "Cara":
            remotepath = "./PeridigmJobs/apiModels/" + os.path.join(
                username, model_name
            )

        else:
            log.error(cluster + " unknown")
            return cluster + " unknown"

        ssh, sftp = FileHandler.sftp_to_cluster(cluster)

        for filename in sftp.listdir(remotepath):
            sftp.remove(os.path.join(remotepath, filename))
        sftp.rmdir(remotepath)
        sftp.close()
        ssh.close()
        log.info(model_name + " has been deleted")
        return model_name + " has been deleted"

    @app.delete("/deleteUserData", tags=["Delete Methods"])
    def delete_user_data(check_date: bool, request: Request, days: Optional[int] = 7):
        """doc"""
        if check_date:
            localpath = "./Output"
            if os.path.exists(localpath):
                names = FileHandler.remove_folder_if_older(localpath, days, True)
                if len(names) != 0:
                    log.info("Data of " + ", ".join(names) + " has been deleted")
                    return "Data of " + ", ".join(names) + " has been deleted"
            log.info("Nothing has been deleted")
            return "Nothing has been deleted"

        username = FileHandler.get_user_name(request, dev)

        localpath = "./Output/" + username
        shutil.rmtree(localpath)
        log.info("Data of " + username + " has been deleted")
        return "Data of " + username + " has been deleted"

    @app.delete("/deleteUserDataFromCluster", tags=["Delete Methods"])
    def delete_user_data_from_cluster(
        cluster: str, check_date: bool, request: Request, days: Optional[int] = 7
    ):
        """doc"""

        if check_date:
            if cluster == "None":
                localpath = "./peridigmJobs"
                names = FileHandler.remove_folder_if_older(localpath, days, True)
            else:
                remotepath = FileHandler.get_remote_path(cluster)

                ssh, sftp = FileHandler.sftp_to_cluster(cluster)

                names = FileHandler.remove_folder_if_older_sftp(
                    sftp, remotepath, days, True
                )

                sftp.close()
                ssh.close()

            log.info("Data of " + names + " has been deleted")
            return "Data of " + names + " has been deleted"

        username = FileHandler.get_user_name(request, dev)

        if cluster == "None":
            remotepath = "./peridigmJobs/" + username
            if os.path.exists(remotepath):
                shutil.rmtree(remotepath)
            log.info("Data of " + username + " has been deleted")
            return "Data of " + username + " has been deleted"

        remotepath = FileHandler.get_remote_user_path(cluster, username)

        ssh, sftp = FileHandler.sftp_to_cluster(cluster)

        FileHandler.remove_all_folder_sftp(sftp, remotepath, False)

        sftp.close()
        ssh.close()

        log.info("Data of " + username + " has been deleted")
        return "Data of " + username + " has been deleted"

    @app.get("/getDocs", tags=["Documentation Methods"])
    def get_docs(name: str = "Introduction", model: bool = False):
        """doc"""

        if model:
            remotepath = "./" + name + "/" + name + ".md"
        else:
            remotepath = "./guides/" + name + ".md"

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
