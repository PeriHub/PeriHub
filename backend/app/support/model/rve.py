# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""
RVE class is extracted from the micofam project: https://gitlab.com/DLR-SY/micofam
"""
import math
import random

from ...support.globals import log


class RVE:

    @staticmethod
    def get_fibre_locations(fib_radius, rve_fvc, dr, lgth):

        # dpth = 100.
        off = -lgth / 2.0

        # ----------------------------------------
        # Constants
        # ----------------------------------------

        PI = math.pi

        # ----------------------------------------
        # RVE Measures
        # ----------------------------------------

        # FibreContent
        fvc = rve_fvc / 100.0
        if fvc < 0.56:
            distribution = "Random"
        else:
            distribution = "NNA"
        maxfib = round(((lgth**2) * fvc) / (PI * (fib_radius + dr) ** 2))
        if maxfib < ((lgth**2) * fvc) / (PI * (fib_radius + dr) ** 2):
            maxfib = maxfib + 1
        if maxfib > 0:
            dmin = (
                (1.0 / 100.0)
                * (((lgth / 2) ** 2.0) * ((1.0 - fvc) ** 2))
                / (2.0 * PI * (fib_radius + dr) * (1.0 + fvc))
            )
            dmax = (
                (1.0 / 10.0) * (((lgth / 2) ** 2.0) * (1.0 - fvc) ** 2) / (2.0 * PI * (fib_radius + dr) * (1.0 + fvc))
            )

        # ----------------------------------------
        # Coordinates for Fibre Placement
        # ----------------------------------------

        counter = 0.0
        reset = int(0)
        refcount = 0.0
        afvc = 0.0
        afvc_best = 0.0
        xcor = []
        ycor = []
        xcor_best = []
        ycor_Best = []  # @UnusedVariable
        radius_old = []
        fvc_fib = 0.0
        attempt = 0
        pos = 0

        while abs(100.0 * fvc - afvc) > 0.25:
            if fvc == 0.0:
                xcor = []
                ycor = []
                afvc = 0.0
                counter = 0.0
                break
            elif pos == len(xcor) and attempt > 0:
                reset = int(reset + 1)
                print(
                    "*** ATTEMPT "
                    + str(reset)
                    + " OF 10: FVF NOT REACHED WITHIN TOLERANCE! REACHED: "
                    + str(afvc)
                    + "%! RESTARTING FIBRE PLACEMENT...! ***"
                )
                if abs(100.0 * fvc - afvc) < abs(100.0 * fvc - afvc_best):
                    xcor_best = xcor
                    ycor_best = ycor
                    radius_old_best = radius_old
                    afvc_best = afvc
                    counter_best = counter  # @UnusedVariable
                if xcor != [] and xcor_best == []:
                    xcor_best = xcor
                    ycor_best = ycor
                    radius_old_best = radius_old
                    afvc_best = afvc
                    counter_best = counter  # @UnusedVariable
                xcor = []
                ycor = []
                radius_old = []
                counter = 0.0
                pos = 0
                fvc_fib = 0.0
                if reset == 10:
                    xcor = xcor_best
                    ycor = ycor_best
                    radius_old = radius_old_best

                    # sexit = getWarningReply('FVF of ' + str(100. * fvc) + '% not reached within tolerance!\n\nContinue with ' + str(round(100.*afvc_best)/100.) + '% FVF? (YES)\nRetry? (NO)\nStop Modeling? (CANCEL)',(YES,NO,CANCEL))  #@UndefinedVariable @UnusedVariable
                    # if sexit == YES:  #@UndefinedVariable
                    print(
                        "*** FVF NOT REACHED WITHIN TOLERANCE! CHOOSING BEST ATTEMPT WITH "
                        + str(afvc_best)
                        + "% FVF! ***"
                    )
                    break
                    # elif sexit == NO:  #@UndefinedVariable
                    #     xcor_best = []
                    #     ycor_best = []
                    #     radius_old_best = []
                    #     afvc_best = 0.
                    #     counter_best = 0. #@UnusedVariable
                    #     xcor = []
                    #     ycor = []
                    #     radius_old = []
                    #     afvc = 0.
                    #     counter = 0.
                    #     reset = 0
                    # elif sexit == CANCEL:  #@UndefinedVariable
                    #     mdb.close()  #@UndefinedVariable
                    #     return
            else:
                pass
            check = 0
            i = 0  # @UnusedVariable
            counter = int(counter)
            if len(xcor) > 0:
                if attempt == 1500:
                    pos = pos + 1
                    attempt = 0
                else:
                    radius = (random.randrange(int(0.95 * fib_radius * 1000.0), int(1.05 * fib_radius * 1000.0))) / (
                        1000.0
                    )
                    afib = PI * (radius + dr / 2.0) ** 2
                    if distribution == "NNA":
                        dist = (
                            random.randrange(
                                int((2 * (fib_radius + dr) + dmin) * 1000.0),
                                int((2 * (fib_radius + dr) + dmax) * 1000.0),
                            )
                        ) / (1000.0)
                        phi = (random.randrange(int(0.0), int((2.0 * PI - PI / 180.0) * 100.0))) / 100.0
                        xrand = xcor[pos] + dist * math.cos(phi)  # @UndefinedVariable
                        yrand = ycor[pos] + dist * math.sin(phi)  # @UndefinedVariable
                    elif distribution == "Random":
                        xrand = off + (random.randrange(int(0.0), int((lgth + 0.65 * radius) * 1000.0), 1.0)) / (1000.0)
                        yrand = off + (random.randrange(int(0.0), int((lgth + 0.65 * radius) * 1000.0), 1.0)) / (1000.0)

                for i1 in range(len(xcor)):
                    if ((xrand - xcor[i1]) ** 2.0 + (yrand - ycor[i1]) ** 2.0) >= (
                        ((radius + radius_old[i1] + 2.0 * dr) + dmin) ** 2.0
                    ):
                        check = 1
                    else:
                        check = 0
                        attempt = attempt + 1
                        break
                if check == 1:
                    if ((xrand - radius - dr - dmin) <= off) or ((yrand - radius - dr - dmin) <= off):
                        pass

                    else:
                        if (
                            (xrand + radius >= lgth + off + 0.35 * radius)
                            and (xrand - radius <= lgth + off - 0.35 * radius)
                            and (lgth + off - yrand - radius - dr > dmin)
                        ):
                            check2 = 0
                            for i2 in range(len(xcor)):
                                if (((xrand - lgth) - xcor[i2]) ** 2 + (yrand - ycor[i2]) ** 2) >= (
                                    (radius + radius_old[i2] + 2 * dr) + dmin
                                ) ** 2:
                                    check2 = 1
                                else:
                                    check2 = 0
                                    attempt = attempt + 1
                                    break
                            if check2 == 1:
                                xcor.append(xrand)
                                xcor.append(xrand - lgth)
                                ycor.append(yrand)
                                ycor.append(yrand)
                                radius_old.append(radius)
                                radius_old.append(radius)
                                counter = counter + 1.0
                                fvc_fib = fvc_fib + afib
                            else:
                                pass
                        elif (
                            (yrand + radius > lgth + off + 0.35 * radius)
                            and (yrand - radius < lgth + off - 0.35 * radius)
                            and (lgth + off - xrand - radius - dr > dmin)
                        ):
                            check2 = 0
                            for i3 in range(len(xcor)):
                                if ((xrand - xcor[i3]) ** 2 + ((yrand - lgth) - ycor[i3]) ** 2) >= (
                                    (radius + radius_old[i3] + 2 * dr) + dmin
                                ) ** 2:
                                    check2 = 1
                                else:
                                    check2 = 0
                                    attempt = attempt + 1
                                    break
                            if check2 == 1:
                                ycor.append(yrand)
                                ycor.append(yrand - lgth)
                                xcor.append(xrand)
                                xcor.append(xrand)
                                radius_old.append(radius)
                                radius_old.append(radius)
                                counter = counter + 1.0
                                fvc_fib = fvc_fib + afib
                            else:
                                pass
                        elif (xrand < lgth + off - radius - dr - dmin) and (yrand < lgth + off - radius - dr - dmin):
                            xcor.append(xrand)
                            ycor.append(yrand)
                            radius_old.append(radius)
                            counter = counter + 1.0
                            fvc_fib = fvc_fib + afib
                        elif (
                            ((yrand + radius) >= lgth + off + 0.35 * radius)
                            and ((xrand + radius) >= lgth + off + 0.35 * radius)
                            and ((yrand - radius) <= lgth + off - 0.35 * radius)
                            and ((xrand - radius) <= lgth + off - 0.35 * radius)
                            and ((xrand) ** 2 + (yrand) ** 2) <= (2 * (lgth + off) - 0.35 * radius) ** 2
                        ):
                            for i4 in range(len(xcor)):
                                check2 = 0
                                if (
                                    (
                                        ((xrand - xcor[i4]) ** 2 + ((yrand - lgth) - ycor[i4]) ** 2)
                                        >= ((radius + radius_old[i4] + 2 * dr) + dmin) ** 2
                                    )
                                    and (
                                        (((xrand - lgth) - xcor[i4]) ** 2 + (yrand - ycor[i4]) ** 2)
                                        >= ((radius + radius_old[i4] + 2 * dr) + dmin) ** 2
                                    )
                                    and (
                                        (((xrand - lgth) - xcor[i4]) ** 2 + ((yrand - lgth) - ycor[i4]) ** 2)
                                        >= ((radius + radius_old[i4] + 2 * dr) + dmin) ** 2
                                    )
                                ):
                                    check2 = 1
                                else:
                                    check2 = 0
                                    attempt = attempt + 1
                                    break
                            if check2 == 1:
                                xcor.append(xrand)
                                xcor.append(xrand)
                                xcor.append(xrand - lgth)
                                xcor.append(xrand - lgth)
                                ycor.append(yrand)
                                ycor.append(yrand - lgth)
                                ycor.append(yrand)
                                ycor.append(yrand - lgth)
                                radius_old.append(radius)
                                radius_old.append(radius)
                                radius_old.append(radius)
                                radius_old.append(radius)
                                counter = counter + 1.0
                                fvc_fib = fvc_fib + afib
                else:
                    pass
            else:
                xrand = (random.randrange(int((off + lgth / 4) * 100.0), int((off + (3 * lgth / 4)) * 100.0))) / 100.0
                yrand = (random.randrange(int((off + lgth / 4) * 100.0), int((off + (3 * lgth / 4)) * 100.0))) / 100.0
                radius = (random.randrange(int(0.95 * fib_radius * 1000.0), int(1.05 * fib_radius * 1000.0))) / (1000.0)
                afib = PI * (radius + dr / 2.0) ** 2
                if (
                    ((xrand + radius) >= lgth + off + 0.35 * radius)
                    and ((yrand + radius + dr + dmin) <= lgth + off)
                    and ((yrand - radius - dr - dmin) >= off)
                ):
                    xcor.append(xrand)
                    xcor.append(xrand - lgth)
                    ycor.append(yrand)
                    ycor.append(yrand)
                    radius_old.append(radius)
                    radius_old.append(radius)
                    counter = counter + 1.0
                    fvc_fib = fvc_fib + afib
                elif (
                    ((yrand + radius) >= lgth + off + 0.35 * radius)
                    and ((xrand + radius + dr + dmin) <= lgth + off)
                    and ((xrand - radius - dr - dmin) >= off)
                ):
                    xcor.append(xrand)
                    xcor.append(xrand)
                    ycor.append(yrand)
                    ycor.append(yrand - lgth)
                    radius_old.append(radius)
                    radius_old.append(radius)
                    counter = counter + 1.0
                    fvc_fib = fvc_fib + afib
                elif (
                    (yrand + radius >= lgth + off + 0.35 * radius)
                    and (xrand + radius >= lgth + off + 0.35 * radius)
                    and (yrand - radius <= lgth + off - 0.35 * radius)
                    and (xrand - radius <= lgth + off - 0.35 * radius)
                ):
                    xcor.append(xrand)
                    xcor.append(xrand)
                    xcor.append(xrand - lgth)
                    xcor.append(xrand - lgth)
                    ycor.append(yrand)
                    ycor.append(yrand - lgth)
                    ycor.append(yrand)
                    ycor.append(yrand - lgth)
                    radius_old.append(radius)
                    radius_old.append(radius)
                    radius_old.append(radius)
                    radius_old.append(radius)
                    counter = counter + 1.0
                    fvc_fib = fvc_fib + afib
                elif (xrand > (lgth + off + 0.65 * radius)) or (yrand > (lgth + off + 0.65 * radius)):
                    pass
                elif (
                    ((xrand - radius - dr - dmin) >= off)
                    and ((yrand - radius - dr - dmin) >= off)
                    and ((xrand + radius + dr + dmin) <= lgth + off)
                    and ((yrand + radius + dr + dmin) <= lgth + off)
                ):
                    xcor.append(xrand)
                    ycor.append(yrand)
                    radius_old.append(radius)
                    counter = counter + 1.0
                    fvc_fib = fvc_fib + afib
                else:
                    pass

            refcount = refcount + 1.0
            afvc = (100.0 * fvc_fib) / (lgth**2)
        if abs(100.0 * fvc - afvc) < 0.25:
            print(
                "*** ATTEMPT " + str(reset + 1) + " OF 10: FIBRE VOLUME FRACTION OF " + str(rve_fvc) + "% REACHED! ***"
            )
            afvc_best = afvc
            counter_best = counter  # @UnusedVariable

        return xcor, ycor
