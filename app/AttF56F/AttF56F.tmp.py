import sys
import os

#xMax = 16
#xMax = int(input("Anzahl in x: "))
#yMax = int(input("Anzahl in y: "))
#zMax = int(input("Anzahl in z: "))

L = 0.01
h = 0.01
B = 0.001


xMax = 102
dx = L/(xMax-1)
yMax = round(xMax*h/L)
if yMax % 2:
    yMax+=1
    xMax=yMax
print (xMax, yMax)
zMax = 1
#zMax = round(xMax*B/L)
#dx = float(input("Schrittweite dx: "))
#dy = float(input("Schrittweite dy: "))
#dz = float(input("Schrittweite dz: "))
dx = L/(xMax-1)
dy = dx
dy = h/(yMax-1)
if zMax == 1:
    dz = B
else:
    dz = B/(zMax-1)
nn=3
vol = dx * dy * dz
print(dx,dy,dz)
print("4.01*dx Horizon: ", 4.01*dx, " Volume: ", vol)

delta = 1 # int(input("Randbereich: "))
i = 0


#xMin = -(xMax/2 - 0.5) * dx
xMin = -L/2
yMin = -h/2
zMin = 0

path = "Output/Att893E/"
if not os.path.exists(path):
    os.mkdir(path)
    
plateFile = open(path+"plate2D.txt","w")
nodeset_1 = open(path+"nodeset2D_1.txt","w")
nodeset_2 = open(path+"nodeset2D_2.txt","w")
nodeset_3 = open(path+"nodeset2D_3.txt","w")
nodeset_4 = open(path+"nodeset2D_4.txt","w")

plateFile.write("# x y z block_id volume\n")
n1 = 0
n2 = 0
for x in range(1, xMax+1):
    for y in range(1, yMax+1):
            
            k = 1
            #if xMin + (x-1) * dx<-a/2:
            #  k=2;
            xVal = xMin + (x-1) * dx
            yVal = yMin + (y-1) * dy
            plateFile.write("%f %f %f %d %.3E\n" % (xVal, yVal, zMin, k, vol))
            i += 1
halfyMax = round(yMax/2)
if halfyMax % 2:
    halfyMax+=1

for x in range(1,5):
    for y in range(1, halfyMax+1):
            i += 1
            
            xVal = xMin - (x) * dx
            yVal = (y-1) * dy+dy
            k = 2
            plateFile.write("%f %f %f %d %.3E\n" % (xVal, yVal, zMin, k, vol))
            nodeset_1.write("%d\n" % (i))
            i += 1
            xVal = L/2 + (x) * dx
            yVal = - (y-1) * dy-dy
            k = 3
            plateFile.write("%f %f %f %d %.3E\n" % (xVal, yVal, zMin, k, vol))
            nodeset_2.write("%d\n" % (i))

for y in range(1,5):
    for x in range(1, xMax+1):
            i += 1
            
            xVal = xMin + (x-1) * dx
            yVal = h/2 + (y) * dy

            k = 4
            plateFile.write("%f %f %f %d %.3E\n" % (xVal, yVal, zMin, k, vol))
            nodeset_3.write("%d\n" % (i))
            i += 1
            xVal = xMin + (x-1) * dx
            yVal = yMin - (y) * dy
            
            k = 5
            plateFile.write("%f %f %f %d %.3E\n" % (xVal, yVal, zMin, k, vol))
            nodeset_4.write("%d\n" % (i))
            
plateFile.close()
nodeset_1.close()
nodeset_2.close()
nodeset_3.close()
nodeset_4.close()
