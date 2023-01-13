# imports
import os

from crackpy.fracture_analysis.analysis import FractureAnalysis
from crackpy.fracture_analysis.data_processing import InputData, CrackTipInfo
from crackpy.fracture_analysis.line_integration import IntegralProperties
from crackpy.fracture_analysis.optimization import OptimizationProperties
from crackpy.fracture_analysis.plot import PlotSettings, Plotter
from crackpy.fracture_analysis.write import OutputWriter
from crackpy.fracture_analysis.read import OutputReader
from crackpy.structure_elements.data_files import Nodemap
from crackpy.structure_elements.material import Material

from exodusreader.exodusreader import ExodusReader
import numpy as np

class CrackAnalysis:

    @staticmethod
    def write_nodemap(file):
        reader = ExodusReader()

        points, point_data, global_data, cell_data, ns, block_data, times = reader.read_timestep(file, 0)

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
        ]

        indexes = np.arange(1, len(block_points_np)+1)

        eps_x = cell_data['Unrotated_StrainXX'][0][damage_id]

        eps_y = cell_data['Unrotated_StrainYY'][0][damage_id]

        eps_xy = cell_data['Unrotated_StrainXY'][0][damage_id]

        Y2 = np.multiply(0.5,np.add(np.add(np.multiply(eps_x, eps_x), np.multiply(eps_y, eps_y)), np.add(np.multiply(2, eps_xy, eps_xy), np.multiply(2, eps_xy))))
        # Y2 = 0.5*(e11^2 + e22^2 + 2*e12^2 + 2*e12)

        # eps_eqv = np.abs(cell_data['Unrotated_StrainXX'][0][damage_id])
        temp = np.multiply(4/3,Y2)
        eps_eqv = np.sqrt(np.abs(temp))

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
                # point_data,
                # nodesAngles[:, [0, 2, 1]],
            ],
            fmt=formatter,
            delimiter="; ",
            newline="\n",
            header=" \t ".join(headerCols),
            comments="",
        )

        return "nodemap.txt", os.path.dirname(file)

    @staticmethod
    def fracture_analysis(model_name, length, height, crack_length, young_modulus, poissions_ratio, nodemap_filename, nodemap_folder):

        # material properties
        material = Material(E=72000, nu_xy=0.33, sig_yield=350)
        material = Material(E=5000, nu_xy=0.34, sig_yield=276)
        material = Material(E=young_modulus, nu_xy=poissions_ratio, sig_yield=276)

        if model_name in ["CompactTension"]:
            int_props = IntegralProperties(
                number_of_paths=13,
                number_of_nodes=100,

                bottom_offset=-0,  # should not be zero for dic results
                top_offset=0,  # should not be zero for dic results

                integral_size_left=-4,
                integral_size_right=2,
                integral_size_top=2,
                integral_size_bottom=-2,

                paths_distance_top=0.5,
                paths_distance_left=0.5,
                paths_distance_right=0.5,
                paths_distance_bottom=0.5,

                mask_tolerance=2,

                buckner_williams_terms=[-1, 1, 2, 3, 4, 5]
            )
            crack_end = crack_length + 0.25 * length
            ct = CrackTipInfo(crack_end, 0, 0, 'right')

        elif model_name in ["KICmodel","KIICmodel"]:
            int_props = IntegralProperties(
                number_of_paths=10,
                number_of_nodes=100,

                bottom_offset=-0,  # should not be zero for dic results
                top_offset=0,  # should not be zero for dic results

                integral_size_left=-1,
                integral_size_right=1,
                integral_size_top=1,
                integral_size_bottom=-1,

                paths_distance_top=0.38,
                paths_distance_left=0.38,
                paths_distance_right=0.38,
                paths_distance_bottom=0.38,

                mask_tolerance=2,

                buckner_williams_terms=[-1, 1, 2, 3, 4, 5]
            )
            crack_end = crack_length
            ct = CrackTipInfo(crack_end, height/2, 0, 'right')

        # optimization
        opt_props = OptimizationProperties(
            angle_gap=10,
            min_radius=5,
            max_radius=10,
            tick_size=0.04,
            terms=[-1, 0, 1, 2, 3, 4, 5]
        )

        # preprocess data
        nodemap = Nodemap(name=nodemap_filename, folder=nodemap_folder)
        input_data = InputData(nodemap=nodemap)
        input_data.calc_stresses(material)
        input_data.transform_data(ct.crack_tip_x, ct.crack_tip_y, ct.crack_tip_angle)

        # fracture analysis
        analysis = FractureAnalysis(
            material=material,
            nodemap=nodemap,
            data=input_data,
            crack_tip_info=ct,
            integral_properties=int_props,
            optimization_properties=opt_props
        )
        analysis.run()

        # plot
        plot_sets = PlotSettings(background='eps_vm', cmap='jet', dpi=300)
        plotter = Plotter(path=os.path.join(nodemap_folder, 'plots'), fracture_analysis=analysis, plot_sets=plot_sets)
        plotter.plot()

        # write
        writer = OutputWriter(path=os.path.join(nodemap_folder, 'results'), fracture_analysis=analysis)
        writer.write_header()
        writer.write_results()

        return os.path.join(nodemap_folder, 'plots', "nodemap_right.png")