# imports
import os

import numpy as np
from crackpy.fracture_analysis.analysis import FractureAnalysis
from crackpy.fracture_analysis.data_processing import CrackTipInfo, InputData
from crackpy.fracture_analysis.line_integration import IntegralProperties
from crackpy.fracture_analysis.optimization import OptimizationProperties
from crackpy.fracture_analysis.plot import PlotSettings, Plotter
from crackpy.fracture_analysis.read import OutputReader
from crackpy.fracture_analysis.write import OutputWriter
from crackpy.structure_elements.data_files import Nodemap, NodemapStructure
from crackpy.structure_elements.material import Material
from exodusreader.exodusreader import ExodusReader


class CrackAnalysis:
    @staticmethod
    def write_nodemap(file):
        reader = ExodusReader()

        (
            points,
            point_data,
            global_data,
            cell_data,
            ns,
            block_data,
            times,
        ) = reader.read_timestep(file, -1)

        damage_blocks = cell_data["Damage"][0]

        block_points = []
        block_displ = []
        damage_id = 0

        for block_id, _ in enumerate(block_data):
            if block_id in damage_blocks:
                block_ids = block_data[block_id][:, 0]
                block_points.append(points[block_ids])
                block_displ.append(point_data["Displacement"][block_ids])
                damage_id = block_id

        block_points_np = np.array(block_points[0])
        block_displ_np = np.array(block_displ[0])

        headerCols = [
            "#",
            "index;",
            "x_undf;",
            "y_undf;",
            "z_undf;",
            "ux;",
            "uy;",
            "uz;",
            "eps_x",
            "eps_y",
            "eps_xy",
            "eps_eqv",
            "s_x",
            "s_y",
            "s_xy",
        ]
        formatter = [
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
            "%15.8e",
        ]

        indexes = np.arange(1, len(block_points_np) + 1)

        eps_x = cell_data["Unrotated_StrainXX"][0][damage_id]
        eps_y = cell_data["Unrotated_StrainYY"][0][damage_id]
        eps_xy = cell_data["Unrotated_StrainXY"][0][damage_id]

        # eps_eqv = (e11^2 + e12^2 - e11*e22 + 3*e12^2)^0.5
        eps_eqv = np.sqrt(eps_x**2 + eps_y**2 - eps_x * eps_y + 3 * eps_xy**2)

        sig_x = cell_data["Partial_StressXX"][0][damage_id]
        sig_y = cell_data["Partial_StressYY"][0][damage_id]
        sig_xy = cell_data["Partial_StressXY"][0][damage_id]

        nodemap_path = os.path.join(os.path.dirname(file), "nodemap.txt")
        np.savetxt(
            nodemap_path,
            np.c_[
                indexes,
                block_points_np[:, [0, 1, 2]],
                block_displ_np[:, [0, 1, 2]],
                eps_x,
                eps_y,
                eps_xy,
                eps_eqv,
                sig_x,
                sig_y,
                sig_xy,
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
        length,
        height,
        crack_length,
        young_modulus,
        poissions_ratio,
        yield_stress,
        nodemap_filename,
        nodemap_folder,
    ):

        # material properties
        material = Material(E=72000, nu_xy=0.33, sig_yield=350)
        material = Material(E=5000, nu_xy=0.34, sig_yield=276)
        material = Material(
            E=young_modulus,
            nu_xy=poissions_ratio,
            sig_yield=yield_stress,
        )

        if model_name in ["CompactTension"]:
            int_props = IntegralProperties(
                number_of_paths=10,
                number_of_nodes=200,
                bottom_offset=-0,  # should not be zero for dic results
                top_offset=0,  # should not be zero for dic results
                integral_size_left=-8,
                integral_size_right=8,
                integral_size_top=8,
                integral_size_bottom=-8,
                paths_distance_top=0.2,
                paths_distance_left=0.2,
                paths_distance_right=0.2,
                paths_distance_bottom=0.2,
                mask_tolerance=2,
                buckner_williams_terms=[-1, 1, 2, 3, 4, 5],
            )
            crack_end = crack_length + 0.25 * length
            ct = CrackTipInfo(crack_end, 0, 0, "right")

            # optimization
            opt_props = OptimizationProperties(
                angle_gap=0,
                min_radius=5,
                max_radius=10,
                tick_size=0.04,
                terms=[-1, 0, 1, 2, 3, 4, 5],
            )

        elif model_name in ["KICmodel", "KIICmodel"]:
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
            crack_end = crack_length
            ct = CrackTipInfo(crack_end, height / 2, 0, "right")

            # optimization
            opt_props = OptimizationProperties(
                angle_gap=0,
                min_radius=1,
                max_radius=2,
                tick_size=0.04,
                terms=[-1, 0, 1, 2, 3, 4, 5],
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
                paths_distance_top=0.05,
                paths_distance_left=0.05,
                paths_distance_right=0.05,
                paths_distance_bottom=0.05,
                mask_tolerance=2,
                buckner_williams_terms=[-1, 1, 2, 3, 4, 5],
            )
            crack_end = crack_length
            ct = CrackTipInfo(crack_end, height / 2, 0, "right")

            # optimization
            opt_props = OptimizationProperties(
                angle_gap=0,
                min_radius=1,
                max_radius=2,
                tick_size=0.04,
                terms=[-1, 0, 1, 2, 3, 4, 5],
            )
        # preprocess data
        nodemap_struc = NodemapStructure(10, 1, 2, 4, 5, 7, 8, 9, False, True)
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

        # plot
        plot_sets = PlotSettings(background="sig_vm", cmap="jet", dpi=300)
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

        return os.path.join(nodemap_folder, "plots", "nodemap_right.png")
