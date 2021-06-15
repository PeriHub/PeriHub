import numpy as np
class Geometry(object):
    def __init__(self):
        pass
    def createPoints(self,coor,dx):
        gridx, gridy = np.meshgrid(np.arange(coor[0], coor[1] + dx[0], dx[0]),np.arange(coor[2], coor[3] + dx[1], dx[1]))
        return gridx.ravel(), gridy.ravel()