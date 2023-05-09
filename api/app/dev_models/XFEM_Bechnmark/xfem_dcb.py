"""
doc
"""
import numpy as np

from support.geometry import Geometry
from support.model_writer import ModelWriter


class XFEMDCB:
    def __init__(
        self,
        xend=1,
        yend=1,
        zend=0,
        dx_value=[0.1, 0.1],
        filename="XFEMDCBmodel",
    ):
        self.xend = xend
        self.yend = yend
        self.zend = zend
        self.dx_value = dx_value
        da = 9.5
        dgap = 3
        tb = 1

        self.pos = [
            0,
            xend / 2 - da / 2 - dgap,
            xend / 2 - da / 2,
            xend / 2 + da / 2,
            xend / 2 + da / 2 + dgap,
            xend,
        ]
        self.yLocs = [0, yend / 2 - tb / 2, yend / 2 + tb / 2, yend]

    def getDiscretization(self, x_value=[0, 0], d=[0.1, 0.1]):
        """doc"""
        dx_value = self.createDx(x_value, d)
        fun = self.fun(
            d[0],
            d[1],
            height=x_value[1] - x_value[0],
            nnum=len(dx_value),
        )

        return fun

    def create_model(self):
        """doc"""
        geo = Geometry()
        x_value, y_value, _ = geo.create_rectangle(
            coor=[0, self.xend, 0, self.yend, 0, self.zend],
            dx_value=self.dx_value,
        )
        vol = np.zeros(len(x_value))
        k = np.ones(len(x_value))
        for idx in range(0, len(x_value)):
            # if y_value[idx] >= self.yend / 2:
            #     k[idx] = self.create_load_block(x_value[idx], y_value[idx], k[idx])
            # else:
            #     k[idx] = self.create_boundary_condition_block(
            #         x_value[idx], y_value[idx], k[idx]
            #     )
            # k[idx] = int(self.create_bc_node(x_value[idx], y_value[idx], k[idx]))
            # k[idx] = int(self.create_load_intro_node(x_value[idx], y_value[idx], k[idx]))
            # k[idx] = int(self.create_block(y_value[idx], k[idx]))

            vol[idx] = self.dx_value[0] * self.dx_value[1]
        model = {"x": x_value, "y": y_value, "k": k, "vol": vol}
        # writer = ModelWriter(filename=self.filename)
        # writer.write_node_sets(model, self.ns_list)
        # writer.write_mesh(model)
        # self.writeXML(writer=writer, model=model)

        return model

    @staticmethod
    def fun(x1, x2, height, nnum):
        """doc"""

        # x_value = [0, 2 * x1, height - 2 * x2, height]
        # y_value = [x1, x1, x1, x2, x2, x2]
        # y_value = [0, 0.5*x1, 2*x1,  height-2*x2, height-0.5*x2, height]
        # y_value = [0, 2 * x2, height - 2 * x1, height]
        A = (-2 * height + nnum * (x1 + x2)) / nnum**3
        thickness = (3 * height - nnum * (2 * x1 + x2)) / nnum**2
        C = x1
        D = 0

        n = np.arange(0, nnum, 1)
        fun = A * n**3 + thickness * n**2 + C * n + D

        return fun

    @staticmethod
    def createDx(x_value, dfunx):
        """doc"""
        # if x_value[-1]-x_value[0]>0:
        dx_value = np.arange(0, x_value[-1] - x_value[0], (dfunx[1] + dfunx[0]) / 2)
        # else:
        #    dx_value = x_value[0]-np.arange(0, x_value[-1]-x_value[0], -(dfunx[1]+dfunx[0])/2)
        return dx_value

    def createPlate(
        self,
        x_value=[0, 0],
        y_value=[0, 0],
        dfunx=[0.1, 0.1],
        dfuny=[0.1, 0.1],
        k=1,
        numIn=0,
    ):
        """doc"""

        string = ""
        stringBC = ""

        dxFun = self.getDiscretization(x_value=x_value, d=dfunx)
        dyFun = self.getDiscretization(x_value=y_value, d=dfuny)

        datx = []
        daty = []
        num = numIn

        for idx in dxFun:
            # length += dxFun(idx)
            length = idx + x_value[0]
            if length > x_value[0] + x_value[1]:
                break
            height = y_value[0]
            for idy in dyFun:
                # height += dyFun(idy)
                height = idy + y_value[0]
                if height > y_value[0] + y_value[1]:
                    break
                num += 1
                kval = k

                datx.append(length)
                daty.append(height)

                if length <= dxFun[0]:
                    stringBC += str(num) + "\n"
                    kval = 1
                if length >= self.xend - dxFun[-1]:
                    stringBC += str(num) + "\n"
                    kval = 2
                vol = idx * idy
                string += str(length) + " " + str(height) + " " + "0" + " " + str(kval) + " " + str(vol) + "\n"
        return string, stringBC, num, datx, daty

    # def createXML(
    #     self, x_value=[0, 0], y_value=[0, 0], dfunx=[0.1, 0.1], dfuny=[0.1, 0.1], k=1
    # ):
    #     """doc"""
    #     pass

    @staticmethod
    def write(fileName="mesh.txt", string=""):
        """doc"""
        with open(fileName, "w", encoding="UTF-8") as file:
            file.write(string)
