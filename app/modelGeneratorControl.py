# Copyright (C) 2021 Deutsches Zentrum fuer Luft- und Raumfahrt(DLR, German Aerospace Center) <www.dlr.de>


from numpy import string_
from numpy.lib.shape_base import split
from GIICmodel.GIICmodel import GIICmodel
from DCBmodel.DCBmodel import DCBmodel
#from XFEM_Bechnmark.XFEMdcb import XFEMDCB
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt

import pandas as pd

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse

from enum import Enum

import shutil

class ModelName(str, Enum):
    GIICmodel = "GIICmodel"
    DCBmodel = "DCBmodel"
class SolverType(str, Enum):
    Verlet = "Verlet"
    NOXQuasiStatic = "NOXQuasiStatic"
class FileType(str, Enum):
    yaml = "yaml"
    xml = "xml"

app = FastAPI()
class ModelControl(object):

    @app.post("/writeModel")
    def writeModel(ModelName: ModelName, Length: float, Width: float, Height: float, Discretization: float, TwoDimensional: bool, RotatedAngles: bool, Solvertype: SolverType, Filetype: FileType):
        # L = 152
        # L = 50
        # W = 10
        # h = 4.95
        # nn = 11

        L = Length
        W = Width
        h = Height
        nn = Discretization
        dx=[h/nn,h/nn,h/nn]

        if ModelName==ModelName.GIICmodel:
            gc = GIICmodel(xend = L, yend = h, zend = W, dx=dx, solvertype = Solvertype, TwoD = TwoDimensional, filetype = Filetype, rot=RotatedAngles)
            model = gc.createModel()

            return {'GIIC': "GIIC-Model has been created", 'dx': dx}

        if ModelName==ModelName.DCBmodel:
            dcb = DCBmodel(xend = L, yend = h, zend = W, dx=dx, solvertype = Solvertype, TwoD = TwoDimensional, filetype = Filetype, rot=RotatedAngles)
            model = dcb.createModel()

            return {'DCB': "DCB-Model has been created", 'dx': dx}
        
        
    @app.get("/viewInputFile")
    def viewInputFile(ModelName: ModelName):

        return FileResponse('./Output/' + ModelName + '/'  + ModelName + '.yaml')

    @app.get("/getModel")
    def getModel(ModelName: ModelName):

        shutil.make_archive(ModelName, "zip", './Output/' + ModelName)

        response = FileResponse(ModelName + ".zip", media_type="application/x-zip-compressed")
        response.headers["Content-Disposition"] = "attachment; filename=" + ModelName + ".zip"
        # return StreamingResponse(iterfile(), media_type="application/x-zip-compressed")
        return response
        
    def __init__(self,**kwargs):
        """doc"""
        self.returnDir = None

    def run(self,**kwargs):
        """doc"""
        
        L = 152
        L = 50
        W = 10
        h = 4.95
        nn = 31
        dx=[h/nn,h/nn,h/nn]
        
        print(dx, 1.92/dx[0])
        
        # dcb = DCBmodel()
        # model = dcb.createModel()
        gc = GIICmodel(xend = L, yend = h, zend = W, dx=dx, solvertype = 'Verlet', TwoD = False, filetype = 'xml', rot=False)
        model = gc.createModel()
        #xm = XFEMDCB(xend = L, yend = 2*h, dx=[0.08,0.08])

    def endRunOnError(self):
        pass
        
        
    def endRun(self, returnDir = None, feFilename = None, runDir = None):
       pass
    
            
        
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        

