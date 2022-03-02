# Copyright (C) 2021 Deutsches Zentrum fuer Luft- und Raumfahrt(DLR, German Aerospace Center) <www.dlr.de>

import sys

sys.path.insert(0, "/home/jt/perihub/api/app")
from models.GIICmodel.GIICmodel import GIICmodel
from models.DCBmodel.DCBmodel import DCBmodel
from models.KalthoffWinkler.KalthoffWinkler import KalthoffWinkler
from Verification.verificationModels import VerificationModels
from models.XFEM_Bechnmark.XFEMdcb import XFEMDCB
from models.Dogbone.Dogbone import Dogbone
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt

import pandas as pd


class ModelControl(object):
    def __init__(self, **kwargs):
        """doc"""
        self.returnDir = None

    def run(self, **kwargs):
        """doc"""

        # L = 152
        # L = 52
        B = 10
        # h = 4.95
        # h = 0.019
        # nn = 21

        h = 200
        L = 100
        nn = 800

        nn = 2 * int(nn / 2) + 1

        nn = 800
        dx = [h / nn, h / nn, h / nn]

        print(dx, 4.01 * dx[0])

        kw = KalthoffWinkler(xend=L, yend=h, zend=B, dx=dx, TwoD=True)
        model = kw.createModel()
        # gc = GIICmodel(xend = L, yend = h, zend = B, dx=dx, TwoD = True)
        # model = gc.createModel()
        # xm = XFEMDCB(xend = L, yend = 2*h, dx=[0.08,0.08])
        # model = xm.createModel()
        # dcb = DCBmodel(dx = dx, TwoD = True)
        # model = dcb.createModel()
        # db = Dogbone(dx = dx, TwoD = False, h1=h)
        # model = db.createModel()
        # veri = VerificationModels()
        # veri.createVerificationModels()

    def endRunOnError(self):
        pass

    def endRun(self, returnDir=None, feFilename=None, runDir=None):
        pass
