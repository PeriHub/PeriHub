# Copyright (C) 2021 Deutsches Zentrum fuer Luft- und Raumfahrt(DLR, German Aerospace Center) <www.dlr.de>

import sys

sys.path.insert(0, "/home/jt/perihub/api/app")
from models.GIICmodel.giic_model import GIICmodel
from models.DCBmodel.dcb_model import DCBmodel
from models.KalthoffWinkler.kalthoff_winkler import KalthoffWinkler
from models.PlateWithHole.plate_with_hole import PlateWithHole
from Verification.verification_models import VerificationModels
from dev_models.XFEM_Bechnmark.xfem_dcb import XFEMDCB
from models.Dogbone.dogbone import Dogbone
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt

import pandas as pd


class ModelControl:
    def __init__(self, **kwargs):
        """doc"""
        self.return_dir = None

    def run(self, **kwargs):
        """doc"""

        # L = 152
        # L = 52
        thickness = 10
        # height = 4.95
        # height = 0.019
        # number_nodes = 21

        height = 200
        L = 100
        number_nodes = 42

        number_nodes = 2 * int(number_nodes / 2) + 1

        number_nodes = 800
        dx_value = [height / number_nodes, height / number_nodes, height / number_nodes]

        print(dx_value, 4.01 * dx_value[0])

        # pw = PlateWithHole(
        #     xend=L, yend=height, zend=thickness, dx_value=dx_value, two_d=True
        # )
        # model = pw.create_model()
        kw = KalthoffWinkler(
            xend=L, yend=height, zend=thickness, dx_value=dx_value, two_d=True
        )
        model = kw.create_model()
        # gc = GIICmodel(xend = L, yend = height, zend = thickness, dx_value=dx_value, two_d = True)
        # model = gc.create_model()
        # xm = XFEMDCB(xend = L, yend = 2*height, dx_value=[0.08,0.08])
        # model = xm.create_model()
        # dcb = DCBmodel(dx_value = dx_value, two_d = True)
        # model = dcb.create_model()
        # db = Dogbone(dx_value=dx_value, two_d=False, height1=height)
        # model = db.create_model()
        # veri = VerificationModels()
        # veri.create_verification_models()

    def endRunOnError(self):
        pass

    def endRun(self, return_dir=None, feFilename=None, runDir=None):
        pass
