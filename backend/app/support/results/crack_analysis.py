# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import math
import os

import numpy as np
from crackpy.fracture_analysis.analysis import FractureAnalysis
from crackpy.fracture_analysis.data_processing import CrackTipInfo, InputData
from crackpy.fracture_analysis.line_integration import IntegralProperties
from crackpy.fracture_analysis.optimization import OptimizationProperties
from crackpy.fracture_analysis.plot import PlotSettings, Plotter

# from crackpy.fracture_analysis.read import OutputReader
from crackpy.fracture_analysis.write import OutputWriter
from crackpy.structure_elements.data_files import Nodemap, NodemapStructure
from crackpy.structure_elements.material import Material
from exodusreader import exodusreader
from matplotlib import pyplot as plt

from ..base_models import Model
from ..globals import log


class CrackAnalysis:
    @staticmethod
    def write_nodemap(file, step):
        log.info("Read Exodus")
        (
            points,
            point_data,
            global_data,
            cell_data,
            ns,
            block_data,
            times,
        ) = exodusreader.read_timestep(file, step)

        np_points_x = np.array(points[:, 0])
        np_points_y = np.array(points[:, 1])
        np_displ_x = np.array(point_data["Displacementsx"])
        np_displ_y = np.array(point_data["Displacementsy"])
        np_eps_x = np.array(point_data["Strainxx"])
        np_eps_y = np.array(point_data["Strainyy"])
        np_eps_xy = np.array(point_data["Strainxy"])
        np_sig_x = np.array(point_data["Cauchy Stressxx"])
        np_sig_y = np.array(point_data["Cauchy Stressyy"])
        np_sig_xy = np.array(point_data["Cauchy Stressxy"])

        np_points_z = np.empty_like(np_points_x)
        np_displ_z = np.empty_like(np_displ_x)
        # block_points_np = np.array(block_points[0])
        # block_displ_np = np.array(block_displ[0])

        headerCols = [
            "#",
            "ID;",
            "x_undef;",
            "y_undef;",
            "z_undef;",
            "u;",
            "v;",
            "w;",
            "epsx",
            "epsy",
            "epsxy",
            "eps_eqv",
            "s_xx",
            "s_yy",
            "s_xy",
        ]
        formatter = [
            "%d",
            "%15.8e",
            "%15.8e",
            "%15.8e",
            "%15.8e",
            "%15.8e",
            "%15.8e",
            "%15.8e",
            "%15.8e",
            "%15.8e",
            "%15.8e",
            "%15.8e",
            "%15.8e",
            "%15.8e",
        ]

        indexes = np.arange(1, len(np_points_x) + 1)

        # eps_eqv = (e11^2 + e12^2 - e11*e22 + 3*e12^2)^0.5
        np_eps_eqv = np.sqrt(np_eps_x**2 + np_eps_y**2 - np_eps_x * np_eps_y + 3 * np_eps_xy**2)

        nodemap_path = os.path.join(os.path.dirname(file), "nodemap.txt")
        log.info("Write Nodemap")
        np.savetxt(
            nodemap_path,
            np.c_[
                indexes,
                np_points_x,
                np_points_y,
                np_points_z,
                np_displ_x,
                np_displ_y,
                np_displ_z,
                np_eps_x,
                np_eps_y,
                np_eps_xy,
                np_eps_eqv,
                np_sig_x,
                np_sig_y,
                np_sig_xy,
            ],
            fmt=formatter,
            delimiter="; ",
            newline="\n",
            header=" \t ".join(headerCols),
            comments="",
        )

        return "nodemap.txt", os.path.dirname(file)

    @staticmethod
    def fracture_analysis(
        model_name,
        height,
        crack_end,
        young_modulus,
        poissions_ratio,
        yield_stress,
        nodemap_filename,
        nodemap_folder,
    ):
        log.info("Fracture Analysis")
        # material properties
        # material = Material(E=72000, nu_xy=0.33, sig_yield=350)
        # material = Material(E=5000, nu_xy=0.34, sig_yield=276)
        material = Material(
            E=young_modulus,
            nu_xy=poissions_ratio,
            sig_yield=yield_stress,
            plane_strain=False,
        )

        if model_name in ["CompactTension"]:
            int_props = IntegralProperties(
                number_of_paths=10,
                number_of_nodes=100,
                bottom_offset=-0,  # should not be zero for dic results
                top_offset=0,  # should not be zero for dic results
                integral_size_left=-5,
                integral_size_right=5,
                integral_size_top=5,
                integral_size_bottom=-5,
                paths_distance_top=0.5,
                paths_distance_left=0.5,
                paths_distance_right=0.5,
                paths_distance_bottom=0.5,
                mask_tolerance=2,
                buckner_williams_terms=[-1, 1, 2, 3, 4, 5],
            )
            ct = CrackTipInfo(crack_end, 0, 0, "r")

            # optimization
            opt_props = OptimizationProperties(
                # angle_gap=20,
                # min_radius=5,
                # max_radius=10,
                # tick_size=0.01,
                # terms=[-1, 0, 1, 2, 3, 4, 5],
            )

        elif model_name in ["KICmodel", "KIICmodel", "DCBmodel"]:
            int_props = IntegralProperties(
                number_of_paths=10,
                number_of_nodes=100,
                bottom_offset=-0,  # should not be zero for dic results
                top_offset=0,  # should not be zero for dic results
                integral_size_left=-2,
                integral_size_right=2,
                integral_size_top=2,
                integral_size_bottom=-2,
                paths_distance_top=0.1,
                paths_distance_left=0.1,
                paths_distance_right=0.1,
                paths_distance_bottom=0.1,
                mask_tolerance=2,
                buckner_williams_terms=[-1, 1, 2, 3, 4, 5],
            )
            ct = CrackTipInfo(crack_end, 0, 0, "r")

            # optimization
            opt_props = OptimizationProperties(
                # angle_gap=0,
                # min_radius=1,
                # max_radius=2,
                # tick_size=0.04,
                # terms=[-1, 0, 1, 2, 3, 4, 5],
            )

        elif model_name in ["ENFmodel"]:
            int_props = IntegralProperties(
                number_of_paths=10,
                number_of_nodes=100,
                bottom_offset=-0,  # should not be zero for dic results
                top_offset=0,  # should not be zero for dic results
                integral_size_left=-0.2,
                integral_size_right=0.2,
                integral_size_top=0.2,
                integral_size_bottom=-0.2,
                paths_distance_top=(height / 2 - 0.25) / 10,
                paths_distance_left=0.05,
                paths_distance_right=0.05,
                paths_distance_bottom=(height / 2 - 0.25) / 10,
                mask_tolerance=2,
                buckner_williams_terms=[-1, 1, 2, 3, 4, 5],
            )
            crack_end = crack_length
            ct = CrackTipInfo(crack_end, height / 2, 0, "r")

            # optimization
            opt_props = OptimizationProperties(
                angle_gap=0,
                min_radius=1,
                max_radius=2,
                tick_size=0.04,
                terms=[-1, 0, 1, 2, 3, 4, 5],
            )
        else:
            log.warning("Model not supported")
            return
        # preprocess data
        nodemap_struc = NodemapStructure(10, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, False, True)
        # nodemap_struc = NodemapStructure(10, 1, 2, 4, 5, 7, 8, 9, False, True)
        nodemap = Nodemap(
            name=nodemap_filename,
            folder=nodemap_folder,
            structure=nodemap_struc,
        )
        input_data = InputData(nodemap=nodemap)
        # input_data.calc_stresses(material)
        input_data.transform_data(ct.crack_tip_x, ct.crack_tip_y, ct.crack_tip_angle)

        # fracture analysis
        analysis = FractureAnalysis(
            material=material,
            nodemap=nodemap,
            data=input_data,
            crack_tip_info=ct,
            integral_properties=int_props,
            optimization_properties=opt_props,
        )
        analysis.run()

        plt.rcParams["image.cmap"] = "coolwarm"
        plt.rcParams["figure.dpi"] = 100

        # plot
        plot_sets = PlotSettings(background="sig_vm")
        plotter = Plotter(
            path=os.path.join(nodemap_folder, "plots"),
            fracture_analysis=analysis,
            plot_sets=plot_sets,
        )
        plotter.plot()

        # write
        writer = OutputWriter(
            path=os.path.join(nodemap_folder, "results"),
            fracture_analysis=analysis,
        )
        writer.write_header()
        writer.write_results()

        return os.path.join(nodemap_folder, "plots", "nodemap_r.png")

    @staticmethod
    def get_g2c(file: str, model: Model, length: float, width: float, crack_length: float, step: int = -1):
        w = width
        a = crack_length - length / 22
        L = length / 2.2

        (
            points,
            point_data,
            global_data,
            cell_data,
            ns,
            block_data,
            time,
        ) = exodusreader.read_timestep(file, step)

        P = global_data["External_Force"][0][1]
        d = -global_data["External_Displacement"][0][1]

        GIIC = (9 * P * math.pow(a, 2) * d * 1000) / (2 * w * (1 / 4 * math.pow(L, 3) + 3 * math.pow(a, 3)))

        log.info(GIIC)

        return GIIC

    @staticmethod
    def get_crack_end(file: str, step: int = -1):

        (
            points,
            point_data,
            global_data,
            cell_data,
            ns,
            block_data,
            time,
        ) = exodusreader.read_timestep(file, step)

        points_y = np.array(points[:, 0])
        damage = point_data["Damage"]

        damaged_points_y = points_y[damage != 0]

        if len(damaged_points_y) == 0:
            log.warning("No damaged points found")
            return 1

        crack_coordinate = np.max(damaged_points_y)

        return crack_coordinate

    @staticmethod
    def get_crack_length(file: str, step: int = -1):

        (
            points,
            point_data,
            global_data,
            cell_data,
            ns,
            block_data,
            time,
        ) = exodusreader.read_timestep(file, step)

        points_x = np.array(points[:, 0])
        points_y = np.array(points[:, 1])
        points_z = np.array(points[:, 2])
        damage = point_data["Damage"]

        damaged_points_x = points_x[damage != 0]
        damaged_points_y = points_y[damage != 0]
        damaged_points_z = points_z[damage != 0]

        if len(damaged_points_x) == 0:
            log.warning("No damaged points found")
            return 1, 1, time

        crack_length = np.sqrt(
            pow(np.max(damaged_points_x) - np.min(damaged_points_x), 2)
            + pow(np.max(damaged_points_y) - np.min(damaged_points_y), 2)
        )
        crack_width = np.max(damaged_points_z) - np.min(damaged_points_z)

        return crack_length, crack_width, time
