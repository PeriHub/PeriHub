"""
doc
"""
# Copyright (C) 2021 Deutsches Zentrum fuer Luft- und Raumfahrt(DLR, German Aerospace Center) <www.dlr.de>

# pylint: disable=no-self-argument, no-method-argument, no-member, import-error

# import uvicorn
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
from models.GIICmodel.giic_model import GIICmodel
from models.DCBmodel.dcb_model import DCBmodel
from models.Dogbone.dogbone import Dogbone
from models.KalthoffWinkler.kalthoff_winkler import KalthoffWinkler
from models.OwnModel.own_model import OwnModel
from support.sbatch_creator import SbatchCreator
from support.file_handler import FileHandler
from support.base_models import ModelData, FileType, RunData, Status


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
if dev:
    print("--- Running in development mode ---")


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
                if (
                    model_data.model == json_data["model"]
                    and model_data.boundaryConditions == json_data["boundaryConditions"]
                ):
                    print("Model not changed")
                    ignore_mesh = True

        with open(json_file, "w", encoding="UTF-8") as file:
            file.write(model_data.to_json())

        # length = 152
        # length = 50
        # width = 10
        # height = 4.95
        # number_nodes = 12

        length = model_data.model.length
        width = model_data.model.width
        height = model_data.model.height
        height2 = model_data.model.height2
        if model_name in {"Dogbone", "Kalthoff-Winkler"}:
            number_nodes = 2 * int(model_data.model.discretization / 2)
        else:
            number_nodes = 2 * int(model_data.model.discretization / 2) + 1
        dx_value = [height / number_nodes, height / number_nodes, height / number_nodes]

        start_time = time.time()

        if model_name == "GIICmodel":
            giic = GIICmodel(
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
                bond_filter=model_data.bondFilters,
                compute=model_data.computes,
                output=model_data.outputs,
                solver=model_data.solver,
                username=username,
                max_nodes=max_nodes,
                ignore_mesh=ignore_mesh,
            )
            result = kalthoff.create_model()

        elif model_data.model.ownModel:
            if model_data.model.translated:
                disc_type = "e"
            else:
                disc_type = "txt"

            own = OwnModel(
                filename=model_name,
                dx_value=dx_value,
                disc_type=disc_type,
                two_d=model_data.model.twoDimensional,
                horizon=model_data.model.horizon,
                material=model_data.materials,
                damage=model_data.damages,
                block=model_data.blocks,
                boundary_condition=model_data.boundaryConditions,
                bond_filter=model_data.bondFilters,
                compute=model_data.computes,
                output=model_data.outputs,
                solver=model_data.solver,
                username=username,
            )
            result = own.create_model()
        else:
            return "Model Name unknown"

        print(
            f"{model_name} has been created in {(time.time() - start_time):.2f} seconds"
        )

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
            return model_name + " results can not be found"

        print("Rename mesh File")
        os.rename(
            os.path.join(localpath, "mesh.g.ascii"),
            os.path.join(localpath, model_name + ".g.ascii"),
        )
        print("Rename peridigm File")
        os.rename(
            os.path.join(localpath, "model.peridigm"),
            os.path.join(localpath, model_name + ".peridigm"),
        )

        print("Copy mesh File")
        if (
            FileHandler.copy_file_to_from_peridigm_container(
                username, model_name, model_name + ".g.ascii", True
            )
            != "Success"
        ):
            return model_name + " can not be translated"

        print("Copy peridigm File")
        if (
            FileHandler.copy_file_to_from_peridigm_container(
                username, model_name, model_name + ".peridigm", True
            )
            != "Success"
        ):
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
            return "ssh connection to " + server + " failed!"
        command = (
            "/usr/local/netcdf/bin/ncgen "
            + os.path.join(remotepath, model_name)
            + ".g.ascii -o "
            + os.path.join(remotepath, model_name)
            + ".g"
            + " && python3 /Peridigm/scripts/peridigm_to_yaml.py "
            + os.path.join(remotepath, model_name)
            + ".peridigm"
            + " && rm "
            + os.path.join(remotepath, model_name)
            + ".peridigm"
        )
        # ' && rm ' +  os.path.join(remotepath, model_name) + '.g.ascii' + \
        print("Peridigm to yaml")
        _, stdout, _ = ssh.exec_command(command)
        stdout.channel.set_combine_stderr(True)
        # output = stdout.readlines()
        ssh.close()

        print("Copy mesh File")
        FileHandler.copy_file_to_from_peridigm_container(
            username, model_name, model_name + ".g", False
        )
        print("Copy yaml File")
        FileHandler.copy_file_to_from_peridigm_container(
            username, model_name, model_name + ".yaml", False
        )

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
        model_name: str, input_string: str, file_type: FileType, request: Request
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

        return model_name + "-InputFile has been saved"

    @app.put("/runModel", tags=["Put Methods"])
    def run_model(
        model_data: RunData,
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
            if mat.MatType == "User Correspondence":
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
                return return_string

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

            return model_name + " has been submitted"

        elif cluster == "Cara":
            initial_jobs = FileHandler.write_get_cara_job_id()
            print(initial_jobs)
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
            file = sftp.file(remotepath + "/" + model_name + ".sbatch", "a", -1)
            file.write(sbatch_string)
            file.flush()
            sftp.close()

            command = "cd " + remotepath + " \n sbatch " + model_name + ".sbatch"
            ssh.exec_command(command)
            ssh.close()

            current_jobs = FileHandler.write_get_cara_job_id()
            print(current_jobs)

            job_id = current_jobs.replace(initial_jobs, "").strip()

            FileHandler.write_cara_job_id_to_model(username, model_name, job_id)

            return model_name + " has been submitted with Job Id: " + job_id

        elif cluster == "None":
            server = "perihub_peridigm"
            remotepath = "/peridigmJobs/" + os.path.join(username, model_name)
            if os.path.exists(os.path.join("." + remotepath, "pid.txt")):
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
            return model_name + " has been submitted"

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

            return "Job has been canceled"

        remotepath = FileHandler.get_remote_model_path(cluster, username, model_name)
        ssh, sftp = FileHandler.sftp_to_cluster(cluster)
        try:
            output_files = sftp.listdir(remotepath)
            filtered_values = list(
                filter(lambda v: match(r"^.+\.log$", v), output_files)
            )
        except paramiko.SFTPError:
            print("LogFile can't be found")
        if len(filtered_values) == 0:
            print("LogFile can't be found")

        job_id = filtered_values[-1].split("-")[-1][:-4]
        command = "scancel " + job_id
        ssh.exec_command(command)
        ssh.close()

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
                return "LogFile can't be found in " + remotepath
            if len(filtered_values) == 0:
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
            return cluster + " unknown"

        ssh, sftp = FileHandler.sftp_to_cluster(cluster)

        try:
            output_files = sftp.listdir(remotepath)
            filtered_values = list(
                filter(lambda v: match(r"^.+\.log$", v), output_files)
            )
        except paramiko.SFTPError:
            return "LogFile can't be found in " + remotepath
        if len(filtered_values) == 0:
            return "LogFile can't be found in " + remotepath
        sftp.chdir(remotepath)
        logfile = sftp.file(filtered_values[-1], "r")
        response = logfile.read()
        sftp.close()
        ssh.close()

        return response

    @app.get("/get_max_fe_size", tags=["Get Methods"])
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
            return model_name + " files can not be found"

    @app.get("/getPlot", tags=["Get Methods"])
    def get_plot(
        model_name: str = "Dogbone",
        cluster: str = "None",
        output_name: str = "Output1",
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        if not FileHandler.copy_results_from_cluster(
            username, model_name, cluster, False
        ):
            raise HTTPException(
                status_code=404,
                detail=model_name + " results can not be found on " + cluster,
            )

        # subprocess.run(['./api/app/support/read.sh'], shell=True)
        with subprocess.Popen(
            [
                "sh support/read.sh globalData "
                + username
                + " "
                + model_name
                + " "
                + output_name
            ],
            shell=True,
        ) as process:
            process.wait()

        time_string = ""
        displacement_string = ""
        force_string = ""
        first_row = True
        try:
            with open(
                "./Results/" + os.path.join(username, model_name) + "/" + "dat.csv",
                "r",
                encoding="UTF-8",
            ) as file:
                reader = csv.reader(file)
                for row in reader:
                    # print(row)
                    if not first_row:
                        time_string += row[-1] + ","
                        displacement_string += row[4] + ","
                        force_string += row[8] + ","
                    first_row = False
            response = [
                time_string.rstrip(time_string[-1]),
                displacement_string.rstrip(displacement_string[-1]),
                force_string.rstrip(force_string[-1]),
            ]
            return response
        except IOError:
            return model_name + " results can not be found on " + cluster

    @app.get("/getPointData", tags=["Get Methods"])
    def get_point_data(
        model_name: str = "Dogbone", own_model: bool = False, request: Request = ""
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        point_string = ""
        block_id_string = ""
        if own_model:
            try:
                with open(
                    "./Output/"
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
                return model_name + " results can not be found"
        else:
            first_row = True
            max_block_id = 1
            try:
                with open(
                    "./Output/"
                    + os.path.join(username, model_name)
                    + "/"
                    + model_name
                    + ".txt",
                    "r",
                    encoding="UTF-8",
                ) as file:
                    reader = csv.reader(file)
                    rows = list(reader)
                    for row in rows:
                        if not first_row:
                            str1 = "".join(row)
                            parts = str1.split(" ")
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
                            parts = str1.split(" ")
                            block_id_string += str(int(parts[3]) / max_block_id) + ","
                        first_row = False
                response = [
                    point_string.rstrip(point_string[-1]),
                    block_id_string.rstrip(block_id_string[-1]),
                ]
                return response
            except IOError:
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
            return model_name + " results can not be found on " + cluster

    @app.get("/getStatus", tags=["Get Methods"])
    def get_status(
        model_name: str = "Dogbone", cluster: str = "None", request: Request = ""
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        status = Status(False, False, False)

        localpath = "./Output/" + os.path.join(username, model_name)
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
        file_type: FileType = FileType.YAML,
        request: Request = "",
    ):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        file_path = (
            "./Output/"
            + os.path.join(username, model_name)
            + "/"
            + model_name
            + "."
            + file_type
        )
        if not os.path.exists(file_path):
            return "Inputfile can't be found"
        try:
            return FileResponse(file_path)
        except IOError:
            return "Inputfile can't be found"

    @app.delete("/deleteModel", tags=["Delete Methods"])
    def delete_model(model_name: str = "Dogbone", request: Request = ""):
        """doc"""
        username = FileHandler.get_user_name(request, dev)

        localpath = "./Output/" + os.path.join(username, model_name)
        if os.path.exists(localpath):
            shutil.rmtree(localpath)
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
            return cluster + " unknown"

        ssh, sftp = FileHandler.sftp_to_cluster(cluster)

        for filename in sftp.listdir(remotepath):
            sftp.remove(os.path.join(remotepath, filename))
        sftp.rmdir(remotepath)
        sftp.close()
        ssh.close()
        return model_name + " has been deleted"

    @app.delete("/deleteUserData", tags=["Delete Methods"])
    def delete_user_data(check_date: bool, request: Request, days: Optional[int] = 7):
        """doc"""
        if check_date:
            localpath = "./Output"
            if os.path.exists(localpath):
                names = FileHandler.remove_folder_if_older(localpath, days, True)
                if len(names) != 0:
                    return "Data of " + ", ".join(names) + " has been deleted"
            return "Nothing has been deleted"

        username = FileHandler.get_user_name(request, dev)

        localpath = "./Output/" + username
        shutil.rmtree(localpath)
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

            return "Data of " + names + " has been deleted"

        username = FileHandler.get_user_name(request, dev)

        if cluster == "None":
            remotepath = "./peridigmJobs/" + username
            if os.path.exists(remotepath):
                shutil.rmtree(remotepath)
            return "Data of " + username + " has been deleted"

        remotepath = FileHandler.get_remote_user_path(cluster, username)

        ssh, sftp = FileHandler.sftp_to_cluster(cluster)

        FileHandler.remove_all_folder_sftp(sftp, remotepath, False)

        sftp.close()
        ssh.close()

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
