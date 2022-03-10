class YAMLcreator:
    def __init__(self, model_writer, block_def=None):
        self.filename = model_writer.filename
        self.material_dict = model_writer.material_dict
        self.damage_dict = model_writer.damage_dict
        self.compute_dict = model_writer.compute_dict
        self.output_dict = model_writer.output_dict
        self.solver_dict = model_writer.solver_dict
        self.block_def = block_def
        self.bondfilters = model_writer.bondfilters
        self.boundary_condition = model_writer.bc_dict
        self.ns_name = model_writer.ns_name
        self.ns_list = model_writer.ns_list
        self.two_d = model_writer.two_d

    @staticmethod
    def translate_xml_to_yaml(string):
        string_yaml = "Peridigm:\n"
        split_string = string.split("\n")
        for spl in split_string:
            if "</ParameterList>" not in spl and "<ParameterList>" not in spl:
                part_string = spl.split('"')
                spaces = spl.split("<")

                if len(part_string) > 3:

                    if "string" in part_string[3]:
                        temp_string = '"' + part_string[5] + '"'
                    else:
                        temp_string = part_string[5]
                    string_yaml += (
                        spaces[0] + part_string[1] + ": " + temp_string + "\n"
                    )
                elif len(part_string) != 1:
                    string_yaml += spaces[0] + part_string[1] + ": \n"

        return string_yaml
