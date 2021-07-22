# Copyright (C) 2021 Deutsches Zentrum fuer Luft- und Raumfahrt(DLR, German Aerospace Center) <www.dlr.de>


from GIICmodel.GIICmodel import GIICmodel
from DCBmodel.DCBmodel import DCBmodel
#from XFEM_Bechnmark.XFEMdcb import XFEMDCB
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt

import pandas as pd

class ModelControl(object):


    def __init__(self,**kwargs):
        """doc"""
        self.returnDir = None

    def run(self,**kwargs):
        """doc"""
        
        L = 152
        L = 62
        B = 10
        h = 4.95/2
        nn = 35
        dx=[2*h/nn,2*h/nn,2*h/nn]
        
        print(dx, 1.92/dx[0])
        
        # dcb = DCBmodel()
        # model = dcb.createModel()
        gc = GIICmodel(xend = L, yend = 2*h, zend = B, dx=dx, solvertype = 'Verlet', TwoD = True, filetype = 'xml', rot=False)
        model = gc.createModel()
        #xm = XFEMDCB(xend = L, yend = 2*h, dx=[0.08,0.08])
    def endRunOnError(self):
        pass
        
        
    def endRun(self, returnDir = None, feFilename = None, runDir = None):
       pass
    
            
        
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        

