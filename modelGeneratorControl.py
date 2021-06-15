# Copyright (C) 2021 Deutsches Zentrum fuer Luft- und Raumfahrt(DLR, German Aerospace Center) <www.dlr.de>


from GIICmodel.GIICmodel import GIICmodel
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
        L = 52
        h = 3.84/2
        nn = 21
        dx=[h/nn,h/nn]
        #print(dx)
        gc = GIICmodel(xend = L, yend = 2*h, dx=[0.07,0.07])
        model = gc.createModel()
        #xm = XFEMDCB(xend = L, yend = 2*h, dx=[0.08,0.08])
    def endRunOnError(self):
        pass
        
        
    def endRun(self, returnDir = None, feFilename = None, runDir = None):
       pass
        
    
            
        
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
