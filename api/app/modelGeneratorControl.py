# Copyright (C) 2021 Deutsches Zentrum fuer Luft- und Raumfahrt(DLR, German Aerospace Center) <www.dlr.de>


# from ntpath import join
# from fastapi import responses
# from numpy import string_
# from numpy.lib.shape_base import split
from GIICmodel.GIICmodel import GIICmodel
from DCBmodel.DCBmodel import DCBmodel
from support.sbatchCreator  import SbatchCreator
#from XFEM_Bechnmark.XFEMdcb import XFEMDCB
# import matplotlib.pyplot as plt
# import pandas as pd
# from typing import List, Optional
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
# from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from enum import Enum

import shutil
import paramiko
import os
import csv
from re import match
import time


class ModelName(str, Enum):
    GIICmodel = "GIICmodel"
    DCBmodel = "DCBmodel"
class FileType(str, Enum):
    yaml = "yaml"
    xml = "xml"

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class ModelControl(object):

    def __init__(self,**kwargs):
        """doc"""
        self.returnDir = None

    def run(self,**kwargs):
        """doc"""
        
        L = 152
        L = 50
        W = 10
        h = 4.95
        nn = 11

        nn = 2*int(nn/2)+1
        dx=[h/nn,h/nn,h/nn]
        
        print(dx, 4.01*dx[0])
        
        # dx=[0.001,0.001,0.001]
        # db = DCBmodel(dx = dx, TwoD = True, filetype = 'xml')
        # model = db.createModel()
        gc = GIICmodel(xend = L, yend = h, zend = W, dx=dx, TwoD = False, rot=False)
        model = gc.createModel()
        #xm = XFEMDCB(xend = L, yend = 2*h, dx=[0.08,0.08])

    def endRunOnError(self):
        pass
        
    def endRun(self, returnDir = None, feFilename = None, runDir = None):
       pass


    @app.post("/generateModel")
    def generateModel(ModelName: ModelName, Length: float, Width: float, Height: float, Discretization: float, TwoDimensional: bool, RotatedAngles: bool, Angle0: float, Angle1: float, Param: dict):#Material: dict, Output: dict):
        # L = 152
        # L = 50
        # W = 10
        # h = 4.95
        # nn = 12

        L = Length
        W = Width
        h = Height
        nn = 2*int(Discretization/2)+1
        dx=[h/nn,h/nn,h/nn]

        start_time = time.time()
        
        if ModelName==ModelName.GIICmodel:
            gc = GIICmodel(xend = L, yend = h, zend = W, dx=dx,
            TwoD = TwoDimensional,
            rot=RotatedAngles, angle=[Angle0,Angle1], 
            material=Param['Param']['Material'], 
            damage=Param['Param']['Damage'], 
            block=Param['Param']['Block'], 
            bc=Param['Param']['BoundaryConditions'],
            compute=Param['Param']['Compute'],  
            output=Param['Param']['Output'], 
            solver=Param['Param']['Solver'])
            model = gc.createModel()

        if ModelName==ModelName.DCBmodel:
            dcb = DCBmodel(xend = L, yend = h, zend = W, dx=dx,
            TwoD = TwoDimensional, 
            rot=RotatedAngles, angle=[Angle0,Angle1], 
            material=Param['Param']['Material'], 
            damage=Param['Param']['Damage'], 
            block=Param['Param']['Block'], 
            bc=Param['Param']['BoundaryConditions'], 
            compute=Param['Param']['Compute'],  
            output=Param['Param']['Output'], 
            solver=Param['Param']['Solver'])
            model = dcb.createModel()

        print()
        return ModelName + ' has been created in ' + "%.2f seconds" % (time.time() - start_time) + ', dx: '+ str(dx)
        
        
    @app.get("/viewInputFile")
    def viewInputFile(ModelName: ModelName, FileType: FileType):
        try:
            return FileResponse('./Output/' + ModelName + '/'  + ModelName + '.' + FileType)
        except:
            return 'Inputfile can\'t be found'

    @app.post("/writeInputFile")
    def writeInputFile(ModelName: ModelName, InputString: str, FileType: FileType):

        fid = open('./Output/' + ModelName + '/'  + ModelName + '.' + FileType ,'w')
        fid.write(InputString)
        fid.close()

        return ModelName + '-InputFile has been saved'

    @app.get("/getModel")
    def getModel(ModelName: ModelName):

        try:
            shutil.make_archive(ModelName, "zip", './Output/' + ModelName)

            response = FileResponse(ModelName + ".zip", media_type="application/x-zip-compressed")
            response.headers["Content-Disposition"] = "attachment; filename=" + ModelName + ".zip"
            # return StreamingResponse(iterfile(), media_type="application/x-zip-compressed")
            return response
        except:
            return 'Modelfiles can\'t be found'


        
    @app.get("/getLogFile")
    def getLogFile(ModelName: ModelName, Cluster: str):

        if Cluster=='FA-Cluster':
            username='hess_ja'
            server='129.247.54.37'
            keypath = 'id_rsa_cluster'
            remotepath = './Peridigm/apiModels/' + ModelName
        
        elif Cluster=='Cara':
            username='hess_ja'
            server='cara.dlr.de'
            keypath = 'id_rsa_cara'
            remotepath = './PeridigmJobs/apiModels/' + ModelName

        else:
            return Cluster + ' unknown'

        ssh = paramiko.SSHClient() 
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server, username=username, allow_agent=False, key_filename=keypath)
        sftp = ssh.open_sftp()
        try:
            outputFiles = sftp.listdir(remotepath)
            filtered_values = list(filter(lambda v: match('^.+\.log$', v), outputFiles))
        except:
            return 'LogFile can\'t be found'
        if(len(filtered_values)==0):
            return 'LogFile can\'t be found'
        sftp.chdir(remotepath)
        logfile = sftp.file(filtered_values[-1],'r')
        response = logfile.read()
        sftp.close()
        ssh.close()

        return response


    @app.get("/getResults")
    def getResults(ModelName: ModelName, Cluster: str, allData: bool, request: Request):
        
        print(request)
        headers = request.headers
        email = request.headers.get('X-Forwarded-Email')
        print(headers)
        print(email)

        if Cluster=='FA-Cluster':
            username='hess_ja'
            server='129.247.54.37'
            keypath = 'id_rsa_cluster'
            remotepath = './Peridigm/apiModels/' + ModelName
        
        elif Cluster=='Cara':
            username='hess_ja'
            server='cara.dlr.de'
            keypath = 'id_rsa_cara'
            remotepath = './PeridigmJobs/apiModels/' + ModelName

        else:
            return Cluster + ' unknown'
        
        localpath = './Results/' + ModelName
        if not os.path.exists('./Results'):
            os.mkdir('./Results')
        if not os.path.exists('./Results/' + ModelName):
            os.mkdir('./Results/' + ModelName)
        ssh = paramiko.SSHClient() 
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server, username=username, allow_agent=False, key_filename=keypath)
        sftp = ssh.open_sftp()
        for filename in sftp.listdir(remotepath):
            if(allData or '.e' in filename):
                sftp.get(os.path.join(remotepath, filename), os.path.join(localpath, filename))
        sftp.close()
        ssh.close()
        
        try:
            shutil.make_archive(ModelName, "zip", './Results/' + ModelName)

            response = FileResponse(ModelName + ".zip", media_type="application/x-zip-compressed")
            response.headers["Content-Disposition"] = "attachment; filename=" + ModelName + ".zip"
            # return StreamingResponse(iterfile(), media_type="application/x-zip-compressed")
            return response
        except:
            return 'Resultfiles can\'t be found'
            

    @app.get("/getPointData")
    def getPointData(ModelName: ModelName):

        pointString=''
        blockIdString=''
        firstRow=True  
        try:
            with open('./Output/' + ModelName + '/'  + ModelName + '.txt', 'r') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if firstRow==False:
                            str1 = ''.join(row)
                            parts = str1.split(" ")
                            pointString+=parts[0]+','+parts[1]+','+parts[2]+','
                            blockIdString+=str(int(parts[3])/10)+','
                        firstRow=False
                        
            response=[pointString.rstrip(pointString[-1]),blockIdString.rstrip(blockIdString[-1])]
            return response
        except:
            return 'Meshfile can\'t be found'

    @app.get("/copyModelToCluster")
    def copyModelToCluster(ModelName: ModelName, Cluster: str):

        if Cluster=='FA-Cluster':
            username='hess_ja'
            server='129.247.54.37'
            keypath = 'id_rsa_cluster'
            remotepath = './Peridigm/apiModels/' + ModelName
        
        elif Cluster=='Cara':
            username='hess_ja'
            server='cara.dlr.de'
            keypath = 'id_rsa_cara'
            remotepath = './PeridigmJobs/apiModels/' + ModelName

        else:
            return Cluster + ' unknown'
        
        ssh = paramiko.SSHClient() 
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server, username=username, allow_agent=False, key_filename=keypath)
        sftp = ssh.open_sftp()
        try:
            sftp.chdir(remotepath)  # Test if remote_path exists
        except IOError:
            sftp.mkdir(remotepath)  # Create remote_path
            sftp.chdir(remotepath)
        for root, dirs, files in os.walk('./Output/' + ModelName):
            for name in files:
                sftp.put(os.path.join(root,name), name)

        sftp.close()
        ssh.close()
        
        return ModelName + ' has been copied to Cluster'

    @app.post("/runModel")
    def runModel(ModelName: ModelName, FileType: FileType, Param: dict):

        if Param['Param']['Job']['cluster']=='FA-Cluster':
            username='hess_ja'
            server='129.247.54.37'
            keypath = 'id_rsa_cluster'
            remotepath = './Peridigm/apiModels/' + ModelName
            ssh = paramiko.SSHClient() 
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(server, username=username, allow_agent=False, key_filename=keypath)
            command = 'cd ' + remotepath + ' \n qperidigm -d -c ' + str(Param['Param']['Job']['tasks']) + ' -O tgz -J ' + ModelName +' -E /home/hess_ja/PeridigmInstall/build/bin/Peridigm '+ ModelName + '.' + FileType
            ssh.exec_command(command)
            ssh.close()

            return ModelName + ' has been submitted'

        elif Param['Param']['Job']['cluster']=='Cara':
            sb = SbatchCreator(filename=ModelName, output=Param['Param']['Output'], job=Param['Param']['Job'])
            sbatchString = sb.createSbatch()
            username='hess_ja'
            server='cara.dlr.de'
            keypath = 'id_rsa_cara'
            remotepath = './PeridigmJobs/apiModels/' + ModelName
            ssh = paramiko.SSHClient() 
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(server, username=username, allow_agent=False, key_filename=keypath)
            sftp = ssh.open_sftp()
            file=sftp.file(remotepath + '/' + ModelName + '.sbatch', "a", -1)
            file.write(sbatchString)
            file.flush()
            sftp.close()

            command = 'cd ' + remotepath + ' \n sbatch '+ ModelName + '.sbatch'
            ssh.exec_command(command)
            ssh.close()

            return ModelName + ' has been submitted'

        else:
            return Param['Param']['Job']['cluster'] + ' unknown'

    @app.post("/cancelJob")
    def cancelJob(ModelName: ModelName, Cluster: str):

        if Cluster=='FA-Cluster':
            username='hess_ja'
            server='129.247.54.37'
            keypath = 'id_rsa_cluster'
            remotepath = './Peridigm/apiModels/' + ModelName

        elif Cluster=='Cara':
            username='hess_ja'
            server='cara.dlr.de'
            keypath = 'id_rsa_cara'
            remotepath = './PeridigmJobs/apiModels/' + ModelName

        else:
            return Cluster + ' unknown'
        
        ssh = paramiko.SSHClient() 
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server, username=username, allow_agent=False, key_filename=keypath)
        sftp = ssh.open_sftp()
        try:
            outputFiles = sftp.listdir(remotepath)
            filtered_values = list(filter(lambda v: match('^.+\.log$', v), outputFiles))
        except:
            print( 'LogFile can\'t be found')
        if(len(filtered_values)==0):
            print(  'LogFile can\'t be found')
        
        jobId = filtered_values[-1].split("-")[-1][:-4]
        command = 'scancel ' + jobId
        ssh.exec_command(command)
        ssh.close()

        return 'Job: ' + jobId + ' has been canceled'

    # uvicorn.run(app, host="0.0.0.0", port=8000)    
    # pointString=''
    # firstRow=True  
    # with open('./Output/' + "GIICmodel" + '/'  + "GIICmodel" + '.txt', 'r') as f:
    #         reader = csv.reader(f)
    #         for row in reader:
    #             if firstRow==False:
    #                 str1 = ''.join(row)
    #                 parts = str1.split(" ")
    #                 pointString+=parts[0]+','+parts[1]+','+parts[2]+','
    #             firstRow=False
                
    # pointString=pointString.rstrip(pointString[-1])

    # from pyevtk.hl import pointsToVTK
    # import meshio
    # import numpy as np 
    # npoints = 100 
    # x = np.random.rand(npoints) 
    # y = np.random.rand(npoints) 
    # z = np.random.rand(npoints) 
    # pressure = np.random.rand(npoints) 
    # temp = np.random.rand(npoints) 
    # test = pointsToVTK("./points", x, y, z, data = {"temp" : temp, "pressure" : pressure})
    # mesh = meshio.read("./points.vtu")
    # points = [
    # [0.0, 0.0],
    # [1.0, 0.0],
    # [0.0, 1.0],
    # [1.0, 1.0],
    # [2.0, 0.0],
    # [2.0, 1.0],
    # ]
    # cells = [
    #     ("triangle", [[0, 1, 2], [1, 3, 2]]),
    #     ("quad", [[1, 4, 5, 3]]),
    # ]

    # mesh = meshio.Mesh(
    #     points,
    #     cells,
    #     # Optionally provide extra data on points, cells, etc.
    #     point_data={"T": [0.3, -1.2, 0.5, 0.7, 0.0, -3.0]},
    #     # Each item in cell data must match the cells array
    #     cell_data={"a": [[0.1, 0.2], [0.4]]},
    # )
    # mesh.write("./foo.stl")
    # print(mesh)
    
    
    # username='hess_ja'
    # server='cara.dlr.de'
    # keypath = 'id_rsa_cara'
    # remotepath = './PeridigmJobs/apiModels/' + 'GIICmodel'
    # ssh = paramiko.SSHClient() 
    # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # ssh.connect(server, username=username, allow_agent=False, key_filename=keypath)
    # sftp = ssh.open_sftp()
    # try:
    #     outputFiles = sftp.listdir(remotepath)
    #     filtered_values = list(filter(lambda v: match('^.+\.log$', v), outputFiles))
    # except:
    #     print( 'LogFile can\'t be found')
    # if(len(filtered_values)==0):
    #     print(  'LogFile can\'t be found')
    
    # jobId = filtered_values[-1].split("-")[-1][:-4]
    # print(jobId)

    # command = 'scancel ' + jobId
    # ssh.exec_command(command)
    # ssh.close()

    # print(' has been submitted')

    # import cadquery
    # cadquery.Workplane('XY').box(1,2,3).toSvg()

        
        
        
        
        
        
        
        
        
        
        
        

