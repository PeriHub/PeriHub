# Copyright (C) 2021 Deutsches Zentrum fuer Luft- und Raumfahrt(DLR, German Aerospace Center) <www.dlr.de>


# from ntpath import join
# from fastapi import responses
# from numpy import string_
# from numpy.lib.shape_base import split
from GIICmodel.GIICmodel import GIICmodel
from DCBmodel.DCBmodel import DCBmodel
from Verification.verificationModels import VerificationModels
from Dogbone.Dogbone import Dogbone
from ownModel.ownModel import OwnModel
from support.sbatchCreator  import SbatchCreator
from support.fileHandler  import fileHandler
#from XFEM_Bechnmark.XFEMdcb import XFEMDCB
# import matplotlib.pyplot as plt
# import pandas as pd
from typing import Optional
from fastapi import FastAPI, HTTPException, Request, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
# from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import re 

import uvicorn
import shutil

from enum import Enum

import paramiko
import os
import csv
from re import match
import time
import subprocess
import requests, zipfile, io


# class ModelName(str, Enum):
#     Dogbone = "Dogbone"
#     GIICmodel = "GIICmodel"
#     DCBmodel = "DCBmodel"
class FileType(str, Enum):
    yaml = "yaml"
    xml = "xml"

class NotFoundException(Exception):
    def __init__(self, name: str):
        self.name = name

tags_metadata = [
    {"name": "Post Methods", "description": "Generate, translate or upload models"},
    {"name": "Put Methods", "description": "Run, cancel or write jobs"},
    {"name": "Get Methods", "description": "Get mesh files, input files or postprocessing data"},
    {"name": "Delete Methods", "description": "Delet user or model data"},
    {"name": "Documentation Methods", "description": "Retrieve markdwon documentaion or bibtex files"},
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
class ModelControl(object):
    def __init__(self,**kwargs):
        """doc"""
        self.returnDir = None

    def run(self,**kwargs):
        """doc"""
        
        L = 152
        L = 52
        B = 10
        h = 4.95
        nn = 19
        
        
        
        nn = 2*int(nn/2)+1
        dx=[h/nn,h/nn,h/nn]
        
        print(dx, 4.01*dx[0])
        
        #gc = GIICmodel(xend = L, yend = h, zend = B, dx=dx, solvertype = 'Verlet', TwoD = True, filetype = 'xml')
        #model = gc.createModel(rot=True)
        #xm = XFEMDCB(xend = L, yend = 2*h, dx=[0.08,0.08])
        dx=[0.00005,0.00005,0.00005]
        #db = DCBmodel()
        #model = db.createModel()
        #print('verifcation models')
        veri = VerificationModels()
        veri.createVerificationModels()
    def endRunOnError(self):
        pass
        
        
    def endRun(self, returnDir = None, feFilename = None, runDir = None):
       pass


    @app.exception_handler(NotFoundException)
    async def notFound_exception_handler(request: Request, exc: NotFoundException):
        return JSONResponse(
            status_code=404,
            content={"message": f"{exc.name} can't be found"},
        )

    @app.post("/generateModel", tags=["Post Methods"])
    def generateModel(ModelName: str, ownModel: bool, translated: bool, Length: float, Width: float, Height: float, Discretization: float, Horizon: float, Structured: bool, TwoDimensional: bool, RotatedAngles: bool, Angle0: float, Angle1: float, Param: dict, request: Request, Height2: Optional[float] = None):#Material: dict, Output: dict):
       
        username = fileHandler.getUserName(request)
        maxNodes = fileHandler.getMaxNodes(username)

         # L = 152
        # L = 50
        # W = 10
        # h = 4.95
        # nn = 12

        L = Length
        W = Width
        h = Height
        if ModelName=='Dogbone':
            nn = 2*int(Discretization/2)
        else:
            nn = 2*int(Discretization/2)+1
        dx=[h/nn,h/nn,h/nn]

        start_time = time.time()
        
        if ModelName=='GIICmodel':
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
            username=username,
            maxNodes=maxNodes)
            result = gc.createModel()

        if ModelName=='DCBmodel':
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
            username = username,
            maxNodes=maxNodes)
            result = dcb.createModel()

        if ModelName=='Dogbone':
            db = Dogbone(xend = L, h1 = h, h2 = Height2, zend = W, dx=dx,
            structured = Structured,
            TwoD = TwoDimensional, 
            rot=RotatedAngles, angle=[Angle0,Angle1], 
            material=Param['Param']['Material'], 
            damage=Param['Param']['Damage'], 
            block=Param['Param']['Block'], 
            bc=Param['Param']['BoundaryConditions'], 
            compute=Param['Param']['Compute'],  
            output=Param['Param']['Output'], 
            solver=Param['Param']['Solver'],
            username = username,
            maxNodes=maxNodes)
            result = db.createModel()

        if ownModel:
            if translated:
                discType = 'e'
            else:
                discType = 'txt'

            own = OwnModel(filename=ModelName, dx=dx,
            DiscType = discType,
            TwoD = TwoDimensional,
            horizon = Horizon,
            material=Param['Param']['Material'], 
            damage=Param['Param']['Damage'], 
            block=Param['Param']['Block'], 
            bc=Param['Param']['BoundaryConditions'], 
            compute=Param['Param']['Compute'],  
            output=Param['Param']['Output'], 
            solver=Param['Param']['Solver'],
            username = username)
            result = own.createModel()

        print(ModelName + ' has been created in ' + "%.2f seconds" % (time.time() - start_time))
        if (result!='Model created'):
            return result
        return ModelName + ' has been created in ' + "%.2f seconds" % (time.time() - start_time) + ', dx: '+ str(dx)
   
    @app.get("/generateMesh", tags=["Get Methods"])
    def generateMesh(ModelName: str, Param: str, request: Request):
        username = fileHandler.getUserName(request)

        # json=Param, 
        print(Param)

        # headers = {
        #     'accept': 'application/json',
        #     'Content-Type': 'multipart/form-data',
        # }

        # files = {
        #     'ZIP': (None, ''),
        #     'JSON': (None, '{\n  "RVE": {\n    "rve_fvc": 30,\n    "rve_radius": 6.6,\n    "rve_lgth": 50,\n    "rve_dpth": 1\n  },\n  "Interface": {\n    "int_ufrac": 10\n  },\n  "Mesh": {\n    "mesh_fib": 35,\n    "mesh_lgth": 35,\n    "mesh_dpth": 1,\n    "mesh_aa": "on"\n  }\n}'),
        # }

        r = requests.patch("https://129.247.54.235:5000/1/PyCODAC/api/micofam/{zip}", verify=False)
        try:
            z = zipfile.ZipFile(io.BytesIO(r.content))

            localpath = './Output/' + os.path.join(username, ModelName)

            if os.path.exists(localpath) == False:
                os.makedirs(localpath)
                
            z.extractall(localpath)
        except:
            return "Micofam request failed"


        outputFiles = os.listdir(localpath)
        filtered_values = list(filter(lambda v: match('^.+\.inp$', v), outputFiles))
        os.rename(os.path.join(localpath, filtered_values[0]), os.path.join(localpath, ModelName + ".inp"))


        # return requests.patch('https://localhost:5000/1/PyCODAC/api/micofam/%7Bzip%7D', headers=headers, files=files)

        # filePath = './Output/' + os.path.join(username, ModelName) + '/'  + ModelName + '.' + FileType
        # if not os.path.exists(filePath):
        #     return 'Inputfile can\'t be found'
        # try:
        #     return FileResponse(filePath)
        # except:
        return "Mesh generated"

    @app.get("/viewInputFile", tags=["Get Methods"])
    def viewInputFile(ModelName: str, FileType: FileType, request: Request):
        username = fileHandler.getUserName(request)

        filePath = './Output/' + os.path.join(username, ModelName) + '/'  + ModelName + '.' + FileType
        if not os.path.exists(filePath):
            return 'Inputfile can\'t be found'
        try:
            return FileResponse(filePath)
        except:
            return 'Inputfile can\'t be found'

    @app.put("/writeInputFile", tags=["Put Methods"])
    def writeInputFile(ModelName: str, InputString: str, FileType: FileType, request: Request):
        username = fileHandler.getUserName(request)

        fid = open('./Output/' + os.path.join(username, ModelName) + '/'  + ModelName + '.' + FileType ,'w')
        fid.write(InputString)
        fid.close()

        return ModelName + '-InputFile has been saved'

    @app.get("/getModel", tags=["Get Methods"])
    def getModel(ModelName: str, request: Request):
        username = fileHandler.getUserName(request)

        try:
            shutil.make_archive(ModelName, "zip", './Output/' + os.path.join(username, ModelName))

            response = FileResponse(ModelName + ".zip", media_type="application/x-zip-compressed")
            response.headers["Content-Disposition"] = "attachment; filename=" + ModelName + ".zip"
            # return StreamingResponse(iterfile(), media_type="application/x-zip-compressed")
            return response
        except:
            raise HTTPException(status_code=404, detail=ModelName + ' files can not be found')
     
    # @app.get("/getVtkFile")
    # def getVtkFile(ModelName: str, request: Request):
    #     username = fileHandler.getUserName(request)

    #     localpath = './Output/' + os.path.join(username, ModelName)

    #     try:
    #         file = os.path.join(localpath, ModelName) + '.vtu'

    #         response = FileResponse(file, media_type=".vtu")
    #         response.headers["Content-Disposition"] = "attachment; filename=" + ModelName + '.vtu'
    #         # return StreamingResponse(iterfile(), media_type="application/x-zip-compressed")
    #         return response
    #     except:
    #         raise HTTPException(status_code=404, detail=ModelName + ' files can not be found')

    @app.get("/getLogFile", tags=["Get Methods"])
    def getLogFile(ModelName: str, Cluster: str, request: Request):

        username = fileHandler.getUserName(request)
        # usermail = fileHandler.getUserMail(request)

        if Cluster=='None':
            
            remotepath = './peridigmJobs/' + os.path.join(username, ModelName)
            try:
                outputFiles = os.listdir(remotepath)
                filtered_values = list(filter(lambda v: match('^.+\.log$', v), outputFiles))
            except:
                return 'LogFile can\'t be found in ' + remotepath
            if(len(filtered_values)==0):
                return 'LogFile can\'t be found in ' + remotepath

            f = open(os.path.join(remotepath, filtered_values[-1]), 'r')
            response = f.read()
            f.close()

            return response

        else:
            if Cluster=='FA-Cluster':
                remotepath = './PeridigmJobs/apiModels/' + os.path.join(username, ModelName)
            
            elif Cluster=='Cara':
                remotepath = './PeridigmJobs/apiModels/' + os.path.join(username, ModelName)

            else:
                return Cluster + ' unknown'

            ssh, sftp = fileHandler.sftpToCluster(Cluster)

            try:
                outputFiles = sftp.listdir(remotepath)
                filtered_values = list(filter(lambda v: match('^.+\.log$', v), outputFiles))
            except:
                return 'LogFile can\'t be found in ' + remotepath
            if(len(filtered_values)==0):
                return 'LogFile can\'t be found in ' + remotepath
            sftp.chdir(remotepath)
            logfile = sftp.file(filtered_values[-1],'r')
            response = logfile.read()
            sftp.close()
            ssh.close()

            return response

    @app.get("/getPublications", tags=["Documentation Methods"])
    def getPublications():
            
        remotepath = './Publications/papers.bib'

        f = open(remotepath, 'r')
        response = f.read()
        f.close()

        return response

    @app.get("/getDocs", tags=["Documentation Methods"])
    def getDocs(Name: str, model: bool):
            
        if model:
            remotepath = './'+ Name+ '/' + Name + '.md'
        else:
            remotepath = './guides/' + Name + '.md'


        f = open(remotepath, 'r')
        response = f.read()
        f.close()

        return response

    @app.get("/getMaxFeSize", tags=["Get Methods"])
    def getMaxFeSize(request: Request):

        username = fileHandler.getUserName(request)
        FeSize = fileHandler.getMaxFeSize(username)

        return FeSize


    @app.get("/getResults", tags=["Get Methods"])
    def getResults(ModelName: str, Cluster: str, allData: bool, request: Request):
        username = fileHandler.getUserName(request)

        if(fileHandler.copyResultsFromCluster(username, ModelName, Cluster, allData)==False):
            raise HTTPException(status_code=404, detail=ModelName + ' results can not be found on ' + Cluster)

        # resultpath = './Results/' + os.path.join(username, ModelName)
        userpath = './Results/' + username
        try:
            shutil.make_archive(os.path.join(userpath, ModelName), "zip", userpath, ModelName)

            response = FileResponse(os.path.join(userpath, ModelName) + ".zip", media_type="application/x-zip-compressed")
            response.headers["Content-Disposition"] = "attachment; filename=" + ModelName + ".zip"
            # return StreamingResponse(iterfile(), media_type="application/x-zip-compressed")
            return response
        except:
            raise HTTPException(status_code=404, detail=ModelName + ' results can not be found on ' + Cluster)

    # @app.get("/getResults")
    # def getResults(ModelName: str, username: str):
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
            
    @app.delete("/deleteModel", tags=["Delete Methods"])
    def deleteModel(ModelName: str, request: Request):
        username = fileHandler.getUserName(request)

        localpath = './Output/' + os.path.join(username, ModelName)
        shutil.rmtree(localpath)
        return ModelName + ' has been deleted'


    @app.delete("/deleteModelFromCluster", tags=["Delete Methods"])
    def deleteModelFromCluster(ModelName: str, Cluster: str, request: Request):
        username = fileHandler.getUserName(request)

        if Cluster=='None':
            remotepath = './peridigmJobs/' + os.path.join(username, ModelName)
            shutil.rmtree(remotepath)
            return ModelName + ' has been deleted'

        else:
            if Cluster=='FA-Cluster':
                remotepath = './PeridigmJobs/apiModels/' + os.path.join(username, ModelName)
            
            elif Cluster=='Cara':
                remotepath = './PeridigmJobs/apiModels/' + os.path.join(username, ModelName)

            else:
                return Cluster + ' unknown'

            ssh, sftp = fileHandler.sftpToCluster(Cluster)

            for filename in sftp.listdir(remotepath):
                sftp.remove(os.path.join(remotepath, filename))
            sftp.rmdir(remotepath)
            sftp.close()
            ssh.close()
            return ModelName + ' has been deleted'

    @app.delete("/deleteUserData", tags=["Delete Methods"])
    def deleteUserData(checkDate: bool, request: Request, days: Optional[int] = 7):
        if checkDate:
            localpath = './Output'
            if os.path.exists(localpath):
                names = fileHandler.removeFolderIfOlder(localpath, days, True)
                if len(names)!=0:
                    return 'Data of ' + ', '.join(names) + ' has been deleted'
            return 'Nothing has been deleted'
        else:
            username = fileHandler.getUserName(request)

            localpath = './Output/' + username
            shutil.rmtree(localpath)
            return 'Data of ' + username + ' has been deleted'

    @app.delete("/deleteUserDataFromCluster", tags=["Delete Methods"])
    def deleteUserDataFromCluster(Cluster: str, checkDate: bool, request: Request, days: Optional[int] = 7):

        if checkDate:
            if Cluster=='None':
                localpath = './peridigmJobs'
                fileHandler.removeFolderIfOlder(localpath, days, True)
            else:
                remotepath = fileHandler.getRemotePath(Cluster)
                
                ssh, sftp = fileHandler.sftpToCluster(Cluster)

                fileHandler.removeFolderIfOlderSftp(sftp, remotepath, days, True)

                sftp.close()
                ssh.close()
        
        else:
            username = fileHandler.getUserName(request)

            if Cluster=='None':
                remotepath = './peridigmJobs/' + username
                if os.path.exists(remotepath):
                    shutil.rmtree(remotepath)
                return 'Data of ' + username + ' has been deleted'

            else:
                remotepath = fileHandler.getRemoteUserPath(Cluster, username)
                
                ssh, sftp = fileHandler.sftpToCluster(Cluster)

                fileHandler.removeAllFolderSftp(sftp, remotepath, False)

                sftp.close()
                ssh.close()
                return 'Data of ' + username + ' has been deleted'

    @app.get("/getPlot", tags=["Get Methods"])
    def getPlot(ModelName: str, Cluster: str, OutputName: str, request: Request):
        username = fileHandler.getUserName(request)

        if(fileHandler.copyResultsFromCluster(username, ModelName, Cluster, False)==False):
            raise HTTPException(status_code=404, detail=ModelName + ' results can not be found on ' + Cluster)

        # subprocess.run(['./api/app/support/read.sh'], shell=True)
        process = subprocess.Popen(['sh support/read.sh globalData ' + username + ' ' + ModelName + ' ' + OutputName], shell=True)
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
            raise HTTPException(status_code=404, detail=ModelName + ' results can not be found on ' + Cluster)

    @app.get("/getImage", tags=["Get Methods"])
    def getImage(ModelName: str, Cluster: str, Output: str,  Variable: str,  Axis: str, dx: float, request: Request):
        username = fileHandler.getUserName(request)

        if(fileHandler.copyResultsFromCluster(username, ModelName, Cluster, False)==False):
            raise NotFoundException(name=ModelName)

        # subprocess.run(['./api/app/support/read.sh'], shell=True)
        process = subprocess.Popen(['sh support/read.sh image ' + username + ' ' + ModelName + ' ' + Output + ' ' + Variable + ' ' + Axis + ' ' + str(dx)], shell=True)
        process.wait()

        try:
            return FileResponse('./Results/' + os.path.join(username, ModelName) + '/'  + Variable + '_' + Axis + '.jpg')
        except:
            raise HTTPException(status_code=404, detail=ModelName + ' results can not be found on ' + Cluster)

    @app.get("/getPointData", tags=["Get Methods"])
    def getPointData(ModelName: str, OwnModel: bool, request: Request):
        username = fileHandler.getUserName(request)

        pointString=''
        blockIdString=''
        if OwnModel:
            try:
                with open('./Output/' + os.path.join(username, ModelName) + '/'  + ModelName + '.g.ascii', 'r') as f:
                        data = f.read()
                        numOfBlocks = re.findall('num_el_blk\s=\s\d*\s;', data)
                        numOfBlocks = int(numOfBlocks[0][13:][:2])
                        coords = re.findall('coord.\s=\s[-\d.,\se]{1,}', data)
                        nodes = re.findall('node_ns[\d]*\s=\s[\d,\s]*', data)
                        blockId = [1]*len(coords[0])
                        for i in range(0,3):
                            coords[i]=coords[i][8:].replace(" ", "").split(',')
                        for i in range(0,numOfBlocks):
                            nodes[i]=nodes[i*2][8:].replace(" ", "").split('=')[1].split(',')
                            for node in nodes[i]:
                                blockId[int(node)-1] = i + 1
                        for i in range(0,len(coords[0])):
                            pointString+=coords[0][i]+','+coords[1][i]+','+coords[2][i]+','
                            blockIdString+=str(blockId[i]/numOfBlocks)+','
                            
                response=[pointString.rstrip(pointString[-1]),blockIdString.rstrip(blockIdString[-1])]
                return response
            except:
                raise HTTPException(status_code=404, detail=ModelName + ' results can not be found')
        else:
            firstRow=True 
            maxBlockId = 1
            try:
                with open('./Output/' + os.path.join(username, ModelName) + '/'  + ModelName + '.txt', 'r') as f:
                        reader = csv.reader(f)
                        rows = list(reader)
                        for row in rows:
                            if firstRow==False:
                                str1 = ''.join(row)
                                parts = str1.split(" ")
                                pointString+=parts[0]+','+parts[1]+','+parts[2]+','
                                if int(parts[3]) > maxBlockId:
                                    maxBlockId = int(parts[3])
                            firstRow=False
                        firstRow=True 
                        for row in rows:
                            if firstRow==False:
                                str1 = ''.join(row)
                                parts = str1.split(" ")
                                blockIdString+=str(int(parts[3])/maxBlockId)+','
                            firstRow=False
                response=[pointString.rstrip(pointString[-1]),blockIdString.rstrip(blockIdString[-1])]
                return response
            except:
                raise HTTPException(status_code=404, detail=ModelName + ' results can not be found')

    @app.post("/uploadfiles", tags=["Post Methods"])
    async def uploadfiles( ModelName: str, request: Request, files: List[UploadFile] = File(...)): 
        username = fileHandler.getUserName(request)

        localpath = './Output/' + os.path.join(username, ModelName)

        if os.path.exists(localpath) == False:
            os.makedirs(localpath)

        for file in files:
            file_location = localpath + f"/{file.filename}"
            with open(file_location, "wb+") as file_object:
                shutil.copyfileobj(file.file, file_object)

        return {"info": f"file '{files[0].file.name}' saved at '{file_location}'"}

    @app.post("/translateModel", tags=["Post Methods"])
    def translateModel(ModelName: str, Filetype: str, Upload: bool, request: Request, files: Optional[List[UploadFile]] = File(...)):
        username = fileHandler.getUserName(request)

        start_time = time.time()

        localpath = './Output/' + os.path.join(username, ModelName)

        if Upload:
            if os.path.exists(localpath) == False:
                os.makedirs(localpath)
            for file in files:
                file_location = localpath + f"/{file.filename}"
                with open(file_location, "wb+") as file_object:
                    shutil.copyfileobj(file.file, file_object)

        inputformat="'ansys (cdb)'"
        if Filetype=='cdb':
            inputformat = 'ansys'
        if Filetype=='inp':
            inputformat = 'abaqus'
            # inputformat = "'ansys (cdb)'"

        command = "java -jar ./support/jCoMoT/jCoMoT-0.0.1-all.jar -ifile " + os.path.join(localpath, ModelName + '.' + Filetype) + \
        " -iformat " + inputformat + " -oformat peridigm -opath " + localpath #+ \
        # " && mv " + os.path.join(localpath, 'mesh.g.ascii ') + os.path.join(localpath, ModelName) + '.g.ascii' + \
        # " && mv " + os.path.join(localpath, 'model.peridigm ') + os.path.join(localpath, ModelName) + '.peridigm'
        # " && mv " + os.path.join(localpath, 'discretization.g.ascii ') + os.path.join(localpath, ModelName) + '.g.ascii' + \
        try:
            subprocess.call(command, shell=True)
        except:
            raise HTTPException(status_code=404, detail=ModelName + ' results can not be found')

        print('Rename mesh File')
        os.rename(os.path.join(localpath, 'mesh.g.ascii'), os.path.join(localpath, ModelName + '.g.ascii'))
        print('Rename peridigm File')
        os.rename(os.path.join(localpath, 'model.peridigm'), os.path.join(localpath, ModelName + '.peridigm'))
        
        print('Copy mesh File')
        if fileHandler.copyFileToFromPeridigmContainer(username, ModelName, ModelName + '.g.ascii', True) != 'Success':
            return ModelName + ' can not be translated'

        print('Copy peridigm File')
        if fileHandler.copyFileToFromPeridigmContainer(username, ModelName, ModelName + '.peridigm', True) != 'Success':
            return ModelName + ' can not be translated'


        # if returnString!='Success':
        #     return returnString

        server='perihub_peridigm'
        remotepath = '/app/peridigmJobs/' + os.path.join(username, ModelName)
        ssh = paramiko.SSHClient() 
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(server, username='root', allow_agent=False, password='root')
        except:
           return "ssh connection to " + server + " failed!"
        command = '/usr/local/netcdf/bin/ncgen ' + os.path.join(remotepath, ModelName) + '.g.ascii -o ' + os.path.join(remotepath, ModelName) + '.g' + \
        ' && python3 /Peridigm/scripts/peridigm_to_yaml.py ' + os.path.join(remotepath, ModelName) + '.peridigm' + \
        ' && rm ' +  os.path.join(remotepath, ModelName) + '.peridigm'
        # ' && rm ' +  os.path.join(remotepath, ModelName) + '.g.ascii' + \
        print('Peridigm to yaml')
        stdin, stdout, stderr = ssh.exec_command(command)
        stdout.channel.set_combine_stderr(True)
        output = stdout.readlines()
        ssh.close()

        print('Copy mesh File')
        fileHandler.copyFileToFromPeridigmContainer(username, ModelName, ModelName + '.g', False)
        print('Copy yaml File')
        fileHandler.copyFileToFromPeridigmContainer(username, ModelName, ModelName + '.yaml', False)

        # command = 'mv ' + os.path.join(localpath, ModelName) + '.g ' + os.path.join(localpath, ModelName) + '.e && meshio convert ' + os.path.join(localpath, ModelName) + '.e ' + os.path.join(localpath, ModelName) + '.vtu'
        # try:
        #     subprocess.call(command, shell=True)
        # except:
        #     raise HTTPException(status_code=404, detail=ModelName + ' results can not be found')

        return ModelName + ' has been translated in ' + "%.2f seconds" % (time.time() - start_time)

    # @app.post("/translateExistModel")
    # def translateExistModel(ModelName: str, Filetype: str, Upload: bool, request: Request):
    #     username = fileHandler.getUserName(request)

    #     start_time = time.time()

    #     localpath = './Output/' + os.path.join(username, ModelName)

    #     inputformat="'ansys (cdb)'"
    #     if Filetype=='cdb':
    #         inputformat = 'ansys'
    #     if Filetype=='inp':
    #         inputformat = 'abaqus'
    #         # inputformat = "'ansys (cdb)'"

    #     command = "java -jar ./support/jCoMoT/jCoMoT-0.0.1-all.jar -ifile " + os.path.join(localpath, ModelName + '.' + Filetype) + \
    #     " -iformat " + inputformat + " -oformat peridigm -opath " + localpath + \
    #     " && mv " + os.path.join(localpath, 'mesh.g.ascii ') + os.path.join(localpath, ModelName) + '.g.ascii' + \
    #     " && mv " + os.path.join(localpath, 'model.peridigm ') + os.path.join(localpath, ModelName) + '.peridigm'
    #     # " && mv " + os.path.join(localpath, 'discretization.g.ascii ') + os.path.join(localpath, ModelName) + '.g.ascii' + \
    #     try:
    #         subprocess.call(command, shell=True)
    #     except:
    #         raise HTTPException(status_code=404, detail=ModelName + ' results can not be found')
        
    #     if fileHandler.copyFileToFromPeridigmContainer(username, ModelName, ModelName + '.g.ascii', True) != 'Success':
    #         return ModelName + ' can not be translated'

    #     if fileHandler.copyFileToFromPeridigmContainer(username, ModelName, ModelName + '.peridigm', True) != 'Success':
    #         return ModelName + ' can not be translated'


    #     # if returnString!='Success':
    #     #     return returnString

    #     server='perihub_peridigm'
    #     remotepath = '/app/peridigmJobs/' + os.path.join(username, ModelName)
    #     ssh = paramiko.SSHClient() 
    #     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #     try:
    #         ssh.connect(server, username='root', allow_agent=False, password='root')
    #     except:
    #        return "ssh connection to " + server + " failed!"
    #     command = '/usr/local/netcdf/bin/ncgen ' + os.path.join(remotepath, ModelName) + '.g.ascii -o ' + os.path.join(remotepath, ModelName) + '.g' + \
    #     ' && python3 /Peridigm/scripts/peridigm_to_yaml.py ' + os.path.join(remotepath, ModelName) + '.peridigm' + \
    #     ' && rm ' +  os.path.join(remotepath, ModelName) + '.peridigm'
    #     # ' && rm ' +  os.path.join(remotepath, ModelName) + '.g.ascii' + \
    #     stdin, stdout, stderr = ssh.exec_command(command)
    #     stdout.channel.set_combine_stderr(True)
    #     output = stdout.readlines()
    #     ssh.close()

    #     fileHandler.copyFileToFromPeridigmContainer(username, ModelName, ModelName + '.g', False)
    #     fileHandler.copyFileToFromPeridigmContainer(username, ModelName, ModelName + '.yaml', False)

    #     # command = 'mv ' + os.path.join(localpath, ModelName) + '.g ' + os.path.join(localpath, ModelName) + '.e && meshio convert ' + os.path.join(localpath, ModelName) + '.e ' + os.path.join(localpath, ModelName) + '.vtu'
    #     # try:
    #     #     subprocess.call(command, shell=True)
    #     # except:
    #     #     raise HTTPException(status_code=404, detail=ModelName + ' results can not be found')

    #     return ModelName + ' has been translated in ' + "%.2f seconds" % (time.time() - start_time)

    @app.put("/runModel", tags=["Put Methods"])
    def runModel(ModelName: str, FileType: FileType, Param: dict, request: Request):
        username = fileHandler.getUserName(request)
        usermail = fileHandler.getUserMail(request)

        Material =  Param['Param']['Material']

        UserMat = False
        for mat in Material:
            if mat['MatType'] == 'User Correspondence':
                UserMat = True
                break

        Cluster =  Param['Param']['Job']['cluster']
        returnString = fileHandler.copyModelToCluster(username, ModelName, Cluster)

        if returnString!='Success':
            return returnString
        if UserMat:
            returnString = fileHandler.copyLibToCluster(username, ModelName, Cluster)
            if returnString!='Success':
                return returnString

        if Cluster=='FA-Cluster':
            remotepath = './PeridigmJobs/apiModels/' + os.path.join(username, ModelName)
            ssh = fileHandler.sshToCluster('FA-Cluster')
            command = 'cd ' + remotepath + ' \n qperidigm -d -c ' + str(Param['Param']['Job']['tasks']) + ' -O tgz -J ' + ModelName +' -E /home/f_peridi/Peridigm/build/bin/Peridigm '+ ModelName + '.' + FileType
            ssh.exec_command(command)
            ssh.close()

            return ModelName + ' has been submitted'

        elif Cluster=='Cara':
            sb = SbatchCreator(filename=ModelName, output=Param['Param']['Output'], job=Param['Param']['Job'], username=username, usermail=usermail)
            sbatchString = sb.createSbatch()
            remotepath = './PeridigmJobs/apiModels/' + os.path.join(username, ModelName)
            ssh, sftp = fileHandler.sftpToCluster('Cara')
            file=sftp.file(remotepath + '/' + ModelName + '.sbatch', "a", -1)
            file.write(sbatchString)
            file.flush()
            sftp.close()

            command = 'cd ' + remotepath + ' \n sbatch '+ ModelName + '.sbatch'
            ssh.exec_command(command)
            ssh.close()

            return ModelName + ' has been submitted'

        elif Cluster=='None':
            server='perihub_peridigm'
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
            try:
                ssh.connect(server, username='root', allow_agent=False, password='root')
            except:
                return "ssh connection to " + server + " failed!"
            command = 'cd /app' + remotepath + ' \n rm ' + ModelName + '.log \n sh /app' + remotepath + '/runPeridigm.sh >> ' + ModelName + '.log &'
            stdin, stdout, stderr  = ssh.exec_command(command)
            #stdin, stdout, stderr = ssh.exec_command('nohup python executefile.py >/dev/null 2>&1 &')
            # stdout=stdout.readlines()
            # stderr=stderr.readlines()
            ssh.close()

            # return stdout + stderr
            return ModelName + ' has been submitted'
        else:
            return Cluster + ' unknown'

    @app.put("/cancelJob", tags=["Put Methods"])
    def cancelJob(ModelName: str, Cluster: str, request: Request):
        username = fileHandler.getUserName(request)

        if Cluster=='None':
            server='perihub_peridigm'
            remotepath = '/peridigmJobs/' + os.path.join(username, ModelName)
            ssh = paramiko.SSHClient() 
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                ssh.connect(server, username='root', allow_agent=False, password='root')
            except:
                return "ssh connection to " + server + " failed!"
            command = 'kill -9 `cat /app' + os.path.join(remotepath, 'pid.txt') + '` \n rm /app' + os.path.join(remotepath, 'pid.txt')
            stdin, stdout, stderr  = ssh.exec_command(command)
            stdout=stdout.readlines()
            stderr=stderr.readlines()
            ssh.close()

            return 'Job has been canceled'

        else:     
            remotepath = fileHandler.getRemoteModelPath(Cluster, username, ModelName)
            ssh, sftp = fileHandler.sftpToCluster(Cluster)
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
    
    # @app.get("/startCron")
    # def startCron():
    #     cron = CronTab(user='root')
    #     job = cron.new(command='echo hello_world')
    #     job.minute.every(1)
    #     cron.write()

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
        
    # fileHandler.copyModelToCluster('hess_ja', 'Dogbone', 'Cara')
        
        
        
        

