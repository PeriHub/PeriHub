import numpy as np
import math
from scipy.interpolate import interp1d
import time
class Geometry(object):
    def __init__(self):
        pass
    def createPoints(self,coor,dx):
        start_time = time.time()
        if coor[4] == coor[5]:
            gridx, gridy = np.meshgrid(np.arange(coor[0], coor[1] + dx[0], dx[0]),np.arange(coor[2], coor[3] + dx[1], dx[1]))    
            gx = gridx.ravel(); gy = gridy.ravel(); gz = 0*gridy.ravel()
        else:
            gridx, gridy, gridz = np.meshgrid(np.arange(coor[0], coor[1] + dx[0], dx[0]),np.arange(coor[2], coor[3] + dx[1], dx[1]),np.arange(coor[4], coor[5] + dx[2], dx[2]))
            gx = gridx.ravel(); gy = gridy.ravel(); gz = gridz.ravel()
        print('Points created in ' + "%.2f seconds" % (time.time() - start_time) )
        return gx,gy,gz


    def checkValLowerNew(self,array,limit):
        return np.where(array <= limit)

    def checkValGreaterNew(self,array,limit):
        return np.where(array >= limit)

    def checkValLower(self,val,limit):
        inside = False

        if val<=limit:
            inside = True
        return inside

    def checkValGreater(self,val,limit):
        inside = False

        if val>=limit:
            inside = True
        return inside

    def createBoundaryCurve(self, h=0, l1=0, R=0, l2=0, alphaMax = 90, alphaMax1 = 90, dl = 0, dh = 0):

        dalpha = 0.025
        # print(alphaMax)
        alpha = np.arange(0,alphaMax,dalpha)
        dalpha1 = alphaMax1/len(alpha)
        if alphaMax1==0:
            alpha1 = np.zeros_like(alpha)
        elif alphaMax == alphaMax1:
            alpha1 = np.arange(0,alphaMax,dalpha)
        else:
            alpha1 = np.arange(0,alphaMax1,dalpha1)
        if len(alpha1) > len(alpha):
            alpha1 = np.arange(0,alphaMax1-dalpha1/2,dalpha1)

        ##################################
        # Start
        ##################################
        x = np.array([0])
        y = np.array([h])
        #########
        # Circle
        #########
        x = np.concatenate((x,l1+dl+R*np.sin((-alpha)/180*np.pi)))
        y = np.concatenate((y,h-dh+R-R*np.cos((-alpha1)/180*np.pi)))
        #########
        # Circle
        #########

        x = np.concatenate((x,l1+dl+l2+R*np.sin(alpha/180*np.pi)))
        y = np.concatenate((y,h-dh+R-R*np.cos(alpha1/180*np.pi)))
        #########
        # End
        #########
  
        x = np.concatenate((x,np.array([2*dl+2*l1+l2+0.01])))
        y = np.concatenate((y,np.array([h])))
        
        topSurf = interp1d(x,y)
        bottomSurf = interp1d(x,-y)
    
        return topSurf, bottomSurf

    def createBoundaryCurveOld(self, h=0, l1=0, R=0, l2=0, alphaMax = 90, dl = 0, dh = 0):

        dalpha = 0.025
        # print(alphaMax)
        alpha = np.arange(0,alphaMax+dalpha,dalpha)
        ##################################
        # Start
        ##################################
        x = np.array([0])
        y = np.array([h])
        #########
        # Circle
        #########
        x = np.concatenate((x,l1+dl+R*np.sin((-alpha)/180*np.pi)))
        y = np.concatenate((y,h+R-dh-R*np.cos((-alpha)/180*np.pi)))
        #########
        # Circle
        #########

        x = np.concatenate((x,l1+dl+l2+R*np.sin(alpha/180*np.pi)))
        y = np.concatenate((y,h-dh+R-R*np.cos(alpha/180*np.pi)))
        #########
        # End
        #########
  
        x = np.concatenate((x,np.array([2*dl+2*l1+l2+0.01])))
        y = np.concatenate((y,np.array([h])))
        
        topSurf = interp1d(x,y)
        bottomSurf = interp1d(x,-y)
   
        # #########
        # # Bottom
        # #########               
        # x = np.array([2*dl+2*l1+l2+0.01])
        # y = np.array([0])
        
        # #########
        # # Circle
        # #########
        # x = np.concatenate((x,l1+dl+l2+R*np.sin((alphaMax-alpha)/180*np.pi)))
        # #x = np.concatenate((x,l1+l2+dl-R*np.cos(alpha/180*np.pi)))
        # y = np.concatenate((y, dh -R + R*np.cos((alphaMax-alpha)/180*np.pi)))

        # #########
        # # Circle
        # #########
        # x = np.concatenate((x,l1+dl+R*np.sin(-alpha/180*np.pi)))
        # y = np.concatenate((y,dh -R +R*np.cos(-alpha/180*np.pi))) #error
        # #########
        # # End
        # #########
        # x = np.concatenate((x,np.array([0])))
        # y = np.concatenate((y,np.array([0])))
        
        # bottomSurf = interp1d(x,y)
    
        return topSurf, bottomSurf