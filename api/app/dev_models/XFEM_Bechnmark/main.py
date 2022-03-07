"""
doc
"""
import matplotlib.pyplot as plt
import numpy as np
from xfem_dcb import XFEMDCB

if __name__ == "__main__":
    ###################
    # Geometry https://elib.dlr.de/127827/1/Voelkerink_JA_XFEM_AM.pdf
    ###################
    LENGTH = 50.5
    HEIGHT = 10
    OVERLAP = 9.5
    TA_VALUE = 0.2
    TG_VALUE = 4.0
    DX_VALUE = 0.25
    DY_VALUE = 0.25
    DA_VALUE = 0.01
    dcb = XFEMDCB(L=LENGTH, da=DA_VALUE)
    # lower plates

    y_values = dcb.getDiscretization(x_value=[0, HEIGHT], d=[0.01, 1])
    y2 = dcb.getDiscretization(x_value=[0, HEIGHT], d=[1, 1])
    xnew = np.arange(0, 1, 0.01)
    # print(y_values(xnew))
    print()
    # print(y2(xnew))

    # plt.plot(y_values, '*')
    # plt.plot(y2, 'x')
    # plt.show()

    run = True
    lp = (LENGTH - OVERLAP) / 2 - TG_VALUE
    tp = (LENGTH + OVERLAP) / 2 + TG_VALUE

    length1 = lp
    length2 = (LENGTH - OVERLAP) / 2
    l3 = (LENGTH + OVERLAP) / 2
    l4 = (LENGTH + OVERLAP) / 2 + TG_VALUE
    l5 = LENGTH
    height1 = HEIGHT - 3 * TA_VALUE
    height2 = HEIGHT
    h3 = HEIGHT + TA_VALUE
    h4 = HEIGHT + 4 * TA_VALUE
    h5 = 2 * HEIGHT + TA_VALUE
    write_string = "# x y z block_id volume\n"
    write_string_lc = ""
    write_string_rc = ""

    x_values = [[0, length1], [length1, length2], [length2, l3], [l3, l4], [l4, l5]]
    dfunx = [
        [DX_VALUE, DX_VALUE],
        [DX_VALUE, DA_VALUE],
        [DA_VALUE, DA_VALUE],
        [DA_VALUE, DX_VALUE],
        [DX_VALUE, DX_VALUE],
    ]
    y_values = [[0, height1], [height1, height2], [height2, h3], [h3, h4], [h4, h5]]
    dfuny = [
        [DY_VALUE, DY_VALUE],
        [DY_VALUE, DA_VALUE],
        [DA_VALUE, DA_VALUE],
        [DA_VALUE, DY_VALUE],
        [DY_VALUE, DY_VALUE],
    ]

    # if run:
    num = 0
    k = 2
    for idx, x_value in enumerate(x_values):
        for idy, y_value in enumerate(y_values):
            if x_value[0] == length1:
                if y_value[0] == 0 or y_value[0] == height1 or y_value[0] == height2:
                    continue
            if x_value[0] == l3:
                if y_value[0] == height2 or y_value[0] == h3 or y_value[0] == h4:
                    continue
            k += 1
            string, stringBC, num, datx, daty = dcb.createPlate(
                x_value=x_value,
                y_value=y_value,
                dfunx=dfunx[idx],
                dfuny=dfuny[idy],
                k=k,
                numIn=num,
            )

            write_string += string
            write_string_lc += stringBC
            plt.plot(datx, daty, "*")
        # string, stringBC, num, datx, daty =
        # dcb.createPlate(x_values = [tp+TG_VALUE,LENGTH], y_values = [0,HEIGHT],
        # dfunx = [DA_VALUE, DX_VALUE], dfuny = [DY_VALUE, DA_VALUE], k = 1, numIn = num)
        # write_string += string
        # write_string_rc = stringBC
        # plt.plot(datx, daty, '*')
    plt.show()
    # top plates
    print(
        "Number of Nodes: ",
        num,
        "horizon 1 4dx: ",
        4 * DX_VALUE,
        "horizon 2 4dx: ",
        4 * DA_VALUE,
    )
    run = False
    if run:
        num = 0
        string, stringBC, num, datx, daty = dcb.createPlate(
            x_value=[0, lp],
            y_value=[HEIGHT + TA_VALUE, 2 * HEIGHT + TA_VALUE],
            dfunx=[DX_VALUE, DA_VALUE],
            dfuny=[DA_VALUE, DY_VALUE],
            k=1,
            numIn=num,
        )
        write_string += string
        write_string_lc += stringBC
        plt.plot(datx, daty, "*")
        string, stringBC, num, datx, daty = dcb.createPlate(
            x_value=[tp + TG_VALUE, LENGTH],
            y_value=[HEIGHT + TA_VALUE, 2 * HEIGHT + TA_VALUE],
            dfunx=[DA_VALUE, DX_VALUE],
            dfuny=[DA_VALUE, DY_VALUE],
            k=1,
            numIn=num,
        )
        write_string += string
        write_string_rc += stringBC
        plt.plot(datx, daty, "*")

        # adhesive
        string, stringBC, num, datx, daty = dcb.createPlate(
            x_value=[0, lp],
            y_value=[HEIGHT, HEIGHT + TA_VALUE],
            dfunx=[DX_VALUE, DA_VALUE],
            dfuny=[DA_VALUE, DA_VALUE],
            k=2,
            numIn=num,
        )
        write_string += string
        write_string_lc += stringBC
        plt.plot(datx, daty, "*")

        string, stringBC, num, datx, daty = dcb.createPlate(
            x_value=[tp + TG_VALUE, LENGTH],
            y_value=[HEIGHT, HEIGHT + TA_VALUE],
            dfunx=[DA_VALUE, DX_VALUE],
            dfuny=[DA_VALUE, DA_VALUE],
            k=2,
            numIn=num,
        )
        write_string += string
        write_string_rc += stringBC
        plt.plot(datx, daty, "*")
        # damage region
        string, stringBC, num, datx, daty = dcb.createPlate(
            x_value=[lp + TG_VALUE, tp],
            y_value=[HEIGHT, HEIGHT + TA_VALUE],
            dfunx=[DA_VALUE, DA_VALUE],
            dfuny=[DA_VALUE, DA_VALUE],
            k=3,
            numIn=num,
        )
        write_string += string
        plt.plot(datx, daty, "*")

        string, stringBC, num, datx, daty = dcb.createPlate(
            x_value=[lp, tp],
            y_value=[HEIGHT + TA_VALUE, 2 * HEIGHT + TA_VALUE],
            dfunx=[DA_VALUE, DA_VALUE],
            dfuny=[DA_VALUE, DY_VALUE],
            k=4,
            numIn=num,
        )
        write_string += string
        plt.plot(datx, daty, "*")

        string, stringBC, num, datx, daty = dcb.createPlate(
            x_value=[lp + TG_VALUE, tp + TG_VALUE],
            y_value=[0, HEIGHT],
            dfunx=[DA_VALUE, DA_VALUE],
            dfuny=[DY_VALUE, DA_VALUE],
            k=4,
            numIn=num,
        )
        write_string += string
        plt.plot(datx, daty, "*")

        plt.show()
        dcb.write(fileName="mesh.txt", string=write_string)
        dcb.write(fileName="bcright.txt", string=write_string_rc)
        dcb.write(fileName="bcleft.txt", string=write_string_lc)
