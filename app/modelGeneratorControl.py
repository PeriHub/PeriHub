# Copyright (C) 2021 Deutsches Zentrum fuer Luft- und Raumfahrt(DLR, German Aerospace Center) <www.dlr.de>


from numpy import string_
from GIICmodel.GIICmodel import GIICmodel
from DCBmodel.DCBmodel import DCBmodel
#from XFEM_Bechnmark.XFEMdcb import XFEMDCB
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt

import pandas as pd

from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()
class ModelControl(object):

    @app.get("/greet")
    def show_greeting():
        return "Es gehtqasdacvabs!"

    @app.post("/dcb")
    def writeDCBmodel(Length: float, Width: float, Height: float, Discretization: float, TwoDimensional: bool, RotatedAngles: bool, Solvertype: str, Filetype: str):
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

        gc = GIICmodel(xend = L, yend = h, zend = W, dx=dx, solvertype = Solvertype, TwoD = TwoDimensional, filetype = Filetype, rot=RotatedAngles)
        model = gc.createModel()
        
        return {'DCB': "DCB-Model has been created", 'dx': dx}

    @app.get("/getModel")
    def getModel():
        return FileResponse('./Output/GIICmodel')
        
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
        dx=[h/nn,h/nn,h/nn]
        
        print(dx, 1.92/dx[0])
        
        # dcb = DCBmodel()
        # model = dcb.createModel()
        gc = GIICmodel(xend = L, yend = h, zend = W, dx=dx, solvertype = 'Verlet', TwoD = True, filetype = 'yaml', rot=True)
        model = gc.createModel()
        #xm = XFEMDCB(xend = L, yend = 2*h, dx=[0.08,0.08])
    def endRunOnError(self):
        pass
        
        
    def endRun(self, returnDir = None, feFilename = None, runDir = None):
       pass
    
            
        
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        

