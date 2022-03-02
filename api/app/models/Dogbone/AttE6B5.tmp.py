import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d


class CheckVal(object):
    def __init__(self):
        pass

    def checkValLower(self, val, limit):
        inside = False

        if val <= limit:
            inside = True
        return inside

    def checkValGreater(self, val, limit):
        inside = False

        if val >= limit:
            inside = True
        return inside

    def createBoundaryCurve(self, h=0, l1=0, R=0, l2=0, alphaMax=90, dl=0, dh=0):

        dalpha = 0.025
        print(alphaMax)
        alpha = np.arange(0, alphaMax + dalpha, dalpha)
        ##################################
        # Start
        ##################################
        x = np.array([0])
        y = np.array([h])
        #########
        # Circle
        #########
        x = np.concatenate((x, l1 + dl + R * np.sin((-alpha) / 180 * np.pi)))
        y = np.concatenate((y, h + R - dh - R * np.cos((-alpha) / 180 * np.pi)))
        #########
        # Circle
        #########

        x = np.concatenate((x, l1 + dl + l2 + R * np.sin(alpha / 180 * np.pi)))
        y = np.concatenate((y, h - dh + R - R * np.cos(alpha / 180 * np.pi)))
        #########
        # End
        #########

        x = np.concatenate((x, np.array([2 * dl + 2 * l1 + l2 + 0.01])))
        y = np.concatenate((y, np.array([h])))

        topSurf = interp1d(x, y)

        #########
        # Bottom
        #########
        x = np.array([2 * l1 + 2 * dl + l2 + 0.1])
        y = np.array([0])

        #########
        # Circle
        #########
        x = np.concatenate(
            (x, l1 + dl + l2 + R * np.sin((alphaMax - alpha) / 180 * np.pi))
        )
        # x = np.concatenate((x,l1+l2+dl-R*np.cos(alpha/180*np.pi)))
        y = np.concatenate((y, dh - R + R * np.cos((alphaMax - alpha) / 180 * np.pi)))

        #########
        # Circle
        #########
        x = np.concatenate((x, l1 + dl + R * np.sin(-alpha / 180 * np.pi)))
        y = np.concatenate((y, dh - R + R * np.cos(-alpha / 180 * np.pi)))  # error
        #########
        # End
        #########
        x = np.concatenate((x, np.array([0])))
        y = np.concatenate((y, np.array([0])))

        bottomSurf = interp1d(x, y)

        return topSurf, bottomSurf


if __name__ == "__main__":
    c = CheckVal()
    dx = 0.001
    t = dx
    Lges = 0.115
    print(dx)
    dx = Lges / int(Lges / dx)

    h1 = 0.019
    h2 = 0.013
    dy = h1 / int(h1 / dx)

    print(dx, dy)
    bc = 0.002
    R = 0.076
    l2 = 0.057
    dl = np.sqrt(R * R - (R - (h1 - h2) / 2) ** 2)

    l1 = (Lges - 2 * dl - l2) / 2
    dh = (h1 - h2) / 2
    alpha = np.arccos((R - dh) / R) * 180 / np.pi

    topSurf, bottomSurf = c.createBoundaryCurve(
        h=h1, l1=l1, R=R, l2=l2, alphaMax=alpha, dl=dl, dh=dh
    )
    blockDef = np.array([0, bc, l1, l1 + 2 * dl + l2, Lges - bc])

    x = np.arange(0, Lges + dx, dx)

    y = np.arange(0, h1 + dy, dy)
    z = np.arange(0, t, dx)
    matNum = 0
    xList = []
    yList = []
    vol = dx * dx  # *dx
    stringLeft = ""
    stringRight = ""
    string = "# x y z block_id volume\n"
    num = 0
    bccount = 0
    for xval in x:
        for yval in y:
            for zval in z:
                if c.checkValGreater(yval, bottomSurf(xval)) and c.checkValLower(
                    yval, topSurf(xval)
                ):
                    num += 1
                    for idx, val in enumerate(blockDef):
                        if c.checkValGreater(xval, val):
                            matNum = idx + 1
                    if c.checkValLower(xval, blockDef[0]):
                        stringLeft += str(num) + "\n"
                        bccount += 1
                    if c.checkValGreater(xval, blockDef[-1]):
                        stringRight += str(num) + "\n"
                        bccount += 1
                    string += (
                        str(xval)
                        + " "
                        + str(yval)
                        + " "
                        + str(zval)
                        + " "
                        + str(matNum)
                        + " "
                        + str(vol)
                        + "\n"
                    )
                    xList.append(xval)
                    yList.append(yval)

    for zval in z:
        string += (
            str(l1 + dl)
            + " "
            + str(0.5 * (h1 - h2))
            + " "
            + str(zval)
            + " "
            + str(3)
            + " "
            + str(vol)
            + "\n"
        )
    xList.append(l1 + dl)
    yList.append(0.5 * (h1 - h2))
    fid = open("dogbone.txt", "w")
    fid.write(string)
    fid.close()

    fid = open("BCleft.txt", "w")
    fid.write(stringLeft)
    fid.close()

    fid = open("BCright.txt", "w")
    fid.write(stringRight)
    fid.close()
    print(
        "numer of Nodes", num, "horizon 4dx", 4.01 * dx, " numer of BC nodes", bccount
    )

    print(np.max(x))
    yt = topSurf(x)
    yb = bottomSurf(x)
    plt.plot(x, yt)
    plt.plot(x, yb)
    x = [l1, l1]
    y = [0, h1]
    y2 = [(h1 - h2) / 2, h2 + (h1 - h2) / 2]
    plt.plot(x, y)
    x = [l1 + dl, l1 + dl]
    plt.plot(x, y2)
    x = [l1 + dl + l2, l1 + dl + l2]
    plt.plot(x, y2)
    x = [l1 + 2 * dl + l2, l1 + 2 * dl + l2]
    plt.plot(x, y)
    plt.plot(xList, yList, "*")
    plt.gca().set_aspect("equal", adjustable="box")
    plt.show()
