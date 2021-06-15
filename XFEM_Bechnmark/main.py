import matplotlib.pyplot as plt
import numpy as np
from XFEMdcb import XFEMDCB
if __name__ == '__main__':
    ###################
    # Geometry https://elib.dlr.de/127827/1/Voelkerink_JA_XFEM_AM.pdf
    ###################
    L = 50.5
    h = 10
    overlap = 9.5
    ta = 0.2
    tg = 4.0
    dx = 0.25
    dy = 0.25
    da = 0.01
    dcb = XFEMDCB(L = L, da = da)
    # lower plates
    

    y = dcb.getDiscretization(x = [0,h], d = [.01, 1])
    y2 = dcb.getDiscretization(x = [0,h], d = [1, 1])
    xnew = np.arange(0, 1, 0.01)
    #print(y(xnew))
    print()
    #print(y2(xnew))
    
    #plt.plot(y, '*')  
    #plt.plot(y2, 'x')  
    #plt.show() 

    
    run = True
    lp = (L - overlap)/2 - tg 
    tp = (L + overlap)/2 + tg
    
    l1 = lp
    l2 = (L - overlap)/2
    l3 = (L + overlap)/2
    l4 = (L + overlap)/2 + tg
    l5 = L
    h1 = h - 3*ta
    h2 = h
    h3 = h + ta
    h4 = h + 4*ta
    h5 = 2*h + ta
    writeString =  "# x y z block_id volume\n"
    writeStringLC = ''
    writeStringRC = ''
    
    x = [[0,l1], [l1,l2],[l2,l3], [l3,l4],[l4,l5]]    
    dfunx = [[dx, dx], [dx, da], [da, da], [da, dx], [dx, dx]]
    y =     [[0,h1], [h1,h2], [h2,h3], [h3,h4], [h4,h5]]
    dfuny = [[dy, dy], [dy, da], [da, da], [da, dy], [dy, dy]]
    
    #if run:
    num  = 0
    k = 2
    for idx in range(0, len(x)):
        for idy in range(0, len(y)):
            if x[idx][0] == l1: 
                if y[idy][0] == 0 or y[idy][0] == h1 or y[idy][0] == h2:
                    continue
            if x[idx][0] == l3:
                if y[idy][0] == h2 or y[idy][0] == h3 or y[idy][0] == h4:
                    continue 
            k += 1 
            string, stringBC, num, datx, daty = dcb.createPlate(x = x[idx],    y = y[idy], dfunx = dfunx[idx], dfuny = dfuny[idy], k = k, numIn = num)
            
            writeString += string
            writeStringLC += stringBC
            plt.plot(datx, daty, '*')
        #string, stringBC, num, datx, daty = dcb.createPlate(x = [tp+tg,L], y = [0,h], dfunx = [da, dx], dfuny = [dy, da], k = 1, numIn = num)
        #writeString += string
        #writeStringRC = stringBC
        #plt.plot(datx, daty, '*')
    plt.show()
        # top plates    
    print('Number of Nodes: ', num, "horizon 1 4dx: ", 4*dx, "horizon 2 4dx: ", 4*da)
    run = False
    if run: 
        num = 0   
        string, stringBC, num, datx, daty = dcb.createPlate(x = [0,lp],    y = [h+ta,2*h+ta], dfunx = [dx, da], dfuny = [da, dy], k = 1, numIn = num)
        writeString += string
        writeStringLC += stringBC
        plt.plot(datx, daty, '*')
        string, stringBC, num, datx, daty = dcb.createPlate(x = [tp+tg,L], y = [h+ta,2*h+ta], dfunx = [da, dx], dfuny = [da, dy], k = 1, numIn = num)
        writeString += string
        writeStringRC += stringBC
        plt.plot(datx, daty, '*')
        
        #adhesive 
        string, stringBC, num, datx, daty = dcb.createPlate(x = [0,lp], y = [h,h+ta], dfunx = [dx, da], dfuny = [da, da], k = 2, numIn = num)
        writeString += string
        writeStringLC += stringBC
        plt.plot(datx, daty, '*')
    
        string, stringBC, num, datx, daty = dcb.createPlate(x = [tp+tg,L], y = [h,h+ta], dfunx = [da, dx], dfuny = [da, da], k = 2, numIn = num)
        writeString += string
        writeStringRC += stringBC
        plt.plot(datx, daty, '*')
        # damage region
        string, stringBC, num, datx, daty = dcb.createPlate(x = [lp+tg,tp], y = [h,h+ta], dfunx = [da, da], dfuny = [da, da], k = 3, numIn = num)
        writeString += string
        plt.plot(datx, daty, '*')
    
        string, stringBC, num, datx, daty = dcb.createPlate(x = [lp,tp],    y = [h+ta,2*h+ta], dfunx = [da,da], dfuny = [da, dy], k = 4, numIn = num)
        writeString += string
        plt.plot(datx, daty, '*')
    
        string, stringBC, num, datx, daty = dcb.createPlate(x = [lp+tg,tp+tg],    y = [0,h], dfunx = [da, da], dfuny = [dy, da], k = 4, numIn = num)
        writeString += string
        plt.plot(datx, daty, '*')
    
    
        plt.show()
        dcb.write(fileName = "mesh.txt", string = writeString)
        dcb.write(fileName = "bcright.txt", string = writeStringRC)
        dcb.write(fileName = "bcleft.txt", string = writeStringLC)
    