import os

# X_MAX = 16
# X_MAX = int(input("Anzahl in x: "))
# Y_MAX = int(input("Anzahl in y: "))
# Z_MAX = int(input("Anzahl in z: "))

LENGTH = 0.01
HEIGHT = 0.01
THICKNESS = 0.001


X_MAX = 102
dx_value = LENGTH / (X_MAX - 1)
Y_MAX = round(X_MAX * HEIGHT / LENGTH)
if Y_MAX % 2:
    Y_MAX += 1
    X_MAX = Y_MAX
print(X_MAX, Y_MAX)
Z_MAX = 1
# Z_MAX = round(X_MAX*THICKNESS/LENGTH)
# dx_value = float(input("Schrittweite dx_value: "))
# dy = float(input("Schrittweite dy: "))
# dz = float(input("Schrittweite dz: "))
dx_value = LENGTH / (X_MAX - 1)
dy = dx_value
dy = HEIGHT / (Y_MAX - 1)
if Z_MAX == 1:
    dz = THICKNESS
else:
    dz = THICKNESS / (Z_MAX - 1)
number_nodes = 3
vol = dx_value * dy * dz
print(dx_value, dy, dz)
print("4.01*dx_value Horizon: ", 4.01 * dx_value, " Volume: ", vol)

delta = 1  # int(input("Randbereich: "))
i = 0


# xMin = -(X_MAX/2 - 0.5) * dx_value
xMin = -LENGTH / 2
yMin = -HEIGHT / 2
zMin = 0

path = "Output/Att893E/"
if not os.path.exists(path):
    os.mkdir(path)

plateFile = open(path + "plate2D.txt", "w")
nodeset_1 = open(path + "nodeset2D_1.txt", "w")
nodeset_2 = open(path + "nodeset2D_2.txt", "w")
nodeset_3 = open(path + "nodeset2D_3.txt", "w")
nodeset_4 = open(path + "nodeset2D_4.txt", "w")

plateFile.write("# x y z block_id volume\n")
n1 = 0
n2 = 0
for x_value in range(1, X_MAX + 1):
    for y_value in range(1, Y_MAX + 1):

        k = 1
        # if xMin + (x_value-1) * dx_value<-a/2:
        #  k=2;
        xVal = xMin + (x_value - 1) * dx_value
        yVal = yMin + (y_value - 1) * dy
        plateFile.write("%f %f %f %d %.3E\n" % (xVal, yVal, zMin, k, vol))
        i += 1
halfyMax = round(Y_MAX / 2)
if halfyMax % 2:
    halfyMax += 1

for x_value in range(1, 5):
    for y_value in range(1, halfyMax + 1):
        i += 1

        xVal = xMin - (x_value) * dx_value
        yVal = (y_value - 1) * dy + dy
        k = 2
        plateFile.write("%f %f %f %d %.3E\n" % (xVal, yVal, zMin, k, vol))
        nodeset_1.write("%d\n" % (i))
        i += 1
        xVal = LENGTH / 2 + (x_value) * dx_value
        yVal = -(y_value - 1) * dy - dy
        k = 3
        plateFile.write("%f %f %f %d %.3E\n" % (xVal, yVal, zMin, k, vol))
        nodeset_2.write("%d\n" % (i))

for y_value in range(1, 5):
    for x_value in range(1, X_MAX + 1):
        i += 1

        xVal = xMin + (x_value - 1) * dx_value
        yVal = HEIGHT / 2 + (y_value) * dy

        k = 4
        plateFile.write("%f %f %f %d %.3E\n" % (xVal, yVal, zMin, k, vol))
        nodeset_3.write("%d\n" % (i))
        i += 1
        xVal = xMin + (x_value - 1) * dx_value
        yVal = yMin - (y_value) * dy

        k = 5
        plateFile.write("%f %f %f %d %.3E\n" % (xVal, yVal, zMin, k, vol))
        nodeset_4.write("%d\n" % (i))

plateFile.close()
nodeset_1.close()
nodeset_2.close()
nodeset_3.close()
nodeset_4.close()
