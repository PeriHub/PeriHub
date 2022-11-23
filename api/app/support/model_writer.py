"""
doc
"""
import os
import time
import numpy as np
from support.xml_creator import XMLcreator
from support.yaml_creator import YAMLcreator

from support.globals import log

# from numba import jit


class ModelWriter:
    """doc"""

    def __init__(self, model_class):
        """doc"""

        self.filename = model_class.filename
        self.meshFile = model_class.meshFile
        self.ns_name = "ns_" + model_class.filename
        self.path = "Output/" + os.path.join(model_class.username, model_class.filename)
        self.bc_dict = model_class.bc_dict
        self.damage_dict = model_class.damage_dict
        self.material_dict = model_class.material_dict
        self.compute_dict = model_class.compute_dict
        self.output_dict = model_class.output_dict
        self.solver_dict = model_class.solver_dict
        self.contact_dict = model_class.contact_dict
        self.bondfilters = model_class.bondfilters
        self.disc_type = model_class.disc_type
        self.two_d = model_class.two_d
        if not os.path.exists("Output"):
            os.mkdir("Output")

        number_of_ns = 0
        node_set_ids = []
        for bcs in self.bc_dict.conditions:
            if bcs.blockId not in node_set_ids:
                number_of_ns += 1
                node_set_ids.append(bcs.blockId)
        self.ns_list = node_set_ids

    def write_node_sets(self, model):
        """doc"""
        for idx, k in enumerate(self.ns_list):
            points = np.where(model[:, 3] == k)
            string = ""
            for point in points[0]:
                string += str(int(point) + 1) + "\n"
            self.file_writer(self.ns_name + "_" + str(idx + 1) + ".txt", string)

    def file_writer(self, filename, string):
        """doc"""
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        with open(self.path + "/" + filename, "w", encoding="UTF-8") as file:
            file.write(string)

    def mesh_file_writer(self, filename, string, mesh_array, mesh_format):
        """doc"""
        log.info("Write mesh file")
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        with open(self.path + "/" + filename, "w", encoding="UTF-8") as file:
            file.write(string)
            np.savetxt(file, mesh_array, fmt=mesh_format, delimiter=" ")

    def write_mesh(self, model):
        """doc"""
        start_time = time.time()
        string = "# x y z block_id volume\n"
        self.mesh_file_writer(
            self.filename + ".txt", string, model, "%.18e %.18e %.18e %d %.18e"
        )
        log.info(f"Mesh written  in {(time.time() - start_time):.2f} seconds")

    def write_mesh_with_angles(self, model):
        """doc"""
        start_time = time.time()
        string = "# x y z block_id volume angle_x angle_y angle_z\n"
        self.mesh_file_writer(
            self.filename + ".txt",
            string,
            model,
            "%.18e %.18e %.18e %d %.18e %.18e %.18e %.18e",
        )
        log.info(f"Mesh written  in {(time.time() - start_time):.2f} seconds")

    def create_file(self, block_def):
        """doc"""
        xml = XMLcreator(self, block_def=block_def)
        string = xml.create_xml()
        if self.solver_dict.filetype == "yaml":
            yaml = YAMLcreator(self, block_def=block_def)

            string = yaml.translate_xml_to_yaml(string)
        # else:
        #    print('Not a supported filetye: ', self.solver_dict['filetype'])

        self.file_writer(self.filename + "." + self.solver_dict.filetype, string)
