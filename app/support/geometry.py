import numpy as np
class Geometry(object):
    def __init__(self):
        pass
    def createPoints(self,coor,dx):
        if coor[4] == coor[5]:
            gridx, gridy = np.meshgrid(np.arange(coor[0], coor[1] + dx[0], dx[0]),np.arange(coor[2], coor[3] + dx[1], dx[1]))    
            gx = gridx.ravel(); gy = gridy.ravel(); gz = 0*gridy.ravel()
        else:
            gridx, gridy, gridz = np.meshgrid(np.arange(coor[0], coor[1] + dx[0], dx[0]),np.arange(coor[2], coor[3] + dx[1], dx[1]),np.arange(coor[4], coor[5] + dx[2], dx[2]))
            gx = gridx.ravel(); gy = gridy.ravel(); gz = gridz.ravel()
        return gx,gy,gz