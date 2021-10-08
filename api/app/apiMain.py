# Copyright (C) 2021 Deutsches Zentrum fuer Luft- und Raumfahrt(DLR, German Aerospace Center) <www.dlr.de>


# from ntpath import join
# from fastapi import responses
# from numpy import string_
# from numpy.lib.shape_base import split
from GIICmodel.GIICmodel import GIICmodel
from DCBmodel.DCBmodel import DCBmodel
from Dogbone.Dogbone import Dogbone
from support.sbatchCreator  import SbatchCreator
from support.fileHandler  import fileHandler
#from XFEM_Bechnmark.XFEMdcb import XFEMDCB
# import matplotlib.pyplot as plt
# import pandas as pd
from typing import Optional
from fastapi import FastAPI, Header, Request
from fastapi.responses import FileResponse
# from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import shutil
import filecmp

from enum import Enum

import paramiko
import os
import csv
from re import match
import time
import subprocess


class ModelName(str, Enum):
    Dogbone = "Dogbone"
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

    @app.post("/generateModel")
    def generateModel(ModelName: ModelName, Length: float, Width: float, Height: float, Discretization: float, TwoDimensional: bool, RotatedAngles: bool, Angle0: float, Angle1: float, Param: dict, request: Request, Height2: Optional[float] = None):#Material: dict, Output: dict):
       
        username = request.headers.get('x-forwarded-preferred-username')
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
            solver=Param['Param']['Solver'],
            username = username)
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
            solver=Param['Param']['Solver'],
            username = username)
            model = dcb.createModel()

        if ModelName==ModelName.Dogbone:
            db = Dogbone(xend = L, h1 = h, h2 = Height2, zend = W, dx=dx,
            TwoD = TwoDimensional, 
            rot=RotatedAngles, angle=[Angle0,Angle1], 
            material=Param['Param']['Material'], 
            damage=Param['Param']['Damage'], 
            block=Param['Param']['Block'], 
            bc=Param['Param']['BoundaryConditions'], 
            compute=Param['Param']['Compute'],  
            output=Param['Param']['Output'], 
            solver=Param['Param']['Solver'],
            username = username)
            model = db.createModel()

        print()
        return ModelName + ' has been created in ' + "%.2f seconds" % (time.time() - start_time) + ', dx: '+ str(dx)
   
    @app.get("/viewInputFile")
    def viewInputFile(ModelName: ModelName, FileType: FileType, request: Request):
        username = request.headers.get('x-forwarded-preferred-username')

        try:
            return FileResponse('./Output/' + os.path.join(username, ModelName) + '/'  + ModelName + '.' + FileType)
        except:
            return 'Inputfile can\'t be found'

    @app.post("/writeInputFile")
    def writeInputFile(ModelName: ModelName, InputString: str, FileType: FileType, request: Request):
        username = request.headers.get('x-forwarded-preferred-username')

        fid = open('./Output/' + os.path.join(username, ModelName) + '/'  + ModelName + '.' + FileType ,'w')
        fid.write(InputString)
        fid.close()

        return ModelName + '-InputFile has been saved'

    @app.get("/getModel")
    def getModel(ModelName: ModelName, request: Request):
        username = request.headers.get('x-forwarded-preferred-username')

        try:
            shutil.make_archive(ModelName, "zip", './Output/' + os.path.join(username, ModelName))

            response = FileResponse(ModelName + ".zip", media_type="application/x-zip-compressed")
            response.headers["Content-Disposition"] = "attachment; filename=" + ModelName + ".zip"
            # return StreamingResponse(iterfile(), media_type="application/x-zip-compressed")
            return response
        except:
            return 'Modelfiles can\'t be found'


        
    @app.get("/getLogFile")
    def getLogFile(ModelName: ModelName, Cluster: str, request: Request):

        username = request.headers.get('x-forwarded-preferred-username')
        usermail = request.headers.get('x-forwarded-email')

        if Cluster=='None':
            
            remotepath = './peridigmJobs/' + os.path.join(username, ModelName)
            try:
                outputFiles = os.listdir(remotepath)
                filtered_values = list(filter(lambda v: match('^.+\.log$', v), outputFiles))
            except:
                return 'LogFile can\'t be found'
            if(len(filtered_values)==0):
                return 'LogFile can\'t be found'

            f = open(os.path.join(remotepath, filtered_values[-1]), 'r')
            response = f.read()
            f.close()

            return response

        else:
            if Cluster=='FA-Cluster':
                remotepath = './Peridigm/apiModels/' + os.path.join(username, ModelName)
            
            elif Cluster=='Cara':
                remotepath = './PeridigmJobs/apiModels/' + os.path.join(username, ModelName)

            else:
                return Cluster + ' unknown'

            ssh, sftp = fileHandler.sftpToCluster(Cluster, 'hess_ja')

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
        username = request.headers.get('x-forwarded-preferred-username')

        fileHandler.copyResultsFromCluster(username, ModelName, Cluster, allData)

        # resultpath = './Results/' + os.path.join(username, ModelName)
        userpath = './Results/' + username
        try:
            shutil.make_archive(os.path.join(userpath, ModelName), "zip", userpath, ModelName)

            response = FileResponse(os.path.join(userpath, ModelName) + ".zip", media_type="application/x-zip-compressed")
            response.headers["Content-Disposition"] = "attachment; filename=" + ModelName + ".zip"
            # return StreamingResponse(iterfile(), media_type="application/x-zip-compressed")
            return response
        except:
            return 'Resultfiles can\'t be found'

    # @app.get("/getResults")
    # def getResults(ModelName: ModelName, username: str):

    #     resultpath = './Results/' + os.path.join(username, ModelName)
    #     userpath = './Results/' + username
    #     try:
    #         shutil.make_archive(ModelName, "zip", userpath, resultpath)

    #         response = FileResponse(os.path.join(userpath, ModelName) + ".zip", media_type="application/x-zip-compressed")
    #         response.headers["Content-Disposition"] = "attachment; filename=" + ModelName + ".zip"
    #         # return StreamingResponse(iterfile(), media_type="application/x-zip-compressed")
    #         return response
    #     except:
    #         return 'Resultfiles can\'t be found'
            
    @app.post("/deleteModel")
    def deleteModel(ModelName: ModelName, request: Request):
        username = request.headers.get('x-forwarded-preferred-username')

        localpath = './Output/' + os.path.join(username, ModelName)
        shutil.rmtree(localpath)
        return ModelName + ' has been deleted'


    @app.post("/deleteModelFromCluster")
    def deleteModelFromCluster(ModelName: ModelName, Cluster: str, request: Request):
        username = request.headers.get('x-forwarded-preferred-username')

        if Cluster=='None':
            remotepath = './peridigmJobs/' + os.path.join(username, ModelName)
            shutil.rmtree(remotepath)
            return ModelName + ' has been deleted'

        else:
            if Cluster=='FA-Cluster':
                remotepath = './Peridigm/apiModels/' + os.path.join(username, ModelName)
            
            elif Cluster=='Cara':
                remotepath = './PeridigmJobs/apiModels/' + os.path.join(username, ModelName)

            else:
                return Cluster + ' unknown'

            ssh, sftp = fileHandler.sftpToCluster(Cluster, username)

            for filename in sftp.listdir(remotepath):
                sftp.remove(os.path.join(remotepath, filename))
            sftp.rmdir(remotepath)
            sftp.close()
            ssh.close()
            return ModelName + ' has been deleted'

    @app.post("/deleteUserData")
    def deleteUserData(request: Request):
        username = request.headers.get('x-forwarded-preferred-username')

        localpath = './Output/' + username
        shutil.rmtree(localpath)
        return 'Data of ' + username + ' has been deleted'

    @app.post("/deleteUserDataFromCluster")
    def deleteUserDataFromCluster(Cluster: str, request: Request):
        username = request.headers.get('x-forwarded-preferred-username')

        if Cluster=='None':
            remotepath = './peridigmJobs/' + username
            shutil.rmtree(remotepath)
            return 'Data of ' + username + ' has been deleted'

        else:
            remotepath = fileHandler.getRemoteUserPath(Cluster, username)
            
            ssh, sftp = fileHandler.sftpToCluster(Cluster, username)

            for filename in sftp.listdir(remotepath):
                for subfilename in sftp.listdir(os.path.join(remotepath, filename)):
                    sftp.remove(os.path.join(remotepath, subfilename))
                sftp.remove(os.path.join(remotepath, filename))
            sftp.rmdir(remotepath)
            sftp.close()
            ssh.close()
            return 'Data of ' + username + ' has been deleted'

    @app.get("/getPlot")
    def getPlot(ModelName: ModelName, Cluster: str, request: Request):
        username = request.headers.get('x-forwarded-preferred-username')

        fileHandler.copyResultsFromCluster(username, ModelName, Cluster, False)

        # subprocess.run(['./api/app/support/read.sh'], shell=True)
        process = subprocess.Popen(['./support/read.sh ' + username + ' ' + ModelName], shell=True)
        process.wait()

        timeString=''
        displacementString=''
        forceString=''
        firstRow=True  
        try:
            with open('./Results/' + os.path.join(username, ModelName) + '/'  + 'dat.csv', 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    # print(row)
                    if firstRow==False:
                        timeString+=row[-1]+','
                        displacementString+=row[4]+','
                        forceString+=row[8]+','
                    firstRow=False
            response=[timeString.rstrip(timeString[-1]),displacementString.rstrip(displacementString[-1]),forceString.rstrip(forceString[-1])]  
            return response
        except:
            return 'Resultfile can\'t be found'

    @app.get("/getImage")
    def getImage(ModelName: ModelName, Cluster: str, request: Request):
        username = request.headers.get('x-forwarded-preferred-username')

        fileHandler.copyResultsFromCluster(username, ModelName, Cluster, False)

        # subprocess.run(['./api/app/support/read.sh'], shell=True)
        process = subprocess.Popen(['./support/read.sh ' + username + ' ' + ModelName], shell=True)
        process.wait()

        try:
            return FileResponse('./Results/' + os.path.join(username, ModelName) + '/'  + 'displ.jpg')
        except:
            return 'Resultfile can\'t be found'

    @app.get("/getPointData")
    def getPointData(ModelName: ModelName, request: Request):
        username = request.headers.get('x-forwarded-preferred-username')

        pointString=''
        blockIdString=''
        firstRow=True  
        try:
            with open('./Output/' + os.path.join(username, ModelName) + '/'  + ModelName + '.txt', 'r') as f:
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
    def copyModelToCluster(ModelName: ModelName, Cluster: str, request: Request):
        username = request.headers.get('x-forwarded-preferred-username')
        
        if Cluster=='None':
            localpath = './Output/' + os.path.join(username, ModelName)
            remotepath = './peridigmJobs/' + os.path.join(username, ModelName)
            if not os.path.exists(remotepath):
                os.makedirs(remotepath)
                # os.chown(remotepath, 'test')
            if not os.path.exists(localpath):
                return ModelName + ' has not been created yet'
            for root, dirs, files in os.walk(localpath):
                if len(files)==0:
                    return ModelName + ' has not been created yet'

                for name in files:
                    shutil.copy(os.path.join(root,name), os.path.join(remotepath,name))
                    # os.chmod(os.path.join(remotepath,name), 0o0777)
                    # os.chown(os.path.join(remotepath,name), 'test')
            return ModelName + ' has been copied'

        else:       
            
            remotepath = fileHandler.getRemoteModelPath(Cluster, username, ModelName)
            userpath = fileHandler.getUserPath(Cluster, username, ModelName) 
            ssh, sftp = fileHandler.sftpToCluster(Cluster, username)

            try:
                sftp.chdir(remotepath)  # Test if remote_path exists
            except IOError:
                sftp.mkdir(userpath)
                sftp.mkdir(remotepath)  # Create remote_path
                sftp.chdir(remotepath)
            for root, dirs, files in os.walk('./Output/' + os.path.join(username, ModelName)):
                if len(files)==0:
                    return ModelName + ' has not been created yet'
                for name in files:
                    sftp.put(os.path.join(root,name), name)

            sftp.close()
            ssh.close()
            
            return ModelName + ' has been copied to Cluster'

    @app.post("/runModel")
    def runModel(ModelName: ModelName, FileType: FileType, Param: dict, request: Request):
        username = request.headers.get('x-forwarded-preferred-username')
        usermail = request.headers.get('x-forwarded-email')

        if Param['Param']['Job']['cluster']=='FA-Cluster':
            remotepath = './Peridigm/apiModels/' + os.path.join(username, ModelName)
            ssh = fileHandler.sshToCluster('FA-Cluster', username)
            command = 'cd ' + remotepath + ' \n qperidigm -d -c ' + str(Param['Param']['Job']['tasks']) + ' -O tgz -J ' + ModelName +' -E /home/hess_ja/PeridigmInstall/build/bin/Peridigm '+ ModelName + '.' + FileType
            ssh.exec_command(command)
            ssh.close()

            return ModelName + ' has been submitted'

        elif Param['Param']['Job']['cluster']=='Cara':
            sb = SbatchCreator(filename=ModelName, output=Param['Param']['Output'], job=Param['Param']['Job'], username=username, usermail=usermail)
            sbatchString = sb.createSbatch()
            remotepath = './PeridigmJobs/apiModels/' + os.path.join(username, ModelName)
            ssh, sftp = fileHandler.sftpToCluster('Cara', username)
            file=sftp.file(remotepath + '/' + ModelName + '.sbatch', "a", -1)
            file.write(sbatchString)
            file.flush()
            sftp.close()

            command = 'cd ' + remotepath + ' \n sbatch '+ ModelName + '.sbatch'
            ssh.exec_command(command)
            ssh.close()

            return ModelName + ' has been submitted'

        elif Param['Param']['Job']['cluster']=='None':
            server='peridigm'
            remotepath = '/peridigmJobs/' + os.path.join(username, ModelName)
            if os.path.exists(os.path.join('.' + remotepath,'pid.txt')):
                return ModelName + ' already submitted'
            sh = SbatchCreator(filename=ModelName, filetype= FileType, remotepath=remotepath, output=Param['Param']['Output'], job=Param['Param']['Job'], username=username, usermail=usermail)
            shString = sh.createSh()
            f = open(os.path.join('.' + remotepath,"runPeridigm.sh"), "w")
            f.write(shString)
            f.close()
            os.chmod(os.path.join('.' + remotepath,"runPeridigm.sh"), 0o0755)
            ssh = paramiko.SSHClient() 
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(server, username='root', allow_agent=False, password='root')
            command = 'cd /app' + remotepath + ' \n rm ' + ModelName + '.log \n sh /app' + remotepath + '/runPeridigm.sh >> ' + ModelName + '.log &'
            stdin, stdout, stderr  = ssh.exec_command(command)
            #stdin, stdout, stderr = ssh.exec_command('nohup python executefile.py >/dev/null 2>&1 &')
            # stdout=stdout.readlines()
            # stderr=stderr.readlines()
            ssh.close()

            # return stdout + stderr
            return ModelName + ' has been submitted'

        else:
            return Param['Param']['Job']['cluster'] + ' unknown'

    @app.post("/cancelJob")
    def cancelJob(ModelName: ModelName, Cluster: str, request: Request):
        username = request.headers.get('x-forwarded-preferred-username')

        if Cluster=='None':
            server='peridigm'
            remotepath = '/peridigmJobs/' + os.path.join(username, ModelName)
            ssh = paramiko.SSHClient() 
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(server, username='root', allow_agent=False, password='root')
            command = 'kill -9 `cat /app' + os.path.join(remotepath, 'pid.txt') + '` \n rm /app' + os.path.join(remotepath, 'pid.txt')
            stdin, stdout, stderr  = ssh.exec_command(command)
            stdout=stdout.readlines()
            stderr=stderr.readlines()
            ssh.close()
            return stdout + stderr

        else:     
            remotepath = fileHandler.getRemoteModelPath(Cluster, username, ModelName)
            ssh, sftp = fileHandler.sftpToCluster(Cluster, username)
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

    # uvicorn.run(app, host="0.0.0.0", port=80)    
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

    # subprocess.run(['api\\app\\support\\ParaView-5.9.1-Windows-Python3.8-msvc2017-64bit\\bin\\pvpython.exe .\\api\\app\\support\\exodusReader.py'], shell=True)
    # p = subprocess.Popen(['./api/app/support/ParaView-5.9.1-Windows-Python3.8-msvc2017-64bit/bin/pvpython.exe api/app/support/exodusReader.py'],
    #                 stdin=subprocess.PIPE,
    #                 stdout=subprocess.PIPE,
    #                 )
    # p.stdin.write("a\n")
    # p.stdin.write("b\n")
    # ...
    # p.stdin.close()
    # p.wait()

    
    # subprocess.run(['api\\app\\support\\read.bat'], shell=True)

    # timeString=''
    # forceString=''
    # firstRow=True  

    # with open('./Output/' + 'GIICmodel' + '/'  + 'dat.csv', 'r') as f:
    #         reader = csv.reader(f)
    #         for row in reader:
    #             # print(row)
    #             if firstRow==False:
    #                 timeString+=row[5]+','
    #                 forceString+=row[4]+','
    #             firstRow=False
       
    # print(timeString)  
    # print(forceString)        
    # response=[timeString.rstrip(timeString[-1]),forceString.rstrip(forceString[-1])]  
    
    # username='hess_ja'
    # ModelName='GIICmodel'
    # FileType='yaml'
    # server='peridigm'
    # remotepath = '/app/PeridigmJobs/' + os.path.join(username, ModelName)
    # command = '/peridigm/build/src/Peridigm ' + os.path.join(remotepath, ModelName + '.' + FileType)
    # print(command)
        
        
        
        
        
        

