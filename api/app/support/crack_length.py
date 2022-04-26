"""
doc
"""
import csv
from tkinter import Y
import matplotlib.pyplot as plt


class CrackLength:

    first_row = True
    time = []
    damage = []
    x = []
    y = []
    z = []
    with open(
        "/home/jt/perihub/api/app/Output/CompactTension/CompactTension_Output1.csv",
        "r",
        encoding="UTF-8",
    ) as file:
        reader = csv.reader(file)
        for lines in reader:
            if not first_row:
                time.append(float(lines[0]))
                damage_list = []
                x_list = []
                y_list = []
                z_list = []
                if lines[1].split(";")[0] != "":
                    for idx in range(0, len(lines[1].split(";")) - 1):
                        damage_list.append(float(lines[1].split(";")[idx]) * 100)
                        x_list.append(float(lines[2].split(";")[idx]))
                        y_list.append(float(lines[3].split(";")[idx]))
                        z_list.append(float(lines[4].split(";")[idx]))

                damage.append(damage_list)
                x.append(x_list)
                y.append(y_list)
                z.append(z_list)
            first_row = False

    plt.scatter(x[-1], y[-1], s=damage[-1])
    plt.show()

    @staticmethod
    def read_csv():
        print("bla")
