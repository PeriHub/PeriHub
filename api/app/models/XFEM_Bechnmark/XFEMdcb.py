import numpy as np
from scipy import interpolate
from support.geometry import Geometry
class XFEMDCB(object):
    def __init__(self, xend = 1, yend = 1, zend = 0, dx=[0.1,0.1], filename = 'XFEMDCBmodel'):
        self.xend = xend
        self.yend = yend
        self.zend = zend
        self.dx = dx
        da = 9.5
        dgap = 3
        tb = 1
        
        self.pos=[0,xend/2  - da/2 - dgap, xend/2  - da/2, xend/2  + da/2, xend/2  + da/2 + dgap, xend]
        self.yLocs=[0,yend/2 - tb/2, yend/2 +tb/2, yend]
    def getDiscretization(self, x = [0,0], d = [0.1, 0.1]):
        dx = self.createDx(x, d)
        fun = self.fun(d[0],d[1], h = x[1]-x[0], nnum = len(dx))
 
        return fun
    def createModel(self):
        geo = Geometry()
        x,y,z = geo.createPoints(coor = [0,self.xend,0,self.yend,0,self.zend], dx = self.dx)
        vol = np.zeros(len(x))
        k = np.ones(len(x))
        for idx in range(0, len(x)):

            if y[idx] >= self.yend/2:
                k[idx] = self.createLoadBlock(x[idx],y[idx],k[idx])
            else:
                k[idx] = self.createBoundaryConditionBlock(x[idx],y[idx],k[idx])
            k[idx] = int(self.createBCNode(x[idx],y[idx], k[idx]))
            k[idx] = int(self.createLoadIntroNode(x[idx],y[idx], k[idx]))
            k[idx] = int(self.createBlock(y[idx],k[idx]))

            vol[idx] = self.dx[0] * self.dx[1]
        model = {'x':x, 'y':y, 'k':k, 'vol':vol}
        writer = ModelWriter(filename = self.filename)
        writer.writeNodeSets(model,self.nsList)
        writer.writeMesh(model)
        self.writeXML(writer = writer, model = model)
        
        return model
    def fun(self, x1, x2, h, nnum):

        x = [0,  2*x1,  h-2*x2,  h]
        #y = [x1, x1, x1, x2, x2, x2]
        #y = [0, 0.5*x1, 2*x1,  h-2*x2, h-0.5*x2, h]
        y = [0,  2*x2,  h-2*x1,  h]
        A = (-2*h + nnum*(x1 + x2))/nnum**3
        B = (3*h - nnum*(2*x1 + x2))/nnum**2
        C = x1
        D = 0
             
        n = np.arange(0, nnum, 1)
        fun = A*n**3 + B*n**2 + C*n + D 
        
        return fun
    def createDx(self, x, dfunx):
        #if x[-1]-x[0]>0:
        dx = np.arange(0,x[-1]-x[0], (dfunx[1]+dfunx[0])/2)
        #else:
        #    dx = x[0]-np.arange(0, x[-1]-x[0], -(dfunx[1]+dfunx[0])/2)
        return dx
    def createPlate(self, x = [0,0], y = [0,0], dfunx = [0.1, 0.1], dfuny = [0.1, 0.1],  k = 1, numIn = 0):
               
        string = ''
        stringBC = ''
        
        dxFun = self.getDiscretization(x=x, d = dfunx)
        dyFun = self.getDiscretization(x=y, d = dfuny)

        datx = []        
        daty = []
        num = numIn

        for idx in dxFun:
            #L += dxFun(idx)
            L = idx +x[0]
            if L>x[0]+x[1]:break
            h = y[0]
            for idy in dyFun:
                #h += dyFun(idy)
                h = idy+y[0]
                if h>y[0]+y[1]:break
                num += 1
                kval = k
                
                datx.append(L)
                daty.append(h)

                if L <= dxFun[0]: 
                    stringBC += str(num) + "\n"
                    kval = 1
                if L >= self.L - dxFun[-1]:
                    stringBC += str(num) + "\n"
                    kval = 2
                vol = idx*idy
                string += str(L) + " " + str(h)+ " " + "0" + " " + str(kval) + " " + str(vol) + "\n"
        return string, stringBC, num, datx, daty
    def createXML(self, x = [0,0], y = [0,0], dfunx = [0.1, 0.1], dfuny = [0.1, 0.1],  k = 1):
        pass
    def write(self, fileName = "mesh.txt", string = ''):
        file = open(fileName,"w")
        file.write(string)
        file.close()
